from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from backend.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)

    name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    registration_number = Column(String, nullable=False)

    mileage = Column(Integer, default=0)
    fuel_level = Column(Integer, default=100)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🤖 AI fields
    ai_risk_level = Column(String, nullable=True)   # LOW / MEDIUM / HIGH
    ai_failure_probability = Column(Float, nullable=True)
    ai_component = Column(String, nullable=True)
    ai_last_analyzed = Column(DateTime, nullable=True)

    # 🔗 Relationship
    appointments = relationship(
        "Appointment",
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )
