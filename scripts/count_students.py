import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def count_students():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DB_NAME')]
    count = await db['users'].count_documents({'role': 'student'})
    print(f'TOTAL_STUDENTS: {count}')
    client.close()

if __name__ == '__main__':
    asyncio.run(count_students())
