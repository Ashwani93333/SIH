"""
AICTE SETU — Comprehensive & Idempotent Demonstration Data Seeder
Populates realistic national regulatory compliance data across 12 fictional institutions,
16 multi-stage applications, statutory deficiencies, EVC inspections, verified documents,
audit trails, and notifications.
"""

from datetime import datetime, timedelta, timezone
import hashlib
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.base import Base, engine, SessionLocal, utc_now
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.models.application import Application, ApplicationRevision, ApplicationStatus
from app.models.compliance import ComplianceRun, ComplianceResult, Deficiency
from app.models.document import DocumentVerification, DocumentType
from app.models.faculty import FacultyMember
from app.models.evc import EVCInspection
from app.models.notification import Notification
from app.models.audit import AuditEvent
from app.core.security import get_password_hash
from app.services.rule_engine import AICTERuleEngine

DEMO_INSTITUTIONS = [
    {
        "name": "Northstar Institute of Technology",
        "code": "NIT-DEL-01",
        "region": "NORTH",
        "address": "Sector 14, Institutional Area, Rohini, New Delhi 110085",
        "type": "TECHNICAL"
    },
    {
        "name": "Riverbend College of Engineering",
        "code": "RCE-MAH-02",
        "region": "WEST",
        "address": "Plot 42, Hinjewadi Phase 2, Pune, Maharashtra 411057",
        "type": "TECHNICAL"
    },
    {
        "name": "Meridian School of Technical Studies",
        "code": "MSTS-KAR-03",
        "region": "SOUTH",
        "address": "Outer Ring Road, Marathahalli, Bengaluru, Karnataka 560037",
        "type": "TECHNICAL"
    },
    {
        "name": "Horizon Institute of Applied Sciences",
        "code": "HIAS-TN-04",
        "region": "SOUTH",
        "address": "Old Mahabalipuram Road, Sholinganallur, Chennai, Tamil Nadu 600119",
        "type": "TECHNICAL"
    },
    {
        "name": "Cedar Valley Polytechnic",
        "code": "CVP-UK-05",
        "region": "NORTH",
        "address": "Chakrata Road, Selaqui Industrial Area, Dehradun, Uttarakhand 248011",
        "type": "POLYTECHNIC"
    },
    {
        "name": "Summit Technical University",
        "code": "STU-RAJ-06",
        "region": "CENTRAL",
        "address": "Jaipur-Ajmer Expressway, Bagru, Jaipur, Rajasthan 303007",
        "type": "TECHNICAL"
    },
    {
        "name": "Bluecrest Institute of Engineering",
        "code": "BIE-WB-07",
        "region": "EAST",
        "address": "Sector V, Salt Lake City, Kolkata, West Bengal 700091",
        "type": "TECHNICAL"
    },
    {
        "name": "Eastern Gateway College of Technology",
        "code": "EGCT-BIH-08",
        "region": "EAST",
        "address": "NH-30, Danapur-Khagaul Road, Patna, Bihar 801105",
        "type": "TECHNICAL"
    },
    {
        "name": "Silverline School of Computing",
        "code": "SSC-GUJ-09",
        "region": "WEST",
        "address": "SG Highway, Gota, Ahmedabad, Gujarat 382481",
        "type": "TECHNICAL"
    },
    {
        "name": "Greenfield Institute of Technical Education",
        "code": "GITE-PUN-10",
        "region": "NORTH",
        "address": "GT Road, Sahnewal, Ludhiana, Punjab 141120",
        "type": "TECHNICAL"
    },
    {
        "name": "Westbridge College of Engineering",
        "code": "WCE-KER-11",
        "region": "SOUTH",
        "address": "Kakkanad InfoPark Express Road, Kochi, Kerala 682030",
        "type": "TECHNICAL"
    },
    {
        "name": "Lakeside Institute of Applied Technology",
        "code": "LIAT-MP-12",
        "region": "CENTRAL",
        "address": "Bhopal Bypass Road, Kolar, Bhopal, Madhya Pradesh 462042",
        "type": "TECHNICAL"
    }
]

