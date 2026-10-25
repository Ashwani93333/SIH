import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    institution_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("institutions.id"), nullable=True)
    application_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("applications.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="INFO")  # INFO, WARNING, CRITICAL
    category: Mapped[str] = mapped_column(String(64), default="COMPLIANCE")  # COMPLIANCE, EVC, SLA, VIGILANCE, SYSTEM
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    deadline_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
