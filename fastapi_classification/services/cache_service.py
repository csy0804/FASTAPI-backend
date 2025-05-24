from typing import Optional, Any, Dict
import json
import logging
from ..core.redis import redis_manager
from ..core.config import settings
from redis import asyncio as aioredis
from ..core.json_encoder import JSONEncoderWithObjectId

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        # 使用 Redis 连接 URL 初始化 Redis 客户端
        # self.redis = aioredis.from_url(settings.REDIS_URL)
        # 暂不在这里初始化，通过依赖注入或其他方式获取连接
        self.redis: Optional[aioredis.Redis] = None

    async def init_redis(self):
         try:
             self.redis = await aioredis.from_url(
                 f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                 db=settings.REDIS_DB,
                 password=settings.REDIS_PASSWORD,
                 encoding="utf-8",
                 decode_responses=True
             )
         except Exception as e:
             print(f"无法连接到 Redis: {e}")
             self.redis = None

    async def close(self):
        if self.redis:
            await self.redis.close()

    @staticmethod
    async def get_cache(key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            data = await redis_manager.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None

    @staticmethod
    async def set_cache(key: str, value: Any, expire: int = None):
        """设置缓存"""
        try:
            # 使用自定义编码器将数据序列化为 JSON 字符串
            await redis_manager.redis.set(
                key,
                json.dumps(value, cls=JSONEncoderWithObjectId),
                ex=expire or settings.REDIS_CACHE_EXPIRE
            )
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")

    @staticmethod
    async def delete_cache(key: str):
        """删除缓存"""
        try:
            await redis_manager.redis.delete(key)
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")

    @staticmethod
    async def clear_pattern(pattern: str):
        """清除匹配的缓存"""
        try:
            keys = await redis_manager.redis.keys(pattern)
            if keys:
                await redis_manager.redis.delete(*keys)
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")

    @staticmethod
    async def get_medical_info_cache(user_id: int) -> Optional[Any]:
        """获取医疗信息缓存"""
        return await CacheService.get_cache(f"medical_info:{user_id}")

    @staticmethod
    async def set_medical_info_cache(user_id: int, value: Any, expire: int = None):
        """设置医疗信息缓存"""
        await CacheService.set_cache(f"medical_info:{user_id}", value, expire)

    @staticmethod
    async def delete_medical_info_cache(user_id: int):
        """删除医疗信息缓存"""
        await CacheService.delete_cache(f"medical_info:{user_id}")

    @staticmethod
    async def get_diagnosis_cache(diagnosis_id: int) -> Optional[Any]:
        """获取诊断缓存"""
        return await CacheService.get_cache(f"diagnosis:{diagnosis_id}")

    @staticmethod
    async def set_diagnosis_cache(diagnosis_id: int, value: Any, expire: int = None):
        """设置诊断缓存"""
        await CacheService.set_cache(f"diagnosis:{diagnosis_id}", value, expire)

    @staticmethod
    async def delete_diagnosis_cache(diagnosis_id: int):
        """删除诊断缓存"""
        await CacheService.delete_cache(f"diagnosis:{diagnosis_id}")

cache_service = CacheService() 