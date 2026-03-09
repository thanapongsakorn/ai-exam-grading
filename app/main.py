from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
import io
import csv
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os
from datetime import datetime
from bson import ObjectId
import sys
import os
# Add project root to sys.path to allow 'app' module import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.models import UserModel
from app.services.ai_service import ai_service
import asyncio
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    db.connect()
    
    # Test connection and handle fallbacks
    connected = await db.test_connection()
    if not connected:
        print("CRITICAL: Failed to establish a database connection.")
        # We continue to allow the app to start, but operations will fail
    
    # Seed Test Data - Wrapped in try-except to prevent hang if DB is unreachable
    try:
        print("Starting database seeding...")
        users_collection = db.db["users"]
        test_users = [
            {"username": "student1", "password": pwd_context.hash("password"), "role": "student"},
            {"username": "teacher1", "password": pwd_context.hash("password"), "role": "teacher"}
        ]
        for user_data in test_users:
            await asyncio.wait_for(users_collection.update_one(
                {"username": user_data["username"], "role": user_data["role"]},
                {"$set": user_data},
                upsert=True
            ), timeout=5.0)
        print("Ensured test users exist.")
            
        # Seed Exam Data
        exams_collection = db.db["exams"]
        from app.models import ExamModel, QuestionModel
        sample_exam = ExamModel(
            subject="ภาษาไทย",
            title="สอบกลางภาค วิชาภาษาไทย",
            description="ข้อสอบอัตนัยวัดความรู้ความเข้าใจในวรรณคดีไทย",
            questions=[
                QuestionModel(id="q1", text="จงอธิบายความสำคัญของวรรณคดีเรื่องขุนช้างขุนแผน", max_score=10),
                QuestionModel(id="q2", text="ตัวละครใดในเรื่องพระอภัยมณีที่ท่านชื่นชอบที่สุด พร้อมเหตุผล", max_score=10)
            ],
            created_by="teacher1"
        )
        await asyncio.wait_for(exams_collection.update_one(
            {"title": sample_exam.title},
            {"$set": sample_exam.model_dump(by_alias=True, exclude_none=True, exclude={"id"})},
            upsert=True
        ), timeout=5.0)
        print("Ensured test exam exists.")
    except asyncio.TimeoutError:
        print("CRITICAL: การเชื่อมต่อฐานข้อมูลล่าช้า! (Database seeding timed out)")
        print("กรุณาตรวจสอบว่าคุณได้เพิ่ม IP ปัจจุบันลงใน MongoDB Atlas Network Access แล้วหรือยัง")
    except Exception as e:
        print(f"CRITICAL: ไม่สามารถเริ่มระบบฐานข้อมูลได้: {e}")

    yield
    # Shutdown: Disconnect DB
    db.disconnect()

app = FastAPI(title="Subjective Exam Grading AI", lifespan=lifespan)

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

from fastapi import Depends, HTTPException

async def get_current_user(request: Request):
    user_cookie = request.cookies.get("user_session")
    if not user_cookie:
        raise HTTPException(status_code=303, detail="Not authenticated", headers={"Location": "/login"})
    
    # Securely verify user and role from database (Server-side check)
    user_cookie = user_cookie.strip()
    user = await db.db["users"].find_one({"username": user_cookie})
    if not user:
        raise HTTPException(status_code=303, detail="User not found", headers={"Location": "/login"})
    return {
        "username": user["username"], 
        "role": user.get("role", "student"),
        "enrolled_subjects": user.get("enrolled_subjects", [])
    }

def teacher_only(user: dict = Depends(get_current_user)):
    if user["role"] != "teacher":
        raise HTTPException(status_code=303, detail="Teacher only", headers={"Location": "/student/dashboard"})
    return user

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 303:
        return RedirectResponse(url=exc.headers.get("Location", "/login"))
    return HTMLResponse(content=exc.detail, status_code=exc.status_code)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "ระบบตรวจข้อสอบอัตนัย"})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "เข้าสู่ระบบ"
    })

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    user_collection = db.db["users"]
    # Find user by username only
    user = await user_collection.find_one({"username": username})
    
    if user and pwd_context.verify(password, user["password"]):
        # Success: Redirect based on role in database
        role = user.get("role", "student")
        target = "/student/dashboard" if role == "student" else "/teacher/dashboard" 
        response = RedirectResponse(url=target, status_code=303)
        response.set_cookie(key="user_session", value=username)
        return response
    
    # Failure: Show error
    role_name = " (นักเรียน)" if role == "student" else " (ผู้สอน)"
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "role": role, 
        "role_name": role_name,
        "error": "Invalid username or password"
    })

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_session")
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    user_collection = db.db["users"]
    
    # Check if user already exists
    existing_user = await user_collection.find_one({"username": username})
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "ชื่อผู้ใช้นี้ถูกใช้งานแล้ว กรุณาเลือกชื่ออื่น"
        })
    
    # Create new student user with empty enrollment list
    new_user = {
        "username": username,
        "password": pwd_context.hash(password),
        "role": "student",
        "enrolled_subjects": []
    }
    
    await user_collection.insert_one(new_user)
    
    # Redirect to login with success message possibly? For now just simple redirect
    return RedirectResponse(url="/login", status_code=303)

