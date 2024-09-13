import aiohttp
import asyncio

from aiohttp import TraceConfig 

class AppClient:
    def __init__(self) -> None:
        pass 

    
async def main() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url="http://localhost:5051") as resp:
            print("Status: ", resp.status)
            # print("Content-type: ", resp.headers["content-type"])

            body = await resp.read()
            print("body: ", str(body))
    
asyncio.run(main())