import os
import shutil
import tempfile
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.application.use_case.product.delete_file import DeleteFile, DeleteFileData
from src.application.use_case.product.upload_file import UploadFile, UploadFileData
from src.domain.entities import Product, ProductFile, Space, User
from src.domain.value_objects import Date, Email, FileSize, FileTypeVO, Name, Role, UniqueId
from src.infrastructure.storage.sqlite_fs_object_store import SqliteFsObjectStore


class TestUploadAndDeleteFileWithSqliteFsObjectStore:

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        self.temp_dir = tempfile.mkdtemp()
        self.blobs_dir = os.path.join(self.temp_dir, "blobs")
        self.db_path = os.path.join(self.temp_dir, "metadata.db")
        self.storage = SqliteFsObjectStore(base_dir=self.blobs_dir, db_path=self.db_path)

        self.file_repo = MagicMock()
        self.product_repo = MagicMock()
        self.user_repo = MagicMock()
        self.space_repo = MagicMock()

        self.upload_uc = UploadFile(
            file_repository=self.file_repo,
            product_repository=self.product_repo,
            user_repository=self.user_repo,
            space_repository=self.space_repo,
            file_storage=self.storage,
        )

        self.delete_uc = DeleteFile(
            file_repository=self.file_repo,
            user_repository=self.user_repo,
            file_storage=self.storage,
        )

        yield
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_upload_and_delete_file_flow_with_object_store(self):
        user_id = uuid4()
        product_id = uuid4()
        space_id = uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.space_id = space_id
        self.user_repo.find_by_id.return_value = mock_user

        mock_product = MagicMock()
        mock_product.id = product_id
        self.product_repo.find_by_id.return_value = mock_product

        mock_space = MagicMock()
        mock_space.storage_quota = 10_000_000
        self.space_repo.find_by_id.return_value = mock_space

        self.file_repo.sum_size_by_user.return_value = 0

        file_bytes = b"%PDF-1.4 Exemplo de Nota Fiscal"
        upload_data = UploadFileData(
            user_id=str(user_id),
            product_id=str(product_id),
            file_name="nf_compra.pdf",
            file_content=file_bytes,
            file_type="nf",
            file_size=len(file_bytes),
        )

        # 1. Executa upload
        result = self.upload_uc.perform(upload_data)
        assert result.is_success
        file_id = result.value["file_id"]
        assert result.value["file_name"] == "nf_compra.pdf"

        # Verifica chamada ao repositório
        self.file_repo.add.assert_called_once()
        added_file: ProductFile = self.file_repo.add.call_args[0][0]
        saved_file_path = added_file.file_path

        # Verifica que o documento está fisicamente no filesystem
        assert os.path.exists(saved_file_path)

        # Verifica que o SQLite do Object Store registrou o arquivo
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM object_metadata WHERE storage_path = ?", (saved_file_path,))
            row = cursor.fetchone()
            assert row is not None
            assert row["filename"] == "nf_compra.pdf"
            assert row["size_bytes"] == len(file_bytes)

        # 2. Executa delete
        self.file_repo.find_by_id.return_value = added_file
        delete_data = DeleteFileData(user_id=str(user_id), file_id=file_id)
        delete_result = self.delete_uc.perform(delete_data)

        assert delete_result.is_success
        assert not os.path.exists(saved_file_path)

        # Verifica que os metadados no SQLite também foram removidos
        with self.storage._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM object_metadata WHERE storage_path = ?", (saved_file_path,))
            assert cursor.fetchone() is None
