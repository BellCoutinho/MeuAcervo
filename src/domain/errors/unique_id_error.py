from src.domain.contracts import DomainError


class InvalidUUIDUniqueIdError(DomainError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f'the {identifier} is not a valid UUID')
