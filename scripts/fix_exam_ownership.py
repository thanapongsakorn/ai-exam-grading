import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def fix_ownership():
    print("🔧 Fixing Exam Ownership...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # Map subject to correct teacher username
    ownership_map = {
        "วิทยาศาสตร์": "teacher_sci",
        "ภาษาไทย": "teacher_thai",
        "คณิตศาสตร์": "teacher_math"
    }
    
    for subject, teacher_username in ownership_map.items():
        result = await db["exams"].update_many(
            {"subject": subject},
            {"$set": {"created_by": teacher_username}}
        )
        print(f"Updated {result.modified_count} exams for {subject} -> {teacher_username}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_ownership())
