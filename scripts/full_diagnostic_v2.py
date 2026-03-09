import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def full_diagnostic(username):
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "diagnostic_results.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"--- DIAGNOSTIC FOR {username} ---\n")
        client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
        db = client[os.getenv('DB_NAME')]
        
        user = await db["users"].find_one({"username": username})
        f.write(f"User Document: {user}\n")
        
        if user:
            enrolled = user.get("enrolled_subjects", [])
            f.write(f"Enrolled Type: {type(enrolled)}\n")
            for s in enrolled:
                 f.write(f"  - '{s}' | Hex: {s.encode('utf-8').hex() if isinstance(s, str) else 'NOT_A_STRING'}\n")
        
        exams = await db["exams"].find({"is_deleted": {"$ne": True}}).to_list(500)
        f.write(f"\nActive Exams ({len(exams)}):\n")
        for ex in exams:
            subj = ex.get("subject")
            f.write(f"  - Title: {ex.get('title'):<30} | Subj: '{subj}' | Hex: {subj.encode('utf-8').hex() if subj else 'NONE'}\n")

        client.close()
    print(f"✅ Diagnostic written to {output_path}")

if __name__ == "__main__":
    import sys
    u = sys.argv[1] if len(sys.argv) > 1 else "student1"
    asyncio.run(full_diagnostic(u))
