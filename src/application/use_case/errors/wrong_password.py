from src.application.contracts import UseCaseError


class WrongPasswordError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "Wrong password")
