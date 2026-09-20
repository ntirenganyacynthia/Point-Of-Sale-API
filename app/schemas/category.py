from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    category_name: str
    category_description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: str | None = None
    category_description: str | None = None


class CategoryRead(CategoryBase):
    category_id: int
    model_config = ConfigDict(from_attributes=True)