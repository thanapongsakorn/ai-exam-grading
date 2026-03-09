import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def expand_exams():
    print("➕ Expanding all exams to 5 questions...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    exams = await db["exams"].find().to_list(10)
    updated_count = 0
    
    for exam in exams:
        subject = exam.get("subject", "ทั่วไป")
        current_len = len(exam.get("questions", []))
        
        if current_len < 5:
            new_questions = []
            for i in range(current_len + 1, 6):
                new_questions.append({
                    "id": f"q{i}",
                    "text": f"คำถามวัดความรู้ {subject} ข้อที่ {i} (วิเคราะห์เชิงลึก)",
                    "max_score": 10
                })
                
            await db["exams"].update_one(
                {"_id": exam["_id"]},
                {"$push": {"questions": {"$each": new_questions}}}
            )
            updated_count += 1
            print(f"Added {len(new_questions)} questions to {subject} exam.")
            
    print(f"✅ Successfully expanded {updated_count} exams to 5 questions each.")
    client.close()

if __name__ == "__main__":
    asyncio.run(expand_exams())