def make_sample_snapshot(inst_code: str, intake: int = 240, location: str = "URBAN", is_compliant: bool = True) -> Dict[str, Any]:
    duration = 4
    total_students = intake * duration
    req_faculty = max(24, int(total_students / 20))
    faculty_count = req_faculty + 4 if is_compliant else max(16, req_faculty - 14)
    prof = max(1, int(faculty_count * 0.12))
    assoc = max(2, int(faculty_count * 0.24))
    asst = faculty_count - prof - assoc

    land = 3.2 if location == "URBAN" else (8.0 if location == "RURAL" else 1.8)
    if not is_compliant:
        land = 1.4 if location == "URBAN" else 4.0

    instructional_area = float(total_students * 5.2) if is_compliant else float(total_students * 3.8)
    pcs = int(total_students / 4) + 20 if is_compliant else int(total_students / 7)

    return {
        "institution_code": inst_code,
        "academic_year": "2026-2027",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "level": "UG",
        "location_type": location,
        "total_sanctioned_intake": intake,
        "course_duration_years": duration,
        "accredited_status": False,
        "faculty": {
            "total_regular_faculty": faculty_count,
            "professors": prof,
            "associate_professors": assoc,
            "assistant_professors": asst,
            "principal": {
                "is_appointed": True,
                "phd_qualified": is_compliant,
                "experience_years": 16.0
            }
        },
        "infrastructure": {
            "land_area_acres": land,
            "instructional_area_sqm": instructional_area,
            "administrative_area_sqm": 1200.0,
            "amenities_area_sqm": 900.0
        },
        "computing": {
            "student_terminals": pcs,
            "internet_bandwidth_mbps": 500.0 if is_compliant else 80.0,
            "system_software_count": 6,
            "application_software_count": 28
        },
        "library": {
            "total_volumes": 14000 if is_compliant else 6000,
            "total_titles": 2800 if is_compliant else 800,
            "national_journals": 26 if is_compliant else 10,
            "international_e_journals": is_compliant,
            "multimedia_terminals": 20
        },
        "safety_and_access": {
            "fire_noc_valid": is_compliant,
            "fire_noc_expiry_date": "2027-04-15" if is_compliant else "2024-01-10",
            "structural_stability_certified": True,
            "potable_water_certified": True,
            "barrier_free_ramps": is_compliant,
            "braille_enabled_lift": is_compliant,
            "disabled_friendly_toilets": is_compliant
        },
        "statutory_committees": {
            "anti_ragging_committee": True,
            "anti_ragging_squad": True,
            "internal_complaints_committee_icc": True,
            "icc_external_member": is_compliant,
            "student_grievance_redressal_committee": True,
            "ombudsman_appointed": True,
            "sc_st_committee": True
        }
    }

