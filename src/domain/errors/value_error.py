from src.domain.contracts import DomainError


class InvalidPurchaseValueError(DomainError):
    def __init__(self) -> None:
        super().__init__('Purchase value must be greater than 0')
