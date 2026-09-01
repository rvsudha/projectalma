"""Seed the database with the attorney account and optional demo data.

python -m scripts.seed            # attorney account only
python -m scripts.seed --demo     # + demo leads + a demo applicant login
"""

from __future__ import annotations

import argparse
import asyncio

from app.db.session import SessionLocal
from app.schemas.lead import LeadCreate
from app.services import leads as lead_service
from app.services import users as user_service
from app.services.users import ensure_seed_attorney

# (first, last, email) — the last entry shares an email with the demo applicant
# account below, so signing in as that applicant shows this case.
_DEMO_LEADS = [
    ("Adele", "Inwood", "ada@example.com"),
    ("Grace", "Kim", "grace@example.com"),
    ("Katherine", "Johnson", "katherine@example.com"),
    ("Sam", "Rivera", "applicant@example.com"),
]

_DEMO_APPLICANT = ("applicant@example.com", "changeme123", "Sam Rivera")

_MINIMAL_PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"


async def _run(demo: bool) -> None:
    async with SessionLocal() as db:
        await ensure_seed_attorney(db)
        if demo:
            for first, last, email in _DEMO_LEADS:
                await lead_service.create_lead(
                    db,
                    payload=LeadCreate(first_name=first, last_name=last, email=email),
                    resume_bytes=_MINIMAL_PDF,
                    resume_filename=f"{first.lower()}_{last.lower()}.pdf",
                    resume_content_type="application/pdf",
                )
            email, password, name = _DEMO_APPLICANT
            if await user_service.get_by_email(db, email) is None:
                await user_service.create_user(
                    db, email=email, password=password, full_name=name, role="applicant"
                )
            await db.commit()
            print(f"inserted {len(_DEMO_LEADS)} demo leads + demo applicant <{email}>")
    print("seed complete")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="insert demo leads + applicant")
    args = parser.parse_args()
    asyncio.run(_run(args.demo))


if __name__ == "__main__":
    main()
