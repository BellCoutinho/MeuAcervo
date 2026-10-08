from src.application.contracts import UseCaseError


class UnauthorizedError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "Unauthorized access")
