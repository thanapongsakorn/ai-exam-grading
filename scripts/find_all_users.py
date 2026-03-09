import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def find_all_users():
    print("🕵️ Listing all users and their enrollments...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    users = await db["users"].find().to_list(100)
    print(f"Total users found: {len(users)}")
    for u in users:
        uname = u.get("username")
        enrolled = u.get("enrolled_subjects", [])
        uname_hex = uname.encode('utf-8').hex() if uname else "NONE"
        print(f"User: '{uname}' | Hex: {uname_hex} | Enrolled: {len(enrolled)} subjects")
        if enrolled:
            print(f"  - Subjects: {enrolled}")
        print("-" * 20)
        
    client.close()

if __name__ == "__main__":
    asyncio.run(find_all_users())
