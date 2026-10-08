from fastapi import APIRouter, Depends, HTTPException, status

from src.entrypoints.rest_api.dependencies import get_current_user, require_admin
from src.entrypoints.rest_api.schemas.user import InviteUserRequest, ChangeUserRoleRequest
from src.main.factories.user_repository_factory import make_user_repository
from src.main.factories.hash_service_factory import make_hash_service

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/invite")
def invite_user(data: InviteUserRequest, admin: dict = Depends(require_admin)):
    from src.application.use_case.user.invite_user import InviteUser, InviteUserData
    use_case = InviteUser(make_user_repository(), make_hash_service())
    result = use_case.perform(InviteUserData(
        admin_id=admin["id"],
        space_id=data.space_id,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value


@router.post("/approve/{user_id}")
def approve_user(user_id: str, admin: dict = Depends(require_admin)):
    from src.application.use_case.user.approve_user import ApproveUser, ApproveUserData
    use_case = ApproveUser(make_user_repository())
    result = use_case.perform(ApproveUserData(admin_id=admin["id"], user_id=user_id))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Usuário aprovado com sucesso"}


@router.delete("/{user_id}")
def remove_user(user_id: str, admin: dict = Depends(require_admin)):
    from src.application.use_case.user.remove_user import RemoveUser, RemoveUserData
    use_case = RemoveUser(make_user_repository())
    result = use_case.perform(RemoveUserData(admin_id=admin["id"], user_id=user_id))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Usuário removido com sucesso"}


@router.patch("/{user_id}/role")
def change_role(user_id: str, data: ChangeUserRoleRequest, admin: dict = Depends(require_admin)):
    from src.application.use_case.user.change_user_role import ChangeUserRole, ChangeUserRoleData
    use_case = ChangeUserRole(make_user_repository())
    result = use_case.perform(ChangeUserRoleData(
        admin_id=admin["id"],
        user_id=user_id,
        new_role=data.new_role,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Perfil atualizado com sucesso"}


@router.get("/all")
def get_all_users(user: dict = Depends(require_admin)):
    from src.application.use_case.user.get_space_users import GetSpaceUsers, GetSpaceUsersData
    from uuid import UUID
    user_repo = make_user_repository()
    user_entity = user_repo.find_by_id(UUID(user["id"]))
    if user_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    space_id = str(user_entity.space_id) if user_entity.space_id else ""
    use_case = GetSpaceUsers(user_repo)
    result = use_case.perform(GetSpaceUsersData(
        user_id=user["id"],
        space_id=space_id,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value
