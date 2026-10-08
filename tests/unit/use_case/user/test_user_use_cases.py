import pytest
from unittest.mock import MagicMock
from src.application.use_case.user.invite_user import InviteUser, InviteUserData
from src.application.use_case.user.approve_user import ApproveUser, ApproveUserData
from src.application.use_case.user.remove_user import RemoveUser, RemoveUserData
from src.application.use_case.user.change_user_role import ChangeUserRole, ChangeUserRoleData
from src.application.use_case.user.get_space_users import GetSpaceUsers, GetSpaceUsersData


class TestInviteUser:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.hash_service = MagicMock()
        self.use_case = InviteUser(self.user_repo, self.hash_service)

    def test_invite_success(self):
        self.user_repo.exist_by_email.return_value = False
        self.hash_service.hash.return_value = "hashed_password"

        result = self.use_case.perform(InviteUserData(
            admin_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            first_name="Maria",
            last_name="Santos",
            email="maria@test.com",
            password="Senha@123",
        ))
        assert result.is_success
        self.user_repo.add.assert_called_once()

    def test_invite_email_already_exists(self):
        self.user_repo.exist_by_email.return_value = True

        result = self.use_case.perform(InviteUserData(
            admin_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            first_name="Maria",
            last_name="Santos",
            email="existing@test.com",
            password="Senha@123",
        ))
        assert result.is_failure

    def test_invite_invalid_user_data(self):
        result = self.use_case.perform(InviteUserData(
            admin_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
            first_name="",
            last_name="Santos",
            email="maria@test.com",
            password="Senha@123",
        ))
        assert result.is_failure


class TestApproveUser:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.use_case = ApproveUser(self.user_repo)

    def test_approve_success(self):
        mock_user = MagicMock()
        self.user_repo.find_by_id.return_value = mock_user

        result = self.use_case.perform(ApproveUserData(
            admin_id="admin-uuid",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        self.user_repo.update.assert_called_once()

    def test_approve_user_not_found(self):
        self.user_repo.find_by_id.return_value = None

        result = self.use_case.perform(ApproveUserData(
            admin_id="admin-uuid",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_failure

    def test_approve_invalid_user_id(self):
        result = self.use_case.perform(ApproveUserData(
            admin_id="admin-uuid",
            user_id="not-a-uuid",
        ))
        assert result.is_failure


class TestRemoveUser:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.use_case = RemoveUser(self.user_repo)

    def test_remove_success(self):
        mock_user = MagicMock()
        self.user_repo.find_by_id.return_value = mock_user

        result = self.use_case.perform(RemoveUserData(
            admin_id="11111111-1111-1111-1111-111111111111",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        self.user_repo.remove_by_id.assert_called_once()

    def test_remove_cannot_remove_self(self):
        result = self.use_case.perform(RemoveUserData(
            admin_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_failure

    def test_remove_user_not_found(self):
        self.user_repo.find_by_id.return_value = None

        result = self.use_case.perform(RemoveUserData(
            admin_id="11111111-1111-1111-1111-111111111111",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_failure

    def test_remove_invalid_id(self):
        result = self.use_case.perform(RemoveUserData(
            admin_id="not-a-uuid",
            user_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_failure


class TestChangeUserRole:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.use_case = ChangeUserRole(self.user_repo)

    def test_change_role_success(self):
        mock_user = MagicMock()
        self.user_repo.find_by_id.return_value = mock_user

        result = self.use_case.perform(ChangeUserRoleData(
            admin_id="admin-uuid",
            user_id="550e8400-e29b-41d4-a716-446655440000",
            new_role="admin",
        ))
        assert result.is_success
        self.user_repo.update.assert_called_once()

    def test_change_role_invalid_role(self):
        result = self.use_case.perform(ChangeUserRoleData(
            admin_id="admin-uuid",
            user_id="550e8400-e29b-41d4-a716-446655440000",
            new_role="invalid_role",
        ))
        assert result.is_failure

    def test_change_role_user_not_found(self):
        self.user_repo.find_by_id.return_value = None

        result = self.use_case.perform(ChangeUserRoleData(
            admin_id="admin-uuid",
            user_id="550e8400-e29b-41d4-a716-446655440000",
            new_role="admin",
        ))
        assert result.is_failure

    def test_change_role_invalid_user_id(self):
        result = self.use_case.perform(ChangeUserRoleData(
            admin_id="admin-uuid",
            user_id="not-a-uuid",
            new_role="admin",
        ))
        assert result.is_failure


class TestGetSpaceUsers:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.use_case = GetSpaceUsers(self.user_repo)

    def test_get_users_success(self):
        mock_user = MagicMock()
        mock_user.id = "user-123"
        mock_user.name.full_name = "Maria Santos"
        mock_user.role.role_type.value = "user"
        mock_user.is_approved = True
        mock_user.storage_used = 1024

        self.user_repo.find_all_by_space.return_value = [mock_user]

        result = self.use_case.perform(GetSpaceUsersData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert len(result.value) == 1

    def test_get_users_invalid_space_id(self):
        result = self.use_case.perform(GetSpaceUsersData(
            user_id="admin-uuid",
            space_id="not-a-uuid",
        ))
        assert result.is_failure

    def test_get_users_empty_space(self):
        self.user_repo.find_all_by_space.return_value = []

        result = self.use_case.perform(GetSpaceUsersData(
            user_id="admin-uuid",
            space_id="550e8400-e29b-41d4-a716-446655440000",
        ))
        assert result.is_success
        assert len(result.value) == 0
