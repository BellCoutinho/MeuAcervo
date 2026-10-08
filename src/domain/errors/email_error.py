from src.domain.contracts import DomainError


class MissingAtSignEmailError(DomainError):
    def __init__(self) -> None:
        super().__init__('The email must contain only an @ sign')


class TooLongLocalPartEmailError(DomainError):
    def __init__(self) -> None:
        super().__init__('Local part of the email must have a maximum of 64 characters')


class TooShortLocalPartEmailError(DomainError):
    def __init__(self) -> None:
        super().__init__('local part must be at least 3 characters long')


class TooShortDomainEmailError(DomainError):
    def __init__(self) -> None:
        super().__init__('domain part must be at least 3 characters long')


class TooLongDomainEmailError(DomainError):
    def __init__(self) -> None:
        super().__init__('The domain part of the email must be a maximum of 255 characters')
