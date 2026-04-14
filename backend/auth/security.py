from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    password = password.strip()

    # bcrypt hard limit
    if len(password.encode("utf-8")) > 72:
        password = password[:72]

    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain.strip(), hashed)
