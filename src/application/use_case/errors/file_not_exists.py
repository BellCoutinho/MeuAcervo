from src.application.contracts import UseCaseError


class FileNotExistsError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "File does not exist")