@app.get("/teacher/dashboard", response_class=HTMLResponse)
async def teacher_dashboard(request: Request, user: dict = Depends(teacher_only)):
    # Only show non-deleted exams created by this teacher
    exams_cursor = db.db["exams"].find({
        "created_by": user["username"],
        "is_deleted": {"$ne": True}
    })
    exams = await exams_cursor.to_list(100)
    for ex in exams:
        ex["id"] = str(ex["_id"])
    
    # Filter submissions that belong to this teacher's exams
    exam_ids = [str(ex["_id"]) for ex in exams]
    submissions_cursor = db.db["submissions"].find({"exam_id": {"$in": exam_ids}}).sort("submitted_at", -1)
    all_submissions = await submissions_cursor.to_list(1000)
    
    # Calculate Stats
    total_exams = len(exams)
    total_subs = len(all_submissions)
    
    # Average score across all graded/reviewed submissions
    graded_subs = [s for s in all_submissions if s.get("status") in ["graded", "reviewed"]]
    total_score_sum = sum(s.get("teacher_total_score", s.get("total_score", 0)) for s in graded_subs)
    avg_score = round(total_score_sum / len(graded_subs), 2) if graded_subs else 0
    
    # Calculate Score Distribution for Charts
    distribution = {"High (8-10)": 0, "Mid (5-7)": 0, "Low (0-4)": 0}
    for s in graded_subs:
        score = s.get("teacher_total_score", s.get("total_score", 0))
        if score >= 8: distribution["High (8-10)"] += 1
        elif score >= 5: distribution["Mid (5-7)"] += 1
        else: distribution["Low (0-4)"] += 1
        
    # Get Unique Subjects for Filter
    subjects = sorted(list(set(ex.get("subject") for ex in exams if ex.get("subject"))))
    
    # NEW: Get Enrolled Students for this teacher's subject(s)
    # Assuming one teacher manages one primary subject for now, but we check all their subjects
    enrolled_students_cursor = db.db["users"].find({
        "role": "student",
        "enrolled_subjects": {"$in": subjects}
    })
    enrolled_students = await enrolled_students_cursor.to_list(1000)
        
    recent_submissions = all_submissions[:10]
    for sub in recent_submissions:
        sub["id"] = str(sub["_id"])
    
    return templates.TemplateResponse("teacher_dashboard.html", {
        "request": request, 
        "user": user["username"],
        "exams": exams,
        "subjects": subjects,
        "submissions": recent_submissions,
        "enrolled_students": enrolled_students,
        "stats": {
            "total_exams": total_exams,
            "total_submissions": total_subs,
            "avg_score": avg_score,
            "distribution": distribution
        }
    })

@app.get("/test_server_reload")
async def test_reload():
    return {"status": "ok", "message": "The server has successfully reloaded!"}

@app.get("/dump_user")
async def dump_user_route(request: Request):
    user_cookie = request.cookies.get("user_session")
    if not user_cookie:
        return {"error": "no cookie"}
    db_name = db.db.name
    user = await db.db["users"].find_one({"username": user_cookie.strip()})
    return {
        "cookie": user_cookie,
        "db": db_name,
        "user_doc": str(user),
        "enrolled": user.get("enrolled_subjects", []) if user else []
    }

