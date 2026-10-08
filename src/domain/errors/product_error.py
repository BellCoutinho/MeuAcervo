from src.domain.contracts import DomainError


class InvalidProductCategoryError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            'Category must be one of: eletronico, eletrodomestico, moveis, utensilios, outros'
        )
