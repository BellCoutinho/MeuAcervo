from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import BinaryIO, Self
from uuid import uuid4

from src.application.contracts.file_storage import FileStorageService
from src.application.contracts.object_storage import ObjectMetadata, ObjectStorageService


class SqliteFsObjectStore(ObjectStorageService, FileStorageService):
    """
    Object Store que utiliza:
    - SQLite para persistir metadados, índices, checksums e informações dos objetos.
    - Sistema de arquivos local (Filesystem) para persistir o conteúdo binário (documentos).
    """

    def __init__(
        self: Self,
        base_dir: str | None = None,
        db_path: str | None = None,
    ) -> None:
        self._base_dir = os.path.abspath(
            base_dir or os.environ.get("OBJECT_STORE_DIR", "./data/storage/blobs")
        )
        self._db_path = os.path.abspath(
            db_path or os.environ.get("OBJECT_STORE_DB", "./data/storage/metadata.db")
        )

        os.makedirs(self._base_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)

        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self: Self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self: Self) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS object_metadata (
                    id TEXT PRIMARY KEY,
                    bucket TEXT NOT NULL,
                    key TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(bucket, key)
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_objects_bucket ON object_metadata(bucket);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_objects_bucket_key ON object_metadata(bucket, key);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_objects_checksum ON object_metadata(checksum);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_objects_storage_path ON object_metadata(storage_path);")
            conn.commit()

    @staticmethod
    def _calculate_checksum(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _resolve_storage_path(self: Self, bucket: str, key: str, object_id: str, ext: str) -> str:
        clean_bucket = "".join(c for c in bucket if c.isalnum() or c in ("-", "_")).strip() or "default"
        bucket_dir = os.path.join(self._base_dir, clean_bucket)
        os.makedirs(bucket_dir, exist_ok=True)

        prefix = object_id[:2]
        partition_dir = os.path.join(bucket_dir, prefix)
        os.makedirs(partition_dir, exist_ok=True)

        file_disk_name = f"{object_id}{ext}"
        return os.path.join(partition_dir, file_disk_name)

    def put_object(
        self: Self,
        bucket: str,
        key: str,
        content: bytes,
        filename: str | None = None,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> ObjectMetadata:
        """
        Armazena o documento binário no sistema de arquivos e registra seus metadados no SQLite.
        Utiliza escrita atômica para evitar arquivos corrompidos.
        """
        now = datetime.now(timezone.utc).isoformat()
        resolved_filename = filename or os.path.basename(key) or "unnamed_object"
        ext = os.path.splitext(resolved_filename)[1]

        if not content_type:
            guessed_type, _ = mimetypes.guess_type(resolved_filename)
            content_type = guessed_type or "application/octet-stream"

        size_bytes = len(content)
        checksum = self._calculate_checksum(content)
        metadata_dict = metadata or {}
        metadata_json = json.dumps(metadata_dict)

        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, storage_path, created_at FROM object_metadata WHERE bucket = ? AND key = ?",
                (bucket, key),
            )
            existing = cursor.fetchone()

            if existing:
                object_id = existing["id"]
                storage_path = existing["storage_path"]
                created_at = existing["created_at"]
            else:
                object_id = str(uuid4())
                storage_path = self._resolve_storage_path(bucket, key, object_id, ext)
                created_at = now

            # Escrita atômica no sistema de arquivos
            tmp_storage_path = f"{storage_path}.tmp.{uuid4().hex}"
            try:
                with open(tmp_storage_path, "wb") as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_storage_path, storage_path)
            except Exception as e:
                if os.path.exists(tmp_storage_path):
                    os.remove(tmp_storage_path)
                raise IOError(f"Falha ao salvar o documento no sistema de arquivos: {e}") from e

            # Persistência de metadados no SQLite
            cursor.execute("""
                INSERT INTO object_metadata(
                    id, bucket, key, filename, content_type, size_bytes,
                    checksum, storage_path, metadata_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bucket, key) DO UPDATE SET
                    filename = excluded.filename,
                    content_type = excluded.content_type,
                    size_bytes = excluded.size_bytes,
                    checksum = excluded.checksum,
                    storage_path = excluded.storage_path,
                    metadata_json = excluded.metadata_json,
                    updated_at = excluded.updated_at;
            """, (
                object_id,
                bucket,
                key,
                resolved_filename,
                content_type,
                size_bytes,
                checksum,
                storage_path,
                metadata_json,
                created_at,
                now,
            ))
            conn.commit()

        return ObjectMetadata(
            id=object_id,
            bucket=bucket,
            key=key,
            filename=resolved_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            checksum=checksum,
            storage_path=storage_path,
            metadata=metadata_dict,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(now),
        )

    def get_object(self: Self, bucket: str, key: str) -> tuple[ObjectMetadata, bytes]:
        meta = self.get_metadata(bucket, key)
        if not meta:
            raise FileNotFoundError(f"Objeto não encontrado: {bucket}/{key}")

        if not os.path.exists(meta.storage_path):
            raise FileNotFoundError(f"Arquivo binário não encontrado no disco: {meta.storage_path}")

        with open(meta.storage_path, "rb") as f:
            content = f.read()

        return meta, content

    def get_object_stream(self: Self, bucket: str, key: str) -> tuple[ObjectMetadata, BinaryIO]:
        meta = self.get_metadata(bucket, key)
        if not meta:
            raise FileNotFoundError(f"Objeto não encontrado: {bucket}/{key}")

        if not os.path.exists(meta.storage_path):
            raise FileNotFoundError(f"Arquivo binário não encontrado no disco: {meta.storage_path}")

        return meta, open(meta.storage_path, "rb")

    def get_metadata(self: Self, bucket: str, key: str) -> ObjectMetadata | None:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, bucket, key, filename, content_type, size_bytes,
                       checksum, storage_path, metadata_json, created_at, updated_at
                FROM object_metadata
                WHERE bucket = ? AND key = ?
                """,
                (bucket, key),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._map_row_to_metadata(row)

    def get_metadata_by_id(self: Self, object_id: str) -> ObjectMetadata | None:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, bucket, key, filename, content_type, size_bytes,
                       checksum, storage_path, metadata_json, created_at, updated_at
                FROM object_metadata
                WHERE id = ?
                """,
                (object_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._map_row_to_metadata(row)

    def delete_object(self: Self, bucket: str, key: str) -> bool:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT storage_path FROM object_metadata WHERE bucket = ? AND key = ?",
                (bucket, key),
            )
            row = cursor.fetchone()
            if not row:
                return False

            storage_path = row["storage_path"]

            cursor.execute(
                "DELETE FROM object_metadata WHERE bucket = ? AND key = ?",
                (bucket, key),
            )
            conn.commit()

        if os.path.exists(storage_path):
            try:
                os.remove(storage_path)
            except OSError:
                pass

        return True

    def list_objects(
        self: Self,
        bucket: str,
        prefix: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ObjectMetadata]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            if prefix:
                cursor.execute(
                    """
                    SELECT id, bucket, key, filename, content_type, size_bytes,
                           checksum, storage_path, metadata_json, created_at, updated_at
                    FROM object_metadata
                    WHERE bucket = ? AND key LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (bucket, f"{prefix}%", limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, bucket, key, filename, content_type, size_bytes,
                           checksum, storage_path, metadata_json, created_at, updated_at
                    FROM object_metadata
                    WHERE bucket = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (bucket, limit, offset),
                )
            rows = cursor.fetchall()
            return [self._map_row_to_metadata(row) for row in rows]

    def exists(self: Self, bucket: str, key: str) -> bool:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM object_metadata WHERE bucket = ? AND key = ?",
                (bucket, key),
            )
            return cursor.fetchone() is not None

    def verify_integrity(self: Self, bucket: str, key: str) -> bool:
        meta = self.get_metadata(bucket, key)
        if not meta:
            return False

        if not os.path.exists(meta.storage_path):
            return False

        try:
            sha = hashlib.sha256()
            with open(meta.storage_path, "rb") as f:
                while chunk := f.read(65536):
                    sha.update(chunk)
            return sha.hexdigest() == meta.checksum
        except OSError:
            return False

    def get_file_path(self: Self, bucket: str, key: str) -> str:
        meta = self.get_metadata(bucket, key)
        if not meta:
            raise FileNotFoundError(f"Objeto não encontrado: {bucket}/{key}")
        return meta.storage_path

    # =========================================================================
    # Implementação da interface FileStorageService (Retrocompatibilidade)
    # =========================================================================

    def save(self: Self, file_content: bytes, file_name: str, sub_dir: str) -> str:
        """
        Salva o documento através do object store usando sub_dir como bucket.
        Retorna o storage_path para manter total compatibilidade com FileStorageService.
        """
        ext = os.path.splitext(file_name)[1]
        unique_key = f"{uuid4().hex}{ext}"
        bucket = sub_dir or "default"

        meta = self.put_object(
            bucket=bucket,
            key=unique_key,
            content=file_content,
            filename=file_name,
            metadata={"original_name": file_name, "sub_dir": sub_dir},
        )
        return meta.storage_path

    def delete(self: Self, file_path: str) -> bool:
        """
        Remove o documento pelo seu caminho físico e remove os metadados do SQLite.
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT bucket, key FROM object_metadata WHERE storage_path = ?",
                (file_path,),
            )
            row = cursor.fetchone()

            if row:
                bucket, key = row["bucket"], row["key"]
                cursor.execute(
                    "DELETE FROM object_metadata WHERE bucket = ? AND key = ?",
                    (bucket, key),
                )
                conn.commit()

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False

        return row is not None

    def get_path(self: Self, file_path: str) -> str:
        return file_path

    # =========================================================================
    # Helpers
    # =========================================================================

    def _map_row_to_metadata(self: Self, row: sqlite3.Row) -> ObjectMetadata:
        try:
            extra_meta = json.loads(row["metadata_json"])
        except (ValueError, TypeError):
            extra_meta = {}

        return ObjectMetadata(
            id=row["id"],
            bucket=row["bucket"],
            key=row["key"],
            filename=row["filename"],
            content_type=row["content_type"],
            size_bytes=row["size_bytes"],
            checksum=row["checksum"],
            storage_path=row["storage_path"],
            metadata=extra_meta,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
