# import logging
import json
from typing import TYPE_CHECKING, Any, Optional
from yarl import URL
from http import HTTPMethod, HTTPStatus
from loguru import logger


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
        self._storage: dict[str, Any] = {}


    async def _get_handler(self, scope: "HTTPScope", send: "ASGISendCallable") -> None:
        """Get value from the storage"""
        key = URL(scope["path"]).parts[-1]
        logger.info({"key": key})
        if v := self._storage.get(key, None):
            await self._send_response(HTTPStatus.OK, send, body=v)
        else: 
            await self._send_response(HTTPStatus.NOT_FOUND, send, body=f"key {key} doesn't exist")
    
    
    async def _put_handler(self, scope: "HTTPScope", send: "ASGISendCallable", receive: "ASGIReceiveCallable") -> None:
        """Put value into a storage"""
        body = await self._read_body(receive)
        key = URL(scope["path"]).parts[-1]
        logger.info({"key": key, "value": body})
        self._storage[key] = body

        await self._send_response(HTTPStatus.ACCEPTED, send)


    async def _del_handler(self, scope: "HTTPScope", send: "ASGISendCallable") -> None:
        """Delete value from the storage"""
        key = URL(scope["path"]).parts[-1]
        try:
            v = self._storage.pop(key)
        except KeyError:
            await self._send_response(HTTPStatus.NOT_FOUND, send, body=f"key {key} doesn't exist") 
            return

        await self._send_response(HTTPStatus.OK, send)


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

        if method == HTTPMethod.GET:
            logger.info({"method": HTTPMethod.GET, "url": scope["path"]})

            # GET data from the whole storage 
            if scope["path"].removesuffix("/") == "/api/storage":
                storage = self._storage.copy() 
                await self._send_response(HTTPStatus.OK, send, body=storage)
            else:
                await self._get_handler(scope, send)

        elif method == HTTPMethod.PUT:
            logger.info({"method": HTTPMethod.PUT, "url": scope["path"]})
            await self._put_handler(scope, send, receive)
        
        elif method == HTTPMethod.DELETE:
            logger.info({"method": HTTPMethod.DELETE, "url": scope["path"]})
            await self._del_handler(scope, send)
        

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
        """Granian server entry point"""
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
            