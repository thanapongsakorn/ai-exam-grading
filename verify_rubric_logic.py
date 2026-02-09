import asyncio
from app.models import ExamModel, QuestionModel, RubricItem, SubmissionModel, AnswerModel
from datetime import datetime

async def verify_rubric_enrichment():
    # 1. Create Mock Data
    rubric = [
        RubricItem(level="Excellent", score=10, description="Perfect answer"),
        RubricItem(level="Good", score=5, description="Partial answer")
    ]
    
    question = QuestionModel(
        id="q1", 
        text="Test Q", 
        max_score=10, 
        rubric=rubric
    )
    
    exam = ExamModel(
        subject="Test Subject",
        title="Test Exam",
        description="Test Desc",
        questions=[question],
        created_by="teacher"
    )
    
    answer = AnswerModel(
        question_id="q1",
        answer_text="Test Answer"
    )
    
    submission = SubmissionModel(
        exam_id="exam_id_123",
        student_username="student",
        answers=[answer],
        status="submitted"
    )
    
    # 2. Simulate the Logic in main.py
    submission_dict = submission.model_dump()
    exam_dict = exam.model_dump()
    
    print("Original Answer keys:", submission_dict["answers"][0].keys())
    
    for ans in submission_dict["answers"]:
        q = next((q for q in exam_dict["questions"] if q["id"] == ans["question_id"]), None)
        ans["question_text"] = q["text"] if q else "Unknown Question"
        ans["max_score"] = q["max_score"] if q else 10
        ans["justification"] = ans.get("justification", "ไม่มีข้อมูล")
        
        # The Logic we added
        ans["rubric"] = q.get("rubric", []) if q else []

    # 3. Verify
    enriched_ans = submission_dict["answers"][0]
    print("\nEnriched Answer keys:", enriched_ans.keys())
    
    if "rubric" in enriched_ans:
        print("\n✅ Rubric found in answer!")
        print(f"Rubric Items: {len(enriched_ans['rubric'])}")
        print(f"First Item: {enriched_ans['rubric'][0]}")
    else:
        print("\n❌ Rubric NOT found in answer!")

if __name__ == "__main__":
    asyncio.run(verify_rubric_enrichment())
