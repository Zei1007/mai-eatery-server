from pydantic import BaseModel
from typing import List


class CartItem(BaseModel):
    productId: str
    quantity: int


class CheckoutRequest(BaseModel):
    items: List[CartItem]


class OrderItemOut(BaseModel):
    id: str
    productId: str
    name: str
    price: float
    quantity: float

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: str
    items: List[OrderItemOut]
    total: float
    timestamp: int

    model_config = {"from_attributes": True}
