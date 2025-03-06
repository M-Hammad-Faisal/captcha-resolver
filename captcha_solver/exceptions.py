class CaptchaError(Exception):
    """Base exception for all captcha-related errors"""

    pass


class CaptchaTimeoutError(CaptchaError):
    """Raised when captcha solving times out"""

    pass


class CaptchaServiceError(CaptchaError):
    """Raised when external captcha service fails"""

    pass


__all__ = ["CaptchaError", "CaptchaTimeoutError", "CaptchaServiceError"]
