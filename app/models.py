from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Annotated, Any
from datetime import datetime
from bson import ObjectId

# Helper to handle ObjectId with Pydantic v2
PyObjectId = Annotated[str, BeforeValidator(str)]

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str
    password: str 
    role: str = "student"  # 'student' or 'teacher'

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class RubricItem(BaseModel):
    level: str = Field(default="") # e.g. "Excellent", "Good", "Fair"
    score: int = Field(default=0, ge=0)
    description: str = Field(default="")

class QuestionModel(BaseModel):
    id: str  # e.g. "q1"
    text: str = Field(..., min_length=5)
    max_score: int = Field(default=10, ge=1)
    answer_key: Optional[str] = Field(default=None, min_length=2) # เฉลย/แนวคำตอบ
    grading_criteria: Optional[str] = None # เกณฑ์การให้คะแนน (Legacy/Simple)
    rubric: List[RubricItem] = [] # New structured rubric

class ExamModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    subject: str = Field(..., min_length=2) # e.g. "วิทยาศาสตร์", "คณิตศาสตร์"
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    questions: List[QuestionModel] = Field(..., min_length=1)
    created_by: str  # teacher username
    is_deleted: bool = Field(default=False)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AnswerModel(BaseModel):
    question_id: str
    answer_text: str
    score: Optional[float] = None # AI Score
    justification: Optional[str] = None # AI Justification
    feedback: Optional[str] = None # AI Feedback
    teacher_score: Optional[float] = None
    teacher_feedback: Optional[str] = None

class SubmissionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    exam_id: str
    student_username: str
    answers: List[AnswerModel] = []
    total_score: Optional[float] = None
    status: str = "submitted"  # submitted, graded
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
