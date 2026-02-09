import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

async def clear_submissions():
    # Connect to database
    db.connect()
    
    try:
        submissions_collection = db.db["submissions"]
        count = await submissions_collection.count_documents({})
        print(f"Found {count} submission(s) to delete.")
        
        if count > 0:
            result = await submissions_collection.delete_many({})
            print(f"Successfully deleted {result.deleted_count} submission(s).")
        else:
            print("No submissions found to delete.")
            
    except Exception as e:
        print(f"Error clearing submissions: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(clear_submissions())
