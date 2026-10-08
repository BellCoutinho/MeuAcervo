from src.application.contracts import UseCaseError


class UserNotExistError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "User does not exist")
