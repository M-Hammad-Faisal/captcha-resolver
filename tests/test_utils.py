import pytest
from time import time
from captcha_solver.utils import retry
from captcha_solver.exceptions import CaptchaError, CaptchaTimeoutError, CaptchaServiceError
from captcha_solver.settings import SETTINGS


def measure_time(func, *args, **kwargs):
    start = time()
    result = func(*args, **kwargs)
    return result, time() - start


def test_retry_success():
    @retry(max_attempts=3)
    def successful_function():
        return "success"

    result = successful_function()
    assert result == "success"


def test_retry_eventual_success():
    attempts = 0

    @retry(max_attempts=3)
    def eventually_successful():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise CaptchaError("Temporary failure")
        return "success"

    result = eventually_successful()
    assert result == "success"
    assert attempts == 2


def test_retry_failure():
    attempts = 0

    @retry(max_attempts=3)
    def failing_function():
        nonlocal attempts
        attempts += 1
        raise CaptchaError("Persistent failure")

    with pytest.raises(CaptchaError) as exc_info:
        failing_function()
    assert str(exc_info.value) == "Persistent failure"
    assert attempts == 3


def test_retry_timing():
    attempts = 0

    @retry(max_attempts=3)
    def timing_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise CaptchaError("Testing timing")
        return "success"

    result, duration = measure_time(timing_function)
    expected_min_time = SETTINGS["retry_delay"] * (attempts - 1)
    assert result == "success"
    assert duration >= expected_min_time
    assert attempts == 3


@pytest.mark.asyncio
async def test_retry_async_success():
    @retry(max_attempts=3)
    async def async_success():
        return "async_success"

    result = await async_success()
    assert result == "async_success"


@pytest.mark.asyncio
async def test_retry_async_retries():
    attempts = 0

    @retry(max_attempts=3)
    async def async_retries():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise CaptchaError("Async temporary failure")
        return "async_success"

    result = await async_retries()
    assert result == "async_success"
    assert attempts == 2


def test_retry_different_exceptions():
    attempts = 0
    exceptions = [CaptchaError, CaptchaTimeoutError, CaptchaServiceError]

    @retry(max_attempts=4)
    def multi_exception_function():
        nonlocal attempts
        attempts += 1
        if attempts <= 3:
            raise exceptions[attempts - 1](f"Exception {attempts}")
        return "success"

    result = multi_exception_function()
    assert result == "success"
    assert attempts == 4


def test_retry_zero_attempts():
    @retry(max_attempts=0)
    def zero_attempts_function():
        raise CaptchaError("Should fail immediately")

    with pytest.raises(CaptchaError) as exc_info:
        zero_attempts_function()
    assert str(exc_info.value) == "Should fail immediately"


def test_retry_negative_attempts():
    @retry(max_attempts=-1)
    def negative_attempts_function():
        raise CaptchaError("Should fail immediately")

    with pytest.raises(CaptchaError) as exc_info:
        negative_attempts_function()
    assert str(exc_info.value) == "Should fail immediately"


def test_retry_no_exception():
    calls = 0

    @retry(max_attempts=3)
    def no_exception_function():
        nonlocal calls
        calls += 1
        return "no_exception"

    result = no_exception_function()
    assert result == "no_exception"
    assert calls == 1


@pytest.mark.parametrize("max_attempts", [1, 3, 5])
def test_retry_parametrized(max_attempts):
    attempts = 0

    @retry(max_attempts=max_attempts)
    def counting_function():
        nonlocal attempts
        attempts += 1
        if attempts <= max_attempts:
            raise CaptchaError("Counting")
        return "done"

    result = counting_function()
    assert attempts == max_attempts + 1
    assert result == "done"


@pytest.mark.asyncio
@pytest.mark.parametrize("max_attempts", [1, 3, 5])
async def test_retry_async_parametrized(max_attempts):
    attempts = 0

    @retry(max_attempts=max_attempts)
    async def async_counting_function():
        nonlocal attempts
        attempts += 1
        if attempts <= max_attempts:
            raise CaptchaError("Async counting")
        return "async_done"

    result = await async_counting_function()
    assert attempts == max_attempts + 1
    assert result == "async_done"
