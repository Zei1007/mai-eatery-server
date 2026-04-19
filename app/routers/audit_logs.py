from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogOut
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(
    log_type: Optional[str] = None,
    user: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    q = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
    if log_type:
        q = q.filter(AuditLog.type == log_type)
    if user:
        q = q.filter(AuditLog.user == user)
    if start:
        q = q.filter(AuditLog.timestamp >= start)
    if end:
        q = q.filter(AuditLog.timestamp <= end)
    return q.all()
