from dataclasses import dataclass
from typing import List

from app.core.types import Gender
from app.repositories import ProductRepository, UserFormRepository
from app.exceptions.service_errors import EntityNotFound
from app.schemas import ProductOut


@dataclass(kw_only=True, frozen=True, slots=True)
class RecommendationService:
    product_repository: ProductRepository
    user_form_repository: UserFormRepository

    async def get_recommendations(
        self, user_id: int, limit: int
    ) -> List[ProductOut]:
        user_form = await self.user_form_repository.get_user_form(user_id)

        if not user_form:
            raise EntityNotFound(
                f"Анкета пользователя с id {user_id} не найдена"
            )

        filters = {"is_active": True}
        products = await self.product_repository.get_all_products(
            limit=limit, **filters
        )

        allergy_names = {a.name.lower() for a in user_form.allergies}
        goal_names = {g.name.lower() for g in user_form.goals}

        recommended = []
        for product in products:
            product_tag_names = {tag.name.lower() for tag in product.tags}

            if product.min_age and product.min_age > user_form.age:
                continue

            if (
                product.gender != Gender.ANY
                and product.gender != user_form.gender
            ):
                continue

            if not product_tag_names.isdisjoint(allergy_names):
                continue

            if goal_names and product_tag_names.isdisjoint(goal_names):
                continue

            recommended.append(product)

        if not recommended:
            raise EntityNotFound("Рекомендации не найдены")

        return [
            ProductOut.model_validate(prod, from_attributes=True)
            for prod in recommended
        ]
