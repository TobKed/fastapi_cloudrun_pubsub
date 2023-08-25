# ruff: noqa: ANN201, ANN001, ANN202
import asyncio

from loguru import logger


def debug_log_function_call(func):
    async def wrapper_async(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        result = await func(*args, **kwargs)
        logger.debug(f"Function {func.__name__} executed")
        return result

    def wrapper_sync(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"Function {func.__name__} executed")
        return result

    if asyncio.iscoroutinefunction(func):
        return wrapper_async
    else:  # noqa: RET505
        return wrapper_sync
