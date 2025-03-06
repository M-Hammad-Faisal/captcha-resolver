import os

import pytest
from captcha_solver import TwoCaptchaSolver


@pytest.mark.skip(reason="Requires 2Captcha API key")
def test_twocaptcha_recaptcha():
    solver = TwoCaptchaSolver(api_key=os.environ["API_KEY"])
    result = solver.solve(
        {
            "sitekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
            "page_url": "https://www.google.com/recaptcha/api2/demo",
        }
    )
    assert result is not None
