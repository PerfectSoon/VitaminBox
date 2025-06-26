from dataclasses import dataclass

from app.core.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.core.security import get_password_hash, verify_password
from app.repositories import UserRepository
from app.schemas import UserAuth, UserCreate, UserOut


@dataclass(kw_only=True, frozen=True, slots=True)
class UserService:
    repository: UserRepository

    async def register(self, user_data: UserCreate) -> UserOut:
        if await self.repository.get_by_email(user_data.email):
            raise UserAlreadyExistsError()
        hashed = await get_password_hash(user_data.password)
        u = await self.repository.create(
            {
                "email": user_data.email,
                "hashed_password": hashed,
                "role": user_data.role,
            }
        )
        return UserOut.model_validate(u)

    async def authenticate(self, auth: UserAuth) -> UserOut:
        u = await self.repository.get_by_email(auth.email)
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
