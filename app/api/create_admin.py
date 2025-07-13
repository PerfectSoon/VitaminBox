import random
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from app.core.types import UserType, Gender
from app.models import Category, Tag, Product, Goal, Allergy
from app.repositories import UserRepository
from app.schemas import UserOut, AdminCreate
from app.services import UserService


fake = Faker("ru_RU")


async def create_admin_user(db: AsyncSession) -> UserOut | None:
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


async def create_tags(db: AsyncSession, count: int = 10) -> List[Tag] | None:
    """Создание тестовых тегов"""
    try:
        tags = []
        existing_names = set()

        for _ in range(count):
            while True:
                name = fake.word().capitalize()
                if name not in existing_names:
                    existing_names.add(name)
                    break

            tag = Tag(name=name)
            tags.append(tag)
            db.add(tag)

        await db.commit()
        print(f"✅ Успешно создано {len(tags)} тегов")
        return tags

    except Exception as e:
        await db.rollback()
        print(f"Ошибка при создании тегов: {e}")
        return None


async def create_categories(
    db: AsyncSession, count: int = 5
) -> List[Category] | None:
    try:
        categories = []
        existing_names = set()

        for _ in range(count):
            while True:
                name = fake.sentence(nb_words=3).rstrip(".")
                if name not in existing_names:
                    existing_names.add(name)
                    break

            category = Category(
                name=name,
                description=(
                    fake.paragraph() if random.random() > 0.3 else None
                ),
            )
            categories.append(category)
            db.add(category)

        await db.commit()
        print(f"✅ Успешно создано {len(categories)} категорий")
        return categories

    except Exception as e:
        await db.rollback()
        print(f"Ошибка при создании категорий: {e}")
        return None


async def create_products(
    db: AsyncSession,
    categories: List[Category],
    tags: List[Tag],
    count: int = 20,
) -> List[Product] | None:
    try:
        products = []
        existing_names = set()

        for _ in range(count):
            while True:
                name = fake.sentence(nb_words=4).rstrip(".")
                if name not in existing_names:
                    existing_names.add(name)
                    break

            product = Product(
                name=name,
                category_id=random.choice(categories).id,
                price=float(
                    fake.random_number(digits=3, fix_len=True)
                    + fake.random_number(digits=2) / 100
                ),
                description=(
                    fake.paragraph() if random.random() > 0.2 else None
                ),
                image_url=fake.image_url() if random.random() > 0.5 else None,
                min_age=random.choice([0, 3, 6, 12, 16, 18]),
                gender=random.choice(list(Gender)),
                is_active=True,
            )

            product_tags_count = random.randint(0, 4)
            if product_tags_count > 0 and tags:
                product.tags = random.sample(
                    tags, min(product_tags_count, len(tags))
                )

            products.append(product)
            db.add(product)

        await db.commit()
        print(f"✅ Успешно создано {len(products)} продуктов")
        return products

    except Exception as e:
        await db.rollback()
        print(f"Ошибка при создании продуктов: {e}")
        return None


async def create_goals(db: AsyncSession) -> List[Goal] | None:
    try:
        goals = []
        goal_names = [
            "Похудение",
            "Набор массы",
            "Поддержание формы",
            "Подготовка к соревнованиям",
            "Реабилитация",
        ]

        for name in goal_names:
            goal = Goal(name=name)
            goals.append(goal)
            db.add(goal)

        await db.commit()
        print(f"✅ Успешно создано {len(goals)} целей")
        return goals

    except Exception as e:
        await db.rollback()
        print(f"Ошибка при создании целей: {e}")
        return None


async def create_allergies(db: AsyncSession) -> List[Allergy] | None:
    try:
        allergies = []
        allergy_names = [
            "Орехи",
            "Молочные продукты",
            "Яйца",
            "Рыба",
            "Морепродукты",
            "Глютен",
            "Соя",
            "Мед",
        ]

        for name in allergy_names:
            allergy = Allergy(name=name)
            allergies.append(allergy)
            db.add(allergy)

        await db.commit()
        print(f"✅ Успешно создано {len(allergies)} аллергий")
        return allergies

    except Exception as e:
        await db.rollback()
        print(f"Ошибка при создании аллергий: {e}")
        return None


async def seed_database(db: AsyncSession) -> None:
    print("\nНачало заполнения базы данных тестовыми данными...")

    tags = await create_tags(db)
    if not tags:
        return

    categories = await create_categories(db)
    if not categories:
        return

    products = await create_products(db, categories, tags)
    if not products:
        return

    goals = await create_goals(db)
    if not goals:
        return

    allergies = await create_allergies(db)
    if not allergies:
        return

    print("\n✅ База данных успешно заполнена тестовыми данными!")
