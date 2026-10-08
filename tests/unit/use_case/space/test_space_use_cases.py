import pytest
from unittest.mock import MagicMock
from src.application.use_case.space.update_space import UpdateSpace, UpdateSpaceData
from src.application.use_case.space.get_space_storage_info import GetSpaceStorageInfo, GetStorageInfoData


class TestUpdateSpace:
    def setup_method(self):
        self.space_repo = MagicMock()
        self.use_case = UpdateSpace(self.space_repo)

    def test_update_name_success(self):
        mock_space = MagicMock()
        self.space_repo.find_by_id.return_value = mock_space

        result = self.use_case.perform(UpdateSpaceData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            name="Novo Nome",
        ))
        assert result.is_success
        self.space_repo.update.assert_called_once()

    def test_update_space_not_found(self):
        self.space_repo.find_by_id.return_value = None

        result = self.use_case.perform(UpdateSpaceData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            name="Novo Nome",
        ))
        assert result.is_failure

    def test_update_invalid_space_id(self):
        result = self.use_case.perform(UpdateSpaceData(
            user_id="admin-uuid",
            space_id="not-a-uuid",
            name="Novo Nome",
        ))
        assert result.is_failure

    def test_update_storage_quota(self):
        mock_space = MagicMock()
        self.space_repo.find_by_id.return_value = mock_space

        result = self.use_case.perform(UpdateSpaceData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            storage_quota=2147483648,
        ))
        assert result.is_success

    def test_update_address_success(self):
        mock_space = MagicMock()
        self.space_repo.find_by_id.return_value = mock_space

        result = self.use_case.perform(UpdateSpaceData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            address="Rua Nova, 456",
        ))
        assert result.is_success


class TestGetSpaceStorageInfo:
    def setup_method(self):
        self.space_repo = MagicMock()
        self.user_repo = MagicMock()
        self.use_case = GetSpaceStorageInfo(self.space_repo, self.user_repo)

    def test_get_storage_info_success(self):
        mock_space = MagicMock()
        mock_space.id = "space-123"
        mock_space.storage_quota = 1073741824

        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.name.full_name = "Maria Santos"
        mock_user.storage_used = 512

        self.space_repo.find_by_id.return_value = mock_space
        self.user_repo.find_all_by_space.return_value = [mock_user]

        result = self.use_case.perform(GetStorageInfoData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert result.value["total_used"] == 512

    def test_get_storage_info_space_not_found(self):
        self.space_repo.find_by_id.return_value = None

        result = self.use_case.perform(GetStorageInfoData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_failure

    def test_get_storage_info_invalid_space_id(self):
        result = self.use_case.perform(GetStorageInfoData(
            user_id="admin-uuid",
            space_id="not-a-uuid",
        ))
        assert result.is_failure

    def test_get_storage_info_no_users(self):
        mock_space = MagicMock()
        mock_space.id = "space-123"
        mock_space.storage_quota = 1073741824

        self.space_repo.find_by_id.return_value = mock_space
        self.user_repo.find_all_by_space.return_value = []

        result = self.use_case.perform(GetStorageInfoData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert result.value["total_used"] == 0
