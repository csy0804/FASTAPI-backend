from redis import asyncio as aioredis
from ..core.config import settings

class RedisManager:
    def __init__(self):
        self.redis = None

    async def init_redis(self):
        self.redis = await aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self):
        if self.redis:
            await self.redis.close()

redis_manager = RedisManager() 