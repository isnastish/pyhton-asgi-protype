import aiohttp
import asyncio
import random # for data generation
from yarl import URL
from contextlib import AsyncExitStack
from typing import Optional

from aiohttp import (
    TraceConfig, 
    TraceResponseChunkReceivedParams, 
    TraceRequestChunkSentParams
)  

from loguru import logger 

async def on_request_start(session: aiohttp.ClientSession, trace_ctx, params) -> None:
    logger.debug("Request started")

async def on_request_end(session: aiohttp.ClientSession, trace_ctx, params) -> None:
    logger.debug("Request ended")

async def on_request_chunk_sent(session: aiohttp.ClientSession, trace_ctx, params: TraceRequestChunkSentParams) -> None:
    print(f"sent chunk {params.chunk}")

async def on_request_chunk_received(session: aiohttp.ClientSession, trace_ctx, params: TraceResponseChunkReceivedParams) -> None:
    """"""
    print(f"received chunk {params.chunk}")


_trace_config = TraceConfig()
_trace_config.on_request_start.append(on_request_start)
_trace_config.on_request_end.append(on_request_end)
# _trace_config.on_response_chunk_sent.append(on_request_chunk_sent)
# _trace_config.on_response_chunk_received.append(on_request_chunk_received)


class Client:
    """Client session wrapper"""

    def __init__(self, base_url: Optional[URL | str] = None) -> None:
        self._base_url = URL(base_url) if base_url else URL("http://localhost:5051")
        self._exit_stack: AsyncExitStack = None
        self._session: aiohttp.ClientSession = None

    async def __aenter__(self) -> aiohttp.ClientSession:
        if self._exit_stack is not None:
            raise RuntimeError("Exist stack already initialized")
        
        self._exit_stack = AsyncExitStack()
        session = await self._exit_stack.enter_async_context(
            aiohttp.ClientSession(base_url=self._base_url, trace_configs=[_trace_config])
        )
        self._session = session

        return session

    async def __aexit__(self, exc_type, exc, traceback):
        if self._exit_stack:
            await self._exit_stack.aclose()

    @property
    def base_url(self) -> str:
        return self._base_url.path 
    

async def main() -> None:
    async with Client() as client:
        async with client.get(url="/api/v1/storage/") as resp:
            if resp.ok:
                print("Status: ", resp.status)
                body = await resp.read()
                print("body: ", str(body))
            else:
                resp.raise_for_status() 
            
        data: bytes = random.randbytes(1024)  
        headers = {
            "content-type": "application/octet-stream"
        }

        async with client.put(url="/api/v1/storage/", data=data, headers=headers) as resp:
            # NOTE: We don't need to check if not resp.ok, it's already done by raise_for_status() procedure
            resp.raise_for_status()
            logger.info({"status": resp.status})
            
            
asyncio.run(main())