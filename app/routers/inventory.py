import uuid
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.stock_log import StockLog
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryOut, StockAdjust
from app.services.audit_service import create_audit_log
from app.services.inventory_service import import_csv
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=List[InventoryOut])
def list_inventory(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    return db.query(InventoryItem).all()


@router.get("/{item_id}", response_model=InventoryOut)
def get_item(item_id: str, db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_item(
    data: InventoryCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    item = InventoryItem(id=f"i-{uuid.uuid4().hex[:8]}", **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=InventoryOut)
def update_item(
    item_id: str,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db.delete(item)
    db.commit()


@router.post("/{item_id}/adjust", response_model=InventoryOut)
def adjust_stock(
    item_id: str,
    data: StockAdjust,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    delta = data.amount if data.type == "addition" else -data.amount
    item.quantity = max(0.0, item.quantity + delta)

    log = StockLog(
        id=f"log-{uuid.uuid4().hex}",
        itemId=item_id,
        itemName=item.name,
        itemUnit=item.unit,
        change=delta,
        type=data.type,
        timestamp=int(time.time() * 1000),
        reason=data.reason or ("Manual Restock" if data.type == "addition" else "Manual Reduction"),
    )
    db.add(log)
    db.commit()
    db.refresh(item)

    direction = "Added" if data.type == "addition" else "Reduced"
    create_audit_log(
        db,
        "Stock Adjustment",
        f"{direction} {data.amount} {item.unit} of {item.name}. Reason: {data.reason or 'Manual'}",
        current_user,
        "inventory",
    )
    return item


@router.post("/import", response_model=List[InventoryOut])
async def import_inventory(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    content = await file.read()
    items = import_csv(db, content)
    create_audit_log(
        db,
        "Import CSV",
        f"Imported inventory with {len(items)} items",
        current_user,
        "inventory",
    )
    return items
