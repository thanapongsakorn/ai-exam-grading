import asyncio
import os
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db
from app.models import ExamModel, QuestionModel, RubricItem

async def seed_exams():
    print("🌱 Seeding Sample Exams...")
    db.connect()
    
    try:
        exams_collection = db.db["exams"]
        
        exams_to_create = [
            # 1. วิทยาศาสตร์
            ExamModel(
                subject="วิทยาศาสตร์",
                title="ความรู้พื้นฐานทางวิทยาศาสตร์และสิ่งแวดล้อม",
                description="ข้อสอบวัดความรู้เกี่ยวกับวัฏจักรธรรมชาติและระบบนิเวศ",
                questions=[
                    QuestionModel(
                        id="sci_q1",
                        text="จงอธิบายกระบวนการเกิดวัฏจักรของน้ำมาพอสังเขป",
                        max_score=10,
                        answer_key="น้ำระเหย กลายเป็นไอ คอนเดนส์เป็นเมฆ และตกลงมาเป็นฝน",
                        rubric=[
                            RubricItem(score=10, level="ดีเยี่ยม", description="อธิบายครบทั้ง 4 ขั้นตอน (ระเหย, ควบแน่น, ฝน, การรวมตัว) อย่างชัดเจน"),
                            RubricItem(score=7, level="ดี", description="อธิบายขั้นตอนสำคัญได้เกือบครบ แต่ขาดรายละเอียดบางส่วน"),
                            RubricItem(score=4, level="พอใช้", description="อธิบายได้เพียงบางขั้นตอน หรือภาพรวมยังไม่ชัดเจน"),
                            RubricItem(score=0, level="ควรปรับปรุง", description="ไม่อธิบายหรือคำตอบไม่ถูกต้อง")
                        ]
                    ),
                    QuestionModel(
                        id="sci_q2",
                        text="ทำไมพืชจึงมีความสำคัญต่อระบบนิเวศและการดำรงชีวิตของมนุษย์",
                        max_score=10,
                        answer_key="พืชเป็นผู้ผลิต สร้างออกซิเจน และเป็นแหล่งอาหาร",
                        rubric=[
                            RubricItem(score=10, level="ดีเยี่ยม", description="ระบุเหตุผลครบถ้วน (ผู้ผลิต, ออกซิเจน, แหล่งอาหาร, สมดุลธรรมชาติ)"),
                            RubricItem(score=6, level="ดี", description="ระบุเหตุผลได้ 2-3 ประเด็นสำคัญ"),
                            RubricItem(score=3, level="พอใช้", description="ระบุเหตุผลได้เพียงประเด็นเดียว"),
                            RubricItem(score=0, level="ควรปรับปรุง", description="คำตอบไม่ตรงประเด็น")
                        ]
                    )
                ],
                created_by="teacher1"
            ),
            # 2. ประวัติศาสตร์
            ExamModel(
                subject="ประวัติศาสตร์",
                title="ประวัติศาสตร์ไทยและการเปลี่ยนแปลงครั้งสำคัญ",
                description="วิเคราะห์เหตุการณ์สำคัญในประวัติศาสตร์ไทย",
                questions=[
                    QuestionModel(
                        id="his_q1",
                        text="จงอธิบายสาเหตุสำคัญที่ทำให้เกิดการเปลี่ยนแปลงการปกครอง พ.ศ. 2475",
                        max_score=10,
                        answer_key="ภาวะเศรษฐกิจตกต่ำ, อิทธิพลแนวคิดประชาธิปไตยจากตะวันตก, ความต้องการสิทธิเสรีภาพ",
                        rubric=[
                            RubricItem(score=10, level="ดีเยี่ยม", description="วิเคราะห์สาเหตุได้ลึกซึ้ง ครอบคลุมทั้งด้านเศรษฐกิจ สังคม และการเมือง"),
                            RubricItem(score=7, level="ดี", description="ระบุสาเหตุสำคัญได้ 2 ด้านขึ้นไปพร้อมคำอธิบายประกอบ"),
                            RubricItem(score=4, level="พอใช้", description="ระบุสาเหตุได้เพียงด้านเดียว หรืออธิบายไม่ชัดเจน"),
                            RubricItem(score=0, level="ควรปรับปรุง", description="ข้อมูลไม่ถูกต้องตามหลักประวัติศาสตร์")
                        ]
                    ),
                    QuestionModel(
                        id="his_q2",
                        text="จงอธิบายบทบาทของรัชกาลที่ 5 ในการปฏิรูประหว่างประเทศเพื่อรักษาเอกราชของไทย",
                        max_score=10,
                        answer_key="การเลิกทาส, การปฏิรูประบบราชการ, การเสด็จประพาสยุโรปเพื่อเจริญสัมพันธไมตรี",
                        rubric=[
                            RubricItem(score=10, level="ดีเยี่ยม", description="ยกตัวอย่างนโยบายและเหตุการณ์สำคัญได้อย่างถูกต้องและชัดเจน"),
                            RubricItem(score=6, level="ดี", description="อธิบายบทบาทสำคัญได้ แต่ขาดตัวอย่างประกอบที่ชัดเจนบางส่วน"),
                            RubricItem(score=3, level="พอใช้", description="จำข้อมูลสับสนหรือให้ข้อมูลเพียงเล็กน้อย"),
                            RubricItem(score=0, level="ควรปรับปรุง", description="ไม่มีข้อมูลที่เป็นประโยชน์")
                        ]
                    )
                ],
                created_by="teacher1"
            ),
            # 3. ภาษาอังกฤษ
            ExamModel(
                subject="ภาษาอังกฤษ",
                title="English Communication and Global Awareness",
                description="Testing essay writing and critical thinking in English.",
                questions=[
                    QuestionModel(
                        id="eng_q1",
                        text="Discuss the importance of learning English in the modern world.",
                        max_score=10,
                        answer_key="Global language for business, technology, education, and international communication.",
                        rubric=[
                            RubricItem(score=10, level="Advanced", description="Excellent grammar, vocabulary, and strong arguments covering multiple sectors."),
                            RubricItem(score=7, level="Intermediate", description="Good flow and clear ideas, but with some minor grammatical errors."),
                            RubricItem(score=4, level="Basic", description="Simple sentences with limited vocabulary and several errors."),
                            RubricItem(score=0, level="Beginner", description="Unintelligible or irrelevant response.")
                        ]
                    ),
                    QuestionModel(
                        id="eng_q2",
                        text="Write a short paragraph about your favorite holiday destination and explain why you like it.",
                        max_score=10,
                        answer_key="Requires descriptive language and reasons (e.g., scenery, culture, activities).",
                        rubric=[
                            RubricItem(score=10, level="Advanced", description="Vivid descriptions and clear reasons with sophisticated vocabulary."),
                            RubricItem(score=6, level="Good", description="Clear choice and reasons, though descriptions may be simple."),
                            RubricItem(score=3, level="Fair", description="Lists the destination but provides weak or repeated reasons."),
                            RubricItem(score=0, level="Poor", description="Fails to describe a destination or give reasons.")
                        ]
                    )
                ],
                created_by="teacher1"
            )
        ]
        
        for exam in exams_to_create:
            # Check if exam with title already exists to avoid duplicates
            existing = await exams_collection.find_one({"title": exam.title})
            if existing:
                print(f"⏩ Skipping existing exam: {exam.title}")
                continue
                
            await exams_collection.insert_one(exam.model_dump(by_alias=True, exclude={"id"}))
            print(f"✅ Created exam: {exam.title}")
            
        print("\n✨ Seeding completed successfully!")

    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_exams())
