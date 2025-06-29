from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.exceptions.service_errors import (
    UserNotFoundError,
    EntityAlreadyExistsError,
    ServiceError,
)

from app.repositories import (
    UserFormRepository,
    AllergyRepository,
    GoalRepository,
)
from app.schemas import (
    UserFormOut,
    UserFormCreate,
    GoalCreate,
    GoalOut,
    AllergyCreate,
    AllergyOut,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class UserFormService:
    form_repository: UserFormRepository
    goal_repository: GoalRepository
    allergy_repository: AllergyRepository

    async def get_user_form(self, user_id: int) -> UserFormOut:
        user_form = await self.form_repository.get_user_form(user_id)
        if not user_form:
            raise UserNotFoundError(
                f"Анкета пользователя с ID={user_id} не найдена"
            )
        return UserFormOut.model_validate(user_form)

    async def create_goal(self, goal_data: GoalCreate) -> GoalOut:
        if await self.goal_repository.get_by_name(goal_data.name):
            raise EntityAlreadyExistsError(
                "Цель с таким названием уже существует"
            )
        try:
            res = await self.goal_repository.create(goal_data.model_dump())
            return GoalOut.model_validate(res)
        except IntegrityError as e:
            raise ServiceError("Ошибка при создании цели", e)

    async def create_allergy(self, allergy_data: AllergyCreate) -> AllergyOut:
        if await self.allergy_repository.get_by_name(allergy_data.name):
            raise EntityAlreadyExistsError(
                "Аллергия с таким названием уже существует"
            )
        res = await self.allergy_repository.create(allergy_data.model_dump())
        return AllergyOut.model_validate(res)

    async def create_user_form(
        self, user_id: int, form_data: UserFormCreate
    ) -> UserFormOut:
        existing = await self.form_repository.get_user_form(user_id)
        if existing:
            raise EntityAlreadyExistsError(
                f"Анкета пользователя с ID={user_id} уже существует"
            )

        base_data = form_data.model_dump(exclude={"goal_ids", "allergy_ids"})

        try:
            user_form_orm = await self.form_repository.create_user_form(
                user_id=user_id,
                form_data=base_data,
                goal_ids=form_data.goal_ids,
                allergy_ids=form_data.allergy_ids,
            )
        except IntegrityError as e:
            if "user_forms_pkey" in str(e.orig):
                raise EntityAlreadyExistsError(
                    f"Анкета пользователя с ID={user_id} уже существует"
                )
            raise ServiceError(f"Ошибка при создании анкеты: {e}")

        return UserFormOut.model_validate(user_form_orm)

    async def delete_user_form(self, user_id: int) -> None:
        user_form = await self.form_repository.get_user_form(user_id)

        if not user_form:
            raise UserNotFoundError(
                f"Анкета пользователя с id {user_id} не найдена"
            )

        await self.form_repository.delete_user_form(user_form.user_id)