@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request, user: dict = Depends(get_current_user)):
    # All available subjects from active exams
    all_exams_cursor = db.db["exams"].find({"is_deleted": {"$ne": True}})
    all_exams = await all_exams_cursor.to_list(500)
    
    available_subjects = sorted(list(set(ex.get("subject", "").strip() for ex in all_exams if ex.get("subject"))))
    enrolled_subjects = [s.strip() for s in user.get("enrolled_subjects", []) if isinstance(s, str)]
    
    # DEBUG LOGGING (Visible in console)
    print(f"--- DASHBOARD DEBUG [{user['username']}] ---")
    print(f"DB Name: {db.db.name}")
    print(f"Raw Enrolled from User Doc: {user.get('enrolled_subjects')}")
    print(f"Final Enrolled List: {enrolled_subjects}")
    print(f"Total Active Exams: {len(all_exams)}")
    
    # Filter exams to only those the student is enrolled in (normalize for matching)
    enrolled_exams = []
    for ex in all_exams:
        subj = ex.get("subject")
        if subj and subj.strip() in enrolled_subjects:
            enrolled_exams.append(ex)
    
    # Group enrolled exams by subject (normalize keys)
    grouped_exams = {}
    for ex in enrolled_exams:
        ex["id"] = str(ex["_id"])
        subject = ex.get("subject", "ทั่วไป").strip()
        if subject not in grouped_exams:
            grouped_exams[subject] = []
        grouped_exams[subject].append(ex)
        
    return templates.TemplateResponse("student_dashboard.html", {
        "request": request, 
        "title": "หน้าแรก (นักเรียน)", 
        "grouped_exams": grouped_exams,
        "available_subjects": available_subjects,
        "enrolled_subjects": enrolled_subjects,
        "user": user["username"]
    })

@app.post("/student/enroll")
async def enroll_subject(request: Request, subject: str = Form(...), user: dict = Depends(get_current_user)):
    user_collection = db.db["users"]
    subject = subject.strip()
    
    # Check if subject exists in any active exam (Using regex for robustness)
    import re
    safe_subject = re.escape(subject)
    exam_exists = await db.db["exams"].find_one({
        "subject": {"$regex": f"^{safe_subject}$", "$options": "i"}, 
        "is_deleted": {"$ne": True}
    })
    
    if not exam_exists:
         # Fallback search: maybe the DB has trailing spaces we missed?
         exam_exists = await db.db["exams"].find_one({
             "subject": {"$regex": f"^\\s*{safe_subject}\\s*$", "$options": "i"},
             "is_deleted": {"$ne": True}
         })
         
    if not exam_exists:
         print(f"DEBUG: Enrollment failed for subject '{subject}' - No match found.")
         return RedirectResponse(url=f"/student/dashboard?error=ไม่พบวิชา: {subject}", status_code=303)
         
    # Add subject to user's enrolled list using $addToSet (ensures uniqueness)
    await user_collection.update_one(
        {"username": user["username"]},
        {"$addToSet": {"enrolled_subjects": subject}}
    )
    
    return RedirectResponse(url="/student/dashboard", status_code=303)

@app.post("/student/unenroll")
async def unenroll_subject(request: Request, subject: str = Form(...), user: dict = Depends(get_current_user)):
    user_collection = db.db["users"]
    subject = subject.strip()
    
    # Remove subject from user's enrolled list using $pull
    await user_collection.update_one(
        {"username": user["username"]},
        {"$pull": {"enrolled_subjects": subject}}
    )
    
    return RedirectResponse(url="/student/dashboard", status_code=303)

@app.get("/exam/{exam_id}", response_class=HTMLResponse)
async def take_exam(request: Request, exam_id: str, user: dict = Depends(get_current_user)):
    exam = await db.db["exams"].find_one({
        "_id": ObjectId(exam_id),
        "is_deleted": {"$ne": True}
    })
    if not exam:
        return HTMLResponse("Exam not found or has been deleted", status_code=404)
        
    exam["id"] = str(exam["_id"])
    return templates.TemplateResponse("exam_take.html", {"request": request, "exam": exam})

@app.get("/exam/waiting/{submission_id}", response_class=HTMLResponse)
async def waiting_page(request: Request, submission_id: str):
    return templates.TemplateResponse("waiting.html", {"request": request, "submission_id": submission_id})

@app.get("/api/submission/status/{submission_id}")
async def get_submission_status(submission_id: str):
    submission = await db.db["submissions"].find_one({"_id": ObjectId(submission_id)})
    if not submission:
        return {"status": "not_found"}
    return {"status": submission.get("status", "submitted")}

