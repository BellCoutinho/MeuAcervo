from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.main.factories.user_repository_factory import make_user_repository
from src.main.factories.token_manager_factory import make_token_manager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    token_manager = make_token_manager()
    result = token_manager.verify(token)
    if result.is_failure:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    return result.value


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: requer perfil administrador",
        )
    return current_user
