import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai_service import AIService
from app.database import db

async def test_key():
    try:
        db.connect()
        service = AIService()
        print("Testing API Key...")
        result = await service.grade_answer(
            question_text="1+1 เท่ากับเท่าไหร่?",
            student_answer="2",
            max_score=1,
            context={"test": "key_verification"}
        )
        print(f"Test Result: {result}")
        if result.get("score") is not None:
            print("SUCCESS: API Key is working!")
        else:
            print("FAILURE: API Key produced no score.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(test_key())
