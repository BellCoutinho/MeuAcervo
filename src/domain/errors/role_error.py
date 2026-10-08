from src.domain.contracts import DomainError


class RoleTypeError(DomainError):
    def __init__(self) -> None:
        super().__init__('Role must be one of the following values: admin, user')
