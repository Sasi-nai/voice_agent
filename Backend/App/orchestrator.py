import re
from datetime import datetime
from .memory import get_session_state, save_session_state, get_patient_memory, save_patient_memory
from .scheduler import SchedulerService

def detect_language(text: str) -> str:
    t = text.lower()
    # Prioritize native script detection: Devanagari (Hindi), Tamil
    if re.search(r"[\u0900-\u097F]", text):
        lang = "hi"
        print(f"DETECT_LANGUAGE input={text!r} -> {lang}")
        return lang
    if re.search(r"[\u0B80-\u0BFF]", text):
        lang = "ta"
        print(f"DETECT_LANGUAGE input={text!r} -> {lang}")
        return lang
    if any(x in t for x in ["namaste", "doctor", "appointment", "book", "schedule"]):
        return "en"
    if any(x in t for x in ["नमस्ते", "डॉक्टर", "अपॉइंटमेंट", "बुक", "रद्द"]):
        return "hi"
    if any(x in t for x in ["வணக்கம்", "மருத்துவர்", "முன்பதிவு", "ரத்து"]):
        return "ta"
    return "en"


def extract_appointment_id(text: str) -> int | None:
    patterns = [
        r"(?:appointment[_ ]?id|appointment id|appt id|appointment)\s*[:#]?\s*(\d+)",
        r"\b(?:cancel|reschedule|re-schedule)\s+(\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def extract_doctor_id(text: str) -> int | None:
    patterns = [
        r"doctor[_ ]?id\s*[:#]?\s*(\d+)",
        r"\bdoctor\s+(\d+)\b",
        r"\bdr\.?\s*(\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def extract_datetime(text: str) -> str | None:
    match = re.search(r"(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}(?::\d{2})?))", text)
    return match.group(0) if match else None

class VoiceOrchestrator:
    def __init__(self, db):
        self.db = db
        self.scheduler = SchedulerService(db)

    async def handle_text(self, session_id: str, patient_id: int, text: str):
        session = await get_session_state(session_id)
        patient_memory = await get_patient_memory(patient_id)

        language = detect_language(text)
        lower = text.lower()
        appointment_id = extract_appointment_id(text)
        doctor_id = extract_doctor_id(text)
        dt_str = extract_datetime(text)
        intent = session.get("intent")

        if "reschedule" in lower or "re-schedule" in lower or "change" in lower:
            session["intent"] = "reschedule"
            await save_session_state(session_id, session)

            if appointment_id is not None and dt_str is not None:
                try:
                    new_time = datetime.fromisoformat(dt_str)
                except ValueError:
                    return {
                        "reply": "I understood your reschedule request, but the datetime format looks invalid. Use YYYY-MM-DDTHH:MM.",
                        "language": language,
                        "trace": ["reschedule_invalid_datetime"],
                    }
                result = await self.scheduler.reschedule(appointment_id, new_time)
                if result["ok"]:
                    session["intent"] = None
                    await save_session_state(session_id, session)
                    return {
                        "reply": f"Appointment {appointment_id} rescheduled successfully.",
                        "language": language,
                        "trace": ["reschedule_success"],
                    }
                reason = result.get("reason")
                msg = {
                    "past_time": "That time is in the past. Please choose a future slot.",
                    "slot_conflict": "That doctor is not available then. Please choose another time.",
                    "not_found": "I could not find that appointment. Please confirm the appointment id.",
                }.get(reason, "Unable to reschedule that appointment.")
                return {"reply": msg, "language": language, "trace": [f"reschedule_failed:{reason}"]}

            if appointment_id is not None:
                return {
                    "reply": "Please share the new datetime to reschedule your appointment, e.g. 2026-06-10T10:30.",
                    "language": language,
                    "trace": ["reschedule_awaiting_datetime"],
                }

            return {
                "reply": "Please share the appointment id and new datetime to reschedule, e.g. appointment 1 2026-06-10T10:30.",
                "language": language,
                "trace": ["reschedule_awaiting_details"],
            }

        if appointment_id is not None and ("cancel" in lower or intent == "cancel"):
            result = await self.scheduler.cancel(appointment_id)
            if result["ok"]:
                session["intent"] = None
                await save_session_state(session_id, session)
                patient_memory["last_cancel"] = appointment_id
                await save_patient_memory(patient_id, patient_memory)
                return {
                    "reply": f"Appointment {appointment_id} canceled successfully.",
                    "language": language,
                    "trace": ["cancel_success"],
                }
            if result.get("reason") == "not_found":
                return {
                    "reply": "I could not find that appointment. Please confirm the appointment id.",
                    "language": language,
                    "trace": ["cancel_failed:not_found"],
                }
            return {
                "reply": "Unable to cancel that appointment.",
                "language": language,
                "trace": ["cancel_failed"],
            }

        if "cancel" in lower or "रद्द" in text or "ரத்து" in text:
            session["intent"] = "cancel"
            await save_session_state(session_id, session)
            return {
                "reply": "Please share the appointment id to cancel.",
                "language": language,
                "trace": ["intent=cancel"],
            }

        if doctor_id is not None and dt_str is not None:
            try:
                start_time = datetime.fromisoformat(dt_str)
            except ValueError:
                return {
                    "reply": "I understood the doctor id, but the datetime format is invalid. Use YYYY-MM-DDTHH:MM.",
                    "language": language,
                    "trace": ["book_invalid_datetime"],
                }
            result = await self.scheduler.book(patient_id, doctor_id, start_time)
            if not result["ok"]:
                reason = result["reason"]
                msg = {
                    "past_time": "That time is in the past. Please choose a future slot.",
                    "doctor_unavailable": "That doctor is unavailable.",
                    "slot_conflict": "That slot is already booked. Please choose another time.",
                }.get(reason, "Unable to book that slot.")
                return {"reply": msg, "language": language, "trace": [f"book_failed:{reason}"]}
            patient_memory["last_booking"] = {"doctor_id": doctor_id, "start_time": dt_str}
            await save_patient_memory(patient_id, patient_memory)
            session["intent"] = None
            await save_session_state(session_id, session)
            return {
                "reply": f"Appointment booked successfully. Booking id {result['appointment_id']}.",
                "language": language,
                "trace": ["book_success"],
            }

        if "book" in lower or "बुक" in text or "முன்பதிவு" in text or "schedule" in lower or "appointment" in lower:
            session["intent"] = "book"
            await save_session_state(session_id, session)
            if doctor_id is None and dt_str is None:
                return {
                    "reply": "I can help book an appointment. Please share doctor id and datetime in ISO format, e.g. doctor 2 2026-06-10T10:30.",
                    "language": language,
                    "trace": ["intent=book", "awaiting doctor_id and datetime"],
                }
            if doctor_id is None:
                return {
                    "reply": "Please provide a doctor id, for example doctor 1 or doctor 2.",
                    "language": language,
                    "trace": ["book_awaiting_doctor_id"],
                }
            if dt_str is None:
                return {
                    "reply": "Please provide the appointment datetime in ISO format, for example 2026-06-10T10:30.",
                    "language": language,
                    "trace": ["book_awaiting_datetime"],
                }

        await save_session_state(session_id, session)
        return {
            "reply": "Sorry, I didn’t understand. Please say book, cancel, or reschedule.",
            "language": language,
            "trace": ["fallback"],
        }
