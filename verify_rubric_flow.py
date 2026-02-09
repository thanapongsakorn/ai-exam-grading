import asyncio
import os
import sys
import json
from datetime import datetime
from bson import ObjectId

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import db
from app.models import ExamModel, QuestionModel, RubricItem
from app.services.ai_service import ai_service

async def verify_rubric_flow():
    print("🚀 Starting Rubric Flow Verification...")
    db.connect()
    
    try:
        # 1. Create a mock exam with rubric
        exams_collection = db.db["exams"]
        mock_rubric = [
            RubricItem(score=10, level="Excellent", description="Complete and accurate explanation."),
            RubricItem(score=5, level="Fair", description="Partial explanation with some errors."),
            RubricItem(score=0, level="Poor", description="Incorrect or no explanation.")
        ]
        
        mock_exam = ExamModel(
            subject="Test Science",
            title="Rubric Test Exam " + datetime.now().strftime("%Y%m%d%H%M%S"),
            description="Testing rubric-based grading",
            questions=[
                QuestionModel(
                    id="q1",
                    text="What is the process of photosynthesis?",
                    max_score=10,
                    answer_key="Plants use sunlight to convert CO2 and water into glucose and oxygen.",
                    rubric=mock_rubric
                )
            ],
            created_by="teacher1"
        )
        
        exam_id = (await exams_collection.insert_one(mock_exam.model_dump(by_alias=True, exclude={"id"}))).inserted_id
        print(f"✅ Mock exam created: {exam_id}")
        
        # 2. Simulate AI Grading
        print("🤖 Simulating AI Grading...")
        student_answer = "Photosynthesis is how plants make food using sunlight and chlorophyll."
        
        result = await ai_service.grade_answer(
            question_text=mock_exam.questions[0].text,
            student_answer=student_answer,
            max_score=mock_exam.questions[0].max_score,
            answer_key=mock_exam.questions[0].answer_key,
            rubric=mock_exam.questions[0].rubric,
            context={"test": "rubric_verification"}
        )
        
        print(f"📊 AI Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 3. Verify Rubric in result (Check AI Justification if it mentions rubric)
        justification = result.get("justification", "").lower()
        feedback = result.get("feedback", "").lower()
        if any(word in justification or word in feedback for word in ["level", "rubric", "เกณฑ์", "ระดับ"]):
            print("✅ AI seems to be using the rubric or grading levels in its response.")
        else:
            print("⚠️ AI response didn't explicitly mention 'rubric' or 'level', but it might still be following it.")

        # 4. Clean up (Optional)
        # await exams_collection.delete_one({"_id": exam_id})
        # print("🧹 Cleaned up mock exam.")

    finally:
        db.disconnect()

if __name__ == "__main__":
    asyncio.run(verify_rubric_flow())
