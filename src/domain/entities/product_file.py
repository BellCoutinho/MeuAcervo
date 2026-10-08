from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from uuid import UUID

    from src.domain.errors import DomainError

from src.domain.contracts import Entity
from src.domain.value_objects import Date, FileSize, FileTypeVO, UniqueId
from src.shared import Result


class ProductFile(Entity):
    def __init__(
        self: Self,
        file_path: str,
        file_name: str,
        file_type: FileTypeVO,
        file_size: FileSize,
        id: UniqueId | None = None,
        uploaded_at: Date | None = None,
        product_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> None:
        self._file_path = file_path
        self._file_name = file_name
        self._file_type = file_type
        self._file_size = file_size
        self._unique_id = id or UniqueId()
        self._uploaded_at = uploaded_at or Date()
        self._product_id = product_id
        self._user_id = user_id

    def __eq__(self: Self, other: Self) -> bool:
        if not isinstance(other, ProductFile):
            return False
        return other.id == self._unique_id

    @property
    def id(self: Self) -> UUID:
        return self._unique_id.identifier

    @property
    def file_path(self: Self) -> str:
        return self._file_path

    @property
    def file_name(self: Self) -> str:
        return self._file_name

    @property
    def file_type(self: Self) -> FileTypeVO:
        return self._file_type

    @property
    def file_size(self: Self) -> FileSize:
        return self._file_size

    @property
    def uploaded_at(self: Self) -> Date:
        return self._uploaded_at

    @property
    def product_id(self: Self) -> UUID | None:
        return self._product_id

    @property
    def user_id(self: Self) -> UUID | None:
        return self._user_id

    @classmethod
    def create(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[Self, list[DomainError]]:
        ft_result = FileTypeVO.create(file_type=kwargs.get("file_type"))
        fs_result = FileSize.create(size=kwargs.get("file_size"))
        id = kwargs.get("id")
        id_result = UniqueId.create(id=id) if id is not None else UniqueId.create()

        validation_result = Result.combine(ft_result, fs_result, id_result)
        if validation_result.is_failure:
            return validation_result

        return Result.ok(ProductFile(
            file_path=kwargs.get("file_path", ""),
            file_name=kwargs.get("file_name", ""),
            file_type=ft_result.value,
            file_size=fs_result.value,
            id=id_result.value,
            product_id=kwargs.get("product_id"),
            user_id=kwargs.get("user_id"),
        ))

    @classmethod
    def validate(
        cls: type[Self], **kwargs: dict[str, Any]
    ) -> Result[bool, list[DomainError]]:
        ft_result = FileTypeVO.validate(file_type=kwargs.get("file_type"))
        fs_result = FileSize.validate(size=kwargs.get("file_size"))
        return Result.combine(ft_result, fs_result)
