from typing import Optional, Any
import json
import logging
from ..core.redis import redis_manager
from ..core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    @staticmethod
    async def set_cache(key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await redis_manager.redis.set(key, value)
            if expire is None:
                expire = settings.REDIS_CACHE_EXPIRE
            await redis_manager.redis.expire(key, expire)
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False

    @staticmethod
    async def get_cache(key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = await redis_manager.redis.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None

    @staticmethod
    async def delete_cache(key: str) -> bool:
        """删除缓存"""
        try:
            await redis_manager.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False

    @staticmethod
    async def clear_cache() -> bool:
        """清除所有缓存"""
        try:
            await redis_manager.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"清除缓存失败: {str(e)}")
            return False

    @staticmethod
    async def set_medical_info_cache(user_id: int, medical_info: dict) -> bool:
        """设置医疗信息缓存"""
        key = f"medical_info:{user_id}"
        return await RedisService.set_cache(key, medical_info)

    @staticmethod
    async def get_medical_info_cache(user_id: int) -> Optional[dict]:
        """获取医疗信息缓存"""
        key = f"medical_info:{user_id}"
        return await RedisService.get_cache(key)

    @staticmethod
    async def delete_medical_info_cache(user_id: int) -> bool:
        """删除医疗信息缓存"""
        key = f"medical_info:{user_id}"
        return await RedisService.delete_cache(key)

    @staticmethod
    async def set_diagnosis_cache(diagnosis_id: int, diagnosis: dict) -> bool:
        """设置诊断缓存"""
        key = f"diagnosis:{diagnosis_id}"
        return await RedisService.set_cache(key, diagnosis)

    @staticmethod
    async def get_diagnosis_cache(diagnosis_id: int) -> Optional[dict]:
        """获取诊断缓存"""
        key = f"diagnosis:{diagnosis_id}"
        return await RedisService.get_cache(key)

    @staticmethod
    async def delete_diagnosis_cache(diagnosis_id: int) -> bool:
        """删除诊断缓存"""
        key = f"diagnosis:{diagnosis_id}"
        return await RedisService.delete_cache(key)

redis_service = RedisService() 