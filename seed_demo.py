"""
AICTE SETU — Demonstration Data Seeder CLI Runner
Run: python seed_demo.py
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.models.base import Base, engine, SessionLocal
from app.services.seeder import seed_demo_dataset
from app.api.routes.faculty import seed_demo_faculty

def main():
    print("=" * 80)
    print(" AICTE SETU — DEMONSTRATION DATA SEEDER")
    print("=" * 80)
    print("[*] Initializing tables if needed...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("[*] Seeding 12 institutions, multi-stage applications, EVC inspections, documents & notifications...")
        summary = seed_demo_dataset(db)
        print("[*] Seeding cross-college faculty deduplication conflict records...")
        seed_demo_faculty(db)
        print("\n[+] SUCCESS! Demo data loaded:")
        for k, v in summary.items():
            print(f"    - {k}: {v}")
        print("=" * 80)
        print("Demo environment is ready. Launch with:")
        print("    npm run dev  or  uvicorn app.main:app --reload --port 8000 --app-dir backend")
        print("=" * 80)
    finally:
        db.close()

if __name__ == "__main__":
    main()
