from src.domain.contracts import DomainError


class InvalidDateError(DomainError):
    def __init__(self) -> None:
        super().__init__('The date must be in ISO 8601 format')
