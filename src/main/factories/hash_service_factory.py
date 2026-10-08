from src.infrastructure.services.argon2_hash_service import Argon2HashService
from src.application.contracts import HashService


def make_hash_service() -> HashService:
    return Argon2HashService()
