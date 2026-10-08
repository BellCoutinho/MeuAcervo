from src.application.contracts import UseCaseError


class QuotaExceededError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "Storage quota exceeded")
