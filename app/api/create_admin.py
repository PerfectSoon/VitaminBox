from sqlalchemy.ext.asyncio import AsyncSession

from app.core.types import UserType
from app.repositories import UserRepository
from app.schemas import UserOut, AdminCreate
from app.services import UserService


async def create_admin(db: AsyncSession) -> UserOut | None:
    try:
        service = UserService(repository=UserRepository(db))

        admin_data = AdminCreate(
            email="admin@admin.com",
            password="admin123",
            name="Админ",
            role=UserType.ADMIN,
        )

        user_out = await service.register_admin(admin_data)
        print(f"✅ Администратор {user_out.email} успешно создан")
        return user_out

    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
