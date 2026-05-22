import asyncio
import sys
sys.path.insert(0, 'Backend')
from sqlalchemy import select
from App.db import SessionLocal
from App.models import Patient

async def main():
    async with SessionLocal() as db:
        res = await db.execute(select(Patient).where(Patient.phone == '9999999999'))
        print('scalar_one_or_none:', res.scalar_one_or_none())

asyncio.run(main())
