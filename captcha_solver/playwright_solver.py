from typing import Optional, Dict, Any

from playwright.sync_api import sync_playwright, Page
from playwright.async_api import async_playwright
from .solver import CaptchaSolver, TwoCaptchaSolver
from .exceptions import CaptchaError
from .logger import logger
from .settings import SETTINGS


class PlaywrightCaptchaSolver(CaptchaSolver):
    def __init__(self, api_key: str):
        super().__init__()
        self.two_captcha = TwoCaptchaSolver(api_key)

    def solve(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                return self._solve_with_page(page, captcha_data)
        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA with Playwright: {str(e)}", exc_info=True)
            raise CaptchaError(f"Failed to solve with Playwright: {str(e)}") from e

    async def solve_async(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                result = await self._solve_with_page_async(page, captcha_data)
                await browser.close()
                return result
        except Exception as e:
            logger.error(
                f"Failed to solve reCAPTCHA asynchronously with Playwright: {str(e)}", exc_info=True
            )
            raise CaptchaError(f"Failed to solve with Playwright: {str(e)}") from e

    def _solve_with_page(self, page: Page, captcha_data: Dict[str, Any]) -> str:
        try:
            page.goto(captcha_data["url"], timeout=SETTINGS["timeout"] * 1000)
        except Exception as e:
            logger.error(
                f"Failed to navigate to URL {captcha_data['url']}: {str(e)}", exc_info=True
            )
            raise CaptchaError(f"Navigation failed: {str(e)}") from e

        captcha_info = self._detect_captcha(page)
        if not captcha_info:
            logger.info(f"No reCAPTCHA detected on {captcha_data['url']}")
            return "no_captcha_detected"

        audio_button = page.query_selector('button[aria-label="Get an audio challenge"]')
        if audio_button:
            logger.info("Switching to audio challenge")
            try:
                audio_button.click()
                page.wait_for_timeout(2000)
            except Exception as e:
                logger.error(f"Failed to switch to audio challenge: {str(e)}", exc_info=True)
                raise CaptchaError(f"Audio switch failed: {str(e)}") from e

        captcha_data.update({"sitekey": captcha_info["sitekey"], "page_url": captcha_data["url"]})

        solution = self.two_captcha.solve(captcha_data)

        try:
            page.evaluate(
                """(solution) => {
                    document.querySelector('textarea[name="g-recaptcha-response"]').value = solution;
                }""",
                solution,
            )
        except Exception as e:
            logger.error(f"Failed to inject reCAPTCHA solution: {str(e)}", exc_info=True)
            raise CaptchaError(f"Solution injection failed: {str(e)}") from e

        return solution

    async def _solve_with_page_async(self, page, captcha_data: Dict[str, Any]) -> str:
        try:
            await page.goto(captcha_data["url"], timeout=SETTINGS["timeout"] * 1000)
        except Exception as e:
            logger.error(
                f"Failed to navigate to URL {captcha_data['url']} asynchronously: {str(e)}",
                exc_info=True,
            )
            raise CaptchaError(f"Navigation failed: {str(e)}") from e

        captcha_info = await self._detect_captcha_async(page)
        if not captcha_info:
            logger.info(f"No reCAPTCHA detected on {captcha_data['url']}")
            return "no_captcha_detected"

        audio_button = await page.query_selector('button[aria-label="Get an audio challenge"]')
        if audio_button:
            logger.info("Switching to audio challenge")
            try:
                await audio_button.click()
                await page.wait_for_timeout(2000)
            except Exception as e:
                logger.error(
                    f"Failed to switch to audio challenge asynchronously: {str(e)}", exc_info=True
                )
                raise CaptchaError(f"Audio switch failed: {str(e)}") from e

        captcha_data.update({"sitekey": captcha_info["sitekey"], "page_url": captcha_data["url"]})

        solution = await self.two_captcha.solve_async(captcha_data)

        try:
            await page.evaluate(
                """(solution) => {
                    document.querySelector('textarea[name="g-recaptcha-response"]').value = solution;
                }""",
                solution,
            )
        except Exception as e:
            logger.error(
                f"Failed to inject reCAPTCHA solution asynchronously: {str(e)}", exc_info=True
            )
            raise CaptchaError(f"Solution injection failed: {str(e)}") from e

        return solution

    def _detect_captcha(self, page: Page) -> Optional[Dict[str, str]]:
        recaptcha_script = page.query_selector('script[src*="recaptcha"]')
        if recaptcha_script:
            try:
                sitekey = page.evaluate(
                    """() => document.querySelector('.g-recaptcha')?.getAttribute('data-sitekey')"""
                )
                if sitekey:
                    return {"sitekey": sitekey}
            except Exception as e:
                logger.error(f"Failed to extract sitekey: {str(e)}", exc_info=True)
                raise CaptchaError(f"Sitekey extraction failed: {str(e)}") from e
        return None

    async def _detect_captcha_async(self, page) -> Optional[Dict[str, str]]:
        recaptcha_script = await page.query_selector('script[src*="recaptcha"]')
        if recaptcha_script:
            try:
                sitekey = await page.evaluate(
                    """() => document.querySelector('.g-recaptcha')?.getAttribute('data-sitekey')"""
                )
                if sitekey:
                    return {"sitekey": sitekey}
            except Exception as e:
                logger.error(f"Failed to extract sitekey asynchronously: {str(e)}", exc_info=True)
                raise CaptchaError(f"Sitekey extraction failed: {str(e)}") from e
        return None
