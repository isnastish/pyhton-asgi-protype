import aiohttp
import asyncio
from yarl import URL
from contextlib import AsyncExitStack
from typing import Optional

from aiohttp import (
    TraceConfig, 
    TraceResponseChunkReceivedParams, 
    TraceRequestChunkSentParams
)  


async def on_request_start(session, trace_ctx, params) -> None:
    print("Request started")

async def on_request_end(session, trace_ctx, params) -> None:
    print("Request ended")

async def on_request_chunk_sent(session, trace_ctx, params: TraceRequestChunkSentParams) -> None:
    """"""
    print(f"sent chunk {params.chunk}")

async def on_request_chunk_received(session, trace_ctx, params: TraceResponseChunkReceivedParams) -> None:
    """"""
    print(f"received chunk {params.chunk}")


_trace_config = TraceConfig()
_trace_config.on_request_start.append(on_request_start)
_trace_config.on_request_end.append(on_request_end)


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
        url = URL("/api/v1/storage/") 
        async with client.get(url=url.path) as resp:
            if resp.ok:
                print("Status: ", resp.status)
                body = await resp.read()
                print("body: ", str(body))
            else:
                resp.raise_for_status() 
            
asyncio.run(main())