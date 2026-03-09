import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

load_dotenv()

async def fix_user_data(username):
    print(f"🛠️ Fixing data for user: {username}")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    user_coll = db["users"]
    
    user = await user_coll.find_one({"username": username})
    if user:
        if user.get("_id") is None:
            print("  ⚠️ Found _id: None. Recreating document with proper ObjectId...")
            # Save data
            data = dict(user)
            del data["_id"]
            
            # Delete old doc
            await user_coll.delete_one({"username": username, "_id": None})
            
            # Insert new doc
            await user_coll.insert_one(data)
            print("  ✅ User recreated with new ObjectId.")
        else:
            print(f"  ✅ User already has valid _id: {user['_id']}")
            
        # Clean enrollments just in case
        enrolled = user.get("enrolled_subjects", [])
        cleaned = sorted(list(set(s.strip() for s in enrolled if isinstance(s, str))))
        if cleaned != enrolled:
            await user_coll.update_one({"username": username}, {"$set": {"enrolled_subjects": cleaned}})
            print(f"  ✅ Enrollment list cleaned: {cleaned}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_user_data("test_stud_1"))
    asyncio.run(fix_user_data("student1"))
