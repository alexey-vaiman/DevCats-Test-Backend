import httpx
import json
import asyncio

async def debug_login():
    url = "http://localhost:8000/v1/admin/auth/login"
    payload = {"username": "admin", "password": "admin123"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Raw Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_login())
