"""
Base scraper class for consistent data collection across different sources.
"""
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from typing import List, Dict, Optional
import logging
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, delay: float = 1.0, headless: bool = True):
        self.delay = delay
        self.headless = headless
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Set up logging for the scraper"""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def get_driver(self) -> webdriver.Chrome:
        """Create and return a Chrome WebDriver instance"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def safe_request(self, url: str, max_retries: int = None, timeout: int = None) -> Optional[requests.Response]:
        """Make a safe HTTP request with retries"""
        if max_retries is None:
            max_retries = getattr(self, 'max_retries', 3)
        if timeout is None:
            timeout = getattr(self, 'timeout_seconds', 10)
            
        for attempt in range(max_retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"All {max_retries} attempts failed for {url}")
                    return None
        return None
    
    @abstractmethod
    def scrape_reviews(self, product_name: str, max_reviews: int = 100) -> List[Dict]:
        """Abstract method to scrape reviews for a product"""
        pass
    
    @abstractmethod
    def get_product_info(self, product_name: str) -> Dict:
        """Abstract method to get basic product information"""
        pass
    
    def save_data(self, data: List[Dict], filename: str, format: str = 'csv'):
        """Save scraped data to file"""
        if not data:
            self.logger.warning("No data to save")
            return
            
        df = pd.DataFrame(data)
        
        if format.lower() == 'csv':
            df.to_csv(filename, index=False, encoding='utf-8')
        elif format.lower() == 'json':
            df.to_json(filename, orient='records', indent=2)
        
        self.logger.info(f"Saved {len(data)} records to {filename}")
    
    def validate_data(self, data: List[Dict]) -> List[Dict]:
        """Basic data validation and cleaning"""
        validated_data = []
        required_fields = ['review_text', 'rating', 'date', 'source']
        
        for item in data:
            # Check required fields
            if all(field in item and item[field] for field in required_fields):
                # Basic text cleaning
                item['review_text'] = item['review_text'].strip()
                if len(item['review_text']) > 10:  # Minimum length check
                    validated_data.append(item)
        
        self.logger.info(f"Validated {len(validated_data)} out of {len(data)} records")
        return validated_data
