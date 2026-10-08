import hashlib
import os
import shutil
import tempfile
import pytest

from src.infrastructure.storage.sqlite_fs_object_store import SqliteFsObjectStore


class TestSqliteFsObjectStore:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        self.temp_dir = tempfile.mkdtemp()
        self.blobs_dir = os.path.join(self.temp_dir, "blobs")
        self.db_path = os.path.join(self.temp_dir, "metadata.db")
        self.store = SqliteFsObjectStore(base_dir=self.blobs_dir, db_path=self.db_path)
        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_directories_and_sqlite_schema(self):
        assert os.path.exists(self.blobs_dir)
        assert os.path.exists(self.db_path)

        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='object_metadata';")
            assert cursor.fetchone() is not None

    def test_put_and_get_object_success(self):
        content = b"Conteudo do documento de teste para o object store"
        meta = self.store.put_object(
            bucket="documents",
            key="doc1.pdf",
            content=content,
            filename="documento_original.pdf",
            content_type="application/pdf",
            metadata={"autor": "Joao", "versao": 1},
        )

        assert meta.bucket == "documents"
        assert meta.key == "doc1.pdf"
        assert meta.filename == "documento_original.pdf"
        assert meta.content_type == "application/pdf"
        assert meta.size_bytes == len(content)
        assert meta.checksum == hashlib.sha256(content).hexdigest()
        assert meta.metadata == {"autor": "Joao", "versao": 1}
        assert os.path.exists(meta.storage_path)

        # Recupera objeto
        retrieved_meta, retrieved_content = self.store.get_object(bucket="documents", key="doc1.pdf")
        assert retrieved_meta.id == meta.id
        assert retrieved_content == content

    def test_get_object_stream(self):
        content = b"Streamable payload binary data"
        self.store.put_object(bucket="media", key="video.mp4", content=content)

        meta, stream = self.store.get_object_stream(bucket="media", key="video.mp4")
        try:
            read_bytes = stream.read()
            assert read_bytes == content
        finally:
            stream.close()

    def test_get_metadata_by_key_and_by_id(self):
        content = b"Apenas metadados"
        created = self.store.put_object(
            bucket="invoices",
            key="inv-001.xml",
            content=content,
            metadata={"status": "paid"},
        )

        by_key = self.store.get_metadata(bucket="invoices", key="inv-001.xml")
        assert by_key is not None
        assert by_key.id == created.id
        assert by_key.metadata == {"status": "paid"}

        by_id = self.store.get_metadata_by_id(created.id)
        assert by_id is not None
        assert by_id.key == "inv-001.xml"

    def test_put_object_upsert(self):
        initial = self.store.put_object(
            bucket="docs",
            key="relatorio.txt",
            content=b"Versao 1",
            metadata={"v": 1},
        )
        updated = self.store.put_object(
            bucket="docs",
            key="relatorio.txt",
            content=b"Versao 2 com mais informacoes",
            metadata={"v": 2},
        )

        assert initial.id == updated.id
        assert updated.size_bytes == len(b"Versao 2 com mais informacoes")
        assert updated.metadata == {"v": 2}

        _, content = self.store.get_object("docs", "relatorio.txt")
        assert content == b"Versao 2 com mais informacoes"

    def test_delete_object_removes_file_and_metadata(self):
        content = b"Arquivo a ser removido"
        meta = self.store.put_object(bucket="temp", key="to_delete.txt", content=content)
        assert os.path.exists(meta.storage_path)

        deleted = self.store.delete_object(bucket="temp", key="to_delete.txt")
        assert deleted is True

        # Arquivo no disco foi apagado
        assert not os.path.exists(meta.storage_path)

        # Metadados no SQLite foram apagados
        assert self.store.get_metadata(bucket="temp", key="to_delete.txt") is None
        assert not self.store.exists(bucket="temp", key="to_delete.txt")

        # Deletar novamente retorna False
        assert self.store.delete_object(bucket="temp", key="to_delete.txt") is False

    def test_list_objects_and_prefix_filter(self):
        self.store.put_object(bucket="assets", key="images/logo.png", content=b"img1")
        self.store.put_object(bucket="assets", key="images/banner.jpg", content=b"img2")
        self.store.put_object(bucket="assets", key="docs/terms.pdf", content=b"doc1")

        all_assets = self.store.list_objects(bucket="assets")
        assert len(all_assets) == 3

        images_only = self.store.list_objects(bucket="assets", prefix="images/")
        assert len(images_only) == 2
        keys = [item.key for item in images_only]
        assert "images/logo.png" in keys
        assert "images/banner.jpg" in keys

    def test_verify_integrity(self):
        content = b"Conteudo confiavel"
        meta = self.store.put_object(bucket="security", key="safe.dat", content=content)

        # Integridade verificada com sucesso
        assert self.store.verify_integrity(bucket="security", key="safe.dat") is True

        # Simular corrupcao fisica do documento no disco
        with open(meta.storage_path, "wb") as f:
            f.write(b"Conteudo alterado indevidamente!")

        # Integridade falha devido a discrepancia no SHA-256
        assert self.store.verify_integrity(bucket="security", key="safe.dat") is False

    def test_file_storage_service_compatibility_methods(self):
        content = b"Conteudo usando a interface compativel"
        file_path = self.store.save(
            file_content=content,
            file_name="contrato.pdf",
            sub_dir="contracts_space",
        )

        assert os.path.exists(file_path)
        assert self.store.get_path(file_path) == file_path

        # Verifica se os metadados foram salvos no SQLite
        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM object_metadata WHERE storage_path = ?", (file_path,))
            row = cursor.fetchone()
            assert row is not None
            assert row["filename"] == "contrato.pdf"
            assert row["bucket"] == "contracts_space"

        # Deletar via caminho fisico
        deleted = self.store.delete(file_path)
        assert deleted is True
        assert not os.path.exists(file_path)

        with self.store._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM object_metadata WHERE storage_path = ?", (file_path,))
            assert cursor.fetchone() is None
