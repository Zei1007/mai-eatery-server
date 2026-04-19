import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.services.audit_service import create_audit_log
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductOut])
def list_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(Product)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    if category:
        q = q.filter(Product.category == category)
    return q.all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    item = db.get(Product, product_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return item


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    product = Product(
        id=f"p-{uuid.uuid4().hex[:8]}",
        name=data.name,
        price=data.price,
        category=data.category,
        image=data.image or f"https://picsum.photos/seed/{data.name}/400/400",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    create_audit_log(db, "Add Menu Item", f"Added product: {product.name} (₱{product.price})", current_user, "menu")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: str,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    create_audit_log(db, "Update Menu Item", f"Updated product: {product.name}", current_user, "menu")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    name = product.name
    db.delete(product)
    db.commit()
    create_audit_log(db, "Delete Menu Item", f"Deleted product: {name}", current_user, "menu")
