from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.core.config import settings
from app.models.base import Base, engine
from app.api.routes.auth import router as auth_router
from app.api.routes.applications import router as applications_router
from app.api.routes.compliance import router as compliance_router
from app.api.routes.documents import router as documents_router
from app.api.routes.faculty import router as faculty_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.evc import router as evc_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.audit import router as audit_router
from app.api.routes.demo import router as demo_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite/Postgres tables on startup
    Base.metadata.create_all(bind=engine)
    try:
        from app.models.base import SessionLocal
        from app.models.application import Application
        from app.services.seeder import seed_demo_dataset
        from app.api.routes.faculty import seed_demo_faculty
        with SessionLocal() as db:
            if db.query(Application).count() == 0:
                seed_demo_dataset(db)
                seed_demo_faculty(db)
    except Exception as e:
        print(f"Notice: Demo data initialization skipped: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AICTE SETU — Self-Evaluation & Transparency Unit (Complete Regulatory Compliance Engine)",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Register All Core Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(applications_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(faculty_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(evc_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Dashboard"])
def get_dashboard():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "AICTE SETU Regulatory Portal is running."}

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AICTE SETU Core Regulatory Engine",
        "system": "Complete National Institutional Compliance Monitoring System",
        "version": settings.VERSION
    }
