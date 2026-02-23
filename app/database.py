import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        # Add serverSelectionTimeoutMS to prevent indefinite hangs if the DB is unreachable
        # Use certifi for reliable SSL verification on various environments
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        self.db = self.client[settings.DB_NAME]
        print("MongoDB client initialized (connection will be tested on first operation)")

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

db = Database()
