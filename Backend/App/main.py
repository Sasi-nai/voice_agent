from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .db import engine, Base, SessionLocal, get_db
from .orchestrator import VoiceOrchestrator
from .seed import seed_data
import time

app = FastAPI(title="Voice Agent Assignment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as db:
        await seed_data(db)

@app.post("/agent/message")
async def agent_message(payload: dict, db: AsyncSession = Depends(get_db)):
    # Timestamp: simulate 'speech_end' when request is received
    speech_end = time.perf_counter()
    session_id = payload.get("session_id", "demo-session")
    patient_id = int(payload.get("patient_id", 1))
    text = payload.get("text", "")

    # STT done (in this demo we receive text directly)
    stt_done = time.perf_counter()

    orch = VoiceOrchestrator(db)
    llm_start = time.perf_counter()
    result = await orch.handle_text(session_id, patient_id, text)
    llm_done = time.perf_counter()

    # TTS not implemented here; simulate tts_done as llm_done for latency measurement
    tts_done = llm_done

    # Attach latency timings (ms)
    timings = {
        "speech_end_ms": int(speech_end * 1000),
        "stt_done_ms": int(stt_done * 1000),
        "llm_done_ms": int(llm_done * 1000),
        "tts_done_ms": int(tts_done * 1000),
        "speech_to_first_audio_ms": int((tts_done - speech_end) * 1000),
    }

    # Log timings for debugging/performance analysis
    print("TIMINGS:", timings)

    # Merge timings into response
    if isinstance(result, dict):
        result.setdefault("timings", {}).update(timings)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}