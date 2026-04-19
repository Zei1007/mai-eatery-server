from pydantic import BaseModel
from typing import Optional


class StockLogOut(BaseModel):
    id: str
    itemId: str
    change: float
    type: str
    timestamp: int
    reason: Optional[str] = None

    model_config = {"from_attributes": True}
