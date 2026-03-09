import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

async def final_verify():
    print("🔍 Final Verification: Question Count per Subject")
    db.connect()
    
    try:
        exams_collection = db.db["exams"]
        teachers = ['teacher_sci', 'teacher_thai', 'teacher_math']
        
        for t in teachers:
            exam = await exams_collection.find_one({"created_by": t})
            if exam:
                q_count = len(exam.get("questions", []))
                print(f"Teacher: {t:12} | Exam: {exam['title']:40} | Questions: {q_count}")
                if q_count == 5:
                    print(f"  ✅ Perfect!")
                else:
                    print(f"  ❌ Expected 5, found {q_count}")
            else:
                print(f"Teacher: {t:12} | ❌ No exam found!")
                
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(final_verify())
