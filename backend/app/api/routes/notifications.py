from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications & Statutory SLA Alerts"])

@router.get("/", summary="List All Notifications & SLA Alerts")
def get_notifications(
    category: Optional[str] = None,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Notification)
    if category:
        query = query.filter(Notification.category == category)
    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifs = query.order_by(Notification.created_at.desc()).all()
    unread_count = db.query(Notification).filter(Notification.is_read == False).count()

    return {
        "unread_count": unread_count,
        "total_count": len(notifs),
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "severity": n.severity,
                "category": n.category,
                "is_read": n.is_read,
                "deadline_date": n.deadline_date,
                "created_at": n.created_at.isoformat()
            } for n in notifs
        ]
    }

@router.post("/{notification_id}/read", summary="Mark Notification as Read")
def mark_as_read(notification_id: str, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    return {"message": "Notification marked as read", "id": notification_id}

@router.post("/mark-all-read", summary="Mark All Notifications Read")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).update({Notification.is_read: True})
    db.commit()
    return {"message": "All notifications marked as read"}
