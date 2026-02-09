
import asyncio
from app.services.ai_service import ai_service
from app.models import RubricItem

async def test_rubric_grading():
    try:
        print("Testing AI Grading with Rubric...")
        
        question = "จงอธิบายวัฏจักรน้ำ"
        student_answer = "น้ำระเหยเป็นไอ ตกมาเป็นฝน แล้วไหลลงทะเล"
        max_score = 10
        
        # Define a Rubric
        rubric = [
            {"score": 10, "level": "ดีมาก", "description": "อธิบายครบ 3 ขั้นตอน (ระเหย, ควบแน่น, หยาดน้ำฟ้า) และยกตัวอย่างประกอบ"},
            {"score": 5, "level": "พอใช้", "description": "อธิบายได้บางขั้นตอน หรือขาดรายละเอียด"},
            {"score": 0, "level": "ปรับปรุง", "description": "ตอบผิดหรือไม่ตอบ"}
        ]
        
        print(f"\nRubric: {rubric}")
        print(f"Student Answer: {student_answer}")
        
        # Call AI Service
        result = await ai_service.grade_answer(
            question_text=question,
            student_answer=student_answer,
            max_score=max_score,
            rubric=rubric, # Pass rubric dict list directly (simulating parsed json)
            context={"test": "rubric_verification"}
        )
        
        print("\n--- AI Result ---")
        print(f"Score: {result['score']}")
        print(f"Justification: {result.get('justification')}")
        print(f"Feedback: {result.get('feedback')}")

    except Exception as e:
        import traceback
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        print("Error occurred. Check error_log.txt")

if __name__ == "__main__":
    asyncio.run(test_rubric_grading())
