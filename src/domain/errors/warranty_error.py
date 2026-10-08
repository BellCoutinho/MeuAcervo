from src.domain.contracts import DomainError


class InvalidWarrantyDateError(DomainError):
    def __init__(self) -> None:
        super().__init__('Warranty date must be a valid ISO 8601 date')
