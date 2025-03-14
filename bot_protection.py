import undetected_chromedriver as uc
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import platform
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedProtectionHandler:
    def __init__(self, api_key=None):
        """
        Initialize protection handler with optional 2captcha API key
        """
        self.solver = TwoCaptcha(api_key) if api_key else None
        self.driver = None
        self.chrome_binary = self._get_chrome_binary()

    def _get_chrome_binary(self):
        """
        Find Chrome/Chromium binary location based on the operating system
        """
        logger.info("Поиск браузера в системе...")

        if platform.system() == 'Windows':
            paths = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
            ]
        else:  # Linux/Unix
            paths = [
                '/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium',  # Путь в Replit
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable'
            ]

        for path in paths:
            if os.path.exists(path):
                logger.info(f"Найден браузер: {path}")
                return path

        error_msg = "Chrome/Chromium не найден. Пожалуйста, убедитесь, что браузер установлен."
        logger.error(error_msg)
        raise Exception(error_msg)

    def init_browser(self, headless=True):
        """
        Initialize undetected-chromedriver for Cloudflare bypass
        """
        try:
            logger.info(f"Инициализация браузера с binary_location: {self.chrome_binary}")

            options = uc.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.binary_location = self.chrome_binary

            self.driver = uc.Chrome(options=options)
            logger.info("Браузер успешно инициализирован")
            return self.driver

        except Exception as e:
            error_msg = f"Ошибка при инициализации браузера: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def solve_captcha(self, site_key, page_url):
        """
        Solve reCAPTCHA using 2captcha service
        """
        if not self.solver:
            raise ValueError("2captcha API key not provided")

        try:
            result = self.solver.recaptcha(
                sitekey=site_key,
                url=page_url
            )
            return result.get('code')
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            return None

    def handle_cloudflare(self, url, timeout=30):
        """
        Handle Cloudflare protection
        """
        if not self.driver:
            self.init_browser()

        try:
            self.driver.get(url)
            # Wait for Cloudflare challenge to be solved
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)  # Additional wait to ensure JavaScript execution
            return self.driver.page_source
        except Exception as e:
            error_msg = f"Ошибка при обходе защиты Cloudflare: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def handle_recaptcha(self, url, site_key):
        """
        Handle reCAPTCHA challenge
        """
        if not self.solver:
            raise ValueError("2captcha API key not provided")

        captcha_response = self.solve_captcha(site_key, url)
        if not captcha_response:
            return None

        if not self.driver:
            self.init_browser()

        try:
            # Execute JavaScript to submit the CAPTCHA response
            script = f"""
            document.getElementById('g-recaptcha-response').innerHTML = '{captcha_response}';
            """
            self.driver.execute_script(script)
            return self.driver.page_source
        except Exception as e:
            error_msg = f"Ошибка при решении капчи: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def cleanup(self):
        """
        Clean up resources
        """
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None