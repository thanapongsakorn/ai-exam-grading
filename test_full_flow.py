import asyncio
from app.database import db
from app.models import ExamModel, QuestionModel, RubricItem
from app.services.ai_service import ai_service
from datetime import datetime
import json

async def test_full_flow():
    print("🚀 Starting Full Flow Test with Rubric...")
    
    # 1. Connect DB
    db.connect()
    
    # 2. CREATE EXAM with Rubric
    print("\n[1] Creating Exam...")
    rubric = [
        RubricItem(level="Excellent", score=10, description="Detailed and correct explanation"),
        RubricItem(level="Poor", score=2, description="Vague or incorrect")
    ]
    
    question = QuestionModel(
        id="q_test_1", 
        text="Explain the importance of photosynthesis.", 
        max_score=10, 
        rubric=rubric
    )
    
    exam = ExamModel(
        subject="Science",
        title="Photosynthesis Test (Auto)",
        description="Testing Rubric Flow",
        questions=[question],
        created_by="teacher1"
    )
    
    exam_id = (await db.db["exams"].insert_one(exam.model_dump(by_alias=True, exclude={"id"}))).inserted_id
    print(f"✅ Exam Created: {exam_id}")

    # 3. SUBMIT EXAM (Student)
    print("\n[2] Submitting Answer...")
    # Good Answer
    student_answer_text = "Photosynthesis is crucial because it produces oxygen for living things and creates food (glucose) for plants, forming the base of the food chain."
    
    submission = {
        "exam_id": str(exam_id),
        "student_username": "student_test",
        "answers": [{
            "question_id": "q_test_1",
            "answer_text": student_answer_text
        }],
        "status": "submitted",
        "submitted_at": datetime.now(),
        "exam_title": exam.title,
        "max_score": 10
    }
    
    sub_id = (await db.db["submissions"].insert_one(submission)).inserted_id
    print(f"✅ Submission Created: {sub_id}")
    
    # 4. AI GRADING (Simulate Background Task)
    print("\n[3] AI Grading...")
    
    # This logic mirrors main.py submit_exam background task
    result = await ai_service.grade_answer(
        question_text=question.text,
        student_answer=student_answer_text,
        max_score=question.max_score,
        rubric=rubric, # Vital: passing the rubric
        context={"test": "true"}
    )
    
    print(f"🤖 AI Result: Score={result['score']}, Feedback='{result['feedback'][:50]}...'")
    
    # Update Submission
    graded_ans = submission["answers"][0]
    graded_ans.update(result)
    
    await db.db["submissions"].update_one(
        {"_id": sub_id},
        {"$set": {
            "answers": [graded_ans],
            "total_score": result['score'],
            "status": "graded"
        }}
    )
    print("✅ Submission Updated with AI Grade")

    # 5. TEACHER REVIEW (Simulate fetching for view)
    print("\n[4] Simulating Teacher Review Fetch...")
    saved_sub = await db.db["submissions"].find_one({"_id": sub_id})
    saved_question = await db.db["exams"].find_one({"_id": exam_id})
    q_data = saved_question["questions"][0]
    
    ans_data = saved_sub["answers"][0]
    
    # Enrich (The Logic we fixed in main.py)
    ans_data["rubric"] = q_data.get("rubric", [])
    
    if "rubric" in ans_data and len(ans_data["rubric"]) > 0:
        print("✅ SUCCESS: Rubric is available for the frontend!")
        print(f"   - Rubric Level 1: {ans_data['rubric'][0]['level']}")
    else:
        print("❌ FAILURE: Rubric missing in answer object.")

    # Cleanup
    await db.db["exams"].delete_one({"_id": exam_id})
    await db.db["submissions"].delete_one({"_id": sub_id})
    print("\n🧹 Cleanup done.")
    db.disconnect()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
