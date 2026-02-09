
import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8003"

async def test_routes():
    async with httpx.AsyncClient(follow_redirects=False) as client:
        print("--- Route Verification ---")
        
        # 1. Test Home
        try:
            r = await client.get(f"{BASE_URL}/")
            print(f"[*] Home page: {r.status_code}")
        except Exception as e:
            print(f"[!] Could not reach server: {e}")
            return

        # 2. Test Teacher Dashboard without login
        r = await client.get(f"{BASE_URL}/teacher/dashboard")
        print(f"[*] Teacher Dashboard (No Login): {r.status_code} (Redirect to {r.headers.get('Location')})")

        # 3. Test Teacher Dashboard with Student Session
        # Cookies: user_session=student1
        r = await client.get(f"{BASE_URL}/teacher/dashboard", cookies={"user_session": "student1"})
        print(f"[*] Teacher Dashboard (As Student): {r.status_code} (Redirect to {r.headers.get('Location')})")
        
        # 4. Test Teacher Dashboard with Teacher Session
        r = await client.get(f"{BASE_URL}/teacher/dashboard", cookies={"user_session": "teacher1"})
        print(f"[*] Teacher Dashboard (As Teacher): {r.status_code}")
        if r.status_code == 200:
            print("    - Successfully accessed teacher dashboard")

if __name__ == "__main__":
    asyncio.run(test_routes())
