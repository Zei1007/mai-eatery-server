from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: str
    action: str
    details: str
    user: str
    timestamp: int
    type: str

    model_config = {"from_attributes": True}
