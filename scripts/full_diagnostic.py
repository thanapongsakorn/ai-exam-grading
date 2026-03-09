import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def full_diagnostic(username):
    print(f"--- DIAGNOSTIC FOR {username} ---")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    user = await db["users"].find_one({"username": username})
    print(f"User Document: {user}")
    
    if user:
        enrolled = user.get("enrolled_subjects", [])
        print(f"Enrolled Type: {type(enrolled)}")
        for s in enrolled:
             print(f"  - '{s}' | Hex: {s.encode('utf-8').hex() if isinstance(s, str) else 'NOT_A_STRING'}")
    
    exams = await db["exams"].find({"is_deleted": {"$ne": True}}).to_list(500)
    print(f"\nActive Exams ({len(exams)}):")
    for ex in exams:
        subj = ex.get("subject")
        print(f"  - Title: {ex.get('title'):<30} | Subj: '{subj}' | Hex: {subj.encode('utf-8').hex() if subj else 'NONE'}")

    client.close()

if __name__ == "__main__":
    import sys
    u = sys.argv[1] if len(sys.argv) > 1 else "student1"
    asyncio.run(full_diagnostic(u))
