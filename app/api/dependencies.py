from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.connection import get_db

from app.core.security import decode_access_token, decode_refresh_token
from app.repositories import (
    UserRepository,
    UserFormRepository,
    GoalRepository,
    AllergyRepository,
    ProductRepository,
    CategoryRepository,
    TagRepository,
    OrderItemRepository,
    PromoRepository,
)
from app.repositories.order import OrderRepository
from app.schemas import TokenData, UserOut
from app.services import (
    UserService,
    UserFormService,
    ProductService,
    OrderService,
    RecommendationService,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:

    return UserService(repository=UserRepository(db))


async def get_order_service(
    db: AsyncSession = Depends(get_db),
) -> OrderService:
    return OrderService(
        order_repository=OrderRepository(db),
        order_item_repository=OrderItemRepository(db),
        product_repository=ProductRepository(db),
        promo_repository=PromoRepository(db),
    )


async def get_user_form_service(
    db: AsyncSession = Depends(get_db),
) -> UserFormService:

    return UserFormService(
        form_repository=UserFormRepository(db),
        goal_repository=GoalRepository(db),
        allergy_repository=AllergyRepository(db),
    )


def get_product_service(
    db: AsyncSession = Depends(get_db),
) -> ProductService:
    return ProductService(
        product_repository=ProductRepository(db),
        category_repository=CategoryRepository(db),
        tag_repository=TagRepository(db),
    )


def get_recommendation_service(
    db: AsyncSession = Depends(get_db),
) -> RecommendationService:
    return RecommendationService(
        product_repository=ProductRepository(db),
        user_form_repository=UserFormRepository(db),
    )


async def get_current_access_token(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    token_data = await decode_access_token(token)

    return token_data


async def get_current_refresh_token(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    token_data = await decode_refresh_token(token)

    return token_data


async def get_current_user(
    token_data: TokenData = Depends(get_current_access_token),
    service: UserService = Depends(get_user_service),
) -> UserOut:

    return await service.get_user(int(token_data.sub))