@app.post("/exam/{exam_id}/submit")
async def submit_exam(request: Request, exam_id: str, user: dict = Depends(get_current_user)):
        
    form_data = await request.form()
    
    exam = await db.db["exams"].find_one({"_id": ObjectId(exam_id)})
    if not exam:
        return HTMLResponse("Exam not found", status_code=404)

    answers = []
    # Loop to find answers matching questions
    for key, value in form_data.items():
        if key.startswith("answer_"):
            q_id = key.replace("answer_", "")
            answers.append({
                "question_id": q_id,
                "answer_text": value
            })
            
    submission = {
        "exam_id": exam_id,
        "subject": exam.get("subject", "ไม่ได้ระบุ"),
        "student_username": user["username"],
        "answers": answers,
        "status": "submitted",
        "submitted_at": datetime.now(),
        "total_score": None,
        # Determine max score for reference if needed
        "exam_title": exam.get("title", "Unknown Exam"), # Denormalize title for easier listing
        "max_score": sum(q["max_score"] for q in exam.get("questions", []))
    }
    
    submission_id = (await db.db["submissions"].insert_one(submission)).inserted_id
    
    # Trigger AI Grading in Background
    async def process_grading(sid, exam_obj, answers_list):
        batch_data = []
        for ans in answers_list:
            q_id = ans["question_id"]
            original_q = next((q for q in exam_obj["questions"] if q["id"] == q_id), None)
            if original_q:
                batch_data.append({
                    "question_text": original_q["text"],
                    "student_answer": ans["answer_text"],
                    "max_score": original_q["max_score"],
                    "answer_key": original_q.get("answer_key"),
                    "rubric": original_q.get("rubric")
                })
        
        if batch_data:
            results = await ai_service.grade_batch(batch_data, context={"student": user["username"], "exam": exam.get("title")})
            
            total_score = 0
            res_idx = 0
            for ans in answers_list:
                original_q = next((q for q in exam_obj["questions"] if q["id"] == ans["question_id"]), None)
                if original_q and res_idx < len(results):
                    res = results[res_idx]
                    ans.update({
                        "score": res.get("score", 0),
                        "justification": res.get("justification"),
                        "feedback": res.get("feedback"),
                        "strengths": res.get("strengths"),
                        "improvements": res.get("improvements")
                    })
                    total_score += res.get("score", 0)
                    res_idx += 1
            
            await db.db["submissions"].update_one(
                {"_id": sid},
                {"$set": {
                    "answers": answers_list,
                    "total_score": total_score,
                    "status": "graded"
                }}
            )

    # Fire and forget (in a real production app, use Celery/BackgroundTasks)
    asyncio.create_task(process_grading(submission_id, exam, answers))
    
    return RedirectResponse(url=f"/exam/waiting/{submission_id}", status_code=303)

@app.get("/results", response_class=HTMLResponse)
async def view_results(request: Request, user: dict = Depends(get_current_user)):
        
    submissions = await db.db["submissions"].find({"student_username": user["username"]}).sort("submitted_at", -1).to_list(100)
    
    # Pre-fetch all relevant exams to avoid multiple DB calls in a loop
    exam_ids = list(set(sub["exam_id"] for sub in submissions if "exam_id" in sub))
    exams_cursor = db.db["exams"].find({"_id": {"$in": [ObjectId(eid) for eid in exam_ids]}})
    exams_list = await exams_cursor.to_list(len(exam_ids))
    exam_map = {str(ex["_id"]): ex for ex in exams_list}

    # Group results by subject (instead of exam title) for better organization
    grouped_results = {}
    for sub in submissions:
        if "submitted_at" in sub:
            sub["submitted_at"] = sub["submitted_at"].strftime("%Y-%m-%d %H:%M")
        
        # Enrich answers with rubric and question info from the exam map
        exam = exam_map.get(str(sub["exam_id"]))
        if exam:
            for ans in sub.get("answers", []):
                q = next((q for q in exam.get("questions", []) if q["id"] == ans["question_id"]), None)
                if q:
                    ans["question_text"] = q.get("text")
                    ans["max_score"] = q.get("max_score")
                    ans["rubric"] = q.get("rubric", [])

        # Group by Subject
        subject = sub.get("subject", "ทั่วไป")
        if subject not in grouped_results:
            grouped_results[subject] = []
        grouped_results[subject].append(sub)
    
    # Calculate Subject Statistics for Summary
    subject_stats = {}
    for subject, subs in grouped_results.items():
        # Only count graded or reviewed submissions for stats
        graded_subs = [s for s in subs if s.get("status") in ("graded", "reviewed")]
        if graded_subs:
            sum_actual = sum(s.get("teacher_total_score") if s.get("status") == "reviewed" else s.get("total_score", 0) for s in graded_subs)
            sum_max = sum(s.get("max_score", 0) for s in graded_subs)
            avg_pct = (sum_actual / sum_max * 100) if sum_max > 0 else 0
            subject_stats[subject] = {
                "count": len(graded_subs),
                "avg_pct": round(avg_pct, 1),
                "total_actual": sum_actual,
                "total_max": sum_max
            }

    return templates.TemplateResponse("results.html", {
        "request": request,
        "grouped_results": grouped_results,
        "subject_stats": subject_stats
    })

