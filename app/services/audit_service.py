import time
import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    details: str,
    user: str,
    log_type: str,
    commit: bool = True,
) -> AuditLog:
    log = AuditLog(
        id=f"audit-{uuid.uuid4().hex}",
        action=action,
        details=details,
        user=user,
        timestamp=int(time.time() * 1000),
        type=log_type,
    )
    db.add(log)
    if commit:
        db.commit()
    return log
