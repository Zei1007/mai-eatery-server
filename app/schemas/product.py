from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    price: float
    category: str
    image: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image: Optional[str] = None


class ProductOut(BaseModel):
    id: str
    name: str
    price: float
    category: str
    image: Optional[str] = None

    model_config = {"from_attributes": True}
