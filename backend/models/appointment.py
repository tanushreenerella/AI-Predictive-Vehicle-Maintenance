from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Index, Integer, Time, text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.base import Base

_ACTIVE = text("status <> 'CANCELLED'")


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        # One active booking per bay per slot. Cancelled rows don't count,
        # so a cancelled slot can be booked again.
        Index(
            "uq_appointments_active_slot_bay",
            "appointment_date", "appointment_time", "bay",
            unique=True,
            postgresql_where=_ACTIVE,
            sqlite_where=_ACTIVE,
        ),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)

    service_type = Column(String, nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    bay = Column(Integer, nullable=False)
    urgency = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="appointments")
    vehicle = relationship("Vehicle", back_populates="appointments")
    status = Column(String, default="CONFIRMED", nullable=False)
