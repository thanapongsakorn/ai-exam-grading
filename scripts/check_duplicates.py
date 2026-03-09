import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def check_duplicates():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    username = "student1"
    docs = await db["users"].find({"username": username}).to_list(100)
    print(f"Found {len(docs)} documents for '{username}'")
    for i, doc in enumerate(docs):
        print(f"DOC {i+1}: _id: {doc.get('_id')}, enrolled: {doc.get('enrolled_subjects')}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(check_duplicates())
