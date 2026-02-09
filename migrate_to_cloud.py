import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env
load_dotenv()

LOCAL_URL = "mongodb://localhost:27017"
CLOUD_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME", "exam_grading_db")

async def migrate():
    print("🚀 Starting Migration: Local -> Cloud...")
    
    local_client = AsyncIOMotorClient(LOCAL_URL)
    cloud_client = AsyncIOMotorClient(CLOUD_URL)
    
    local_db = local_client[DB_NAME]
    cloud_db = cloud_client[DB_NAME]
    
    collections = ["users", "exams", "submissions", "audit_logs"]
    
    for coll_name in collections:
        print(f"📦 Migrating collection: {coll_name}...")
        
        # Get data from local
        cursor = local_db[coll_name].find({})
        docs = await cursor.to_list(None)
        
        if docs:
            # Clear cloud collection first to avoid duplicates if re-running
            await cloud_db[coll_name].delete_many({})
            # Insert to cloud
            await cloud_db[coll_name].insert_many(docs)
            print(f"✅ Migrated {len(docs)} documents for {coll_name}")
        else:
            print(f"ℹ️ No documents found for {coll_name}")
            
    # Create Indexes on Cloud
    print("⚡ Creating Indexes on Cloud...")
    await cloud_db["users"].create_index("username", unique=True)
    await cloud_db["submissions"].create_index("submitted_at")
    await cloud_db["submissions"].create_index("student_username")
    print("✅ Indexes created.")
    
    local_client.close()
    cloud_client.close()
    print("🏁 Migration Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(migrate())
