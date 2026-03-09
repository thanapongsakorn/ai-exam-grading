import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def run_diagnostics():
    print("🔍 Running Final System Diagnostics...")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    
    # Check 1: Orphaned Exams (Created by teachers that don't exist)
    teachers = await db['users'].find({'role':'teacher'}).to_list(100)
    teacher_usernames = [t['username'] for t in teachers]
    
    exams = await db['exams'].find().to_list(100)
    orphaned_exams = [e for e in exams if e.get('created_by') not in teacher_usernames]
    print(f"\n1. Orphaned Exams Check: Found {len(orphaned_exams)} orphans.")
    if orphaned_exams:
        for oe in orphaned_exams:
            print(f"   -> Exam '{oe.get('title')}' owned by missing user '{oe.get('created_by')}'")
            
    # Check 2: Invalid Student Enrollments (Subjects that don't exist as exams)
    students = await db['users'].find({'role':'student'}).to_list(100)
    active_subjects = list(set([e.get('subject') for e in exams if not e.get('is_deleted')]))
    
    bad_enrollments = []
    for student in students:
        for sub in student.get('enrolled_subjects', []):
            if sub not in active_subjects:
                bad_enrollments.append({"student": student['username'], "invalid_subject": sub})
                
    print(f"\n2. Invalid Enrollments Check: Found {len(bad_enrollments)} broken links.")
    if bad_enrollments:
        for be in bad_enrollments:
            print(f"   -> Student '{be['student']}' is enrolled in missing subject '{be['invalid_subject']}'")
            
    # Check 3: Duplicate Users
    pipeline = [{"$group": {"_id": "$username", "count": {"$sum": 1}}}, {"$match": {"count": {"$gt": 1}}}]
    duplicates = await db['users'].aggregate(pipeline).to_list(100)
    print(f"\n3. Duplicate User Check: Found {len(duplicates)} duplicate usernames.")
    
    if len(orphaned_exams) == 0 and len(bad_enrollments) == 0 and len(duplicates) == 0:
        print("\n✅ ALL DIAGNOSTICS PASSED: The database is clean and structurally sound.")
    else:
        print("\n⚠️ WARNING: Issues found in database integrity.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
