from src.domain.contracts import DomainError


class TooShortSpaceNameError(DomainError):
    def __init__(self) -> None:
        super().__init__('the "space_name" must contain at least 3 characters')


class TooLongSpaceNameError(DomainError):
    def __init__(self) -> None:
        super().__init__('the "space_name" must have a maximum of 100 characters')
