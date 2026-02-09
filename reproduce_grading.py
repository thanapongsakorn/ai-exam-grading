
import asyncio
import sys
import os

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.services.ai_service import ai_service
from app.database import db

async def test_grading():
    print("Connecting to DB...")
    db.connect()
    
    print("Testing AI Grading without Answer Key...")
    
    question = "1 + 1 เท่ากับเท่าไหร่"
    student_answer = "1 + 1 เท่ากับ 2"
    max_score = 10
    
    # Case 1: No Answer Key, No Criteria (Simulating the issue)
    print(f"\n--- Scenario 1: No Answer Key ---")
    result = await ai_service.grade_answer(
        question_text=question,
        student_answer=student_answer,
        max_score=max_score,
        answer_key=None,
        grading_criteria=None,
        context={"test": "repro"}
    )
    
    print(f"Score: {result['score']}/{max_score}")
    print(f"Justification: {result.get('justification')}")
    print(f"Feedback: {result.get('feedback')}")
    
    if result['score'] < max_score:
        print("ISSUE REPRODUCED: Score is not full despite correct answer.")
    else:
        print("Score is full. Issue not reproduced with simple math.")

    # Case 2: Subjective Question without Key
    print(f"\n--- Scenario 2: Subjective Question without Key ---")
    question_sub = "จงอธิบายความสำคัญของดวงอาทิตย์ต่อสิ่งมีชีวิตบนโลก"
    answer_sub = "ดวงอาทิตย์ให้แสงสว่างและความร้อน ซึ่งจำเป็นต่อการสังเคราะห์แสงของพืชที่เป็นผู้ผลิตในห่วงโซ่อาหาร ทำให้สิ่งมีชีวิตอื่นๆ ดำรงอยู่ได้ และยังกำหนดวัฏจักรของน้ำและสภาพอากาศ"
    
    result_sub = await ai_service.grade_answer(
        question_text=question_sub,
        student_answer=answer_sub,
        max_score=10,
        answer_key=None,
        grading_criteria=None,
        context={"test": "repro_sub"}
    )
    
    print(f"Score: {result_sub['score']}/{max_score}")
    print(f"Justification: {result_sub.get('justification')}")
    
    if result_sub['score'] < 8: # Expecting high score for good answer
        print("ISSUE REPRODUCED: Score is unexpectedly low for subjective question.")
    else:
        print(f"Score seems reasonable: {result_sub['score']}")

if __name__ == "__main__":
    asyncio.run(test_grading())
