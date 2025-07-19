from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from loguru import logger
import redis.asyncio as redis
from typing import Optional

from src.core.config import settings


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect_to_mongo(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
            
            # Create indexes
            await self.create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def close_mongo_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def connect_to_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close_redis_connection(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("created_at")
            
            # Searches collection indexes
            await self.database.searches.create_index("user_id")
            await self.database.searches.create_index("is_active")
            await self.database.searches.create_index("last_executed")
            
            # Vehicles collection indexes
            await self.database.vehicles.create_index("source")
            await self.database.vehicles.create_index("external_id")
            await self.database.vehicles.create_index([("source", 1), ("external_id", 1)], unique=True)
            await self.database.vehicles.create_index("make")
            await self.database.vehicles.create_index("model")
            await self.database.vehicles.create_index("year")
            await self.database.vehicles.create_index("price")
            await self.database.vehicles.create_index("location.state")
            await self.database.vehicles.create_index("discovered_at")
            await self.database.vehicles.create_index("last_seen_at")
            await self.database.vehicles.create_index("is_active")
            
            # Geospatial index for location coordinates
            await self.database.vehicles.create_index([("location.coordinates", "2dsphere")])
            
            # Opportunities collection indexes
            await self.database.opportunities.create_index("vehicle_id")
            await self.database.opportunities.create_index("search_id")
            await self.database.opportunities.create_index("projected_profit")
            await self.database.opportunities.create_index("confidence_score")
            await self.database.opportunities.create_index("created_at")
            await self.database.opportunities.create_index("status")
            
            # Compound index for opportunity queries
            await self.database.opportunities.create_index([
                ("confidence_score", -1),
                ("projected_profit", -1),
                ("created_at", -1)
            ])
            
            # Alerts collection indexes
            await self.database.alerts.create_index("opportunity_id")
            await self.database.alerts.create_index("user_id")
            await self.database.alerts.create_index("sent_at")
            await self.database.alerts.create_index("status")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
            raise


# Global database instance
db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    await db.connect_to_mongo()
    await db.connect_to_redis()


async def close_mongo_connection():
    """Close MongoDB connection"""
    await db.close_mongo_connection()
    await db.close_redis_connection()


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db.database


def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    return db.redis_client 