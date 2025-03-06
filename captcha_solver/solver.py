import time

import requests
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .exceptions import CaptchaError, CaptchaTimeoutError
from .logger import logger
from .settings import SETTINGS


class CaptchaSolver(ABC):
    def __init__(self):
        self.session = requests.Session()

    @abstractmethod
    def solve(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        pass

    @abstractmethod
    async def solve_async(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        pass

    def close(self):
        self.session.close()


class TwoCaptchaSolver(CaptchaSolver):
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = SETTINGS["api_endpoint"]

    def solve(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        try:
            if "sitekey" not in captcha_data or "page_url" not in captcha_data:
                logger.error("Missing required captcha_data fields: sitekey or page_url")
                raise ValueError("Must provide sitekey and page_url")
            return self._solve_recaptcha(captcha_data)
        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA: {str(e)}", exc_info=True)
            raise CaptchaError(f"Failed to solve with 2Captcha: {str(e)}") from e

    async def solve_async(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        try:
            if "sitekey" not in captcha_data or "page_url" not in captcha_data:
                logger.error("Missing required captcha_data fields: sitekey or page_url")
                raise ValueError("Must provide sitekey and page_url")
            return await self._solve_recaptcha_async(captcha_data)
        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA asynchronously: {str(e)}", exc_info=True)
            raise CaptchaError(f"Failed to solve with 2Captcha: {str(e)}") from e

    def _solve_recaptcha(self, captcha_data: Dict[str, Any]) -> str:
        payload = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": captcha_data["sitekey"],
            "pageurl": captcha_data["page_url"],
            "json": 1,
        }
        try:
            resp = self.session.post(f"{self.base_url}/in.php", data=payload)
            resp.raise_for_status()
            result = resp.json()
            if result["status"] != 1:
                logger.error(f"2Captcha submission failed: {result['request']}")
                raise CaptchaError(f"2Captcha submission failed: {result['request']}")
            captcha_id = result["request"]

            for _ in range(20):
                resp = self.session.get(
                    f"{self.base_url}/res.php?key={self.api_key}&action=get&id={captcha_id}&json=1"
                )
                result = resp.json()
                if result["status"] == 1:
                    return result["request"]
                if result["request"] == "CAPCHA_NOT_READY":
                    time.sleep(5)
                else:
                    logger.error(f"2Captcha polling error: {result['request']}")
                    raise CaptchaError(f"2Captcha error: {result['request']}")
            logger.error("2Captcha timeout after polling attempts")
            raise CaptchaTimeoutError("2Captcha timeout")
        except requests.RequestException as e:
            logger.error(f"HTTP request to 2Captcha failed: {str(e)}", exc_info=True)
            raise CaptchaError(f"Network error with 2Captcha: {str(e)}") from e

    async def _solve_recaptcha_async(self, captcha_data: Dict[str, Any]) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._solve_recaptcha, captcha_data)
