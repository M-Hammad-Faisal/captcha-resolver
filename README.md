# Captcha Solver

A Python library for solving reCAPTCHA v2 challenges using Playwright and the 2Captcha service. This package replicates
the functionality of the JavaScript/TypeScript [
`puppeteer-extra-plugin-recaptcha`](https://github.com/berstend/puppeteer-extra-plugin-recaptcha), adapted for Python
and Playwright. It automatically detects reCAPTCHA instances on a webpage, solves them (including both image and audio
challenges), and injects the solutions.

## Features

- **reCAPTCHA v2 Support**: Solves both image-based (e.g., tile selection) and audio-based challenges.
- **Automatic Detection**: Identifies reCAPTCHA instances using Playwright by scanning for reCAPTCHA scripts and
  `data-sitekey`.
- **2Captcha Integration**: Leverages the 2Captcha API for reliable CAPTCHA solving.
- **Audio Switching**: Switches to audio challenges when available, matching the Puppeteer plugin’s behavior.
- **Synchronous and Asynchronous**: Offers both `solve()` (sync) and `solve_async()` (async) methods.
- **Error Logging**: Logs errors and key events using Python’s `logging` module for debugging and transparency.

## Prerequisites

- Python 3.8 or higher
- A [2Captcha API key](https://2captcha.com/) (sign up to get one)

## Installation

Install the package from PyPI:

```bash
pip install captcha-solver
```

Install Playwright browsers (required for runtime):

```bash
playwright install
```

## Usage

### Basic Example (Synchronous)

Solve a reCAPTCHA on a webpage:

```python
from captcha_solver import PlaywrightCaptchaSolver

solver = PlaywrightCaptchaSolver(api_key="your-2captcha-api-key")
result = solver.solve({'url': 'https://www.google.com/recaptcha/api2/demo'})
print(f"reCAPTCHA solved: {result}")
```

## Asynchronous Example

For async workflows:

```python
import asyncio
from captcha_solver import PlaywrightCaptchaSolver


async def main():
    solver = PlaywrightCaptchaSolver(api_key="your-2captcha-api-key")
    result = await solver.solve_async({'url': 'https://www.google.com/recaptcha/api2/demo'})
    print(f"reCAPTCHA solved: {result}")


asyncio.run(main())
```

## Logging

Errors and key events are logged using Python’s logging module. To see logs, configure a handler:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('captcha_solver')

solver = PlaywrightCaptchaSolver(api_key="your-2captcha-api-key")
result = solver.solve({'url': 'https://www.google.com/recaptcha/api2/demo'})
```

Example output:

```text
2025-03-05 12:00:00,123 - captcha_solver - INFO - Switching to audio challenge
2025-03-05 12:00:02,456 - captcha_solver - ERROR - Failed to inject reCAPTCHA solution: Element not found
```

## How It Works

- __Detection__: Navigates to the URL and checks for reCAPTCHA scripts (`script[src*="recaptcha"]`) and `data-sitekey`.
- __Audio Switching__: If an audio challenge option is available (e.g., `button[aria-label="Get an audio challenge"]`),
  it switches to audio mode.
- __Solving__: Submits the `sitekey` and URL to 2Captcha for solving.
- __Injection__: Injects the solution token into the `g-recaptcha-response` textarea.

## Development

To contribute or run tests:

- Clone the repository:
  ```bash
  git clone https://github.com/M-Hammad-Faisal/captcha-resolver.git
  cd captcha-solver
  ```
- Install dependencies with Poetry:

  ```bash
  poetry install
  poetry run playwright install
  ```

- Format and lint code:

  ```bash
  poetry run black .
  poetry run ruff check .
  ```

- Commit changes with conventional commits:

  ```bash
  poetry run cz commit
  ```

  Example: `feat: add new feature`, `fix: resolve bug`.

- Run tests:

  ```bash
  poetry run pytest tests/ -v
  ```

__Note__: Tests requiring the 2Captcha API are skipped by default. Set your API key and remove `@pytest.mark.skip` to
run them.

## Configuration

Settings are defined in settings.py and can be adjusted:

- `timeout`: Page load timeout (default: 10 seconds)
- `max_retries`: Retry attempts (default: 3)
- `retry_delay`: Delay between retries (default: 2 seconds)
- `api_endpoint`: 2Captcha API endpoint (default: `https://api.2captcha.com`)

## Limitations

- __reCAPTCHA v3__: Only solves visible challenges (v3 typically uses scoring).
- __Scope__: Limited to reCAPTCHA v2, matching puppeteer-extra-plugin-recaptcha.
- __Dependencies__: Requires a paid 2Captcha API key.

## Contributing

Submit issues or pull requests on GitHub:

- Fork the repository.
- Create a feature branch (`git checkout -b feature/your-feature`).
- Commit changes (`git commit -am 'Add your feature'`).
- Push to the branch (`git push origin feature/your-feature`).
- Create a pull request.

See PULL_REQUEST_TEMPLATE.md and ISSUE_TEMPLATE for guidelines

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Inspired by puppeteer-extra-plugin-recaptcha.
- Built with [Playwright](https://playwright.dev/) and [2Captcha](https://2captcha.com/).
