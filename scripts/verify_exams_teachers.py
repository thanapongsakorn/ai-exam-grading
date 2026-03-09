import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def verify():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    exams = await db['exams'].find().to_list(100)
    print(f'Total exams: {len(exams)}')
    
    by_teacher = {}
    for e in exams:
        created_by = e.get('created_by', 'unknown')
        subject = e.get('subject', 'unknown')
        if created_by not in by_teacher:
            by_teacher[created_by] = {}
        if subject not in by_teacher[created_by]:
            by_teacher[created_by][subject] = 0
        by_teacher[created_by][subject] += 1
        
    for t, subjs in by_teacher.items():
        print(f'Teacher: {t}')
        for s, count in subjs.items():
            print(f'  - Subject: {s}, Exams: {count}')
            
    client.close()

if __name__ == '__main__':
    asyncio.run(verify())
