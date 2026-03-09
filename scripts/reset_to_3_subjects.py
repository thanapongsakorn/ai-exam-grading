import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def reset_db():
    print("🔄 Resetting Database to 3 Teachers, 3 Subjects...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # 1. Find Teachers
    teachers = await db["users"].find({"role": "teacher"}).to_list(10)
    print(f"👨‍🏫 Found {len(teachers)} teachers:")
    for t in teachers:
        print(f"  - {t['username']}")
        
    if len(teachers) < 3:
        print("⚠️ Warning: Less than 3 teachers found! Proceeding with what we have.")
        
    # Pick exactly 3 teachers (or as many as available up to 3)
    selected_teachers = teachers[:3]
    
    # Define the 3 subjects and exams
    subject_map = [
        {"subject": "คณิตศาสตร์", "title": "ข้อสอบคณิตศาสตร์ (หลัก)"},
        {"subject": "ภาษาไทย", "title": "ข้อสอบภาษาไทย (หลัก)"},
        {"subject": "วิทยาศาสตร์", "title": "ข้อสอบวิทยาศาสตร์ (หลัก)"}
    ]
    
    # 2. Delete ALL existing exams
    await db["exams"].delete_many({})
    print("🗑️ Deleted all existing exams.")
    
    # 3. Create the 3 new exams
    new_exams = []
    for i, t in enumerate(selected_teachers):
        sm = subject_map[i % len(subject_map)]
        exam = {
            "title": sm["title"],
            "subject": sm["subject"],
            "description": f"ข้อสอบทดสอบความรู้พื้นฐานวิชา {sm['subject']}",
            "questions": [
                {"id": "q1", "text": f"คำถามวัดความรู้ {sm['subject']} ข้อที่ 1", "max_score": 10},
                {"id": "q2", "text": f"คำถามวัดความรู้ {sm['subject']} ข้อที่ 2", "max_score": 10}
            ],
            "created_by": t["username"],
            "is_deleted": False
        }
        new_exams.append(exam)
        
    if new_exams:
        await db["exams"].insert_many(new_exams)
        print("✅ Created 3 new exams for the 3 teachers.")
        
    # 4. Redistribute the 10 students to these 3 subjects
    students = await db["users"].find({"role": "student"}).to_list(100)
    print(f"🎓 Found {len(students)} students.")
    
    available_subjects = [sm["subject"] for sm in subject_map[:len(selected_teachers)]]
    
    for i, s in enumerate(students):
        # Assign 1 subject to each student in a round-robin fashion, ensuring ~3-4 students per subject
        assigned_subject = available_subjects[i % len(available_subjects)]
        await db["users"].update_one(
            {"_id": s["_id"]},
            {"$set": {"enrolled_subjects": [assigned_subject]}}
        )
        
    print(f"✅ Reassigned {len(students)} students to the {len(available_subjects)} new subjects.")

    # Verification
    print("\n--- 📊 FINAL DISTRIBUTION ---")
    for sub in available_subjects:
        count = await db["users"].count_documents({"role": "student", "enrolled_subjects": sub})
        print(f"📘 {sub:<15}: {count} students")

    client.close()

if __name__ == "__main__":
    asyncio.run(reset_db())
