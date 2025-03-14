import random
import time
from typing import List, Optional
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime
from models import Product, ScrapingConfig

class Scraper:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    ]

    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None

    def _get_headers(self):
        return self.config.headers or {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def _init_selenium(self):
        if not self.driver:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument(f'user-agent={random.choice(self.USER_AGENTS)}')
            self.driver = webdriver.Chrome(options=options)

    def _cleanup_selenium(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scrape_product(self, url: str) -> Product:
        if self.config.use_selenium:
            self._init_selenium()
            self.driver.get(url)
            time.sleep(random.uniform(1, 3))  # Random delay to avoid detection
            html = self.driver.page_source
        else:
            response = requests.get(url, headers=self._get_headers(), 
                                 proxies={'http': self.config.proxy, 'https': self.config.proxy} if self.config.proxy else None)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        
        name = soup.select_one(self.config.selectors['name']).text.strip()
        price = float(soup.select_one(self.config.selectors['price']).text.strip().replace('$', '').replace(',', ''))
        description = soup.select_one(self.config.selectors['description']).text.strip()
        
        return Product(
            id=None,
            name=name,
            price=price,
            description=description,
            url=url,
            marketplace=self.config.url_pattern.split('/')[2],
            created_at=datetime.now()
        )

    def scrape_products(self, urls: List[str], progress_callback=None) -> List[Product]:
        products = []
        total = len(urls)
        
        try:
            for i, url in enumerate(urls, 1):
                try:
                    product = self.scrape_product(url)
                    products.append(product)
                    if progress_callback:
                        progress_callback(i / total * 100)
                    time.sleep(random.uniform(1, 3))  # Random delay between requests
                except Exception as e:
                    print(f"Error scraping {url}: {str(e)}")
        finally:
            self._cleanup_selenium()
            
        return products
