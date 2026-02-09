import httpx
import asyncio

async def trigger_error():
    async with httpx.AsyncClient() as client:
        # Login
        resp = await client.post("http://127.0.0.1:8003/login", data={
            "role": "teacher",
            "username": "teacher1",
            "password": "password"
        })
        print(f"Login status: {resp.status_code}")
        
        # Dashboard
        resp = await client.get("http://127.0.0.1:8003/teacher/dashboard")
        print(f"Dashboard status: {resp.status_code}")
        if resp.status_code == 500:
            print("Error 500 triggered!")
        else:
            print(f"Content length: {len(resp.text)}")

if __name__ == "__main__":
    asyncio.run(trigger_error())
