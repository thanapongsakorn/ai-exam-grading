import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def clear_old_data():
    print("🧹 Cleaning up old submission data...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # Check how many submissions exist
    count = await db["submissions"].count_documents({})
    print(f"Found {count} submission(s) in the database.")
    
    if count > 0:
        result = await db["submissions"].delete_many({})
        print(f"✅ Successfully deleted {result.deleted_count} old submission record(s).")
    else:
        print("✅ No submission records found. Database is already clean.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_old_data())
