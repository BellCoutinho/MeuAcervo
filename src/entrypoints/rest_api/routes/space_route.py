from fastapi import APIRouter, Depends, HTTPException, status

from src.entrypoints.rest_api.dependencies import get_current_user, require_admin
from src.entrypoints.rest_api.schemas.space import UpdateSpaceRequest
from src.main.factories.space_repository_factory import make_space_repository
from src.main.factories.user_repository_factory import make_user_repository

router = APIRouter(prefix="/api/space", tags=["space"])


@router.get("")
def get_space(user: dict = Depends(get_current_user)):
    from src.main.factories.space_repository_factory import make_space_repository
    space_repo = make_space_repository()
    from uuid import UUID
    space = space_repo.find_by_user_id(UUID(user["id"]))
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")
    return {
        "space_id": str(space.id),
        "name": space.name.name,
        "address": space.address.address,
        "utility_unit_number": space.utility_unit_number.number,
        "storage_quota": space.storage_quota,
    }


@router.put("")
def update_space(data: UpdateSpaceRequest, user: dict = Depends(require_admin)):
    from src.application.use_case.space.update_space import UpdateSpace, UpdateSpaceData
    from uuid import UUID
    user_repo = make_user_repository()
    user_entity = user_repo.find_by_id(UUID(user["id"]))
    if user_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    space_id = str(user_entity.space_id) if user_entity.space_id else ""
    use_case = UpdateSpace(make_space_repository())
    result = use_case.perform(UpdateSpaceData(
        user_id=user["id"],
        space_id=space_id,
        name=data.name,
        address=data.address,
        utility_unit_number=data.utility_unit_number,
        storage_quota=data.storage_quota,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return {"message": "Espaço atualizado com sucesso"}


@router.get("/storage-info")
def get_storage_info(user: dict = Depends(require_admin)):
    from src.application.use_case.space.get_space_storage_info import GetSpaceStorageInfo, GetStorageInfoData
    from uuid import UUID
    user_repo = make_user_repository()
    user_entity = user_repo.find_by_id(UUID(user["id"]))
    if user_entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    space_id = str(user_entity.space_id) if user_entity.space_id else ""
    use_case = GetSpaceStorageInfo(make_space_repository(), user_repo)
    result = use_case.perform(GetStorageInfoData(
        user_id=user["id"],
        space_id=space_id,
    ))
    if result.is_failure:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(result.error))
    return result.value
