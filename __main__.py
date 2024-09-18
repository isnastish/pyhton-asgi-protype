from granian import Granian
from granian.constants import Interfaces
from granian.log import LogLevels


if __name__ == '__main__':
   g = Granian(
      target="app.app:app", 
      address="0.0.0.0", # listen on any address 
      port=5051, 
      interface=Interfaces.ASGI, 
      websockets=False, 
      log_access=True, 
      log_enabled=True, 
      log_level=LogLevels.debug, 
   )

   g.serve()
    