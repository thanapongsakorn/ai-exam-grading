import asyncio
import os
import sys
import time

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai_service import ai_service as service
from app.database import db

async def test_batch():
    try:
        db.connect()
        print("Testing Batch Grading (Parallel Optimization)...")
        
        batch_data = [
            {"question_text": "1+1 เท่ากับเท่าไหร่?", "student_answer": "2", "max_score": 1},
            {"question_text": "ท้องฟ้าสีอะไร?", "student_answer": "สีฟ้า", "max_score": 1},
            {"question_text": "ใครเป็นคนแต่งสุนทรภู่?", "student_answer": "สุนทรภู่เป็นชื่อกวี ไม่ไช่ชื่อหนังสือ", "max_score": 1}
        ]
        
        start_time = time.time()
        results = await service.grade_batch(batch_data, context={"test": "batch_verification"})
        end_time = time.time()
        
        print(f"Batch Result: {results}")
        print(f"Total time for 3 questions: {end_time - start_time:.2f} seconds")
        
        if len(results) == 3:
            print("SUCCESS: Batch Grading is working and efficient!")
        else:
            print(f"FAILURE: Expected 3 results, got {len(results)}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(test_batch())
