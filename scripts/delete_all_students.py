import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def delete_all_students():
    print("🗑️ Deleting all student records...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # Check how many we are deleting first
    count = await db["users"].count_documents({"role": "student"})
    print(f"Found {count} student(s) to delete.")
    
    if count > 0:
        result = await db["users"].delete_many({"role": "student"})
        print(f"✅ Successfully deleted {result.deleted_count} student record(s).")
    else:
        print("✅ No student records found. Database is already clean.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(delete_all_students())
