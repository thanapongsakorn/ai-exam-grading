
import asyncio
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "exam_db")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("--- Security Verification ---")
    
    # 1. Check Password Hashing
    user = await db["users"].find_one({"username": "student1"})
    if user:
        is_hashed = user["password"].startswith("$2b$") or user["password"].startswith("$2a$")
        print(f"[*] Password for student1 is hashed: {is_hashed}")
        print(f"[*] Password verification works: {pwd_context.verify('password', user['password'])}")
    else:
        print("[!] student1 not found")

    # 2. Check Role Logic
    teacher = await db["users"].find_one({"username": "teacher1"})
    if teacher:
        print(f"[*] teacher1 role is correct: {teacher['role'] == 'teacher'}")
    else:
        print("[!] teacher1 not found")
        
    # 3. Check AI Logs (Phase 3)
    log_count = await db["ai_logs"].count_documents({})
    print(f"[*] AI Logs found in DB: {log_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify())
