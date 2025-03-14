import undetected_chromedriver as uc
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class AdvancedProtectionHandler:
    def __init__(self, api_key=None):
        """
        Initialize protection handler with optional 2captcha API key
        """
        self.solver = TwoCaptcha(api_key) if api_key else None
        self.driver = None

    def init_browser(self, headless=True):
        """
        Initialize undetected-chromedriver for Cloudflare bypass
        """
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        
        self.driver = uc.Chrome(options=options)
        return self.driver

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
            print(f"Error solving CAPTCHA: {str(e)}")
            return None

    def handle_cloudflare(self, url, timeout=30):
        """
        Handle Cloudflare protection
        """
        if not self.driver:
            self.init_browser()
            
        self.driver.get(url)
        try:
            # Wait for Cloudflare challenge to be solved
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)  # Additional wait to ensure JavaScript execution
            return self.driver.page_source
        except Exception as e:
            print(f"Error bypassing Cloudflare: {str(e)}")
            return None

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
            
        # Execute JavaScript to submit the CAPTCHA response
        script = f"""
        document.getElementById('g-recaptcha-response').innerHTML = '{captcha_response}';
        """
        self.driver.execute_script(script)
        return self.driver.page_source

    def cleanup(self):
        """
        Clean up resources
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
