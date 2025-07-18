from .auth import router as auth_router
from .user_form import router as user_form_router
from .product import router as product_router
from .order import router as order_router
from .admin.user import router as admin_user_router
from .admin.product import router as admin_product_router
from .admin.promo import router as admin_promo_router

__all__ = [
    "auth_router",
    "user_form_router",
    "product_router",
    "order_router",
    "admin_user_router",
    "admin_product_router",
    "admin_promo_router",
]
