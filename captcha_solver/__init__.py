from .solver import CaptchaSolver, TwoCaptchaSolver
from .playwright_solver import PlaywrightCaptchaSolver
from .exceptions import CaptchaError, CaptchaServiceError, CaptchaTimeoutError

__version__ = "0.1.0"
__all__ = [
    "CaptchaSolver",
    "TwoCaptchaSolver",
    "PlaywrightCaptchaSolver",
    "CaptchaServiceError",
    "CaptchaError",
    "CaptchaTimeoutError",
]
