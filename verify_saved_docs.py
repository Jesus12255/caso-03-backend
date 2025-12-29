import asyncio
import aiohttp

async def verify_endpoints():
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # 1. List
        print("Testing List...")
        try:
            async with session.get(f"{base_url}/document/list") as resp:
                print(f"List Status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    print(f"Found {len(data)} documents.")
                    if len(data) > 0:
                        print("Sample Doc:", data[0])
                else:
                    print("List failed:", await resp.text())
        except Exception as e:
            print(f"List failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_endpoints())
