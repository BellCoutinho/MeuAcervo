from src.application.contracts import UseCaseError


class SpaceNotExistsError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "Space does not exist")
