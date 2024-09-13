import aiohttp
import asyncio
from yarl import URL

from aiohttp import TraceConfig  

class Client:
    def __init__(self) -> None:
        pass 

async def on_request_start(session, trace_ctx, params) -> None:
    print("Request started")

async def on_request_end(session, trace_ctx, params) -> None:
    print("Request ended")

async def on_request_chunk_sent(session, trace_ctx, params) -> None:
    """"""

async def on_request_chunk_received(session, trace_ctx, params) -> None:
    """"""

# TODO: Implement TraceConfig    
trace_config = TraceConfig()
trace_config.on_request_start.append(on_request_start)
trace_config.on_request_end.append(on_request_end)

async def main() -> None:
    async with aiohttp.ClientSession(base_url="http://localhost:5051", trace_configs=[trace_config]) as session:
        url = URL("/api/v1/storage/") 
        url.with_query({"key": "value"})
        async with session.get(url=url.path) as resp:
            if resp.ok:
                print("Status: ", resp.status)
                body = await resp.read()
                print("body: ", str(body))
            else:
                resp.raise_for_status() 
            
    
asyncio.run(main())