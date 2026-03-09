import asyncio
import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def debug_subjects():
    print("🕵️ Debugging Subject Names in Database...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db_name = os.getenv('DB_NAME')
    db = client[db_name]
    
    exams_collection = db["exams"]
    exams = await exams_collection.find({"is_deleted": {"$ne": True}}).to_list(100)
    
    print(f"Found {len(exams)} active exams.")
    for e in exams:
        subj = e.get('subject')
        print(f"Title: {e.get('title'):<40} | Subject: '{subj}' | Hex: {subj.encode('utf-8').hex() if subj else 'NONE'}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_subjects())
