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

    async def grade_answer(self, question_text: str, student_answer: str, max_score: int, answer_key: str = None, grading_criteria: str = None, rubric: list = None, context: dict = None):
        print(f"AI Grading started for question: {question_text[:30]}...")

        rubric_text = ""
        if rubric:
            rubric_text = "\n[เกณฑ์การให้คะแนนแบบละเอียด (Rubric)]\n"
            for item in rubric:
                # Handle both dict (from raw json) and RubricItem object
                if hasattr(item, 'dict'): item = item.dict()
                rubric_text += f"- คะแนน {item.get('score')} ({item.get('level')}): {item.get('description')}\n"
            rubric_text += "\nคำสั่งพิเศษ: จงให้คะแนนตามเกณฑ์ใน Rubric นี้อย่างเคร่งครัด\n"

        if answer_key:
            instruction_mode = "1. การวิเคราะห์ (Systematic Comparison): เปรียบเทียบคำตอบของนักเรียนกับ 'คำตอบเฉลย' และ 'เกณฑ์การให้คะแนน' ทีละประเด็น"
            key_info = f"- คำตอบเฉลย/แนวคำตอบมาตรฐาน: {answer_key}"
        else:
            instruction_mode = "1. การวิเคราะห์ (Fact-based Evaluation): ประเมินความถูกต้องตามหลักวิชาการ (เนื่องจากไม่มีเฉลยระบุไว้ ให้ใช้ความรู้ของ AI ตัดสิน)"
            key_info = "- คำตอบเฉลย/แนวคำตอบมาตรฐาน: ไม่ได้ระบุ (ให้ใช้ความรู้ทั่วไปของ AI และให้คะแนนตามความถูกต้องของเนื้อหา)"

        criteria_text = grading_criteria if grading_criteria else "ประเมินตามความถูกต้องและความสมเหตุสมผล"

        prompt = f"""
        คุณคือระบบผู้เชี่ยวชาญ (Expert System) ในการประเมินข้อสอบอัตนัยที่เน้นความเที่ยงตรงสูง
        จงดำเนินการวิเคราะห์และประเมินคำตอบของนักเรียนตามหลักการดังนี้:
        
        [ข้อมูลประกอบการประเมิน]
        - โจทย์: {question_text}
        {key_info}
        - เกณฑ์การให้คะแนนทั่วไป: {criteria_text}
        {rubric_text}
        - คะแนนเต็ม: {max_score}
        
        [คำตอบของนักเรียน]
        {student_answer}
        
        [กระบวนการประเมิน (Strict Instructions)]
        {instruction_mode}
        2. การแจกแจงคะแนน (Scoring Breakdown): ระบุว่าคะแนนแต่ละส่วนมาจากความถูกต้องตรงไหน (หากมี Rubric ให้ระบุว่าตกอยู่ในเกณฑ์ระดับใด)
        3. การให้คะแนนสุทธิ: คะแนนรวมต้องอยู่ระหว่าง 0 ถึง {max_score} เท่านั้น
        4. การให้คำแนะนำ (Feedback): ระบุจุดแข็ง (Strengths) และสิ่งที่ควรปรับปรุง (Improvements) เพื่อพัฒนาในครั้งต่อไป
        
        [รูปแบบการตอบกลับ (Strict JSON)]
        {{
            "score": [ตัวเลขคะแนนสุทธิ],
            "justification": "[สรุปการแจกแจงคะแนนทีละขั้น และเหตุผลที่หักหรือให้คะแนนในแต่ละส่วน]",
            "feedback": "[ภาพรวมการประเมินในเชิงวิชาการและสร้างสรรค์]",
            "strengths": "[ระบุประเด็นที่นักเรียนตอบได้ถูกต้อง]",
            "improvements": "[ระบุสิ่งที่ขาดหายไปหรือควรเพิ่มเติม]"
        }}
        """
        
        for attempt in range(3): # Retry up to 3 times
            try:
                response = self.model.generate_content(prompt)
                text = response.text
                
                # Log interaction
                log_entry = {
                    "timestamp": datetime.now(),
                    "context": context,
                    "raw_response": text,
                    "parsed_result": None,
                    "attempt": attempt + 1,
                    "status": "pending"
                }

                # cleaner extraction of JSON (handle markdown blocks)
                json_str = text
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    json_str = text.split("```")[1].split("```")[0].strip()
                
                # regex fallback
                match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        # Ensure score doesn't exceed max
                        result['score'] = min(float(result.get('score', 0)), max_score)
                        
                        # Update log with success
                        log_entry["parsed_result"] = result
                        log_entry["status"] = "success"
                        await db.db["ai_logs"].insert_one(log_entry)
                        
                        return result
                    except json.JSONDecodeError as je:
                        log_entry["status"] = f"parse_error: {str(je)}"
                        await db.db["ai_logs"].insert_one(log_entry)
                        raise je
            except Exception as e:
                print(f"Attempt {attempt+1} failed for Gemini call: {e}")
                traceback.print_exc()
                if attempt == 2:
                    # Final log for failure
                    await db.db["ai_logs"].insert_one({
                        "timestamp": datetime.now(),
                        "context": context,
                        "error": str(e),
                        "status": "failed"
                    })
                    return {"score": 0, "feedback": f"เกิดข้อผิดพลาดจาก AI: {str(e)}", "strengths": "", "improvements": ""}
                await asyncio.sleep(1) # Wait before retry
                
        return {"score": 0, "feedback": "ไม่สามารถประมวลผลคำตอบได้ในขณะนี้", "strengths": "", "improvements": ""}

ai_service = AIService()
