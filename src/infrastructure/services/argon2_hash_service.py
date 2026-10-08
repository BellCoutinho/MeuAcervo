import secrets
from typing import Self

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from src.application.contracts import HashService


class Argon2HashService(HashService):
    def __init__(self: Self) -> None:
        self.hasher = PasswordHasher(
            time_cost=1,
            memory_cost=47104,
            parallelism=1,
            hash_len=64,
            salt_len=16,
            type=Type.ID,
        )

    def hash(self: Self, password: str) -> str:
        salt = secrets.token_urlsafe(16).encode('utf-8')
        return self.hasher.hash(password=password, salt=salt)

    def verify(self: Self, password: str, digest: str) -> bool:
        try:
            is_valid = self.hasher.verify(hash=digest, password=password)
        except VerifyMismatchError:
            return False
        except InvalidHashError:
            return False
        except VerificationError:
            return False
        else:
            return is_valid
