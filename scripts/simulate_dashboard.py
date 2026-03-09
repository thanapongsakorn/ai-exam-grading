import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def simulate_dashboard(username):
    print(f"🎬 Simulating Dashboard for: {username}")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    user = await db["users"].find_one({"username": username})
    if not user:
        print("❌ User not found.")
        return
        
    all_exams = await db["exams"].find({"is_deleted": {"$ne": True}}).to_list(100)
    print(f"Total exams found: {len(all_exams)}")
    
    # Matching Logic from main.py
    available_subjects = sorted(list(set(ex.get("subject").strip() for ex in all_exams if ex.get("subject"))))
    print(f"Available Subjects (stripped): {available_subjects}")
    
    enrolled_raw = user.get("enrolled_subjects", [])
    print(f"Enrolled Subjects (raw): {enrolled_raw}")
    
    enrolled_subjects = [s.strip() for s in enrolled_raw if isinstance(s, str)]
    print(f"Enrolled Subjects (stripped): {enrolled_subjects}")
    
    # Filtering
    enrolled_exams = []
    for ex in all_exams:
        subj = ex.get("subject")
        if subj and subj.strip() in enrolled_subjects:
            enrolled_exams.append(ex)
            
    print(f"Enrolled Exams found: {len(enrolled_exams)}")
    for ex in enrolled_exams:
        print(f"  - {ex.get('title')} ({ex.get('subject')})")
        
    # Grouping
    grouped_exams = {}
    for ex in enrolled_exams:
        subject = ex.get("subject", "ทั่วไป")
        if subject not in grouped_exams:
            grouped_exams[subject] = []
        grouped_exams[subject].append(ex)
        
    print(f"Grouped Exams keys: {list(grouped_exams.keys())}")
    
    client.close()

if __name__ == "__main__":
    import sys
    user_to_check = sys.argv[1] if len(sys.argv) > 1 else "student1"
    asyncio.run(simulate_dashboard(user_to_check))