@app.get("/results/{submission_id}", response_class=HTMLResponse)
async def view_single_result(request: Request, submission_id: str, user: dict = Depends(get_current_user)):
    submission = await db.db["submissions"].find_one({"_id": ObjectId(submission_id)})
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Security check: Only owner or teacher can view
    if user["role"] != "teacher" and submission["student_username"] != user["username"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this result")
    
    # Enrich with exam data
    exam = await db.db["exams"].find_one({"_id": ObjectId(submission["exam_id"])})
    if exam:
        if "submitted_at" in submission:
            submission["submitted_at"] = submission["submitted_at"].strftime("%Y-%m-%d %H:%M")
            
        for ans in submission.get("answers", []):
            q = next((q for q in exam.get("questions", []) if q["id"] == ans["question_id"]), None)
            if q:
                ans["question_text"] = q.get("text")
                ans["max_score"] = q.get("max_score")
                ans["rubric"] = q.get("rubric", [])

    # Wrap in grouped_results format to reuse results.html template
    grouped_results = {
        submission.get("exam_title", "รายวิชา"): [submission]
    }
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "grouped_results": grouped_results,
        "single_view": True
    })


@app.post("/submission/{sub_id}/delete")
async def delete_submission(request: Request, sub_id: str, user: dict = Depends(get_current_user)):
        
    # Verify ownership before deleting
    submission = await db.db["submissions"].find_one({"_id": ObjectId(sub_id)})
    if submission and submission["student_username"] == user["username"]:
        await db.db["submissions"].delete_one({"_id": ObjectId(sub_id)})
        
    return RedirectResponse(url="/results", status_code=303)

@app.get("/teacher/exam/create", response_class=HTMLResponse)
async def create_exam_page(request: Request, user: dict = Depends(teacher_only)):
    return templates.TemplateResponse("exam_form.html", {"request": request, "title": "สร้างข้อสอบใหม่", "exam": None})

@app.post("/teacher/exam/create")
async def create_exam_submit(request: Request, user: dict = Depends(teacher_only)):
    
    form = await request.form()
    subject = form.get("subject")
    title = form.get("title")
    description = form.get("description")
    
    # Extract questions
    q_texts = form.getlist("q_text[]")
    q_scores = form.getlist("q_score[]")
    q_keys = form.getlist("q_key[]")
    q_rubric_jsons = form.getlist("q_rubric_json[]")
    
    from app.models import ExamModel, QuestionModel, RubricItem
    from pydantic import ValidationError
    import json
    
    try:
        questions = []
        for i in range(len(q_texts)):
            # Parse Rubric JSON
            rubric_list = []
            if i < len(q_rubric_jsons) and q_rubric_jsons[i]:
                try:
                    rubric_raw = json.loads(q_rubric_jsons[i])
                    rubric_list = [RubricItem(**r) for r in rubric_raw]
                except Exception as e:
                    print(f"Error parsing rubric for q{i+1}: {e}")
                    rubric_list = []

            questions.append(QuestionModel(
                id=f"q{i+1}",
                text=q_texts[i],
                max_score=int(q_scores[i]),
                answer_key=q_keys[i] if i < len(q_keys) and q_keys[i].strip() else None,
                grading_criteria=None,
                rubric=rubric_list
            ))
            
        exam = ExamModel(
            subject=subject,
            title=title,
            description=description,
            questions=questions,
            created_by=user["username"]
        )
        
        await db.db["exams"].insert_one(exam.model_dump(by_alias=True, exclude={"id"}))
        return RedirectResponse(url="/teacher/dashboard", status_code=303)

    except ValidationError as e:
        # Return form with error
        return templates.TemplateResponse("exam_form.html", {
            "request": request,
            "title": "สร้างข้อสอบใหม่",
            "exam": {
                "subject": subject,
                "title": title,
                "description": description,
                "questions": [
                    {"text": q_texts[i], "max_score": q_scores[i], "answer_key": q_keys[i] if i < len(q_keys) else "", "rubric": []}
                    for i in range(len(q_texts))
                ]
            },
            "error": "ข้อมูลไม่ถูกต้อง: กรุณากรอกข้อมูลให้ครบถ้วนและถูกต้องตามรูปแบบที่กำหนด"
        })
    except Exception as e:
        print(f"Unexpected error in create_exam: {e}")
        return templates.TemplateResponse("exam_form.html", {
            "request": request,
            "title": "สร้างข้อสอบใหม่",
            "exam": None,
            "error": f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {str(e)}"
        })

