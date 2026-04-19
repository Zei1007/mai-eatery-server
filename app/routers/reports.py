from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.inventory import InventoryItem
from app.schemas.reports import SalesStatsOut, RankingsOut, ProductRankingOut
from app.schemas.inventory import InventoryOut
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales", response_model=SalesStatsOut)
def sales_stats(
    start: Optional[int] = None,
    end: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(Order)
    if start:
        q = q.filter(Order.timestamp >= start)
    if end:
        q = q.filter(Order.timestamp <= end)
    orders = q.all()

    total_sales = sum(o.total for o in orders)
    order_count = len(orders)
    avg = total_sales / order_count if order_count else 0.0
    return {"total_sales": total_sales, "order_count": order_count, "avg_order_value": avg}


@router.get("/rankings", response_model=RankingsOut)
def rankings(
    start: Optional[int] = None,
    end: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(Order)
    if start:
        q = q.filter(Order.timestamp >= start)
    if end:
        q = q.filter(Order.timestamp <= end)
    orders = q.all()

    product_sales: dict[str, float] = {}
    for order in orders:
        for item in order.items:
            product_sales[item.name] = product_sales.get(item.name, 0) + item.quantity

    sorted_rankings = [
        ProductRankingOut(name=name, qty=qty)
        for name, qty in sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
    ]
    return {"rankings": sorted_rankings}


@router.get("/low-stock", response_model=List[InventoryOut])
def low_stock(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    return db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.minThreshold
    ).all()
