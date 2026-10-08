from src.application.contracts import UseCaseError


class UserAlreadyExistsError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "User already exists")
