# Article: https://medium.com/azure-tutorials/a-deep-dive-into-python-logging-practical-examples-for-developers-ca45a072e709
import logging
import logging.config
import traceback
import json

from typing import Any

# 1. Loggers (used by python modules) 

# 2. Handlers defined where messages should be sent. 
# Console, files, network sockets, external services. 
# More than one handler could be added to the logger. 

# 3. Formatters determine the layout of log messages.
# Basically this is the format of the logs, which include 
# timestamp, log levels etc.

# 4. Log Levels
# DEBUG, INFO, WARNING, ERROR and CRITICAL. 
# Loggers could be configured to capture messages at or above a certain level.

# 5. Logging configuration
# Logging could be configured programatically or via the configuration files

# 6. Logging to files for persisting logs

_logging_fmt = "%(levelno)s-%(levelname)s-%(asctime)s-%(name)s-%(message)s" 
# %(levelno)s - is the level number
# %(name)s - name of the logging object
# %(asctime)s - time the log message was generated
# %(levelname)s - severity level of the log message   
# %(message)s - log message itself

# could be only called once
logging.basicConfig(level=logging.DEBUG, 
                    filemode='w', 
                    filename="myapp.log", 
                    format=_logging_fmt, 
                    datefmt = "%y-%m-%d %H:%M:%S",
                    )

_logger = logging.getLogger("App")

# test logging
_logger.debug({"this is the log": "this is the log value"})
_logger.info({"this is the log": "this is the log value"})
_logger.warning({"this is the log": "this is the log value"})
_logger.error({"this is the log": "this is the log value"})
_logger.critical({"this is the log": "this is the log value"})

# the following format for displaying logs
# severity:logger_name:message

# TODO: Ask Matias to explain about json formatter and logging formatters in general
# Especially how to configure format function
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord)-> str:
        msg: dict[str, str] = {
            "level": record.levelname, 
            "module": record.name
        }

        if isinstance(record.msg, dict):
            msg = record.msg | msg
        else: 
            msg["message"] = record.getMessage()
        
        # this is for logging exceptions
        if record.exc_info:
            exc_type, ex, tb = record.exc_info
            msg["exception_type"] = exc_type.__name__
            msg["exception_info"] = str(ex)
            msg["traceback"] = "\n".join(traceback.format_tb(tb))
        
        return json.dumps(msg)

# TODO: Ask Matias about log filters as well.
class LogAugmentationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return True
    
# TODO: Ask Matias whether it's ok to set logging config 
# in multiple places.
_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1, 
    "formatters": {
        "json": {
            "()": JsonFormatter
        }, 
    }, 
    "disable_existing_loggers": False, 
}

logging.config.dictConfig(_LOGGING_CONFIG)
