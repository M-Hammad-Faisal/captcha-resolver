import os

import pytest
from captcha_solver import PlaywrightCaptchaSolver


@pytest.mark.skip(reason="Requires 2Captcha API key")
def test_playwright_solver_recaptcha():
    solver = PlaywrightCaptchaSolver(api_key=os.environ["API_KEY"])
    result = solver.solve({"url": "https://www.google.com/recaptcha/api2/demo"})
    assert result is not None


@pytest.mark.skip(reason="Requires 2Captcha API key")
@pytest.mark.asyncio
async def test_playwright_solver_async_recaptcha():
    solver = PlaywrightCaptchaSolver(api_key=os.environ["API_KEY"])
    result = await solver.solve_async({"url": "https://www.google.com/recaptcha/api2/demo"})
    assert result is not None
