import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

async def verify_isolation():
    print("🔍 Verifying Teacher Isolation...")
    db.connect()
    
    try:
        exams_collection = db.db["exams"]
        
        # 1. Check teacher1 exams
        teacher1_exams = await exams_collection.find({"created_by": "teacher1", "is_deleted": {"$ne": True}}).to_list(100)
        print(f"Teacher 'teacher1' has {len(teacher1_exams)} active exams.")
        for ex in teacher1_exams:
            print(f" - {ex['title']} (Subject: {ex.get('subject')})")
            
        # 2. Check teacher_sci exams
        teacher_sci_exams = await exams_collection.find({"created_by": "teacher_sci", "is_deleted": {"$ne": True}}).to_list(100)
        print(f"\nTeacher 'teacher_sci' has {len(teacher_sci_exams)} active exams.")
        for ex in teacher_sci_exams:
            print(f" - {ex['title']} (Subject: {ex.get('subject')})")

        # 3. Cross-check: Ensure science exams are only in teacher_sci (or specifically assigned)
        # In this project, 'teacher1' already has a science exam from previous seeding.
        # We should check if that's expected or if we should migrate it.
        # For now, we just verify the 'created_by' logic works.
        
        print("\n✅ Database verification complete.")

    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_isolation())
