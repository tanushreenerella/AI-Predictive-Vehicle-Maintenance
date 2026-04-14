from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.base import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # user | admin
    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔗 Relationship
    appointments = relationship(
        "Appointment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
