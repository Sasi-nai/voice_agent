import asyncio
from sqlalchemy import select
from App.db import SessionLocal
from App.models import Doctor, Patient
from App.seed import seed_data

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(Patient).where(Patient.phone == '9999999999'))
        patients = res.scalars().all()
        print('existing patients', patients)
        res = await db.execute(select(Doctor).where(Doctor.name == 'Dr. Rao'))
        print('existing Dr. Rao', res.scalars().all())
        res = await db.execute(select(Doctor).where(Doctor.name == 'Dr. Priya'))
        print('existing Dr. Priya', res.scalars().all())
        try:
            await seed_data(db)
            print('seed_data ran successfully')
        except Exception as err:
            print('seed_data error', err)

asyncio.run(main())
