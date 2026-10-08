from src.domain.contracts import DomainError


class InvalidFileTypeError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            'File type must be one of: nf, photo, video, contract, other'
        )


class InvalidFileSizeError(DomainError):
    def __init__(self) -> None:
        super().__init__('File size must be greater than 0')
