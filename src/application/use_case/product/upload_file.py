from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import ProductNotExistsError, QuotaExceededError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import FileStorageService
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductFileRepository, ProductRepository, SpaceRepository, UserRepository


class UploadFileData(NamedTuple):
    user_id: str
    product_id: str
    file_name: str
    file_content: bytes
    file_type: str
    file_size: int


class UploadFile(UseCase):
    def __init__(
        self: Self,
        file_repository: ProductFileRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
        space_repository: SpaceRepository,
        file_storage: FileStorageService,
    ) -> None:
        self._file_repository = file_repository
        self._product_repository = product_repository
        self._user_repository = user_repository
        self._space_repository = space_repository
        self._file_storage = file_storage

    def perform(
        self: Self,
        parameters: UploadFileData,
    ) -> Result[dict, list[DomainError | ProductNotExistsError | QuotaExceededError]]:
        from uuid import UUID
        try:
            user_id = UUID(parameters.user_id)
            product_id = UUID(parameters.product_id)
        except ValueError:
            return Result.fail([ProductNotExistsError("Invalid ID")])

        product = self._product_repository.find_by_id(product_id)
        if product is None:
            return Result.fail([ProductNotExistsError("Product not found")])

        user = self._user_repository.find_by_id(user_id)
        if user is None:
            return Result.fail([ProductNotExistsError("User not found")])

        current_used = self._file_repository.sum_size_by_user(user_id)
        space = self._space_repository.find_by_id(user.space_id) if user.space_id else None
        if space and (current_used + parameters.file_size) > space.storage_quota:
            return Result.fail([QuotaExceededError("Storage quota exceeded")])

        file_path = self._file_storage.save(
            file_content=parameters.file_content,
            file_name=parameters.file_name,
            sub_dir=str(product_id),
        )

        from src.domain.entities import ProductFile
        from src.domain.value_objects import FileTypeVO, FileSize

        ft_result = FileTypeVO.create(file_type=parameters.file_type)
        fs_result = FileSize.create(size=parameters.file_size)
        if ft_result.is_failure:
            return ft_result
        if fs_result.is_failure:
            return fs_result

        file_result = ProductFile.create(
            file_path=file_path,
            file_name=parameters.file_name,
            file_type=parameters.file_type,
            file_size=parameters.file_size,
            product_id=product_id,
            user_id=user_id,
        )
        if file_result.is_failure:
            return file_result

        self._file_repository.add(file_result.value)
        self._user_repository.update_storage_used(user_id, current_used + parameters.file_size)

        return Result.ok({
            "file_id": str(file_result.value.id),
            "file_name": parameters.file_name,
        })

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: UploadFileData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
