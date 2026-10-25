from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.audit import AuditEvent

router = APIRouter(prefix="/audit", tags=["Regulatory Audit Trail & Timeline"])

@router.get("/logs", summary="List Audit Logs")
def get_audit_logs(
    action: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if action:
        query = query.filter(AuditEvent.action == action)
    if severity:
        query = query.filter(AuditEvent.severity == severity)

    events = query.order_by(AuditEvent.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "actor_name": e.actor_name,
            "actor_role": e.actor_role,
            "action": e.action,
            "resource_type": e.resource_type,
            "institution_name": e.institution_name,
            "summary": e.summary,
            "details": e.details or {},
            "severity": e.severity,
            "is_demo_event": e.is_demo_event
        } for e in events
    ]
