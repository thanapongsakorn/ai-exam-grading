@echo off
echo Starting the Subjective Exam Grading AI System...
echo Note: Make sure you have MongoDB running if required later.
echo.
call venv\Scripts\activate
python -m uvicorn app.main:app --reload
pause
