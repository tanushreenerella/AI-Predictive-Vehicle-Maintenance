from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.models.user import User
from backend.auth.security import hash_password, verify_password
from backend.auth.jwt import create_access_token
from backend.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
    "id": current_user.id,
    "email": current_user.email,
    "role": current_user.role,
}

@router.post("/signup")
def signup(data: dict, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data["email"]).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        email=data["email"],
        hashed_password=hash_password(data["password"]),
        role=data.get("role", "user")
    )
    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.id, "role": user.role})

    response = Response()
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    return response

@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data["email"]).first()

    if not user or not verify_password(data["password"], user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "role": user.role})

    response = Response()
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60*60*24*7
    )
    return response
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
