import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        # Initial client setup
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        self.db = self.client[settings.DB_NAME]
        print("MongoDB client initialized with certifi.")

    async def test_connection(self):
        """Tests the connection and tries fallbacks if SSL fails."""
        try:
            print("Testing MongoDB connection...")
            await asyncio.wait_for(self.client.admin.command('ping'), timeout=5.0)
            print("✅ MongoDB connection successful.")
            return True
        except Exception as e:
            print(f"⚠️ Connection with certifi failed: {e}")
            if "SSL" in str(e) or "TLS" in str(e):
                print("Attempting fallback to system trust store...")
                self.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
                self.db = self.client[settings.DB_NAME]
                try:
                    await asyncio.wait_for(self.client.admin.command('ping'), timeout=5.0)
                    print("✅ Connection successful using system trust store.")
                    return True
                except Exception as e2:
                    print(f"⚠️ Fallback to system trust store failed: {e2}")
                    
                    print("Attempting fallback with tlsAllowInvalidCertificates=True (Insecure)...")
                    self.client = AsyncIOMotorClient(
                        settings.MONGODB_URL,
                        serverSelectionTimeoutMS=5000,
                        connectTimeoutMS=5000,
                        tlsAllowInvalidCertificates=True
                    )
                    self.db = self.client[settings.DB_NAME]
                    try:
                        await asyncio.wait_for(self.client.admin.command('ping'), timeout=5.0)
                        print("✅ Connection successful (Insecure mode).")
                        return True
                    except Exception as e3:
                        print(f"❌ All connection attempts failed: {e3}")
            return False

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

db = Database()
