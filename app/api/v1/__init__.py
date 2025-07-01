from .auth import router as auth_router
from .user_form import router as user_form_router
from .product import router as product_router

__all__ = [
    "auth_router",
    "user_form_router",
    "product_router",
]
