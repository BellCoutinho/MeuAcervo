from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from src.entrypoints.rest_api.dependencies import get_current_user, require_admin
from src.entrypoints.rest_api.schemas.auth import (
    RegisterRequest, LoginRequest, ChangePasswordRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
)
from src.main.factories.user_repository_factory import make_user_repository
from src.main.factories.space_repository_factory import make_space_repository
from src.main.factories.hash_service_factory import make_hash_service
from src.main.factories.token_manager_factory import make_token_manager

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    from src.application.use_case.auth.register_user import RegisterUser, RegistrationData
    use_case = RegisterUser(make_user_repository(), make_space_repository(), make_hash_service())
    result = use_case.perform(RegistrationData(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password,
        space_name=data.space_name,
        space_address=data.space_address,
        utility_unit_number=data.utility_unit_number,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.post("/login")
def login(data: LoginRequest):
    from src.application.use_case.auth.login import LoginUseCase, Credential
    use_case = LoginUseCase(make_user_repository(), make_hash_service(), make_token_manager())
    result = use_case.perform(Credential(email=data.email, password=data.password))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(result.error))
    return result.value


@router.patch("/change-password")
def change_password(data: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    from src.application.use_case.auth.change_password import ChangePassword, ChangePasswordData
    use_case = ChangePassword(make_user_repository(), make_hash_service())
    result = use_case.perform(ChangePasswordData(
        user_id=user["id"],
        current_password=data.current_password,
        new_password=data.new_password,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Senha alterada com sucesso"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    from src.application.use_case.auth.request_password_reset import RequestPasswordReset, RequestResetData
    use_case = RequestPasswordReset(make_user_repository())
    result = use_case.perform(RequestResetData(email=data.email))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    from src.application.use_case.auth.reset_password import ResetPassword, ResetPasswordData
    use_case = ResetPassword(make_user_repository(), make_hash_service())
    result = use_case.perform(ResetPasswordData(token=data.token, new_password=data.new_password))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Senha redefinida com sucesso"}
