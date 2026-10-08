from src.domain.contracts import DomainError


class TooShortAddressError(DomainError):
    def __init__(self) -> None:
        super().__init__('the "address" must contain at least 5 characters')


class TooLongAddressError(DomainError):
    def __init__(self) -> None:
        super().__init__('the "address" must have a maximum of 200 characters')