@app.get("/teacher/exam/edit/{exam_id}", response_class=HTMLResponse)
async def edit_exam_page(request: Request, exam_id: str, user: dict = Depends(teacher_only)):
    
    exam = await db.db["exams"].find_one({"_id": ObjectId(exam_id)})
    if not exam: return HTMLResponse("Exam not found", status_code=404)
    
    # Ownership Check
    if exam.get("created_by") != user["username"]:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this exam.")
        
    exam["id"] = str(exam["_id"])
    return templates.TemplateResponse("exam_form.html", {"request": request, "title": "แก้ไขข้อสอบ", "exam": exam})

@app.post("/teacher/exam/edit/{exam_id}")
async def edit_exam_submit(request: Request, exam_id: str, user: dict = Depends(teacher_only)):
    
    form = await request.form()
    # Similar to create, but update
    q_texts = form.getlist("q_text[]")
    q_scores = form.getlist("q_score[]")
    q_keys = form.getlist("q_key[]")
    q_rubric_jsons = form.getlist("q_rubric_json[]")
    
    from app.models import QuestionModel, RubricItem
    from pydantic import ValidationError
    import json

    try:
        questions = []
        for i in range(len(q_texts)):
            # Parse Rubric JSON
            rubric_list = []
            if i < len(q_rubric_jsons) and q_rubric_jsons[i]:
                try:
                    rubric_raw = json.loads(q_rubric_jsons[i])
                    rubric_list = [RubricItem(**r) for r in rubric_raw]
                except Exception as e:
                    print(f"Error parsing rubric for q{i+1}: {e}")
                    rubric_list = []

            questions.append(QuestionModel(
                id=f"q{i+1}",
                text=q_texts[i],
                max_score=int(q_scores[i]),
                answer_key=q_keys[i] if i < len(q_keys) and q_keys[i].strip() else None,
                grading_criteria=None,
                rubric=rubric_list
            ))
            
        # Ownership Check
        existing_exam = await db.db["exams"].find_one({"_id": ObjectId(exam_id)})
        if not existing_exam or existing_exam.get("created_by") != user["username"]:
             raise HTTPException(status_code=403, detail="You do not have permission to edit this exam.")

        await db.db["exams"].update_one(
            {"_id": ObjectId(exam_id)},
            {"$set": {
                "subject": form.get("subject"),
                "title": form.get("title"),
                "description": form.get("description"),
                "questions": [q.model_dump() for q in questions]
            }}
        )
        return RedirectResponse(url="/teacher/dashboard", status_code=303)

    except ValidationError as e:
        return templates.TemplateResponse("exam_form.html", {
            "request": request,
            "title": "แก้ไขข้อสอบ",
            "exam": {
                "id": exam_id,
                "subject": form.get("subject"),
                "title": form.get("title"),
                "description": form.get("description"),
                "questions": [
                    {"text": q_texts[i], "max_score": q_scores[i], "answer_key": q_keys[i] if i < len(q_keys) else "", "rubric": []}
                    for i in range(len(q_texts))
                ]
            },
            "error": "ข้อมูลไม่ถูกต้อง: กรุณากรอกข้อมูลให้ครบถ้วนและถูกต้องตามรูปแบบที่กำหนด"
        })
    except Exception as e:
        print(f"Unexpected error in edit_exam: {e}")
        return templates.TemplateResponse("exam_form.html", {
            "request": request,
            "title": "แก้ไขข้อสอบ",
            "exam": {"id": exam_id},
            "error": f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {str(e)}"
        })

@app.post("/teacher/exam/delete/{exam_id}")
async def delete_exam(request: Request, exam_id: str, user: dict = Depends(teacher_only)):
    # Ownership Check
    exam = await db.db["exams"].find_one({"_id": ObjectId(exam_id)})
    if not exam or exam.get("created_by") != user["username"]:
         raise HTTPException(status_code=403, detail="You do not have permission to delete this exam.")

    # Soft Delete: Set is_deleted to True
    await db.db["exams"].update_one(
        {"_id": ObjectId(exam_id)},
        {"$set": {"is_deleted": True}}
    )
    return RedirectResponse(url="/teacher/dashboard", status_code=303)

