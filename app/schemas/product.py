from pydantic import BaseModel, Field
from typing import Optional, List


class IngredientIn(BaseModel):
    inventoryItemId: str
    inventoryItemName: str
    quantity: float
    unit: str


class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    image: Optional[str] = None
    ingredients: List[IngredientIn] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image: Optional[str] = None
    ingredients: Optional[List[IngredientIn]] = None


class IngredientOut(BaseModel):
    inventoryItemId: str = Field(alias="inventory_item_id")
    inventoryItemName: str = Field(alias="inventory_item_name")
    quantity: float
    unit: str

    model_config = {"from_attributes": True, "populate_by_name": True}


class ProductOut(BaseModel):
    id: str
    name: str
    price: float
    category: str
    image: Optional[str] = None
    ingredients: List[IngredientOut] = []

    model_config = {"from_attributes": True}
