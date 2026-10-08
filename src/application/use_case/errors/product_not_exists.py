from src.application.contracts import UseCaseError


class ProductNotExistsError(UseCaseError):
    def __init__(self, message: str = "") -> None:
        super().__init__(message or "Product does not exist")
