from loguru import logger
from collections.abc import Callable
from typing import Any


__all__ = ["rangetest", "advance_rangetest"]


def rangetest(*argranges):
    """Decorator used to check range boundaries."""
    logger.info({"argranges is_tuple": isinstance(argranges, tuple)})

    def on_decorator(func: Callable[[Any], Any]):
        code = func.__code__
        all_args = code.co_varnames[:code.co_argcount]
        func_name = func.__name__
        func_doc_str = func.__doc__
        expected_args = list(all_args)

        logger.info({
            "func_doc_str": func_doc_str, 
            "func_name": func_name, 
            "func.__code__": func.__code__, 
            "all_args": all_args, 
            "expected_args": expected_args
        })

        def on_call(*args):
            logger.info({"is_tuple": isinstance(args, tuple), "len(args)": len(args)})

            for (ix, low, high) in argranges: 
                logger.info({"args[ix]": args[ix], "ix": ix, "low": low, "high": high})

                if args[ix] < low or args[ix] > high:
                    raise TypeError(f"Arument {ix} not in a range [{low}, {high}]")
                
            return func(*args)
        return on_call
    
    return on_decorator 


def advance_rangetest(**argranges):
    """"""
    def on_decorator(func: Callable[[Any], Any]) -> Callable:
        code = func.__code__
        all_args = code.co_varnames[:code.co_argcount]
        func_name = func.__name__

        logger.info({
            "func_name": func_name, 
            "func.__code__": func.__code__, 
            "all_args": all_args, 
        })

        def on_call(*pargs, **kwargs): 
            # All pargs match first N expected args by position
            # the rest must be in kargs or be omitted defaults
            expected = list(all_args)
            positionals = expected[:len(pargs)]

            for (arg_name, (low, high)) in argranges.items():
                if arg_name in kwargs:
                    # was passed by name
                    logger.info({"arg_name": arg_name})

                    if kwargs[arg_name] < low or kwargs[arg_name] > high:
                        raise TypeError(f"{func_name} Argument {arg_name} is out of range [{low}, {high}]")

                elif arg_name in positionals: 
                    # was passed by position
                    position = positionals.index(arg_name)
                    if pargs[position] < low or pargs[position] > high:
                        raise TypeError(f"{func_name} Argument {arg_name} is out of range [{low}, {high}]")
                else:
                    # not passed: default
                    logger.info(f"Argument {arg_name} defaulted")

            return func(*pargs, **kwargs)
        
        return on_call
    
    return on_decorator
