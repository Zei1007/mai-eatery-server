from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import create_access_token
from app.services.audit_service import create_audit_log
from app.config import settings
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    if data.username != settings.ADMIN_USERNAME or data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(data.username)
    create_audit_log(db, "Login", f"User {data.username} logged in", data.username, "auth")
    return {"access_token": token}


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    create_audit_log(db, "Logout", f"User {current_user} logged out", current_user, "auth")
    return {"message": "Logged out"}


@router.get("/me")
def me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