def seed_demo_dataset(db: Session) -> Dict[str, Any]:
    """
    Idempotently seeds all 12 institutions, demo users for every role,
    applications in all stages, open deficiencies, EVC visits, and audit events.
    """
    # 1. Seed or retrieve Institutions
    inst_lookup: Dict[str, Institution] = {}
    for d in DEMO_INSTITUTIONS:
        inst = db.query(Institution).filter(Institution.institution_code == d["code"]).first()
        if not inst:
            inst = Institution(
                name=d["name"],
                institution_code=d["code"],
                region=d["region"],
                address=d["address"],
                institution_type=d["type"]
            )
            db.add(inst)
            db.commit()
            db.refresh(inst)
        inst_lookup[d["code"]] = inst

    # 2. Seed Standard Demo Users
    hashed_pwd = get_password_hash("AicteDemo2026!")

    users_spec = [
        {"email": "director@aicte-india.org", "name": "Dr. Rameshwar Nath (National Director)", "role": UserRole.SUPER_ADMIN, "inst": None},
        {"email": "officer.sharma@aicte-india.org", "name": "Dr. Sunita Sharma (Regional Scrutiny Officer)", "role": UserRole.SCRUTINY_OFFICER, "inst": None},
        {"email": "officer.patel@aicte-india.org", "name": "Prof. Arvind Patel (Bureau Officer, West)", "role": UserRole.SCRUTINY_OFFICER, "inst": None},
        {"email": "evc.head@aicte-india.org", "name": "Dr. K. S. Rao (EVC Committee Convener)", "role": UserRole.SCRUTINY_OFFICER, "inst": None},
        {"email": "admin@northstar.edu.in", "name": "Prof. Amit Verma (Principal)", "role": UserRole.COLLEGE_ADMIN, "inst": "NIT-DEL-01"},
        {"email": "admin@riverbend.edu.in", "name": "Dr. Priya Kulkarni (Director)", "role": UserRole.COLLEGE_ADMIN, "inst": "RCE-MAH-02"},
        {"email": "admin@meridian.edu.in", "name": "Prof. C. S. Reddy (Principal)", "role": UserRole.COLLEGE_ADMIN, "inst": "MSTS-KAR-03"}
    ]

    user_lookup: Dict[str, User] = {}
    for u in users_spec:
        user = db.query(User).filter(User.email == u["email"]).first()
        inst_id = inst_lookup[u["inst"]].id if u["inst"] else None
        if not user:
            user = User(
                email=u["email"],
                hashed_password=hashed_pwd,
                full_name=u["name"],
                role=u["role"],
                institution_id=inst_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        user_lookup[u["email"]] = user

    # 3. Seed 16 Applications across workflow stages if fewer than 10 exist
    existing_app_count = db.query(Application).count()
    rule_engine = AICTERuleEngine()

    if existing_app_count < 12:
        now = datetime.now(timezone.utc)
        officer = user_lookup["officer.sharma@aicte-india.org"]
        college_user = user_lookup["admin@northstar.edu.in"]

        applications_spec = [
            # 1. Northstar: APPROVED (EoA Granted)
            {"code": "NIT-DEL-01", "intake": 240, "status": ApplicationStatus.APPROVED, "comp": "COMPLIANT", "vers": 2, "loc": "URBAN", "remarks": "Full compliance verified across all 6 statutory parameters. EoA granted."},
            # 2. Riverbend: RECTIFIED (under review with v2 revision)
            {"code": "RCE-MAH-02", "intake": 300, "status": ApplicationStatus.UNDER_REVIEW, "comp": "COMPLIANT", "vers": 2, "loc": "URBAN", "remarks": "Rectification revision submitted. Faculty cadre balanced. Awaiting final order."},
            # 3. Meridian: DEFICIENCY_ISSUED (Active FSR deficiency)
            {"code": "MSTS-KAR-03", "intake": 240, "status": ApplicationStatus.DEFICIENCY_ISSUED, "comp": "DEFICIENT", "vers": 1, "loc": "URBAN", "remarks": "Deficiency Notice #DEF-FSR-03: Regular faculty shortfall (14 positions vacant)."},
            # 4. Horizon: APPROVED (EoA Granted)
            {"code": "HIAS-TN-04", "intake": 180, "status": ApplicationStatus.APPROVED, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Excellent academic infrastructure. 100% compliance verified."},
            # 5. Cedar Valley: DEFICIENCY_ISSUED (Land Area shortfall)
            {"code": "CVP-UK-05", "intake": 120, "status": ApplicationStatus.DEFICIENCY_ISSUED, "comp": "DEFICIENT", "vers": 1, "loc": "RURAL", "remarks": "Deficiency Notice: Contiguous land area 4.2 acres does not meet rural norm of 7.5 acres."},
            # 6. Summit: UNDER_REVIEW (EVC inspection in progress)
            {"code": "STU-RAJ-06", "intake": 360, "status": ApplicationStatus.UNDER_REVIEW, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Physical EVC committee visit scheduled for campus verification."},
            # 7. Bluecrest: APPROVED (EoA Granted)
            {"code": "BIE-WB-07", "intake": 240, "status": ApplicationStatus.APPROVED, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Compliant in all respects. Clearance order generated."},
            # 8. Eastern Gateway: REJECTED (Multiple lapsed deadlines)
            {"code": "EGCT-BIH-08", "intake": 180, "status": ApplicationStatus.REJECTED, "comp": "DEFICIENT", "vers": 1, "loc": "RURAL", "remarks": "Failure to address Fire NOC lapse and lack of qualified regular Principal after two show cause notices."},
            # 9. Silverline: SUBMITTED (Technical Scrutiny Queue)
            {"code": "SSC-GUJ-09", "intake": 300, "status": ApplicationStatus.SUBMITTED, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Lodged and queue-assigned for preliminary documentary scrutiny."},
            # 10. Greenfield: DEFICIENCY_ISSUED (Safety & Committees)
            {"code": "GITE-PUN-10", "intake": 180, "status": ApplicationStatus.DEFICIENCY_ISSUED, "comp": "DEFICIENT", "vers": 1, "loc": "RURAL", "remarks": "Deficiency Notice: Expired Fire NOC and unconstituted POSH/ICC committee."},
            # 11. Westbridge: UNDER_REVIEW (Scrutiny in progress)
            {"code": "WCE-KER-11", "intake": 240, "status": ApplicationStatus.UNDER_REVIEW, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Scrutiny officer reviewing chartered stability certificates."},
            # 12. Lakeside: APPROVED (EoA Granted)
            {"code": "LIAT-MP-12", "intake": 240, "status": ApplicationStatus.APPROVED, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Approved with zero non-compliances."},
            # 13. Northstar (Intake expansion application): SUBMITTED
            {"code": "NIT-DEL-01", "intake": 360, "status": ApplicationStatus.SUBMITTED, "comp": "COMPLIANT", "vers": 1, "loc": "URBAN", "remarks": "Additional intake proposal for Artificial Intelligence division."},
            # 14. Riverbend (New Programme): DRAFT
            {"code": "RCE-MAH-02", "intake": 120, "status": ApplicationStatus.DRAFT, "comp": None, "vers": 1, "loc": "URBAN", "remarks": "Draft in preparation by institutional registrar."},
            # 15. Meridian (Revision 2): RECTIFIED
            {"code": "MSTS-KAR-03", "intake": 240, "status": ApplicationStatus.UNDER_REVIEW, "comp": "COMPLIANT", "vers": 2, "loc": "URBAN", "remarks": "Rectification: Contracted 14 faculty members; letters of appointment uploaded."},
            # 16. Summit (Extension of Approval): APPROVED
            {"code": "STU-RAJ-06", "intake": 240, "status": ApplicationStatus.APPROVED, "comp": "COMPLIANT", "vers": 2, "loc": "URBAN", "remarks": "Approval restored after satisfactory physical committee inspection."}
        ]

        for i, spec in enumerate(applications_spec):
            inst = inst_lookup[spec["code"]]
            is_comp = spec["comp"] == "COMPLIANT"
            snap = make_sample_snapshot(spec["code"], spec["intake"], spec["loc"], is_compliant=is_comp)
            submitted_time = now - timedelta(days=20 - i)
            approved_time = submitted_time + timedelta(days=5) if spec["status"] == ApplicationStatus.APPROVED else None

            app = Application(
                institution_id=inst.id,
                application_type="EXTENSION_OF_APPROVAL",
                programme="ENGINEERING_AND_TECHNOLOGY",
                academic_year="2026-2027",
                declared_student_intake=spec["intake"],
                status=spec["status"],
                assigned_officer_id=officer.id,
                version_number=spec["vers"],
                payload_snapshot=snap,
                compliance_status=spec["comp"],
                officer_remarks=spec["remarks"],
                submitted_at=submitted_time,
                approved_at=approved_time,
                created_at=submitted_time - timedelta(days=2)
            )
            db.add(app)
            db.commit()
            db.refresh(app)

            # Revisions
            rev1 = ApplicationRevision(
                application_id=app.id,
                revision_number=1,
                author_id=college_user.id,
                change_summary="Initial Application Lodged",
                snapshot_data=snap,
                changed_fields={},
                compliance_summary={"overall_status": spec["comp"] or "PENDING"},
                created_at=app.created_at
            )
            db.add(rev1)

            if spec["vers"] >= 2:
                rev2 = ApplicationRevision(
                    application_id=app.id,
                    revision_number=2,
                    author_id=college_user.id,
                    change_summary="Rectified statutory faculty & infrastructure shortfalls",
                    snapshot_data=snap,
                    changed_fields={"faculty": {"before": 34, "after": 52}, "computing": {"before": 160, "after": 260}},
                    compliance_summary={"overall_status": "COMPLIANT"},
                    created_at=app.submitted_at or now
                )
                db.add(rev2)

            # Compliance Run
            if spec["comp"]:
                comp_run = ComplianceRun(
                    application_id=app.id,
                    evaluated_at=app.submitted_at or now,
                    evaluation_period="2026-2027",
                    input_snapshot=snap,
                    overall_status=spec["comp"],
                    created_by="system-rule-engine"
                )
                db.add(comp_run)
                db.commit()
                db.refresh(comp_run)

                # If Deficient, add Deficiencies
                if spec["comp"] == "DEFICIENT":
                    if "FSR" in spec["remarks"] or "faculty" in spec["remarks"]:
                        d1 = Deficiency(
                            application_id=app.id,
                            field_key="AICTE_RULE_FSR_01",
                            description="Regular faculty shortfall: Available faculty count is below the mandatory 1:20 ratio.",
                            severity="CRITICAL",
                            status="OPEN",
                            first_seen_at=now - timedelta(days=12)
                        )
                        db.add(d1)
                    if "Land" in spec["remarks"]:
                        d2 = Deficiency(
                            application_id=app.id,
                            field_key="AICTE_RULE_AREA_02",
                            description="Contiguous land shortfall: Campus has 4.2 acres against statutory requirement of 7.5 acres for rural zone.",
                            severity="HIGH",
                            status="OPEN",
                            first_seen_at=now - timedelta(days=10)
                        )
                        db.add(d2)
                    if "Fire" in spec["remarks"] or "Safety" in spec["remarks"]:
                        d3 = Deficiency(
                            application_id=app.id,
                            field_key="AICTE_RULE_SAFETY_05",
                            description="State Fire Services NOC expired on 10-01-2024. Building lacks valid renewal clearance.",
                            severity="CRITICAL",
                            status="OPEN",
                            first_seen_at=now - timedelta(days=14)
                        )
                        db.add(d3)

            db.commit()

    # 4. Seed EVC Committee Inspections
    if db.query(EVCInspection).count() == 0:
        apps = db.query(Application).all()
        if len(apps) >= 4:
            evc1 = EVCInspection(
                application_id=apps[0].id,
                institution_id=apps[0].institution_id,
                inspection_type="PHYSICAL_EVC",
                scheduled_date="2026-10-18",
                status="COMPLETED",
                panel_members=[
                    {"name": "Prof. H. S. Sharma", "role": "Convener", "affiliation": "IIT Delhi"},
                    {"name": "Dr. Anjali Menon", "role": "Subject Expert", "affiliation": "NIT Trichy"},
                    {"name": "Er. R. V. Kulkarni", "role": "Council Architect", "affiliation": "CoA Empanelled"}
                ],
                observations={"infrastructure": "Fully compliant with IS standards", "laboratories": "Adequate computing & IoT labs", "library": "Exceeds required volumes"},
                recommendation="CLEARANCE_RECOMMENDED",
                report_summary="The Expert Visiting Committee inspected physical premises, faculty records, and computer terminals. All facilities conform to APH 2026 standards."
            )
            evc2 = EVCInspection(
                application_id=apps[2].id,
                institution_id=apps[2].institution_id,
                inspection_type="PHYSICAL_EVC",
                scheduled_date="2026-10-28",
                status="SCHEDULED",
                panel_members=[
                    {"name": "Dr. S. K. Nair", "role": "Convener", "affiliation": "IISc Bengaluru"},
                    {"name": "Dr. M. Chacko", "role": "Subject Expert", "affiliation": "NIT Calicut"}
                ],
                recommendation=None,
                report_summary="Scheduled physical visit to verify rectified faculty cadre and computing lab installations."
            )
            evc3 = EVCInspection(
                application_id=apps[5].id,
                institution_id=apps[5].institution_id,
                inspection_type="VIRTUAL_EVC",
                scheduled_date="2026-11-02",
                status="SCHEDULED",
                panel_members=[
                    {"name": "Prof. Ajay Singhal", "role": "Convener", "affiliation": "MNIT Jaipur"},
                    {"name": "Er. Vikram Rathore", "role": "Civil Expert", "affiliation": "State PWD"}
                ],
                recommendation=None,
                report_summary="Virtual inspection to audit barrier-free Divyangjan lifts and ramps."
            )
            evc4 = EVCInspection(
                application_id=apps[1].id,
                institution_id=apps[1].institution_id,
                inspection_type="PHYSICAL_EVC",
                scheduled_date="2026-10-22",
                status="PENDING_REPORT",
                panel_members=[
                    {"name": "Dr. Meera Joshi", "role": "Convener", "affiliation": "COEP Pune"},
                    {"name": "Prof. G. N. Deshpande", "role": "AICTE Representative", "affiliation": "WRO Mumbai"}
                ],
                recommendation="CLEARANCE_RECOMMENDED",
                report_summary="Inspection concluded on campus; official signed minutes awaiting committee upload."
            )
            db.add_all([evc1, evc2, evc3, evc4])
            db.commit()

    # 5. Seed Verified Documents (Document AI)
    if db.query(DocumentVerification).count() == 0:
        inst_first = db.query(Institution).first()
        doc_samples = [
            {
                "type": DocumentType.FIRE_NOC,
                "file": "state_fire_noc_2026.pdf",
                "auth": "Delhi Fire Services Headquarters",
                "cert": "DFS/NOC/2026/9941",
                "valid": "2027-04-14",
                "status": "VERIFIED",
                "conf": 0.98,
                "flag": None
            },
            {
                "type": DocumentType.LAND_DEED,
                "file": "registered_land_title_deed.pdf",
                "auth": "Sub-Registrar Office, Revenue Dept",
                "cert": "DL-SR-2018-8421",
                "valid": "PERPETUAL",
                "status": "VERIFIED",
                "conf": 0.96,
                "flag": None
            },
            {
                "type": DocumentType.BUILDING_STABILITY,
                "file": "structural_soundness_audit.pdf",
                "auth": "Govt Empanelled Chartered Structural Engineer",
                "cert": "SE/MCD/2026/4102",
                "valid": "2028-12-31",
                "status": "VERIFIED",
                "conf": 0.95,
                "flag": None
            },
            {
                "type": DocumentType.WATER_POTABILITY,
                "file": "phed_water_test_report.pdf",
                "auth": "Public Health Engineering Department (PHED)",
                "cert": "PHED-LAB-2026-5512",
                "valid": "2027-03-31",
                "status": "VERIFIED",
                "conf": 0.97,
                "flag": None
            },
            {
                "type": DocumentType.FIRE_NOC,
                "file": "expired_fire_clearance_2024.pdf",
                "auth": "Municipal Fire Brigade Department",
                "cert": "MFB/2021/3301",
                "valid": "2024-01-10",
                "status": "FLAGGED",
                "conf": 0.42,
                "flag": "Certificate lapsed over 24 months ago; failed digital signature verification."
            }
        ]
        for ds in doc_samples:
            text_sim = f"OFFICIAL STATUTORY DOCUMENT CERTIFICATION: {ds['type']}\nAuthority: {ds['auth']}\nCert: {ds['cert']}\nValidity: {ds['valid']}"
            sha = hashlib.sha256(text_sim.encode()).hexdigest()
            doc_rec = DocumentVerification(
                institution_id=inst_first.id,
                doc_type=ds["type"],
                filename=ds["file"],
                file_hash=sha,
                ocr_status="COMPLETED",
                extracted_text=text_sim,
                extracted_metadata={
                    "issuing_authority": ds["auth"],
                    "certificate_number": ds["cert"],
                    "valid_till": ds["valid"],
                    "is_digitally_signed": ds["status"] == "VERIFIED"
                },
                verification_status=ds["status"],
                confidence_score=ds["conf"],
                flag_reason=ds["flag"]
            )
            db.add(doc_rec)
        db.commit()

    # 6. Seed Notifications
    if db.query(Notification).count() == 0:
        notifs = [
            {
                "title": "Approaching SLA Deadline: Extension of Approval",
                "message": "Application for Riverbend College of Engineering has reached Day 12 of statutory 15-day scrutiny timeline.",
                "severity": "WARNING",
                "category": "SLA",
                "deadline": "2026-10-27"
            },
            {
                "title": "Statutory Deficiency Notice Issued",
                "message": "Deficiency issued to Meridian School of Technical Studies for Faculty-to-Student Ratio (FSR) shortfall. Rectification due in 14 days.",
                "severity": "CRITICAL",
                "category": "COMPLIANCE",
                "deadline": "2026-11-04"
            },
            {
                "title": "EVC Physical Inspection Confirmed",
                "message": "Expert Visiting Committee panel visit scheduled for Northstar Institute of Technology on 28 October 2026.",
                "severity": "INFO",
                "category": "EVC",
                "deadline": "2026-10-28"
            },
            {
                "title": "Vigilance Alert: Dual-Employment Flagged",
                "message": "National faculty deduplication cross-check flagged 2 faculty members listed simultaneously in active salary rolls across two colleges.",
                "severity": "CRITICAL",
                "category": "VIGILANCE",
                "deadline": None
            },
            {
                "title": "Fire NOC Renewal Reminder",
                "message": "State Fire Services NOC for Cedar Valley Polytechnic is scheduled to expire within 30 days.",
                "severity": "WARNING",
                "category": "COMPLIANCE",
                "deadline": "2026-11-15"
            }
        ]
        for n in notifs:
            notif_rec = Notification(
                title=n["title"],
                message=n["message"],
                severity=n["severity"],
                category=n["category"],
                is_read=False,
                deadline_date=n["deadline"]
            )
            db.add(notif_rec)
        db.commit()

    # 7. Seed Audit Events
    if db.query(AuditEvent).count() == 0:
        events = [
            ("Dr. Sunita Sharma", "SCRUTINY_OFFICER", "APPLICATION_APPROVED", "Northstar Institute of Technology", "Approved Extension of Approval (EoA) after all 6 statutory rules satisfied.", "INFO"),
            ("Prof. Amit Verma", "COLLEGE_ADMIN", "RECTIFICATION_SUBMITTED", "Riverbend College of Engineering", "Lodged Application Revision v2 resolving faculty cadre imbalance.", "INFO"),
            ("AICTE Rule Engine", "SYSTEM", "DEFICIENCY_DETECTED", "Meridian School of Technical Studies", "Identified FSR shortfall of 14 regular faculty members.", "WARNING"),
            ("Dr. K. S. Rao", "EVC_CONVENER", "EVC_INSPECTION_SCHEDULED", "Summit Technical University", "Constituted 3-member Expert Visiting Committee for physical campus verification.", "INFO"),
            ("Document AI Pipeline", "SYSTEM", "CERTIFICATE_FLAGGED", "Cedar Valley Polytechnic", "Flagged Fire NOC certificate due to lapsed validity date (2024).", "CRITICAL"),
            ("Vigilance Engine", "SYSTEM", "FRAUD_BREACH_DETECTED", "Multi-College", "Cross-matched hashed PAN and flagged 2 ghost faculty drawing concurrent salaries.", "CRITICAL"),
            ("Dr. Rameshwar Nath", "DIRECTORATE_HQ", "SYSTEM_POLICY_APPLIED", "National", "Applied APH 2026.1 deterministic compliance baseline across all regional directorates.", "INFO")
        ]
        for actor, role, action, inst_name, summary, sev in events:
            ev = AuditEvent(
                actor_name=actor,
                actor_role=role,
                action=action,
                institution_name=inst_name,
                summary=summary,
                severity=sev,
                is_demo_event=True
            )
            db.add(ev)
        db.commit()

    total_inst = db.query(Institution).count()
    total_apps = db.query(Application).count()
    total_defs = db.query(Deficiency).count()
    total_evc = db.query(EVCInspection).count()
    total_docs = db.query(DocumentVerification).count()
    total_notifs = db.query(Notification).count()
    total_audit = db.query(AuditEvent).count()

    return {
        "status": "SUCCESS",
        "institutions": total_inst,
        "applications": total_apps,
        "deficiencies": total_defs,
        "evc_inspections": total_evc,
        "documents": total_docs,
        "notifications": total_notifs,
        "audit_events": total_audit
    }

if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = seed_demo_dataset(db)
        print("Demo dataset seeded successfully:", res)
    finally:
        db.close()