@app.get("/teacher/submissions", response_class=HTMLResponse)
async def teacher_submissions(request: Request, user: dict = Depends(teacher_only)):
    # Get this teacher's exams first
    teacher_exams = await db.db["exams"].find({"created_by": user["username"]}).to_list(1000)
    exam_ids = [str(e["_id"]) for e in teacher_exams]
    exam_map = {str(e["_id"]): e.get("subject", "ไม่ได้ระบุ") for e in teacher_exams}

    # Only show submissions for this teacher's exams
    submissions = await db.db["submissions"].find({"exam_id": {"$in": exam_ids}}).sort("submitted_at", -1).to_list(1000)
    
    unique_subjects = sorted(list(set(exam_map.values())))
    unique_students = sorted(list(set(sub.get("student_username") for sub in submissions if "student_username" in sub)))

    # Calculate Student Stats
    student_stats = {}
    for student in unique_students:
        student_subs = [s for s in submissions if s.get("student_username") == student]
        graded_subs = [s for s in student_subs if s.get("status") in ("graded", "reviewed")]
        
        avg_score = 0
        if graded_subs:
            sum_score = sum(s.get("teacher_total_score", s.get("total_score", 0)) for s in graded_subs)
            avg_score = round(sum_score / len(graded_subs), 2)
            
        student_stats[student] = {
            "count": len(student_subs),
            "avg_score": avg_score
        }

    for sub in submissions:
        sub["id"] = str(sub["_id"])
        # Fallback to map if subject missing in submission
        if "subject" not in sub:
            sub["subject"] = exam_map.get(str(sub["exam_id"]), "ไม่ได้ระบุ")
            
        if "submitted_at" in sub:
            sub["submitted_at"] = sub["submitted_at"].strftime("%Y-%m-%d %H:%M")
            
    return templates.TemplateResponse("teacher_submissions.html", {
        "request": request,
        "submissions": submissions,
        "subjects": unique_subjects,
        "students": unique_students,
        "student_stats": student_stats
    })

@app.get("/teacher/submission/{sub_id}/review", response_class=HTMLResponse)
async def review_submission_page(request: Request, sub_id: str, user: dict = Depends(teacher_only)):
    
    submission = await db.db["submissions"].find_one({"_id": ObjectId(sub_id)})
    if not submission: return HTMLResponse("Submission not found", status_code=404)
    
    # Get associated exam
    exam = await db.db["exams"].find_one({"_id": ObjectId(submission["exam_id"])})
    
    # Ownership Check
    if not exam or exam.get("created_by") != user["username"]:
        raise HTTPException(status_code=403, detail="You do not have permission to review this submission.")
    
    # Enrich answers with question text and AI details
    for ans in submission["answers"]:
        q = next((q for q in exam["questions"] if q["id"] == ans["question_id"]), None)
        ans["question_text"] = q["text"] if q else "Unknown Question"
        ans["max_score"] = q["max_score"] if q else 10
        # Ensure AI fields exist for template safety
        ans["justification"] = ans.get("justification", "ไม่มีข้อมูล")
        # Attach Rubric for display
        ans["rubric"] = q.get("rubric", []) if q else []
        
    submission["id"] = str(submission["_id"])
    submission["submitted_at"] = submission["submitted_at"].strftime("%Y-%m-%d %H:%M")
    
    return templates.TemplateResponse("submission_review.html", {"request": request, "submission": submission})

