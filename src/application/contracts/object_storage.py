from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import BinaryIO, Self


@dataclass(frozen=True)
class ObjectMetadata:
    id: str
    bucket: str
    key: str
    filename: str
    content_type: str
    size_bytes: int
    checksum: str
    storage_path: str
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self: Self) -> dict:
        return {
            "id": self.id,
            "bucket": self.bucket,
            "key": self.key,
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "storage_path": self.storage_path,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else str(self.updated_at),
        }


class ObjectStorageService(ABC):
    """Contrato para serviço de armazenamento de objetos (Object Store)."""

    @abstractmethod
    def put_object(
        self: Self,
        bucket: str,
        key: str,
        content: bytes,
        filename: str | None = None,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> ObjectMetadata:
        """Armazena um objeto e grava seus metadados."""
        pass

    @abstractmethod
    def get_object(self: Self, bucket: str, key: str) -> tuple[ObjectMetadata, bytes]:
        """Recupera os metadados e os bytes de um objeto."""
        pass

    @abstractmethod
    def get_object_stream(self: Self, bucket: str, key: str) -> tuple[ObjectMetadata, BinaryIO]:
        """Recupera os metadados e o stream aberto de leitura do documento."""
        pass

    @abstractmethod
    def get_metadata(self: Self, bucket: str, key: str) -> ObjectMetadata | None:
        """Recupera apenas os metadados do objeto."""
        pass

    @abstractmethod
    def get_metadata_by_id(self: Self, object_id: str) -> ObjectMetadata | None:
        """Recupera os metadados de um objeto pelo seu ID único."""
        pass

    @abstractmethod
    def delete_object(self: Self, bucket: str, key: str) -> bool:
        """Remove o documento físico e seus metadados."""
        pass

    @abstractmethod
    def list_objects(
        self: Self,
        bucket: str,
        prefix: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ObjectMetadata]:
        """Lista os metadados dos objetos em um bucket com filtro por prefixo e paginação."""
        pass

    @abstractmethod
    def exists(self: Self, bucket: str, key: str) -> bool:
        """Verifica se o objeto existe no storage e banco de metadados."""
        pass

    @abstractmethod
    def verify_integrity(self: Self, bucket: str, key: str) -> bool:
        """Verifica se o checksum SHA-256 do arquivo no filesystem bate com o registrado no SQLite."""
        pass

    @abstractmethod
    def get_file_path(self: Self, bucket: str, key: str) -> str:
        """Retorna o caminho físico do documento no sistema de arquivos."""
        pass
