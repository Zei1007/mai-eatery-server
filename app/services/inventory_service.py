import csv
import io
import uuid
from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem


def import_csv(db: Session, content: bytes) -> list[InventoryItem]:
    """Parse CSV bytes and upsert inventory items. Returns upserted items."""
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    upserted = []

    for row in reader:
        item_id = row.get("id") or f"i-{uuid.uuid4().hex[:8]}"
        existing = db.get(InventoryItem, item_id)

        if existing:
            existing.name = row["name"]
            existing.quantity = float(row["quantity"])
            existing.unit = row["unit"]
            existing.minThreshold = float(row["minThreshold"])
            upserted.append(existing)
        else:
            item = InventoryItem(
                id=item_id,
                name=row["name"],
                quantity=float(row["quantity"]),
                unit=row["unit"],
                minThreshold=float(row["minThreshold"]),
            )
            db.add(item)
            upserted.append(item)

    db.commit()
    return upserted
