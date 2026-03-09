import asyncio
import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def verify_enrollment_logic():
    print("🔬 Verifying Enrollment Search Logic...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # 1. Get all available subjects as the dashboard would
    exams = await db["exams"].find({"is_deleted": {"$ne": True}}).to_list(100)
    available_subjects = sorted(list(set(ex.get("subject").strip() for ex in exams if ex.get("subject"))))
    
    print(f"Available Subjects: {available_subjects}")
    
    for sub in available_subjects:
        print(f"\nChecking subject: '{sub}' (len: {len(sub)})")
        # 2. Try to find it as the enroll_subject route would
        found = await db["exams"].find_one({"subject": sub, "is_deleted": {"$ne": True}})
        if found:
            print(f"  ✅ Found via exact match!")
        else:
            print(f"  ❌ NOT found via exact match!")
            # 3. Try partial/stripped match
            partial = await db["exams"].find_one({"subject": {"$regex": f"^{sub}\\s*$"}})
            if partial:
                print(f"  💡 Found with regex! Actual in DB: '{partial.get('subject')}' (len: {len(partial.get('subject'))})")
            else:
                print(f"  😱 Even regex failed!")

    client.close()

if __name__ == "__main__":
    asyncio.run(verify_enrollment_logic())
