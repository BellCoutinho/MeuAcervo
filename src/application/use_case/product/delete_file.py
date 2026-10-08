from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Self

from src.application.use_case.errors import FileNotExistsError
from src.application.contracts import UseCase
from src.shared import Result

if TYPE_CHECKING:
    from src.application.contracts import FileStorageService
    from src.domain.contracts import DomainError
    from src.domain.repositories import ProductFileRepository, UserRepository


class DeleteFileData(NamedTuple):
    user_id: str
    file_id: str


class DeleteFile(UseCase):
    def __init__(
        self: Self,
        file_repository: ProductFileRepository,
        user_repository: UserRepository,
        file_storage: FileStorageService,
    ) -> None:
        self._file_repository = file_repository
        self._user_repository = user_repository
        self._file_storage = file_storage

    def perform(
        self: Self,
        parameters: DeleteFileData,
    ) -> Result[bool, list[DomainError | FileNotExistsError]]:
        from uuid import UUID
        try:
            file_id = UUID(parameters.file_id)
        except ValueError:
            return Result.fail([FileNotExistsError("Invalid file ID")])

        file = self._file_repository.find_by_id(file_id)
        if file is None:
            return Result.fail([FileNotExistsError("File not found")])

        self._file_storage.delete(file.file_path)
        self._file_repository.remove_by_id(file_id)

        if file.user_id:
            current_used = self._file_repository.sum_size_by_user(file.user_id)
            self._user_repository.update_storage_used(file.user_id, current_used)

        return Result.ok(True)

    @classmethod
    def validate_parameters(
        cls: type[Self],
        parameters: DeleteFileData,
    ) -> Result[bool, list[DomainError]]:
        return Result.ok(True)
