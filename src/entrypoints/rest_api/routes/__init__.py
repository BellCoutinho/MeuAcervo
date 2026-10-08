from .auth_route import router as auth_router
from .space_route import router as space_router
from .user_route import router as user_router
from .product_route import router as product_router
from .file_route import router as file_router

__all__ = [
    'auth_router',
    'space_router',
    'user_router',
    'product_router',
    'file_router',
]
