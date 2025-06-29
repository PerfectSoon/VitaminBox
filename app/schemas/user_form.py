from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.types import Gender


class GoalBase(BaseModel):
    name: str = Field(max_length=100)

    model_config = ConfigDict(from_attributes=True)


class GoalOut(GoalBase):
    id: int


class GoalCreate(GoalBase):
    pass


class AllergyBase(BaseModel):
    name: str = Field(max_length=100)

    model_config = ConfigDict(from_attributes=True)


class AllergyOut(AllergyBase):
    id: int


class AllergyCreate(AllergyBase):
    pass


class UserFormBase(BaseModel):
    age: int = Field(ge=1, le=120)
    gender: Gender
    physical_activity: bool
    water_activity: bool
    smoking_activity: bool
    alcohol_activity: bool
    computer_activity: bool
    sport_activity: bool
    sleep_activity: bool

    model_config = ConfigDict(from_attributes=True)


class UserFormCreate(UserFormBase):
    goal_ids: List[int] | None = None
    allergy_ids: List[int] | None = None


class UserFormUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[Gender] = None
    physical_activity: Optional[bool] = None
    water_activity: Optional[bool] = None
    smoking_activity: Optional[bool] = None
    alcohol_activity: Optional[bool] = None
    computer_activity: Optional[bool] = None
    sport_activity: Optional[bool] = None
    sleep_activity: Optional[bool] = None
    goal_ids: Optional[List[int]] = None
    allergy_ids: Optional[List[int]] = None


class UserFormOut(UserFormBase):
    goals: List[GoalOut] | None = None
    allergies: List[AllergyOut] | None = None
