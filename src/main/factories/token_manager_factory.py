from src.infrastructure.services.jwt_token_manager import JWTTokenManager
from src.application.contracts import TokenManager


def make_token_manager() -> TokenManager:
    return JWTTokenManager()
