import time
from functools import wraps
import asyncio
from .settings import SETTINGS


def retry(max_attempts: int = SETTINGS["max_retries"]):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts or max_attempts < 0:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    await asyncio.sleep(SETTINGS["retry_delay"])
            raise func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts or max_attempts < 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise e
                    time.sleep(SETTINGS["retry_delay"])
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
