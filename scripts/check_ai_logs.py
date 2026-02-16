import asyncio
import os
import sys
from bson import json_util
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import db

async def check_logs():
    try:
        db.connect()
        # Find the latest log entry
        latest_log = await db.db["ai_logs"].find().sort("timestamp", -1).limit(1).to_list(1)
        if latest_log:
            print("LATEST AI LOG ENTRY:")
            print(json.dumps(json.loads(json_util.dumps(latest_log[0])), indent=2, ensure_ascii=False))
        else:
            print("No AI logs found.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_logs())
