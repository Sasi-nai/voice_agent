import json
from redis.asyncio import Redis
from .config import settings

redis_client: Redis | None = None
redis_unavailable = False
session_fallback: dict[str, str] = {}
patient_fallback: dict[str, str] = {}

async def get_redis():
    global redis_client, redis_unavailable
    if redis_unavailable:
        return None

    if redis_client is None:
        try:
            redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
            await redis_client.ping()
        except Exception:
            redis_client = None
            redis_unavailable = True
            return None

    return redis_client

async def save_session_state(session_id: str, data: dict, ttl: int = 1800):
    r = await get_redis()
    payload = json.dumps(data)
    if r is not None:
        await r.set(f"session:{session_id}", payload, ex=ttl)
        return

    session_fallback[session_id] = payload

async def get_session_state(session_id: str) -> dict:
    r = await get_redis()
    if r is not None:
        raw = await r.get(f"session:{session_id}")
        return json.loads(raw) if raw else {}

    raw = session_fallback.get(session_id)
    return json.loads(raw) if raw else {}

async def save_patient_memory(patient_id: int, data: dict):
    r = await get_redis()
    payload = json.dumps(data)
    if r is not None:
        await r.set(f"patient:{patient_id}", payload)
        return

    patient_fallback[str(patient_id)] = payload

async def get_patient_memory(patient_id: int) -> dict:
    r = await get_redis()
    if r is not None:
        raw = await r.get(f"patient:{patient_id}")
        return json.loads(raw) if raw else {}

    raw = patient_fallback.get(str(patient_id))
    return json.loads(raw) if raw else {}