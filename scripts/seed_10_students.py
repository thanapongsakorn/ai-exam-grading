import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_students():
    print("🌱 Seeding 10 test students...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # 1. Get all available subjects
    all_exams = await db["exams"].find({"is_deleted": {"$ne": True}}).to_list(500)
    subjects = sorted(list(set(ex.get("subject", "").strip() for ex in all_exams if ex.get("subject"))))
    print(f"📚 Available Subjects ({len(subjects)}): {subjects}")
    
    if not subjects:
        print("❌ No subjects found. Please create exams first.")
        return

    # 2. Create 10 users and distribute subjects (at least 2 per subject)
    password = "password123"
    hashed_password = pwd_context.hash(password)
    
    users_to_insert = []
    subject_assignments = {sub: [] for sub in subjects}
    
    for i in range(1, 11):
        username = f"student{i:02d}"
        
        # Determine subjects for this student (Round-robin to ensure distribution)
        # Assuming we need at least 2 students per subject, with 10 students and ~5 subjects,
        # each student taking 2 subjects almost guarantees coverage, but let's be systematic.
        
        stu_subjects = []
        # Give each student 2-3 subjects based on their index
        start_idx = (i * 2) % len(subjects)
        for offset in range(3): # Each gets 3 subjects
            sub = subjects[(start_idx + offset) % len(subjects)]
            if sub not in stu_subjects:
                stu_subjects.append(sub)
                subject_assignments[sub].append(username)
                
        user_doc = {
            "username": username,
            "password": hashed_password,
            "role": "student",
            "enrolled_subjects": stu_subjects
        }
        users_to_insert.append(user_doc)
        
    # 3. Insert into DB
    result = await db["users"].insert_many(users_to_insert)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} students.")
    
    # 4. Print Summary for User
    print("\n--- 📋 SUMMARY OF CREATED ACCOUNTS ---")
    print(f"Password for all accounts: {password}\n")
    
    for user in users_to_insert:
        subs = ", ".join(user['enrolled_subjects'])
        print(f"👤 {user['username']:<12} -> {subs}")
        
    print("\n--- 📊 SUBJECT DISTRIBUTION ---")
    for sub, students in subject_assignments.items():
        print(f"📘 {sub:<15}: {len(students)} students {students}")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_students())
