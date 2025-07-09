from dataclasses import dataclass
from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.exceptions.service_errors import (
    UserNotFoundError,
    EntityAlreadyExistsError,
    ServiceError,
    EntityNotFound,
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
    UserFormUpdate,
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

    async def get_allergies(self) -> List[AllergyOut]:
        list_allergies = await self.allergy_repository.get_all()
        if not list_allergies:
            raise EntityNotFound(f"Список аллергий пуст")
        return [
            AllergyOut.model_validate(allergy) for allergy in list_allergies
        ]

    async def get_goals(self) -> List[GoalOut]:
        list_goals = await self.goal_repository.get_all()
        if not list_goals:
            raise EntityNotFound(f"Список целей пуст")
        return [GoalOut.model_validate(goal) for goal in list_goals]

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

    async def update_user_form(
            self, user_id: int, form_data: UserFormUpdate
    ) -> UserFormOut:

        existing_form = await self.form_repository.get_user_form(user_id)
        if not existing_form:
            raise EntityNotFound(f"Анкета пользователя с ID={user_id} не найдена")

        try:

            base_data = form_data.model_dump(
                exclude_unset=True,
                exclude={"goal_ids", "allergy_ids"}
            )

            if base_data:
                await self.form_repository.update(
                    db_obj=existing_form,
                    obj_data=base_data
                )

            if form_data.goal_ids is not None:
                current_goal_ids = {g.id for g in existing_form.goals}
                new_goal_ids = set(form_data.goal_ids)

                if current_goal_ids != new_goal_ids:
                    await self.goal_repository.update_form_goals(
                        user_id=user_id,
                        goal_ids=list(new_goal_ids)
                    )


            if form_data.allergy_ids is not None:
                current_allergy_ids = {a.id for a in existing_form.allergies}
                new_allergy_ids = set(form_data.allergy_ids)

                if current_allergy_ids != new_allergy_ids:
                    await self.allergy_repository.update_form_allergies(
                        user_id=user_id,
                        allergy_ids=list(new_allergy_ids)
                    )


            updated_form = await self.form_repository.get_user_form(user_id)
            return UserFormOut.model_validate(updated_form, from_attributes=True)

        except SQLAlchemyError as e:
            raise RuntimeError(f"Ошибка при обновлении анкеты: {e}") from e

        except ValueError as e:
            raise ServiceError(f"Ошибка валидации данных: {str(e)}")
        except IntegrityError as e:
            raise ServiceError(f"Ошибка сохранения данных: {str(e)}")

    async def delete_allergy(self, allergy_id: int) -> None:
        allergy = await self.allergy_repository.get_by_id(allergy_id)

        if not allergy:
            raise EntityNotFound(f"Аллергия с id {allergy_id} не найден")

        await self.allergy_repository.delete(allergy_id)

    async def delete_goal(self, goal_id: int) -> None:
        goal = await self.goal_repository.get_by_id(goal_id)

        if not goal:
            raise EntityNotFound(f"Тэг с id {goal_id} не найден")

        await self.goal_repository.delete(goal_id)
