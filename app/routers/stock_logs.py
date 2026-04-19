from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.stock_log import StockLog
from app.schemas.stock_log import StockLogOut
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/stock-logs", tags=["stock-logs"])


@router.get("", response_model=List[StockLogOut])
def list_stock_logs(
    item_id: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(StockLog).order_by(StockLog.timestamp.desc())
    if item_id:
        q = q.filter(StockLog.itemId == item_id)
    if start:
        q = q.filter(StockLog.timestamp >= start)
    if end:
        q = q.filter(StockLog.timestamp <= end)
    return q.all()
