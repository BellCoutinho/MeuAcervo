from src.domain.contracts import DomainError


class TooShortNameError(DomainError):
    def __init__(self) -> None:
        super().__init__('the "name" must contain at least 3 characters')


class TooLongNameError(DomainError):
    def __init__(self) -> None:
        super().__init__('the "name" must have a maximum of 100 characters')
