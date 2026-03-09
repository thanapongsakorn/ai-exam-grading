import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

async def verify_fix():
    print("🔍 Verifying Connection Fix...")
    db.connect()
    success = await db.test_connection()
    if success:
        print("✅ SUCCESS: Connection established!")
    else:
        print("❌ FAILURE: All connection attempts failed.")

if __name__ == "__main__":
    asyncio.run(verify_fix())
