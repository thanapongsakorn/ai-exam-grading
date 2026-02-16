import google.generativeai as genai
import json
import re
import asyncio
from datetime import datetime
from app.config import settings
from app.database import db
import traceback

class AIService:
    def __init__(self):
        # ล้างช่องว่างและตรวจสอบความถูกต้องเบื้องต้น
        api_key = settings.GEMINI_API_KEY.strip()
        key_len = len(api_key)
        print(f"DEBUG: Loading Gemini API Key. Length: {key_len}")
        print(f"DEBUG: Key context: {api_key[:4]}...{api_key[-4:] if key_len > 4 else ''}")
        
        if key_len < 30:
            print("WARNING: API Key looks too short! (Usually around 39 characters)")
            
        genai.configure(api_key=api_key)
        # ใช้ชื่อโมเดลที่แนะนำและเสถียรที่สุด
        self.model = genai.GenerativeModel('gemini-flash-latest')
        # Lazy initialization for semaphore to avoid event loop issues
        self._semaphore = None

    @property
    def semaphore(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(5)
        return self._semaphore

    async def grade_batch(self, questions_data: list, context: dict = None):
        """
        Grades all answers in one go for maximum quota efficiency.
        questions_data: list of dicts {question_text, student_answer, max_score, answer_key, rubric}
        """
        async with self.semaphore:
            print(f"AI Batch Grading started for {len(questions_data)} questions.")
            
            questions_prompt = ""
            for i, q in enumerate(questions_data):
                rubric_text = ""
                if q.get('rubric'):
                    rubric_text = "\n[เกณฑ์ Rubric]\n"
                    for item in q['rubric']:
                        if hasattr(item, 'dict'): item = item.dict()
                        rubric_text += f"- {item.get('score')} คะแนน: {item.get('description')}\n"

                questions_prompt += f"""
--- ข้อที่ {i+1} ---
โจทย์: {q['question_text']}
แนวคำตอบ: {q.get('answer_key') or 'ไม่ได้ระบุ'}
คะแนนเต็ม: {q['max_score']}
{rubric_text}
คำตอบของนักเรียน: {q['student_answer']}
"""

            prompt = f"""
คุณคือระบบผู้เชี่ยวชาญในการตรวจข้อสอบอัตนัย (Subjective Exam Grader) 
จงประเมินคำตอบของนักเรียนทีละข้อตามข้อมูลที่กำหนดให้ โดยให้คะแนนอย่างเที่ยงตรงตามเกณฑ์

[ข้อมูลข้อสอบ]
{questions_prompt}

[กฎการตรวจ]
1. ประเมินความถูกต้องตามหลักวิชาการและเกณฑ์ที่ให้มา
2. ให้คะแนนสุทธิ [0 ถึง คะแนนเต็ม] เท่านั้น
3. สำหรับแต่ละข้อ จงระบุจุดแข็ง (Strengths) และสิ่งที่ควรปรับปรุง (Improvements)

[รูปแบบการตอบกลับ (Strict JSON Array)]
จงตอบกลับเป็น JSON Array ของอ็อบเจกต์ในลำดับที่ถูกต้อง ดังนี้:
[
    {{
        "score": [คะแนนข้อ 1],
        "justification": "[เหตุผลสั้นๆ]",
        "feedback": "[คำแนะนำรวม]",
        "strengths": "[จุดเด่น]",
        "improvements": "[จุดที่ควรแก้]"
    }},
    ...
]
"""
            for attempt in range(3):
                try:
                    print(f"  Attempt {attempt+1}: Calling Gemini API for single batch...")
                    response = await self.model.generate_content_async(prompt)
                    
                    if not response.parts:
                        print(f"  Warning: Response was blocked or empty.")
                        continue
                        
                    text = response.text
                    json_str = text
                    if "```json" in text:
                        json_str = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        json_str = text.split("```")[1].split("```")[0].strip()
                    
                    match = re.search(r'\[.*\]', json_str, re.DOTALL)
                    if match:
                        results = json.loads(match.group())
                        if len(results) == len(questions_data):
                            print(f"  Successfully parsed {len(results)} results.")
                            # Success log
                            try:
                                await db.db["ai_logs"].insert_one({
                                    "timestamp": datetime.now(),
                                    "context": context,
                                    "status": "success",
                                    "batch_size": len(questions_data)
                                })
                            except Exception as db_e:
                                print(f"  DB Log Error (Non-critical): {db_e}")
                            return results
                        else:
                            print(f"  Batch size mismatch: expected {len(questions_data)}, got {len(results)}")
                    else:
                        print(f"  Failed to find JSON array in response: {text[:100]}...")
                except Exception as e:
                    print(f"  Batch attempt {attempt+1} failed: {e}")
                    await asyncio.sleep(1)

            # Fallback to empty results
            return [{"score": 0, "feedback": "เกิดข้อผิดพลาดในการตรวจ"} for _ in range(len(questions_data))]

    async def grade_answer(self, question_text: str, student_answer: str, max_score: int, answer_key: str = None, grading_criteria: str = None, rubric: list = None, context: dict = None):
        # Single grading now just calls the batch with one item for consistency or remains as is
        results = await self.grade_batch([{
            "question_text": question_text,
            "student_answer": student_answer,
            "max_score": max_score,
            "answer_key": answer_key,
            "rubric": rubric
        }], context)
        return results[0]

ai_service = AIService()
