import logging
import json
from typing import TYPE_CHECKING, Any, Optional
from yarl import URL
from http import HTTPMethod, HTTPStatus
from loguru import logger


# True when writing code in vscode, false otherwise
if TYPE_CHECKING:
    from asgiref.typing import (
        Scope,
        HTTPScope, 
        ASGIReceiveCallable, 
        ASGISendCallable, 
        LifespanScope, 
    )


class ASGIApp:
    def __init__(self) -> None:
        self._storage: dict[str, str] = {}

    async def _read_body(self, receive: "ASGIReceiveCallable") -> bytes:
        """Read request body"""
        body_chunks: list[bytes] = []

        while True: 
            msg = await receive()
            if msg["type"] == "http.request":
                # msg["body"] contains the request body 
                # if body is missing, defaults to b""
                chunk = msg["body"]
                if chunk:
                    logger.debug({"chunk": chunk})
                    body_chunks.append(chunk)

                if not msg["more_body"]:
                    break
            elif msg["type"] == "http.disconnected": 
                raise RuntimeError("Disconnected event")
            else:
                raise RuntimeError("Unknown ASGIN event", msg["type"])
                

        return b"".join(body_chunks)
        
    async def _send_response(self, http_status: HTTPStatus, send: "ASGISendCallable", body: bytes | str | dict = b"", headers: Optional[dict[str, str]] = None) -> None:
        """Send response to the server"""
        headers = dict(headers) if headers else {}  

        # We always send data in bytes
        if isinstance(body, str):
            body = body.encode()
            headers["content-type"] = "text/plain"
        elif isinstance(body, dict): 
            body = json.dumps(body).encode()
            headers["content-type"] = "application/json"
        
        # convert headers to binary stream  
        def headers_to_bytes(headers: dict[str, str]) -> list[tuple[bytes, bytes]]:
            return [(k.lower().encode(), v.encode()) for k, v in headers.items()] 
        
        await send({
            "type": "http.response.start",
            "status": http_status,  
            "headers": headers_to_bytes(headers)
        })

        await send({"type": "http.response.body", "body": body, "more_body": False})


    async def _handle_http_protocol(self, scope: "HTTPScope", receive: "ASGIReceiveCallable", send: "ASGISendCallable") -> None:
        """Handle http calls"""
        method = scope["method"] 
        if method not in (HTTPMethod.PUT, HTTPMethod.GET, HTTPMethod.POST, HTTPMethod.DELETE):
            raise RuntimeError(f"Unsupported method {scope['method']}")

        logger.info({"url": scope["path"]})

        if method == HTTPMethod.GET:
            logger.info({"method": HTTPMethod.GET})
            await self._send_response(HTTPStatus.OK, send, )

        elif method == HTTPMethod.PUT:
            logger.info({"method": HTTPMethod.PUT})
            body = await self._read_body(receive)
            print(f"{body=}")

            await self._send_response(HTTPStatus.ACCEPTED, send)
        

    async def _handle_lifespan_protocol(self, scope: "LifespanScope", receive: "ASGIReceiveCallable", send: "ASGISendCallable") -> None:
        """Handle lifespan calls"""
        while True:
            event = await receive()
            if event["type"] == "lifespan.startup":
               await send({"type": "lifespan.startup.complete"}) 
            elif event["type"] == "lifespan.shutdown":
                break
                
        await send({"type": "lifespan.shutdown.complete"})


    async def __call__(self, scope: "Scope", receive: "ASGIReceiveCallable", send: "ASGISendCallable") -> Any:
        try:
            if scope["type"] == "lifespan":
                logger.debug("lifespan protocol is used")
                await self._handle_lifespan_protocol(scope, receive, send)
            elif scope["type"] == "http":
                logger.debug("http protocol is used")
                await self._handle_http_protocol(scope, receive, send)
            else:
                raise RuntimeError("Unknown ASGI protocol type", scope["type"])
            
        except Exception as ex:
            print(ex)

# this would be invoked by the granian server
app = ASGIApp()
            