from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.seeder import seed_demo_dataset
from app.api.routes.faculty import seed_demo_faculty
from app.models.institution import Institution
from app.models.application import Application
from app.models.compliance import Deficiency
from app.models.evc import EVCInspection
from app.models.document import DocumentVerification
from app.models.faculty import FacultyMember

router = APIRouter(prefix="/demo", tags=["Demonstration Environment Management"])

@router.post("/seed", summary="Idempotently Seed Demonstration Data")
def seed_demo(db: Session = Depends(get_db)):
    """Triggers the safe, idempotent demonstration dataset seeder."""
    result = seed_demo_dataset(db)
    seed_demo_faculty(db)
    return {
        "message": "AICTE SETU Demonstration dataset seeded successfully",
        "data_summary": result
    }

@router.get("/status", summary="Check Demo Dataset Status")
def demo_status(db: Session = Depends(get_db)):
    """Returns count of active demo entities in the database."""
    return {
        "is_seeded": db.query(Application).count() > 0,
        "institutions_count": db.query(Institution).count(),
        "applications_count": db.query(Application).count(),
        "deficiencies_count": db.query(Deficiency).count(),
        "evc_inspections_count": db.query(EVCInspection).count(),
        "documents_count": db.query(DocumentVerification).count(),
        "faculty_members_count": db.query(FacultyMember).count()
    }
