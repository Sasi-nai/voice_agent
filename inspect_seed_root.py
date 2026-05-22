import asyncio
import sys
sys.path.insert(0, 'Backend')
from sqlalchemy import select
from App.db import SessionLocal
from App.models import Patient, Doctor
from App.seed import seed_data

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(Patient).where(Patient.phone == '9999999999'))
        print('patients', res.scalars().all())
        res = await db.execute(select(Doctor).where(Doctor.name == 'Dr. Rao'))
        print('rao', res.scalars().all())
        res = await db.execute(select(Doctor).where(Doctor.name == 'Dr. Priya'))
        print('priya', res.scalars().all())
        try:
            await seed_data(db)
            print('seed ok')
        except Exception as e:
            print('seed error', e)

asyncio.run(main())
