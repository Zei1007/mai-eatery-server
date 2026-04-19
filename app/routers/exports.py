import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.models.inventory import InventoryItem
from app.models.order import Order
from app.models.stock_log import StockLog
from app.models.audit_log import AuditLog
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/export", tags=["exports"])


def _csv_response(rows: list[list], headers: list[str], filename: str) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/inventory")
def export_inventory(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    items = db.query(InventoryItem).all()
    rows = [[i.id, i.name, i.quantity, i.unit, i.minThreshold] for i in items]
    return _csv_response(rows, ["id", "name", "quantity", "unit", "minThreshold"], "inventory.csv")


@router.get("/orders")
def export_orders(
    start: Optional[int] = None,
    end: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(Order).options(joinedload(Order.items))
    if start:
        q = q.filter(Order.timestamp >= start)
    if end:
        q = q.filter(Order.timestamp <= end)
    orders = q.all()
    rows = [[o.id, o.timestamp, o.total, "; ".join(f"{i.quantity}x {i.name}" for i in o.items)] for o in orders]
    return _csv_response(rows, ["id", "timestamp", "total", "items"], "orders.csv")


@router.get("/stock-logs")
def export_stock_logs(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    logs = db.query(StockLog).order_by(StockLog.timestamp.desc()).all()
    rows = [[l.id, l.itemId, l.change, l.type, l.timestamp, l.reason] for l in logs]
    return _csv_response(rows, ["id", "itemId", "change", "type", "timestamp", "reason"], "stock_logs.csv")


@router.get("/audit-logs")
def export_audit_logs(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    rows = [[l.id, l.action, l.details, l.user, l.timestamp, l.type] for l in logs]
    return _csv_response(rows, ["id", "action", "details", "user", "timestamp", "type"], "audit_logs.csv")
