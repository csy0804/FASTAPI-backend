from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_classification.core.config import settings

# 初始化 MongoDB 客户端
# 使用 settings.MONGODB_URL 获取连接字符串
client = AsyncIOMotorClient(settings.MONGODB_URL)

# 获取数据库实例
db = client[settings.MONGODB_DB]

# 创建一个简单的对象来封装客户端和数据库实例，以匹配 database.py 的导入和使用方式
class MongoDBContainer:
    def __init__(self, client, db):
        self.client = client
        self.db = db

# 导出包含客户端和数据库的容器实例
mongodb = MongoDBContainer(client, db)

# 可选：如果需要，也可以导出数据库实例
# db = client[settings.MONGODB_DB]

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]

    async def close_database_connection(self):
        if self.client:
            self.client.close()

async def get_database():
    return mongodb.db

# 在应用关闭时关闭客户端连接的函数
async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close() 