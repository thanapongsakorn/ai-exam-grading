import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import ExamModel, QuestionModel

async def seed_science_exam():
    # Connect to database
    db.connect()
    
    # Check if science exam already exists to avoid duplicates
    existing = await db.db["exams"].find_one({"title": "วิชาวิทยาศาสตร์ (พื้นฐาน)"})
    if existing:
        print("Science exam already exists.")
        db.disconnect()
        return

    questions = [
        QuestionModel(
            id="q1",
            text="จงอธิบายกระบวนการเกิดปรากฏการณ์เรือนกระจก (Greenhouse Effect) และผลกระทบต่อสิ่งแวดล้อม",
            max_score=10,
            answer_key="ก๊าซเรือนกระจก (เช่น CO2, CH4) กักเก็บความร้อนสะท้อนจากผิวโลก ทำให้อุณหภูมิโลกสูงขึ้น ส่งผลต่อสภาพภูมิอากาศและการละลายของน้ำแข็งขั้วโลก",
            grading_criteria="ต้องมีการกล่าวถึงชื่อก๊าซเรือนกระจกอย่างน้อย 1 ชนิด, กลไกการกักเก็บความร้อน, และผลกระทบต่ออุณหภูมิโลก"
        ),
        QuestionModel(
            id="q2",
            text="เหตุใดการสังเคราะห์แสงของพืชจึงมีความสำคัญต่อระบบนิเวศของสิ่งมีชีวิตบนโลก?",
            max_score=10,
            answer_key="เป็นกระบวนการผลิตอาหาร (น้ำตาล) และก๊าซออกซิเจน ซึ่งเป็นพื้นฐานของห่วงโซ่อาหารและการหายใจของสิ่งมีชีวิต",
            grading_criteria="ต้องอธิบายเรื่องการเปลี่ยนพลังงานแสงเป็นพลังงานเคมี (อาหาร) และการปล่อยออกซิเจน"
        )
    ]
    
    science_exam = ExamModel(
        title="วิชาวิทยาศาสตร์ (พื้นฐาน)",
        description="ทดสอบความรู้พื้นฐานด้านปรากฏการณ์ธรรมชาติและระบบนิเวศ",
        questions=questions,
        created_by="teacher1"
    )
    
    result = await db.db["exams"].insert_one(science_exam.model_dump(by_alias=True, exclude={"id"}))
    print(f"Science exam inserted with id: {result.inserted_id}")
    
    db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_science_exam())
