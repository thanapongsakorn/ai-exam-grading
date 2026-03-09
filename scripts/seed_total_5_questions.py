import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import QuestionModel, RubricItem

async def seed_total_5_questions():
    print("🌱 Adding questions to reach 5 total per subject...")
    db.connect()
    
    try:
        exams_collection = db.db["exams"]
        
        # 1. Science (teacher_sci)
        sci_new_questions = [
            QuestionModel(
                id="sci_q2",
                text="จงอธิบายกฎแห่งการอนุรักษ์พลังงาน พร้อมยกตัวอย่างประกอบ",
                max_score=10,
                answer_key="พลังงานไม่สูญหายแต่เปลี่ยนรูปได้ เช่น พลังงานไฟฟ้าเปลี่ยนเป็นความร้อน",
                rubric=[
                    RubricItem(score=10, level="ดีมาก", description="อธิบายหลักการถูกต้องและมีตัวอย่างชัดเจน"),
                    RubricItem(score=0, level="ต้องปรับปรุง", description="อธิบายผิดหลักการ")
                ]
            ),
            QuestionModel(
                id="sci_q3",
                text="ส่วนประกอบใดของเซลล์พืชที่ทำหน้าที่ในการสังเคราะห์ด้วยแสง และมีกระบวนการอย่างไรเบื้องต้น",
                max_score=10,
                answer_key="คลอโรพลาสต์ ใช้แสงร่วมกับคาร์บอนไดออกไซด์และน้ำในการสร้างน้ำตาล",
                rubric=[
                    RubricItem(score=10, level="คนเก่ง", description="ระบุคลอโรพลาสต์และอธิบายกระบวนการครบถ้วน")
                ]
            ),
            QuestionModel(
                id="sci_q4",
                text="จงสรุปขั้นตอนการทำงานของวัฏจักรน้ำมาพอสังเขป",
                max_score=10,
                answer_key="การระเหย การควบแน่น การเกิดฝน และการรวมตัวของน้ำ",
                rubric=[
                    RubricItem(score=10, level="ดี", description="ระบุครบ 4 ขั้นตอนหลัก")
                ]
            ),
            QuestionModel(
                id="sci_q5",
                text="อุปกรณ์ความปลอดภัยขั้นพื้นฐานที่จำเป็นต้องมีในห้องปฏิบัติการเคมีมีอะไรบ้าง จงยกตัวอย่าง 3 อย่าง",
                max_score=10,
                answer_key="เสื้อกาวน์ แว่นตานิรภัย ถุงมือ หรือที่ล้างตาฉุกเฉิน",
                rubric=[
                    RubricItem(score=10, level="ดี", description="ยกตัวอย่างถูกต้อง 3 อย่างขึ้นไป")
                ]
            )
        ]
        
        # 2. Thai (teacher_thai)
        thai_new_questions = [
            QuestionModel(
                id="thai_q2",
                text="จงอธิบายความหมายของสำนวน 'ชักใบให้เรือเสีย' และยกตัวอย่างสถานการณ์ที่เหมาะสม",
                max_score=10,
                answer_key="พูดหรือทำสิ่งที่ขวางการสนทนาทำให้เสียเรื่อง",
                rubric=[RubricItem(score=10, level="ดี", description="อธิบายความหมายและยกตัวอย่างได้ถูกต้อง")]
            ),
            QuestionModel(
                id="thai_q3",
                text="หลักการใช้ 'เขาสมิง' และ 'เขา' ในบริบทที่ต่างกันคืออย่างไร",
                max_score=10,
                answer_key="คำนามเฉพาะและคำสรรพนาม",
                rubric=[RubricItem(score=10, level="ดี", description="แยกบริบทได้ชัดเจน")]
            ),
            QuestionModel(
                id="thai_q4",
                text="เพราะเหตุใดการอ่านจับใจความสำคัญจึงมีความสำคัญในการเรียนรู้",
                max_score=10,
                answer_key="ช่วยให้สรุปประเด็นหลักและประหยัดเวลาในการทำความเข้าใจ",
                rubric=[RubricItem(score=10, level="ดี", description="บอกเหตุผลความสำคัญได้ดี")]
            ),
            QuestionModel(
                id="thai_q5",
                text="จงแต่งประโยคที่ประกอบด้วย ประธาน กริยา และกรรม อย่างละ 1 ประโยคพร้อมระบุส่วนประกอบ",
                max_score=10,
                answer_key="แมว(ประธาน) กิน(กริยา) ปลา(กรรม)",
                rubric=[RubricItem(score=10, level="ดี", description="แต่งประโยคและแยกส่วนประกอบได้ถูกต้อง")]
            )
        ]
        
        # 3. Math (teacher_math)
        math_new_questions = [
            QuestionModel(
                id="math_q2",
                text="จงหาค่าของ x จากสมการ 2x + 10 = 30 พร้อมแสดงวิธีคิด",
                max_score=10,
                answer_key="x = 10",
                rubric=[RubricItem(score=10, level="ดี", description="แสดงวิธีทำถูกต้องและหาค่า x ได้ 10")]
            ),
            QuestionModel(
                id="math_q3",
                text="รูปสามเหลี่ยมที่มีฐานยาว 10 ซม. และสูง 8 ซม. จะมีพื้นที่เท่าใด",
                max_score=10,
                answer_key="40 ตารางเซนติเมตร",
                rubric=[RubricItem(score=10, level="ดี", description="ใช้สูตร 1/2 * ฐาน * สูง คำนวณได้ถูกต้อง")]
            ),
            QuestionModel(
                id="math_q4",
                text="ค่าเฉลี่ยเลขคณิตของ 5, 10, 15, 20 คือเท่าใด",
                max_score=10,
                answer_key="12.5",
                rubric=[RubricItem(score=10, level="ดี", description="คำนวณผลรวมหารด้วยจำนวนได้ถูกต้อง")]
            ),
            QuestionModel(
                id="math_q5",
                text="สินค้าชิ้นหนึ่งราคา 500 บาท ลดราคา 20% จะต้องจ่ายเงินกี่บาท",
                max_score=10,
                answer_key="400 บาท",
                rubric=[RubricItem(score=10, level="ดี", description="คำนวณส่วนลดและราคาขายจริงได้ถูกต้อง")]
            )
        ]
        
        subjects = {
            "teacher_sci": sci_new_questions,
            "teacher_thai": thai_new_questions,
            "teacher_math": math_new_questions
        }
        
        for teacher, q_list in subjects.items():
            exam = await exams_collection.find_one({"created_by": teacher})
            if exam:
                current_questions = exam.get("questions", [])
                # Filter out those we might have already added if script is re-run
                existing_ids = [q.get("id") for q in current_questions]
                to_add = [q.model_dump(by_alias=True) for q in q_list if q.id not in existing_ids]
                
                if to_add:
                    await exams_collection.update_one(
                        {"_id": exam["_id"]},
                        {"$push": {"questions": {"$each": to_add}}}
                    )
                    print(f"✅ Added {len(to_add)} questions to exam created by {teacher}.")
                else:
                    print(f"⏩ No new questions to add for {teacher}.")
            else:
                print(f"❌ Could not find exam for teacher: {teacher}")
                
        print("\n✨ All exams now have 5 questions!")

    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_total_5_questions())
