from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, products, inventory, orders, stock_logs, audit_logs, reports, exports
import app.models.product_ingredient  # ensure table is registered before create_all

# ── Seed data ────────────────────────────────────────────────────────────────

INITIAL_PRODUCTS = []

INITIAL_INVENTORY = []


def _seed(db):
    from app.models.product import Product
    from app.models.inventory import InventoryItem

    if db.query(Product).count() == 0:
        db.bulk_insert_mappings(Product, INITIAL_PRODUCTS)
        db.commit()

    if db.query(InventoryItem).count() == 0:
        db.bulk_insert_mappings(InventoryItem, INITIAL_INVENTORY)
        db.commit()


# ── App lifecycle ─────────────────────────────────────────────────────────────

def _migrate(conn):
    """Add columns introduced after initial schema without breaking existing DBs."""
    for col, col_type in [("itemName", "TEXT"), ("itemUnit", "TEXT")]:
        try:
            conn.execute(f"ALTER TABLE stock_logs ADD COLUMN {col} {col_type}")
            conn.commit()
        except Exception:
            pass  # column already exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        _migrate(conn)
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Mai Eatery API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(stock_logs.router)
app.include_router(audit_logs.router)
app.include_router(reports.router)
app.include_router(exports.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "mai-eatery-api"}
