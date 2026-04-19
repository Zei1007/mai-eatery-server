from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.schemas.order import CheckoutRequest, OrderOut
from app.services.checkout_service import process_checkout
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=List[OrderOut])
def list_orders(
    start: Optional[int] = None,
    end: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(Order).options(joinedload(Order.items)).order_by(Order.timestamp.desc())
    if start:
        q = q.filter(Order.timestamp >= start)
    if end:
        q = q.filter(Order.timestamp <= end)
    return q.all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    if not data.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    try:
        order = process_checkout(db, data.items, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    # Re-load with items relationship
    db.refresh(order)
    return db.query(Order).options(joinedload(Order.items)).filter(Order.id == order.id).first()
