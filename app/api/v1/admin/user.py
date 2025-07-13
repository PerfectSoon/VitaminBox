from fastapi import Depends, HTTPException, APIRouter, status

from app.api.dependencies import (
    get_user_service,
    get_user_form_service,
    get_current_admin,
)
from app.exceptions.service_errors import (
    UserNotFoundError,
    EntityAlreadyExistsError,
    ServiceError,
)
from app.schemas import UserOut, GoalOut, GoalCreate, AllergyOut, AllergyCreate
from app.services import UserService, UserFormService

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Получить профиль пользователя по его ID",
    status_code=status.HTTP_200_OK,
)
async def read_profile_by_id(
    user_id: int,
    admin: UserOut = Depends(get_current_admin),
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/goal",
    response_model=GoalOut,
    summary="Создать цель",
    status_code=status.HTTP_201_CREATED,
)
async def create_goal(
    goal_in: GoalCreate,
    admin: UserOut = Depends(get_current_admin),
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        return await service.create_goal(goal_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    "/allergy",
    response_model=AllergyOut,
    summary="Создать аллергию",
    status_code=status.HTTP_201_CREATED,
)
async def create_allergy(
    allergy_in: AllergyCreate,
    admin: UserOut = Depends(get_current_admin),
    service: UserFormService = Depends(get_user_form_service),
):
    try:
        return await service.create_allergy(allergy_in)
    except EntityAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(e)
        )
    except ServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
