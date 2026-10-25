import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, utc_now

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    actor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), default="APPLICATION")
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    institution_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    severity: Mapped[str] = mapped_column(String(32), default="INFO")  # INFO, WARNING, CRITICAL
    is_demo_event: Mapped[bool] = mapped_column(Boolean, default=True)
