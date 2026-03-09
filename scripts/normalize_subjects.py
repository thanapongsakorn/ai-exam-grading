import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

async def normalize_subjects():
    print("🧹 Normalizing subject names in 'exams' collection...")
    db.connect()
    
    try:
        exams_collection = db.db["exams"]
        
        # Find all exams
        cursor = exams_collection.find({})
        async for exam in cursor:
            old_subject = exam.get("subject")
            if old_subject:
                new_subject = old_subject.strip()
                if old_subject != new_subject:
                    await exams_collection.update_one(
                        {"_id": exam["_id"]},
                        {"$set": {"subject": new_subject}}
                    )
                    print(f"  ✅ Normalized: '{old_subject}' -> '{new_subject}'")
        
        print("🎉 Normalization complete.")
            
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(normalize_subjects())
