
import asyncio
from app.database import db
from pprint import pprint

async def check_latest_exam():
    print("Connecting to DB...")
    db.connect()
    
    print("\n--- Latest Exam ---")
    exam = await db.db["exams"].find().sort("_id", -1).limit(1).to_list(length=1)
    
    with open("exam_dump.txt", "w", encoding="utf-8") as f:
        if not exam:
            f.write("No exams found.\n")
        else:
            f.write(str(exam[0]))
            
    print("Exam written to exam_dump.txt")

if __name__ == "__main__":
    asyncio.run(check_latest_exam())
