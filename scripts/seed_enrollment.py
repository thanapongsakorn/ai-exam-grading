import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

async def seed_enrollment():
    print("🌱 Seeding enrollment for 'student1'...")
    db.connect()
    
    try:
        user_collection = db.db["users"]
        
        # Subjects to enroll in
        subjects_to_enroll = ["วิทยาศาสตร์", "คณิตศาสตร์"]
        
        result = await user_collection.update_one(
            {"username": "student1"},
            {"$set": {"enrolled_subjects": subjects_to_enroll}}
        )
        
        if result.matched_count > 0:
            print(f"✅ Successfully enrolled 'student1' in: {', '.join(subjects_to_enroll)}")
        else:
            print("❌ User 'student1' not found. Please register or seed the user first.")
            
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_enrollment())
