import asyncio
import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

async def main():
    r = Redis.from_url(url, decode_responses=True)
    ok = await r.ping()
    print('PING', ok)
    await r.close()

asyncio.run(main())
