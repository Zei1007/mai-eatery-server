from pydantic import BaseModel
from typing import Optional


class InventoryCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    minThreshold: float


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    minThreshold: Optional[float] = None


class InventoryOut(BaseModel):
    id: str
    name: str
    quantity: float
    unit: str
    minThreshold: float

    model_config = {"from_attributes": True}


class StockAdjust(BaseModel):
    amount: float
    type: str  # "addition" | "reduction"
    reason: Optional[str] = None
