import uuid
from datetime import datetime
from typing import Optional, Any, List
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class EVCInspection(Base):
    __tablename__ = "evc_inspections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), nullable=False)
    institution_id: Mapped[str] = mapped_column(String(36), ForeignKey("institutions.id"), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String(64), default="PHYSICAL_EVC")  # PHYSICAL_EVC, VIRTUAL_EVC, SAC_HEARING
    scheduled_date: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="SCHEDULED")  # SCHEDULED, IN_PROGRESS, COMPLETED, PENDING_REPORT
    panel_members: Mapped[List[dict[str, Any]]] = mapped_column(JSON, default=list)
    observations: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    recommendation: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # CLEARANCE_RECOMMENDED, DEFICITS_NOTED, RE_INSPECTION_REQUIRED
    report_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    application: Mapped["Application"] = relationship("Application")
    institution: Mapped["Institution"] = relationship("Institution")