@app.post("/teacher/submission/{sub_id}/review")
async def review_submission_submit(request: Request, sub_id: str, user: dict = Depends(teacher_only)):
    
    form = await request.form()
    action = form.get("action")
    submission = await db.db["submissions"].find_one({"_id": ObjectId(sub_id)})
    
    if action == "regrade":
        # Get associated exam
        exam = await db.db["exams"].find_one({"_id": ObjectId(submission["exam_id"])})
        
        # Define the grading function using Batch Processing
        async def process_grading_task(sid, exam_obj, answers_list):
            batch_data = []
            for ans in answers_list:
                q_id = ans["question_id"]
                original_q = next((q for q in exam_obj["questions"] if q["id"] == q_id), None)
                if original_q:
                    batch_data.append({
                        "question_text": original_q["text"],
                        "student_answer": ans["answer_text"],
                        "max_score": original_q["max_score"],
                        "answer_key": original_q.get("answer_key"),
                        "rubric": original_q.get("rubric")
                    })

            if batch_data:
                results = await ai_service.grade_batch(batch_data, context={"student": submission["student_username"], "exam_id": submission["exam_id"], "action": "regrade"})
                
                total_score = 0
                res_idx = 0
                for ans in answers_list:
                    original_q = next((q for q in exam_obj["questions"] if q["id"] == ans["question_id"]), None)
                    if original_q and res_idx < len(results):
                        res = results[res_idx]
                        ans.update({
                            "score": res.get("score", 0),
                            "justification": res.get("justification"),
                            "feedback": res.get("feedback"),
                            "strengths": res.get("strengths"),
                            "improvements": res.get("improvements")
                        })
                        total_score += res.get("score", 0)
                        res_idx += 1

                await db.db["submissions"].update_one(
                    {"_id": sid},
                    {"$set": {
                        "answers": answers_list,
                        "total_score": total_score,
                        "status": "graded" 
                    }}
                )

        # Trigger re-grading
        asyncio.create_task(process_grading_task(ObjectId(sub_id), exam, submission["answers"]))
        return RedirectResponse(url="/teacher/submissions", status_code=303)

    # Normal save logic
    updated_answers = []
    total_teacher_score = 0
    audit_entries = []
    
    for ans in submission["answers"]:
        q_id = ans["question_id"]
        t_score = float(form.get(f"t_score_{q_id}")) if form.get(f"t_score_{q_id}") else ans.get("score")
        t_feedback = form.get(f"t_feedback_{q_id}")
        
        # Audit: Detect change
        if t_score != ans.get("teacher_score") or t_feedback != ans.get("teacher_feedback"):
            audit_entries.append({
                "question_id": q_id,
                "old_score": ans.get("teacher_score", ans.get("score")),
                "new_score": t_score,
                "old_feedback": ans.get("teacher_feedback", ""),
                "new_feedback": t_feedback
            })

        ans["teacher_score"] = t_score
        ans["teacher_feedback"] = t_feedback
        total_teacher_score += ans["teacher_score"]
        updated_answers.append(ans)
        
    # Log Change if any
    if audit_entries:
        await db.db["audit_logs"].insert_one({
            "submission_id": sub_id,
            "teacher": user["username"],
            "changes": audit_entries,
            "timestamp": datetime.now()
        })

    await db.db["submissions"].update_one(
        {"_id": ObjectId(sub_id)},
        {"$set": {
            "answers": updated_answers,
            "teacher_total_score": total_teacher_score,
            "status": "reviewed"
        }}
    )
    
    return RedirectResponse(url="/teacher/submissions", status_code=303)

@app.get("/teacher/exam/{exam_id}/export")
async def export_results(exam_id: str, user: dict = Depends(teacher_only)):
    # Ownership Check
    exam = await db.db["exams"].find_one({"_id": ObjectId(exam_id)})
    if not exam or exam.get("created_by") != user["username"]:
         raise HTTPException(status_code=403, detail="You do not have permission to export this exam.")

    # Fetch all submissions for this exam
    submissions = await db.db["submissions"].find({"exam_id": exam_id}).to_list(1000)
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header
    header = ["Student", "Submitted At", "AI Score", "Teacher Score", "Status"]
    writer.writerow(header)
    
    for sub in submissions:
        writer.writerow([
            sub.get("student_username"),
            sub.get("submitted_at").strftime("%Y-%m-%d %H:%M"),
            sub.get("total_score"),
            sub.get("teacher_total_score", ""),
            sub.get("status")
        ])
    
    output.seek(0)
    filename = f"results_{exam['title'].replace(' ', '_')}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')), # Adding BOM for Excel compatibility with Thai text
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/teacher/audit-logs", response_class=HTMLResponse)
async def view_audit_logs(request: Request, user: dict = Depends(teacher_only)):
    logs = await db.db["audit_logs"].find().sort("timestamp", -1).to_list(100)
    for log in logs:
        log["id"] = str(log["_id"])
        log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M")
        
    return templates.TemplateResponse("audit_logs.html", {"request": request, "logs": logs, "user": user["username"]})

@app.get("/teacher/students", response_class=HTMLResponse)
async def view_students_performance(request: Request, user: dict = Depends(teacher_only)):
    # Group submissions by student
    submissions = await db.db["submissions"].find().to_list(2000)
    student_stats = {}
    
    for sub in submissions:
        username = sub["student_username"]
        if username not in student_stats:
            student_stats[username] = {"submissions": 0, "total_score": 0, "graded_count": 0}
            
        student_stats[username]["submissions"] += 1
        if sub.get("status") in ["graded", "reviewed"]:
            score = sub.get("teacher_total_score", sub.get("total_score", 0))
            student_stats[username]["total_score"] += score
            student_stats[username]["graded_count"] += 1
            
    # Calculate averages
    performance_list = []
    for user_id, stats in student_stats.items():
        avg = round(stats["total_score"] / stats["graded_count"], 2) if stats["graded_count"] > 0 else 0
        performance_list.append({
            "username": user_id,
            "submissions": stats["submissions"],
            "avg_score": avg
        })
        
    return templates.TemplateResponse("student_performance.html", {
        "request": request, 
        "students": performance_list, 
        "user": user["username"]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
