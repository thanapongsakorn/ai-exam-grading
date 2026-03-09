import asyncio
import os
import sys
from passlib.context import CryptContext

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import ExamModel, QuestionModel, RubricItem

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_additional_teachers():
    print("🌱 Seeding Thai and Math Teachers and Exams...")
    db.connect()
    
    try:
        users_collection = db.db["users"]
        exams_collection = db.db["exams"]
        
        teachers_data = [
            {
                "username": "teacher_thai",
                "password": "password123",
                "subject": "ภาษาไทย",
                "exam_title": "วรรณคดีและภาษาไทยร่วมสมัย",
                "exam_desc": "ทดสอบความเข้าใจในวิวัฒนาการของภาษาและวรรณคดีไทย",
                "question": {
                    "text": "จงอธิบายความสำคัญของการใช้คำราชาศัพท์ในสังคมไทยในปัจจุบัน",
                    "key": "เป็นการแสดงความเคารพและรักษาวัฒนธรรมอันดีงามของไทย",
                    "rubric": [
                        RubricItem(score=10, level="ดีเยี่ยม", description="อธิบายเหตุผลได้ลึกซึ้ง ครอบคลุมทั้งด้านวัฒนธรรมและภาษา"),
                        RubricItem(score=5, level="พอใช้", description="อธิบายได้ในระดับพื้นฐาน"),
                        RubricItem(score=0, level="ควรปรับปรุง", description="ไม่อธิบายหรือคำตอบไม่ถูกต้อง")
                    ]
                }
            },
            {
                "username": "teacher_math",
                "password": "password123",
                "subject": "คณิตศาสตร์",
                "exam_title": "ตรรกศาสตร์และการพิสูจน์ทางคณิตศาสตร์",
                "exam_desc": "ทดสอบทักษะการคิดคำนวณและการให้เหตุผลทางคณิตศาสตร์",
                "question": {
                    "text": "จงอธิบายความแตกต่างระหว่างการให้เหตุผลแบบอุปนัยและนิรนัย พร้อมยกตัวอย่าง",
                    "key": "อุปนัยคือสรุปจากกรณีเฉพาะไปสู่ทั่วไป นิรนัยคือสรุปจากกฎทั่วไปไปสู่กรณีเฉพาะ",
                    "rubric": [
                        RubricItem(score=10, level="ดีเยี่ยม", description="คำนิยามถูกต้องและมีตัวอย่างที่ชัดเจนทั้งสองแบบ"),
                        RubricItem(score=5, level="พอใช้", description="อธิบายได้แต่ตัวอย่างไม่ชัดเจน"),
                        RubricItem(score=0, level="ควรปรับปรุง", description="อธิบายไม่ถูกต้อง")
                    ]
                }
            }
        ]
        
        for data in teachers_data:
            # 1. Create Teacher
            existing_user = await users_collection.find_one({"username": data["username"]})
            if not existing_user:
                await users_collection.insert_one({
                    "username": data["username"],
                    "password": pwd_context.hash(data["password"]),
                    "role": "teacher"
                })
                print(f"✅ Created teacher: {data['username']}")
            else:
                print(f"⏩ Teacher {data['username']} already exists.")

            # 2. Create Exam
            existing_exam = await exams_collection.find_one({"title": data["exam_title"]})
            if not existing_exam:
                exam = ExamModel(
                    subject=data["subject"],
                    title=data["exam_title"],
                    description=data["exam_desc"],
                    questions=[
                        QuestionModel(
                            id=f"{data['username']}_q1",
                            text=data["question"]["text"],
                            max_score=10,
                            answer_key=data["question"]["key"],
                            rubric=data["question"]["rubric"]
                        )
                    ],
                    created_by=data["username"]
                )
                await exams_collection.insert_one(exam.model_dump(by_alias=True, exclude={"id"}))
                print(f"✅ Created exam: {data['exam_title']}")
            else:
                print(f"⏩ Exam '{data['exam_title']}' already exists.")
            
        print("\n✨ Seeding completed successfully!")

    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_additional_teachers())
