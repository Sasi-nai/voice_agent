from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Appointment, Doctor

class SchedulerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def doctor_exists(self, doctor_id: int) -> bool:
        res = await self.db.execute(select(Doctor).where(Doctor.id == doctor_id, Doctor.active == True))
        return res.scalar_one_or_none() is not None

    async def is_conflict(self, doctor_id: int, start_time: datetime, end_time: datetime) -> bool:
        stmt = select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "booked",
            and_(Appointment.start_time < end_time, Appointment.end_time > start_time),
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def book(self, patient_id: int, doctor_id: int, start_time: datetime, duration_min: int = 30):
        end_time = start_time + timedelta(minutes=duration_min)
        if start_time <= datetime.utcnow():
            return {"ok": False, "reason": "past_time"}

        if not await self.doctor_exists(doctor_id):
            return {"ok": False, "reason": "doctor_unavailable"}

        if await self.is_conflict(doctor_id, start_time, end_time):
            return {"ok": False, "reason": "slot_conflict"}

        appt = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_time=start_time,
            end_time=end_time,
            status="booked",
        )
        self.db.add(appt)
        await self.db.commit()
        await self.db.refresh(appt)
        return {"ok": True, "appointment_id": appt.id}

    async def reschedule(self, appointment_id: int, new_start_time: datetime, duration_min: int = 30):
        stmt = select(Appointment).where(Appointment.id == appointment_id, Appointment.status == "booked")
        res = await self.db.execute(stmt)
        appt = res.scalar_one_or_none()
        if appt is None:
            return {"ok": False, "reason": "not_found"}

        if new_start_time <= datetime.utcnow():
            return {"ok": False, "reason": "past_time"}

        end_time = new_start_time + timedelta(minutes=duration_min)
        conflict_stmt = select(Appointment).where(
            Appointment.doctor_id == appt.doctor_id,
            Appointment.status == "booked",
            Appointment.id != appointment_id,
            and_(Appointment.start_time < end_time, Appointment.end_time > new_start_time),
        )
        conflict_res = await self.db.execute(conflict_stmt)
        if conflict_res.scalar_one_or_none():
            return {"ok": False, "reason": "slot_conflict"}

        appt.start_time = new_start_time
        appt.end_time = end_time
        await self.db.commit()
        await self.db.refresh(appt)
        return {"ok": True, "appointment_id": appointment_id}

    async def cancel(self, appointment_id: int):
        stmt = select(Appointment).where(Appointment.id == appointment_id, Appointment.status == "booked")
        res = await self.db.execute(stmt)
        appt = res.scalar_one_or_none()
        if appt is None:
            return {"ok": False, "reason": "not_found"}

        appt.status = "canceled"
        await self.db.commit()
        return {"ok": True, "appointment_id": appointment_id}