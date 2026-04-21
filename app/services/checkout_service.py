import time
import uuid
from typing import List
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.inventory import InventoryItem
from app.models.order import Order, OrderItem
from app.models.stock_log import StockLog
from app.models.audit_log import AuditLog
from app.schemas.order import CartItem

# Converts sub-units to the base inventory unit before deduction
_UNIT_TO_BASE = {
    "g":  ("kg",     1 / 1000),
    "ml": ("liters", 1 / 1000),
}


def _to_base(quantity: float, unit: str):
    if unit in _UNIT_TO_BASE:
        base_unit, factor = _UNIT_TO_BASE[unit]
        return quantity * factor, base_unit
    return quantity, unit


def process_checkout(db: Session, cart: List[CartItem], username: str) -> Order:
    now_ms = int(time.time() * 1000)

    # 1. Resolve products from DB (never trust client prices/names)
    resolved = []
    total = 0.0
    for cart_item in cart:
        product = db.get(Product, cart_item.productId)
        if not product:
            raise ValueError(f"Product {cart_item.productId} not found")
        line_total = product.price * cart_item.quantity
        total += line_total
        resolved.append({
            "product": product,
            "order_qty": cart_item.quantity,
            "name": product.name,
            "price": product.price,
        })

    # 2. Create Order record
    order_id = f"ord-{uuid.uuid4().hex}"
    order = Order(id=order_id, total=total, timestamp=now_ms)
    db.add(order)

    for r in resolved:
        db.add(OrderItem(
            id=f"oi-{uuid.uuid4().hex}",
            order_id=order_id,
            productId=r["product"].id,
            name=r["name"],
            price=r["price"],
            quantity=r["order_qty"],
        ))

    # 3. Deduct inventory based on each product's stored ingredients
    for r in resolved:
        product = r["product"]
        order_qty = r["order_qty"]

        if not product.ingredients:
            continue  # no ingredients configured — skip deduction

        for ing in product.ingredients:
            # Total deduction = ingredient_qty_per_order × number_ordered
            raw_qty = ing.quantity * order_qty
            deduct_qty, _ = _to_base(raw_qty, ing.unit)

            inv_item = db.get(InventoryItem, ing.inventory_item_id)
            if not inv_item:
                continue  # inventory item was deleted — skip silently

            inv_item.quantity = max(0.0, inv_item.quantity - deduct_qty)

            db.add(StockLog(
                id=f"log-{uuid.uuid4().hex}",
                itemId=inv_item.id,
                itemName=inv_item.name,
                itemUnit=inv_item.unit,
                change=-deduct_qty,
                type="sale",
                timestamp=now_ms,
                reason=f"Sold via {product.name} ×{order_qty} in order {order_id}",
            ))

    # 4. Audit log
    item_summary = ", ".join(f"{r['name']} ×{r['order_qty']}" for r in resolved)
    db.add(AuditLog(
        id=f"audit-{uuid.uuid4().hex}",
        action="Order Placed",
        details=f"Order {order_id} — {item_summary} — ₱{total:.2f}",
        user=username,
        timestamp=now_ms,
        type="order",
    ))

    db.commit()
    db.refresh(order)
    return order
