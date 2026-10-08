import pytest
from unittest.mock import MagicMock
from src.application.use_case.auth.register_user import RegisterUser, RegistrationData
from src.application.use_case.auth.login import LoginUseCase, Credential
from src.application.use_case.auth.change_password import ChangePassword, ChangePasswordData
from src.application.use_case.auth.request_password_reset import RequestPasswordReset, RequestResetData
from src.application.use_case.auth.reset_password import ResetPassword, ResetPasswordData
from src.domain.entities import Space, User, Account


class TestRegisterUser:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.space_repo = MagicMock()
        self.hash_service = MagicMock()
        self.use_case = RegisterUser(self.user_repo, self.space_repo, self.hash_service)

    def test_register_success(self):
        self.user_repo.exist_by_email.return_value = False
        self.hash_service.hash.return_value = "hashed_password_123"

        result = self.use_case.perform(RegistrationData(
            first_name="João",
            last_name="Silva",
            email="joao@test.com",
            password="Senha@123",
            space_name="Minha Casa",
            space_address="Rua A, 123",
            utility_unit_number="12345",
        ))
        assert result.is_success
        self.space_repo.add.assert_called_once()
        self.user_repo.add.assert_called_once()

    def test_register_already_exists(self):
        self.user_repo.exist_by_email.return_value = True

        result = self.use_case.perform(RegistrationData(
            first_name="João",
            last_name="Silva",
            email="joao@test.com",
            password="Senha@123",
            space_name="Minha Casa",
            space_address="Rua A, 123",
            utility_unit_number="12345",
        ))
        assert result.is_failure


class TestLoginUseCase:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.hash_service = MagicMock()
        self.token_manager = MagicMock()
        self.use_case = LoginUseCase(self.user_repo, self.hash_service, self.token_manager)

    def test_login_success(self):
        mock_account = MagicMock()
        mock_account.email.address = "joao@test.com"
        mock_account.password.passphrase = "hashed_pass"
        mock_account.user_id = "user-123"

        mock_user = MagicMock()
        mock_user.role.role_type.value = "user"
        mock_user.id = "user-123"

        self.user_repo.find_account_by_email.return_value = mock_account
        self.hash_service.verify.return_value = True
        self.user_repo.find_by_id.return_value = mock_user
        self.token_manager.create.return_value = "jwt-token-123"

        result = self.use_case.perform(Credential(
            email="joao@test.com",
            password="Senha@123",
        ))
        assert result.is_success
        assert result.value["access_token"] == "jwt-token-123"

    def test_login_wrong_password(self):
        mock_account = MagicMock()
        mock_account.password.passphrase = "hashed_pass"

        self.user_repo.find_account_by_email.return_value = mock_account
        self.hash_service.verify.return_value = False

        result = self.use_case.perform(Credential(
            email="joao@test.com",
            password="Wrong@123",
        ))
        assert result.is_failure


class TestChangePassword:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.hash_service = MagicMock()
        self.use_case = ChangePassword(self.user_repo, self.hash_service)

    def test_change_password_success(self):
        mock_account = MagicMock()
        mock_account.password.passphrase = "old_hashed"

        self.user_repo.find_account_by_user_id.return_value = mock_account
        self.hash_service.verify.return_value = True
        self.hash_service.hash.return_value = "new_hashed"

        result = self.use_case.perform(ChangePasswordData(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            current_password="Old@1234",
            new_password="New@1234",
        ))
        assert result.is_success
        self.user_repo.update_account.assert_called_once()

    def test_change_password_wrong_current(self):
        mock_account = MagicMock()
        mock_account.password.passphrase = "old_hashed"

        self.user_repo.find_account_by_user_id.return_value = mock_account
        self.hash_service.verify.return_value = False

        result = self.use_case.perform(ChangePasswordData(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            current_password="Wrong@123",
            new_password="New@1234",
        ))
        assert result.is_failure

    def test_change_password_user_not_found(self):
        self.user_repo.find_account_by_user_id.return_value = None

        result = self.use_case.perform(ChangePasswordData(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            current_password="Old@1234",
            new_password="New@1234",
        ))
        assert result.is_failure

    def test_change_password_invalid_user_id(self):
        result = self.use_case.perform(ChangePasswordData(
            user_id="not-a-uuid",
            current_password="Old@1234",
            new_password="New@1234",
        ))
        assert result.is_failure

    def test_change_password_invalid_new_password(self):
        mock_account = MagicMock()
        mock_account.password.passphrase = "old_hashed"

        self.user_repo.find_account_by_user_id.return_value = mock_account
        self.hash_service.verify.return_value = True

        result = self.use_case.perform(ChangePasswordData(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            current_password="Old@1234",
            new_password="weak",
        ))
        assert result.is_failure


class TestRequestPasswordReset:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.use_case = RequestPasswordReset(self.user_repo)

    def test_request_reset_email_exists(self):
        mock_account = MagicMock()
        self.user_repo.find_account_by_email.return_value = mock_account

        result = self.use_case.perform(RequestResetData(email="joao@test.com"))
        assert result.is_success
        assert "reset_token" in result.value
        self.user_repo.update_account.assert_called_once()

    def test_request_reset_email_not_exists(self):
        self.user_repo.find_account_by_email.return_value = None

        result = self.use_case.perform(RequestResetData(email="noone@test.com"))
        assert result.is_success
        assert "reset_token" not in result.value

    def test_request_reset_invalid_email(self):
        result = self.use_case.perform(RequestResetData(email="invalid"))
        assert result.is_failure


class TestResetPassword:
    def setup_method(self):
        self.user_repo = MagicMock()
        self.hash_service = MagicMock()
        self.use_case = ResetPassword(self.user_repo, self.hash_service)

    def test_reset_password_success(self):
        mock_account = MagicMock()
        mock_account.reset_token_expiry = None

        self.user_repo.find_account_by_reset_token.return_value = mock_account
        self.hash_service.hash.return_value = "new_hashed"

        result = self.use_case.perform(ResetPasswordData(
            token="valid-token-123",
            new_password="New@1234",
        ))
        assert result.is_success
        self.user_repo.update_account.assert_called_once()

    def test_reset_password_invalid_token(self):
        self.user_repo.find_account_by_reset_token.return_value = None

        result = self.use_case.perform(ResetPasswordData(
            token="invalid-token",
            new_password="New@1234",
        ))
        assert result.is_failure

    def test_reset_password_empty_token(self):
        result = self.use_case.perform(ResetPasswordData(
            token="",
            new_password="New@1234",
        ))
        assert result.is_failure

    def test_reset_password_weak_new_password(self):
        mock_account = MagicMock()
        mock_account.reset_token_expiry = None

        self.user_repo.find_account_by_reset_token.return_value = mock_account

        result = self.use_case.perform(ResetPasswordData(
            token="valid-token-123",
            new_password="weak",
        ))
        assert result.is_failure
