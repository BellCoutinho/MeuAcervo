from src.application.contracts import UseCaseError


class InvalidTokenError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "Invalid or expired token")
