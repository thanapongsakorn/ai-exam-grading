import asyncio
import os
import time
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_parallel_logic():
    print("⚡ Testing Parallel Execution Mockup...")
    
    async def mock_ai_call(q_id, sleep_time):
        print(f"🤖 Starting Question {q_id} (will take {sleep_time}s)...")
        await asyncio.sleep(sleep_time)
        print(f"✅ Finished Question {q_id}")
        return 10

    start_time = time.time()
    
    # Simulate 3 questions taking 2s, 3s, and 1s respectively
    tasks = [
        mock_ai_call(1, 2),
        mock_ai_call(2, 3),
        mock_ai_call(3, 1)
    ]
    
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    total_time = end_time - start_time
    print(f"\n📊 Total time taken: {total_time:.2f}s")
    print(f"💰 Total Score: {sum(results)}")
    
    if total_time < 4: # Should be roughly 3s (the max), not 6s (the sum)
        print("🚀 Parallel Logic Verified! It's much faster.")
    else:
        print("🐢 Sequential Logic detected. Optimization failed.")

if __name__ == "__main__":
    asyncio.run(test_parallel_logic())
