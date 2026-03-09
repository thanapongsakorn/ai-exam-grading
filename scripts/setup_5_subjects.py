import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def setup():
    print("🔄 Expanding to 5 Teachers/Subjects & Distributing Students...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # 1. Ensure 2 new teachers exist
    new_teachers = [
        {"username": "teacher_eng", "password": pwd_context.hash("password123"), "role": "teacher"},
        {"username": "teacher_soc", "password": pwd_context.hash("password123"), "role": "teacher"}
    ]
    
    for nt in new_teachers:
        exists = await db["users"].find_one({"username": nt["username"]})
        if not exists:
            await db["users"].insert_one(nt)
            
    # 2. Ensure 2 new exams exist
    new_exams = [
        {"subject": "ภาษาอังกฤษ", "title": "ข้อสอบภาษาอังกฤษ (หลัก)", "created_by": "teacher_eng"},
        {"subject": "สังคมศึกษา", "title": "ข้อสอบสังคมศึกษา (หลัก)", "created_by": "teacher_soc"}
    ]
    for ne in new_exams:
        exists = await db["exams"].find_one({"subject": ne["subject"]})
        if not exists:
            exam_data = {
                "title": ne["title"],
                "subject": ne["subject"],
                "description": f"ข้อสอบทดสอบความรู้พื้นฐานวิชา {ne['subject']}",
                "questions": [
                    {"id": "q1", "text": f"คำถามวัดความรู้ {ne['subject']} ข้อที่ 1", "max_score": 10},
                    {"id": "q2", "text": f"คำถามวัดความรู้ {ne['subject']} ข้อที่ 2", "max_score": 10}
                ],
                "created_by": ne["created_by"],
                "is_deleted": False
            }
            await db["exams"].insert_one(exam_data)
            
    # 3. We now have 5 core subjects
    subjects = ["คณิตศาสตร์", "ภาษาไทย", "วิทยาศาสตร์", "ภาษาอังกฤษ", "สังคมศึกษา"]
    
    # 4. Distribute 10 students so each gets exactly 2 subjects 
    # This matrix guarantees exactly 4 students per subject overall
    distribution = [
        [0, 1], # student01: คณิต, ไทย
        [1, 2], # student02: ไทย, วิทย์
        [2, 3], # student03: วิทย์, อังกฤษ
        [3, 4], # student04: อังกฤษ, สังคม
        [4, 0], # student05: สังคม, คณิต
        [0, 2], # student06: คณิต, วิทย์
        [1, 3], # student07: ไทย, อังกฤษ
        [2, 4], # student08: วิทย์, สังคม
        [3, 0], # student09: อังกฤษ, คณิต
        [4, 1]  # student10: สังคม, ไทย
    ]
    
    print("\n--- 🧑‍🎓 STUDENT ENROLLMENTS (2 subjects each) ---")
    for i in range(1, 11):
        username = f"student{i:02d}"
        idxs = distribution[i-1]
        enrolled = [subjects[idx] for idx in idxs]
        
        await db["users"].update_one(
            {"username": username, "role": "student"},
            {"$set": {"enrolled_subjects": enrolled}}
        )
        print(f"👤 {username:<12}: {', '.join(enrolled)}")
        
    print("\n✅ Setup Complete!")
    
    # 5. Verify Distribution
    print("\n--- 📊 FINAL SUBJECT DISTRIBUTION ---")
    for sub in subjects:
        count = await db["users"].count_documents({"role": "student", "enrolled_subjects": sub})
        print(f"📘 {sub:<15}: {count} students")

    client.close()

if __name__ == "__main__":
    asyncio.run(setup())
