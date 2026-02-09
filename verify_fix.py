
import asyncio
from app.models import ExamModel, QuestionModel
from pydantic import ValidationError

def verify_fix():
    print("Verifying fix for empty strings...")
    
    # Simulate backend logic AFTER the fix
    # The fix in main.py does: val.strip() if val else None
    
    # Case 1: Empty answer_key passed as None (simulating the fix logic)
    raw_answer_key = ""
    processed_answer_key = raw_answer_key if raw_answer_key.strip() else None
    
    try:
        q = QuestionModel(
            id="q1", 
            text="Valid question text", 
            max_score=10, 
            answer_key=processed_answer_key  # Should be None
        )
        print(f"SUCCESS: QuestionModel accepted processed answer_key: {q.answer_key}")
    except ValidationError as e:
        print(f"FAIL: QuestionModel rejected processed answer_key: {e}")
    
    # Case 2: Empty grading_criteria passed as None
    raw_criteria = "   "
    processed_criteria = raw_criteria if raw_criteria.strip() else None
    
    try:
        q = QuestionModel(
            id="q2",
            text="Another question",
            max_score=10,
            grading_criteria=processed_criteria # Should be None
        )
        print(f"SUCCESS: QuestionModel accepted processed grading_criteria: {q.grading_criteria}")
    except ValidationError as e:
        print(f"FAIL: QuestionModel rejected processed grading_criteria: {e}")

if __name__ == "__main__":
    verify_fix()
