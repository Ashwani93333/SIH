from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.compliance import (
    InstitutionInputSnapshot,
    ComplianceEvaluationResponse
)
from app.services.rule_engine import AICTERuleEngine

router = APIRouter(prefix="/compliance", tags=["Compliance & Rules"])
rule_engine = AICTERuleEngine()

SIX_CORE_RULES_METADATA = [
    {
        "rule_key": "AICTE_RULE_FSR_01",
        "rule_version": "2026.1",
        "name": "Faculty-to-Student Ratio & Cadre Distribution",
        "severity": "CRITICAL",
        "prescribed_norm": "1:20 UG Engg (1:15 PG/Accredited), 1:2:6 Cadre ratio, Ph.D. Principal mandatory",
        "source_reference": "AICTE APH Appendix 7"
    },
    {
        "rule_key": "AICTE_RULE_AREA_02",
        "rule_version": "2026.1",
        "name": "Instructional & Built-Up Area Norms",
        "severity": "HIGH",
        "prescribed_norm": "Land area (Urban >= 2.5 acres, Rural >= 7.5 acres) and instructional carpet area",
        "source_reference": "AICTE APH Appendix 4"
    },
    {
        "rule_key": "AICTE_RULE_COMP_LAB_03",
        "rule_version": "2026.1",
        "name": "Student-to-Computer Ratio & Computing Infrastructure",
        "severity": "HIGH",
        "prescribed_norm": "1:4 computer ratio, min leased line bandwidth (100-500 Mbps), software licenses",
        "source_reference": "AICTE APH Appendix 5"
    },
    {
        "rule_key": "AICTE_RULE_LIB_04",
        "rule_version": "2026.1",
        "name": "Library Resources, Titles & Consortium Subscriptions",
        "severity": "MEDIUM",
        "prescribed_norm": "Min 100 titles & 500 volumes per division, national print journals & e-journal consortium",
        "source_reference": "AICTE APH Appendix 5"
    },
    {
        "rule_key": "AICTE_RULE_SAFETY_05",
        "rule_version": "2026.1",
        "name": "Statutory Safety & Divyangjan Barrier-Free Access",
        "severity": "CRITICAL",
        "prescribed_norm": "Valid Fire NOC, Structural stability, potable water, Divyangjan ramps & accessible toilets",
        "source_reference": "RPwD Act 2016, NBC & Fire Safety Directives"
    },
    {
        "rule_key": "AICTE_RULE_COMM_06",
        "rule_version": "2026.1",
        "name": "Mandatory Statutory Oversight Committees",
        "severity": "CRITICAL",
        "prescribed_norm": "Anti-Ragging Squad, ICC/POSH with external member, SGRC & Ombudsman, SC/ST Committee",
        "source_reference": "Supreme Court Directives, UGC Regulations 2009, POSH Act 2013"
    }
]

@router.get("/rules", summary="List the 6 Active Core AICTE Rules")
def list_rules():
    """Returns the regulatory metadata and thresholds for the 6 core AICTE statutory rules."""
    return {
        "count": len(SIX_CORE_RULES_METADATA),
        "version": AICTERuleEngine.RULE_VERSION,
        "rules": SIX_CORE_RULES_METADATA
    }

@router.post("/check", response_model=ComplianceEvaluationResponse, summary="Evaluate Institutional Compliance")
def check_compliance(snapshot: InstitutionInputSnapshot):
    """
    Deterministically evaluates an institutional data snapshot against all 6 Core AICTE Statutory Rules.
    Returns the comprehensive deficiency matrix with required values, actual values, and shortfalls.
    """
    return rule_engine.evaluate_all(snapshot)

@router.get("/deficiencies", summary="List All Active Statutory Deficiencies")
def list_deficiencies(
    severity: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    from app.models.compliance import Deficiency
    from app.models.application import Application
    from app.models.institution import Institution

    query = db.query(Deficiency)
    if severity:
        query = query.filter(Deficiency.severity == severity)
    if status:
        query = query.filter(Deficiency.status == status)

    defs = query.order_by(Deficiency.first_seen_at.desc()).all()
    out = []
    for d in defs:
        app = db.query(Application).filter(Application.id == d.application_id).first()
        inst = app.institution if app else None
        out.append({
            "id": d.id,
            "application_id": d.application_id,
            "institution_name": inst.name if inst else "Unknown",
            "institution_code": inst.institution_code if inst else "N/A",
            "region": inst.region if inst else "NORTH",
            "academic_year": app.academic_year if app else "2026-2027",
            "field_key": d.field_key,
            "description": d.description,
            "severity": d.severity,
            "status": d.status,
            "first_seen_at": d.first_seen_at.isoformat() if d.first_seen_at else None,
            "resolved_at": d.resolved_at.isoformat() if d.resolved_at else None
        })
    return out

