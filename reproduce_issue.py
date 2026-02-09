
import asyncio
from app.models import ExamModel, QuestionModel
from pydantic import ValidationError

def test_validation_error():
    print("Testing Pydantic validation with empty strings...")
    
    # Case 1: Empty answer_key (simulating form submission where user leaves it blank)
    try:
        q = QuestionModel(
            id="q1", 
            text="Valid question text", 
            max_score=10, 
            answer_key=""  # This should fail min_length=2
        )
        print("FAIL: QuestionModel accepted empty answer_key")
    except ValidationError as e:
        print(f"SUCCESS: QuestionModel rejected empty answer_key as expected: {e}")
        
    # Case 2: Empty description
    try:
        e = ExamModel(
            subject="Thai",
            title="Test Exam",
            description="Test", # Too short (min 5)
            questions=[QuestionModel(id="q1", text="Valid text", max_score=10)],
            created_by="teacher"
        )
        print("FAIL: ExamModel accepted short description")
    except ValidationError as e:
        print(f"SUCCESS: ExamModel rejected short description as expected: {e}")

if __name__ == "__main__":
    test_validation_error()
