from pydantic import BaseModel
from typing import List


class SalesStatsOut(BaseModel):
    total_sales: float
    order_count: int
    avg_order_value: float


class ProductRankingOut(BaseModel):
    name: str
    qty: float


class RankingsOut(BaseModel):
    rankings: List[ProductRankingOut]
