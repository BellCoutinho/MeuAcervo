from src.application.contracts import UseCaseError


class MissingParameterError(UseCaseError):
    def __init__(self, parameter: str) -> None:
        super().__init__(f'the parameter {parameter} is missing')
