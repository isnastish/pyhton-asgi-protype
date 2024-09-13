from typing import TYPE_CHECKING, Any
from yarl import URL
import logging

# True when writing code in vscode, false otherwise
if TYPE_CHECKING:
    from asgiref.typing import (
        Scope,
        HTTPScope, 
        ASGIReceiveCallable, 
        ASGISendCallable, 
        LifespanScope, 
    )

# configure logging level
logging.basicConfig(level=logging.DEBUG)

# create logger
_logger = logging.getLogger(__name__)


class App:
    def __init__(self) -> None:
        self._storage: dict[str, str] = {}

    async def _handle_http_protocol(self, scope: "HTTPScope", receive: "ASGIReceiveCallable", send: "ASGISendCallable") -> None:
        """Handle http calls"""
        method = scope["method"] 
        if method not in ("PUT", "GET"):
            raise RuntimeError(f"Unsupported method {scope['method']}")

        if method == "GET":
            url = scope["path"]
            print(f"{url=}")

            # This doesn't get an actual query string
            query = scope["query_string"]
            print(f"{query=}")
            
            await send({
            "type": "http.response.start",
            "status": 200,  
            "headers": [
                [b"content-type", b"text/plain"],
            ]
            })

            await send({
                "type": "http.response.body", 
                "body": b"Hello World!",
                "more_body": False,
            })

        elif method == "PUT":
            url = scope["path"]
            print(f"{url=}")
        

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
                _logger.info("lifespan protocol is used")
                await self._handle_lifespan_protocol(scope, receive, send)
            elif scope["type"] == "http":
                _logger.info("http protocol is used")
                await self._handle_http_protocol(scope, receive, send)
            else:
                raise RuntimeError("Unknown ASGI protocol type", scope["type"])
            
        except Exception as ex:
            print(ex)

# this would be invoked by the granian server
app = App()
            