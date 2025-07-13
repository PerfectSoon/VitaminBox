from dataclasses import dataclass

from app.exceptions.service_errors import (
    UserNotFoundError,
    InvalidCredentialsError,
    EntityAlreadyExistsError,
)
from app.core.security import get_password_hash, verify_password
from app.repositories import UserRepository
from app.schemas import UserAuth, UserCreate, UserOut, AdminCreate, UserUpdate


@dataclass(kw_only=True, frozen=True, slots=True)
class UserService:
    repository: UserRepository

    async def register(self, user_data: UserCreate) -> UserOut:
        if await self.repository.get_user_by_email(user_data.email):
            raise EntityAlreadyExistsError()
        hashed = await get_password_hash(user_data.password)
        data = user_data.model_dump(exclude={"password"})
        data["hashed_password"] = hashed

        u = await self.repository.create(data)
        return UserOut.model_validate(u)

    async def authenticate(self, auth: UserAuth) -> UserOut:
        u = await self.repository.get_user_by_email(auth.email)
        if not u:
            raise UserNotFoundError()
        if not await verify_password(auth.password, u.hashed_password):
            raise InvalidCredentialsError()
        return UserOut.model_validate(u)

    async def get_user(self, user_id: int) -> UserOut:
        u = await self.repository.get_by_id(user_id)
        if not u:
            raise UserNotFoundError(f"ID={user_id} не найден")
        return UserOut.model_validate(u)

    async def register_admin(self, user_data: AdminCreate) -> UserOut:
        if await self.repository.get_user_by_email(user_data.email):
            raise EntityAlreadyExistsError()

        hashed = await get_password_hash(user_data.password)

        data = user_data.model_dump(exclude={"password"})
        data["hashed_password"] = hashed

        u = await self.repository.create(data)
        return UserOut.model_validate(u)

    async def update_user(
        self, user_id: int, user_data: UserUpdate, partial: bool = True
    ) -> UserOut:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"Пользователь с ID={user_id} не найден")

        update_dict = {}

        if user_data.name is not None:
            update_dict["name"] = user_data.name

        if user_data.email is not None:
            update_dict["email"] = user_data.email

        if user_data.password is not None:
            update_dict["hashed_password"] = get_password_hash(
                user_data.password
            )

        if user_data.role is not None:
            update_dict["role"] = user_data.role

        if update_dict:
            updated_user = await self.repository.update(user, update_dict)
        else:
            updated_user = user

        return UserOut.model_validate(updated_user)
