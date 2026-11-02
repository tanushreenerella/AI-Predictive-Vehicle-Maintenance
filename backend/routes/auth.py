from fastapi import APIRouter, Depends, Request, Response, HTTPException
from email_validator import validate_email
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.models.user import User
from backend.auth.security import hash_password, verify_password
from backend.auth.jwt import create_access_token
from backend.auth.dependencies import get_current_user
from backend.rate_limit import AUTH_LIMIT, limiter

router = APIRouter(prefix="/auth", tags=["Auth"])
@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
    "id": current_user.id,
    "email": current_user.email,
    "role": current_user.role,
}


def normalize_email(value: str) -> str:
    return value.strip().lower()


def _find_user_by_email(db: Session, email: str):
    # Accounts created before emails were normalized may be stored with
    # mixed case or stray spaces, so compare the normalized column too.
    return db.query(User).filter(func.lower(func.trim(User.email)) == email).first()


class SignupRequest(BaseModel):
    # Any other field sent by the client (e.g. "role") is ignored.
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: str) -> str:
        value = normalize_email(value)
        validate_email(value, check_deliverability=False)
        return value


class LoginRequest(BaseModel):
    # Only presence is enforced: existing accounts predate the signup rules,
    # so rejecting a short password or odd email here could lock them out.
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def email_normalized(cls, value: str) -> str:
        value = normalize_email(value)
        if not value:
            raise ValueError("Email is required")
        return value


@router.post("/signup")
@limiter.limit(AUTH_LIMIT)
def signup(request: Request, data: SignupRequest, db: Session = Depends(get_db)):
    if _find_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
@limiter.limit(AUTH_LIMIT)
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    user = _find_user_by_email(db, data.email)

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
