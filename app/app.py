# TODO: Ask Matias to explain about type-checking, 
# in particular under which conditions TYPE_CHECKING constant is set to True 
from typing import TYPE_CHECKING, Any
from yarl import URL

if TYPE_CHECKING:
    from asgiref.typing import (
        Scope,
        HTTPScope, 
        ASGIReceiveCallable, 
        ASGISendCallable
    )

async def _handle_http_protocol(scope: "HTTPScope", receive: "ASGIReceiveCallable", send: "ASGISendCallable") -> None:
    """Handle http calls"""
    path = URL(scope["path"])
    print(f"{path=}")
    
    await send({
       "type": "http.response.start",
       "status": 200,  
       "headers": [
           [b"content-type", b"text/plain"],
       ]
    })

    await send({
        "type": "http.response.body", 
        "body": b"Hello World!"
    })
    

async def _handle_lifespan_protocol(scope, receive, send) -> None:
    """Handle lifespan calls"""


class App:
    def __init__(self) -> None:
        pass

    async def __call__(self, scope: "Scope", receive: "ASGIReceiveCallable", send: "ASGISendCallable") -> Any:
        # TODO: Ask Matias why do we have to handle an exception while determining scope["type"]
        # Why do we need to handle generic exception if we raise RuntimeError
        try:
            if scope["type"] == "lifespan":
                await _handle_lifespan_protocol(scope, receive, send)
            elif scope["type"] == "http":
                await _handle_http_protocol(scope, receive, send)
            else:
                raise RuntimeError("Unknown ASGI protocol type", scope["type"])
            
        except Exception as ex: # broad exception caught 
            print(ex)

app = App()
            