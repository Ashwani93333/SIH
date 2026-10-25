from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.evc import EVCInspection
from app.models.application import Application
from app.models.institution import Institution

router = APIRouter(prefix="/evc", tags=["Expert Visiting Committee (EVC) & Hearings"])

class EVCInspectionCreate(BaseModel):
    application_id: str
    inspection_type: str = "PHYSICAL_EVC"
    scheduled_date: str
    panel_members: List[Dict[str, Any]] = []
    report_summary: Optional[str] = None

class EVCReportSubmission(BaseModel):
    observations: Dict[str, Any]
    recommendation: str  # CLEARANCE_RECOMMENDED, DEFICITS_NOTED, RE_INSPECTION_REQUIRED
    report_summary: str

@router.get("/inspections", summary="List EVC Inspections")
def list_inspections(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(EVCInspection)
    if status_filter:
        query = query.filter(EVCInspection.status == status_filter)
    inspections = query.order_by(EVCInspection.created_at.desc()).all()

    out = []
    for ins in inspections:
        inst = ins.institution
        app = ins.application
        out.append({
            "id": ins.id,
            "application_id": ins.application_id,
            "institution_id": ins.institution_id,
            "institution_name": inst.name if inst else "Unknown",
            "institution_code": inst.institution_code if inst else "N/A",
            "region": inst.region if inst else "NORTH",
            "academic_year": app.academic_year if app else "2026-2027",
            "application_status": app.status if app else "UNDER_REVIEW",
            "inspection_type": ins.inspection_type,
            "scheduled_date": ins.scheduled_date,
            "status": ins.status,
            "panel_members": ins.panel_members or [],
            "observations": ins.observations,
            "recommendation": ins.recommendation,
            "report_summary": ins.report_summary,
            "created_at": ins.created_at.isoformat()
        })
    return out

@router.post("/inspections", status_code=status.HTTP_201_CREATED, summary="Schedule EVC Inspection")
def schedule_inspection(
    data: EVCInspectionCreate,
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == data.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    inspection = EVCInspection(
        application_id=app.id,
        institution_id=app.institution_id,
        inspection_type=data.inspection_type,
        scheduled_date=data.scheduled_date,
        panel_members=data.panel_members,
        status="SCHEDULED",
        report_summary=data.report_summary
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return {"message": "EVC Inspection scheduled successfully", "inspection_id": inspection.id}

@router.post("/inspections/{inspection_id}/complete", summary="Submit EVC Committee Report & Recommendation")
def complete_inspection(
    inspection_id: str,
    report: EVCReportSubmission,
    db: Session = Depends(get_db)
):
    ins = db.query(EVCInspection).filter(EVCInspection.id == inspection_id).first()
    if not ins:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    ins.status = "COMPLETED"
    ins.observations = report.observations
    ins.recommendation = report.recommendation
    ins.report_summary = report.report_summary
    db.commit()
    db.refresh(ins)

    return {"message": "Committee report recorded successfully", "status": ins.status, "recommendation": ins.recommendation}
