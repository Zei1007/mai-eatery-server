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


def process_checkout(db: Session, cart: List[CartItem], username: str) -> Order:
    # 1. Recalculate total from DB prices — never trust client totals
    resolved_items = []
    total = 0.0
    for cart_item in cart:
        product = db.get(Product, cart_item.productId)
        if not product:
            raise ValueError(f"Product {cart_item.productId} not found")
        line_total = product.price * cart_item.quantity
        total += line_total
        resolved_items.append({
            "productId": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": cart_item.quantity,
        })

    # 2. Create Order + OrderItem records
    order_id = f"ord-{uuid.uuid4().hex}"
    order = Order(id=order_id, total=total, timestamp=int(time.time() * 1000))
    db.add(order)

    for ri in resolved_items:
        db.add(OrderItem(
            id=f"oi-{uuid.uuid4().hex}",
            order_id=order_id,
            **ri,
        ))

    # 3-6. Inventory deductions
    inventory_items = db.query(InventoryItem).all()
    now_ms = int(time.time() * 1000)

    for inv in inventory_items:
        first_word = inv.name.split()[0]

        # Generic name-match deduction
        sold = next((r for r in resolved_items if first_word in r["name"]), None)
        if sold:
            deduction = sold["quantity"]
            inv.quantity = max(0.0, inv.quantity - deduction)
            db.add(StockLog(
                id=f"log-{uuid.uuid4().hex}",
                itemId=inv.id,
                change=-deduction,
                type="sale",
                timestamp=now_ms,
                reason=f"Sold in order {order_id}",
            ))

        # Special: Rice — deduct total_meal_count * 0.01 sacks
        if inv.name == "Rice":
            meal_count = sum(r["quantity"] for r in resolved_items)
            deduction = meal_count * 0.01
            inv.quantity = max(0.0, inv.quantity - deduction)
            db.add(StockLog(
                id=f"log-{uuid.uuid4().hex}",
                itemId=inv.id,
                change=-deduction,
                type="sale",
                timestamp=now_ms,
                reason=f"Rice used for {meal_count} meals in order {order_id}",
            ))

        # Special: Eggs — deduct for silog + Extra Egg items
        if inv.name == "Eggs":
            egg_count = sum(
                r["quantity"] for r in resolved_items
                if "silog" in r["name"].lower() or r["name"] == "Extra Egg"
            )
            if egg_count > 0:
                inv.quantity = max(0.0, inv.quantity - egg_count)
                db.add(StockLog(
                    id=f"log-{uuid.uuid4().hex}",
                    itemId=inv.id,
                    change=-egg_count,
                    type="sale",
                    timestamp=now_ms,
                    reason=f"Eggs used for {egg_count} items in order {order_id}",
                ))

    # 7. Audit log
    db.add(AuditLog(
        id=f"audit-{uuid.uuid4().hex}",
        action="Order Placed",
        details=f"Order {order_id} placed for ₱{total:.2f} ({len(resolved_items)} line items)",
        user=username,
        timestamp=now_ms,
        type="order",
    ))

    # 8. Atomic commit
    db.commit()
    db.refresh(order)
    return order
