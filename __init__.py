# import asyncio
# from threading import Thread
# from functools import wraps
# from typing import Callable, Any, Awaitable


# def wrap_async_proc(func: Callable[[Any, Any], Awaitable[Any]]):
    # """"""
    # @wraps(func)
    # def wrapper(*args, **kwargs): 
        # return asyncio.run(func(*args, **kwargs))

    # return wrapper


# async def main() -> None:
    # """Emulate long-running event"""

    # @wrap_async_proc
    # async def thread_proc(thread_id: int):
        # print(f"thread {thread_id} started")
        # await asyncio.sleep(3) 
        # print(f"thread {thread_id} finished")

    # threads = []
    # for i in range(5): 
        # t = Thread(target=thread_proc, args=(i, ))
        # t.start()
        # threads.append(t)
    
    # for t in threads:
        # t.join()


# if __name__ == '__main__':
    # asyncio.run(main())

    