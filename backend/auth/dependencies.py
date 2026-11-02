from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.models.user import User
from backend.auth.jwt import decode_token

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    token = None

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    # Role is read from the database, not the token, so demoting an admin
    # takes effect immediately rather than when their token expires.
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
