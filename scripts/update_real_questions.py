import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# Real questions tailored to each subject and topic
QUESTIONS_DATA = {
    "คณิตศาสตร์": [
        "จงอธิบายคอนเซปต์ของความน่าจะเป็น (Probability) พร้อมยกตัวอย่างสถานการณ์ในชีวิตประจำวันมา 1 ตัวอย่าง",
        "สมการเชิงเส้นตัวแปรเดียวคืออะไร? จงเขียนสมการ 1 รูปแบบแล้วแสดงวิธีหาคำตอบอย่างละเอียด",
        "ทฤษฎีบทพีทาโกรัสมีประโยชน์อย่างไรในการหาความยาวด้านของรูปสามเหลี่ยมมุมฉาก?",
        "อธิบายความแตกต่างระหว่าง 'ค่าเฉลี่ย' (Mean) และ 'มัธยฐาน' (Median) พร้อมยกตัวอย่างชุดข้อมูล",
        "ฟังก์ชัน (Function) ทางคณิตศาสตร์คืออะไร มีความเกี่ยวข้องกับการแสดงความสัมพันธ์ระหว่างตัวแปรอย่างไร?"
    ],
    "ภาษาไทย": [
        "จงอธิบายความหมายและยกตัวอย่างของคำว่า 'คำไวพจน์' (คำพ้องความหมาย) มาอย่างน้อย 5 คำ",
        "โครงสร้างของการเขียนเรียงความประกอบด้วยอะไรบ้าง? แต่ละส่วนมีความสำคัญอย่างไร",
        "การแต่งกลอนแปดมีฉันทลักษณ์และข้อบังคับในการสัมผัสอย่างไรบ้าง จงอธิบาย",
        "ความแตกต่างระหว่าง 'ภาษาพูด' และ 'ภาษาเขียน' คืออะไร? ควรเลือกใช้ในสถานการณ์ไหน?",
        "อธิบายคุณค่าทางวรรณศิลป์ที่มักพบในวรรณคดีไทย (เช่น การเล่นคำ, การใช้ภาพพจน์)"
    ],
    "วิทยาศาสตร์": [
        "กระบวนการสังเคราะห์ด้วยแสง (Photosynthesis) ของพืชมีองค์ประกอบสำคัญอะไรบ้าง และให้ผลผลิตคืออะไร?",
        "อธิบายความแตกต่างระหว่าง 'การเปลี่ยนแปลงทางกายภาพ' และ 'การเปลี่ยนแปลงทางเคมี' พร้อมยกตัวอย่าง",
        "แรงโน้มถ่วง (Gravity) มีผลอย่างไรต่อโลกของเราและระบบสุริยะ?",
        "เซลล์พืชและเซลล์สัตว์มีความแตกต่างกันในเรื่องของโครงสร้างอะไรบ้าง?",
        "วัฏจักรของน้ำ (Water Cycle) ประกอบด้วยขั้นตอนหลักอะไรบ้าง จงอธิบายมาโดยสังเขป"
    ],
    "ภาษาอังกฤษ": [
        "Explain the difference between Present Simple and Present Continuous tense, and provide one example for each.",
        "Write a short paragraph (3-4 sentences) introducing yourself and your hobbies.",
        "What are adjectives used for in an English sentence? Give 3 examples of adjectives.",
        "Explain how to form a regular past tense verb and provide examples.",
        "Explain the concept of 'countable' vs 'uncountable' nouns and list 3 examples of each."
    ],
    "สังคมศึกษา": [
        "ประชาธิปไตยคืออะไร? และหลักการสำคัญของระบอบประชาธิปไตยมีอะไรบ้าง?",
        "อธิบายสาเหตุหลักที่ทำให้เกิดภาวะโลกร้อน (Global Warming) และผลกระทบที่มีต่อสภาพแวดล้อม",
        "องค์ประกอบของแผนที่มีอะไรบ้าง? และมีประโยชน์อย่างไรในการศึกษาภูมิศาสตร์",
        "ความหมายและหน้าที่เบื้องต้นของ 'ธนาคารพาณิชย์' ในระบบเศรษฐกิจคืออะไร?",
        "อธิบายความสำคัญของการปฏิวัติอุตสาหกรรม (Industrial Revolution) ที่มีต่อโลกสมัยใหม่"
    ]
}

async def update_real_questions():
    print("🧠 Updating exams with real academic questions...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    updated = 0
    for subject, questions in QUESTIONS_DATA.items():
        # Find the 5 exams for this subject, ordered by title (หัวข้อที่ 1 -> 5)
        exams = await db["exams"].find({"subject": subject}).sort("title", 1).to_list(5)
        
        for i, exam in enumerate(exams):
            if i < len(questions):
                real_question = questions[i]
                
                # Update the question text and description
                await db["exams"].update_one(
                    {"_id": exam["_id"]},
                    {
                        "$set": {
                            "description": f"แบบทดสอบวัดความรู้เชิงบรรยายและวิเคราะห์",
                            "questions.0.text": real_question,
                            "questions.0.max_score": 10
                        }
                    }
                )
                updated += 1
                
    print(f"✅ Successfully updated {updated} exams with real questions.")
    client.close()

if __name__ == "__main__":
    asyncio.run(update_real_questions())
