from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_data(db: AsyncSession):
    await db.execute(
        text(
            "INSERT OR IGNORE INTO doctors(name, specialty, active) VALUES (:name, :specialty, :active)"
        ),
        {"name": "Dr. Rao", "specialty": "General Medicine", "active": True},
    )
    await db.execute(
        text(
            "INSERT OR IGNORE INTO doctors(name, specialty, active) VALUES (:name, :specialty, :active)"
        ),
        {"name": "Dr. Priya", "specialty": "Pediatrics", "active": True},
    )
    await db.execute(
        text(
            "INSERT OR IGNORE INTO patients(name, phone, preferred_language, notes) VALUES (:name, :phone, :preferred_language, '')"
        ),
        {"name": "Vijay", "phone": "9999999999", "preferred_language": "en"},
    )
    await db.commit()