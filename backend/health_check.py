import httpx
import asyncio

async def check():
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get("http://localhost:8000/health")
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")

asyncio.run(check())
