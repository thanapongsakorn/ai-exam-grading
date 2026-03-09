import asyncio
import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    mongodb_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DB_NAME")
    
    print(f"Testing connection to: {mongodb_url[:20]}...")
    
    try:
        # Try with certifi first (current setup)
        client = AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        await client.admin.command('ping')
        print("✅ Connection successful with certifi!")
    except Exception as e:
        print(f"❌ Connection failed with certifi: {e}")
        
        try:
            # Try without tlsCAFile (system trust store)
            print("\nRetrying without tlsCAFile (using system trust store)...")
            client = AsyncIOMotorClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000
            )
            await client.admin.command('ping')
            print("✅ Connection successful WITHOUT tlsCAFile!")
        except Exception as e2:
            print(f"❌ Connection failed WITHOUT tlsCAFile: {e2}")

if __name__ == "__main__":
    asyncio.run(test_connection())
