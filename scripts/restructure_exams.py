import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def structure_exams():
    print("🔄 Restructuring Exams: 5 Topics per Subject, 1 Question Each...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # Define subjects and their owners
    subjects_info = [
        {"subject": "คณิตศาสตร์", "teacher": "teacher_math"},
        {"subject": "ภาษาไทย", "teacher": "teacher_thai"},
        {"subject": "วิทยาศาสตร์", "teacher": "teacher_sci"},
        {"subject": "ภาษาอังกฤษ", "teacher": "teacher_eng"},
        {"subject": "สังคมศึกษา", "teacher": "teacher_soc"}
    ]
    
    # 1. Delete all existing exams
    await db["exams"].delete_many({})
    print("🗑️ Deleted all previous exams.")
    
    # 2. Create 5 separate exams for each subject
    new_exams = []
    
    for info in subjects_info:
        for i in range(1, 6):
            exam = {
                "title": f"ข้อสอบ{info['subject']} หัวข้อที่ {i}",
                "subject": info['subject'],
                "description": f"แบบทดสอบย่อยวิชา{info['subject']} ประจำหัวข้อที่ {i}",
                "questions": [
                    {
                        "id": "q1", 
                        "text": f"จงอธิบายและวิเคราะห์เนื้อหาของ{info['subject']}ในหัวข้อที่ {i}", 
                        "max_score": 10
                    }
                ],
                "created_by": info['teacher'],
                "is_deleted": False
            }
            new_exams.append(exam)
            
    # 3. Insert into DB
    result = await db["exams"].insert_many(new_exams)
    print(f"✅ Successfully created {len(result.inserted_ids)} separate exams (5 per subject).")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(structure_exams())
