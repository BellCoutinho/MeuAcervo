from src.domain.contracts import DomainError


class WeakPasswordError(DomainError):
    def __init__(self) -> None:
        super().__init__('The password is too short. Passwords with less than 8 characters are considered weak')


class TooLongPasswordError(DomainError):
    def __init__(self) -> None:
        super().__init__('Maximum password length of 64 characters has been exceeded')


class MissingSpecialCharacterPasswordError(DomainError):
    def __init__(self) -> None:
        super().__init__('The password must contain at least one of the following special characters: [!@#$%^&*?]')


class MissingNumberPasswordError(DomainError):
    def __init__(self) -> None:
        super().__init__('The password must contain at least one number')


class HashLengthError(DomainError):
    def __init__(self) -> None:
        super().__init__('The "hashed_password" must be 148 characters long')
