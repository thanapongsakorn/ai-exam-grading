import asyncio
import os
import sys
from passlib.context import CryptContext

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import ExamModel, QuestionModel, RubricItem

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_teacher_science():
    print("🌱 Seeding Science Teacher and Exam...")
    db.connect()
    
    try:
        # 1. Create Teacher
        users_collection = db.db["users"]
        teacher_username = "teacher_sci"
        teacher_password = "password123"
        
        existing_user = await users_collection.find_one({"username": teacher_username})
        if not existing_user:
            await users_collection.insert_one({
                "username": teacher_username,
                "password": pwd_context.hash(teacher_password),
                "role": "teacher"
            })
            print(f"✅ Created teacher: {teacher_username}")
        else:
            print(f"⏩ Teacher {teacher_username} already exists.")

        # 2. Create Science Exam
        exams_collection = db.db["exams"]
        science_exam = ExamModel(
            subject="วิทยาศาสตร์",
            title="การทดลองวิทยาศาสตร์พื้นฐาน 101",
            description="ข้อสอบวัดความรู้พื้นฐานเกี่ยวกับการทดลองและกระบวนการทางวิทยาศาสตร์",
            questions=[
                QuestionModel(
                    id="sci_new_q1",
                    text="จงอธิบายความสำคัญของตัวแปรควบคุมในการทดลองวิทยาศาสตร์",
                    max_score=10,
                    answer_key="ตัวแปรควบคุมช่วยให้มั่นใจว่าผลลัพธ์ที่เกิดมาจากตัวแปรต้นเพียงอย่างเดียว",
                    rubric=[
                        RubricItem(score=10, level="ดีเยี่ยม", description="อธิบายเหตุผลได้ชัดเจนและถูกต้องตามหลักการทดลอง"),
                        RubricItem(score=5, level="พอใช้", description="อธิบายได้บ้างแต่ยังไม่ครอบคลุม"),
                        RubricItem(score=0, level="ควรปรับปรุง", description="ไม่อธิบายหรือคำตอบไม่ถูกต้อง")
                    ]
                )
            ],
            created_by=teacher_username
        )
        
        existing_exam = await exams_collection.find_one({"title": science_exam.title})
        if not existing_exam:
            await exams_collection.insert_one(science_exam.model_dump(by_alias=True, exclude={"id"}))
            print(f"✅ Created science exam: {science_exam.title}")
        else:
            print(f"⏩ Science exam '{science_exam.title}' already exists.")
            
        print("\n✨ Seeding completed successfully!")

    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_teacher_science())
