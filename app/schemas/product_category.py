from typing import Optional, List

from pydantic import Field, BaseModel, ConfigDict

from app.core.types import Gender


class TagBase(BaseModel):
    name: str = Field(max_length=100)


class TagCreate(TagBase):
    pass


class CategoryBase(BaseModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryCreate(CategoryBase):
    pass


class ProductBase(BaseModel):
    name: str = Field(max_length=255)
    price: float = Field(gt=0)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: Optional[str] = Field(None, max_length=500)
    min_age: Optional[int] = Field(None, ge=0)
    gender: Gender = Field(default=Gender.ANY)
    is_active: bool = Field(default=True)


class TagOut(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryOut(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductOut(ProductBase):
    id: int
    category: CategoryOut
    tags: List[TagOut] = []

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    total: int
    products: List[ProductOut]

class ProductCreate(ProductBase):
    category_id: int
    tag_ids: List[int] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
