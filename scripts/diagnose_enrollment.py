import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def diagnose_user_exams(username):
    print(f"🔍 Diagnosing data for user: {username}")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    user = await db["users"].find_one({"username": username})
    if not user:
        print("❌ User not found.")
        return
        
    enrolled = user.get("enrolled_subjects", [])
    print(f"User Enrolled Subjects: {enrolled}")
    for s in enrolled:
        print(f"  - '{s}' | Hex: {s.encode('utf-8').hex()}")
        
    all_exams = await db["exams"].find({"is_deleted": {"$ne": True}}).to_list(100)
    print(f"\nActive Exams in DB ({len(all_exams)}):")
    for ex in all_exams:
        subj = ex.get("subject")
        print(f"  - Title: {ex.get('title'):<30} | Subject: '{subj}' | Hex: {subj.encode('utf-8').hex() if subj else 'NONE'}")
        
    # Simulation of filtering logic
    normalized_enrolled = [s.strip() for s in enrolled if isinstance(s, str)]
    matches = []
    for ex in all_exams:
        subj = ex.get("subject")
        if subj and subj.strip() in normalized_enrolled:
            matches.append(ex.get("title"))
            
    print(f"\nFiltering Result (Simulated): {matches}")
    client.close()

if __name__ == "__main__":
    import sys
    user_to_check = sys.argv[1] if len(sys.argv) > 1 else "student1"
    asyncio.run(diagnose_user_exams(user_to_check))
