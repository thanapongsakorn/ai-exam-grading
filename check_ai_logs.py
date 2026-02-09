
import asyncio
from app.database import db
from pprint import pprint

async def check_logs():
    print("Connecting to DB...")
    db.connect()
    
    print("\n--- Latest 5 AI Logs ---")
    logs_cursor = db.db["ai_logs"].find().sort("timestamp", -1).limit(5)
    logs = await logs_cursor.to_list(length=5)
    
    with open("ai_logs_dump.txt", "w", encoding="utf-8") as f:
        if not logs:
            f.write("No logs found.\n")
        
        for log in logs:
            f.write(f"\nID: {log.get('_id')}\n")
            f.write(f"Timestamp: {log.get('timestamp')}\n")
            f.write(f"Status: {log.get('status')}\n")
            f.write(f"Context: {log.get('context')}\n")
            f.write(f"Error: {log.get('error')}\n")
            if log.get("raw_response"):
                f.write(f"Raw Response Preview: {log.get('raw_response')[:200]}...\n")
                f.write(f"Full Raw Response: {log.get('raw_response')}\n")
    print("Logs written to ai_logs_dump.txt")

if __name__ == "__main__":
    asyncio.run(check_logs())
