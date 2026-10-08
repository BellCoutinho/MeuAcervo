from src.domain.contracts import DomainError


class MissingParameterError(DomainError):
    def __init__(self, parameter: str) -> None:
        super().__init__(f'the parameter {parameter} is missing')
