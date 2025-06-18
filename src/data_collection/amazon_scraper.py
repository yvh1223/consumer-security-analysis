"""
Amazon reviews scraper for security software products.
"""
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlencode

class AmazonScraper(BaseScraper):
    """Scraper for Amazon product reviews"""
    
    def __init__(self, delay: float = 2.0, headless: bool = True):
        super().__init__(delay, headless)
        self.base_url = "https://www.amazon.com"
        
        # Update headers for Amazon
        self.session.headers.update({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_product_info(self, product_name: str) -> Dict:
        """Get basic product information from Amazon"""
        search_results = self.search_products(product_name, limit=3)
        
        if not search_results:
            return {}
        
        return {
            'name': product_name,
            'source': 'Amazon',
            'products_found': len(search_results),
            'scraped_at': datetime.now().isoformat(),
            'top_product': search_results[0] if search_results else None
        }
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for products on Amazon"""
        search_terms = [
            f"{query} antivirus software",
            f"{query} internet security",
            f"{query} security software"
        ]
        
        all_products = []
        
        for search_term in search_terms:
            products = self._search_amazon(search_term, limit // len(search_terms))
            all_products.extend(products)
            
            if len(all_products) >= limit:
                break
        
        return all_products[:limit]
    
    def _search_amazon(self, search_term: str, limit: int = 5) -> List[Dict]:
        """Search Amazon for specific term"""
        search_url = f"{self.base_url}/s"
        params = {
            'k': search_term,
            'ref': 'sr_pg_1'
        }
        
        full_url = f"{search_url}?{urlencode(params)}"
        response = self.safe_request(full_url)
        
        if not response:
            return []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:limit]:
                product = self._extract_product_info(container)
                if product and self._is_security_product(product, search_term):
                    products.append(product)
            
            self.logger.info(f"Found {len(products)} relevant products for '{search_term}'")
            return products
            
        except Exception as e:
            self.logger.error(f"Error parsing Amazon search results: {e}")
            return []
    
    def _extract_product_info(self, container) -> Dict:
        """Extract product information from search result container"""
        try:
            product = {}
            
            # Product title
            title_elem = container.find('h2', class_='s-size-mini')
            if title_elem:
                link_elem = title_elem.find('a')
                if link_elem:
                    product['title'] = link_elem.get_text(strip=True)
                    product['url'] = self.base_url + link_elem.get('href', '')
            
            # Price
            price_elem = container.find('span', class_='a-price-whole')
            if price_elem:
                product['price'] = price_elem.get_text(strip=True)
            
            # Rating
            rating_elem = container.find('span', class_='a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    product['rating'] = float(rating_match.group(1))
            
            # Number of reviews
            reviews_elem = container.find('a', {'href': re.compile(r'#customerReviews')})
            if reviews_elem:
                reviews_text = reviews_elem.get_text()
                reviews_match = re.search(r'([\d,]+)', reviews_text)
                if reviews_match:
                    product['review_count'] = int(reviews_match.group(1).replace(',', ''))
            
            product['source'] = 'Amazon'
            product['scraped_at'] = datetime.now().isoformat()
            
            return product if product.get('title') else None
            
        except Exception as e:
            self.logger.warning(f"Error extracting product info: {e}")
            return None
    
    def _is_security_product(self, product: Dict, search_term: str) -> bool:
        """Check if product is actually a security software product"""
        title = product.get('title', '').lower()
        
        # Must contain security-related terms
        security_terms = ['antivirus', 'security', 'protection', 'firewall', 'internet security']
        has_security = any(term in title for term in security_terms)
        
        # Should not be hardware unless it's security hardware
        hardware_terms = ['router', 'camera', 'device']
        is_hardware = any(term in title for term in hardware_terms)
        
        return has_security and not is_hardware
    
    def scrape_reviews(self, product_name: str, max_reviews: int = 100) -> List[Dict]:
        """Scrape reviews for a security product"""
        # For now, return mock data since Amazon has strict anti-bot measures
        # In a real implementation, you'd need more sophisticated techniques
        
        self.logger.info(f"Amazon scraper: Creating sample data for {product_name}")
        
        # Return sample/mock reviews to demonstrate the infrastructure
        mock_reviews = [
            {
                'product_name': product_name,
                'source': 'Amazon',
                'review_text': f"Great {product_name} antivirus software. Protects my computer well.",
                'rating': 4,
                'date': '2024-01-15',
                'reviewer_name': 'Customer123',
                'helpful_votes': 5,
                'scraped_at': datetime.now().isoformat()
            },
            {
                'product_name': product_name,
                'source': 'Amazon',
                'review_text': f"Had some issues with {product_name} slowing down my system.",
                'rating': 2,
                'date': '2024-02-20',
                'reviewer_name': 'TechUser456',
                'helpful_votes': 3,
                'scraped_at': datetime.now().isoformat()
            }
        ]
        
        # Take only the requested number
        result = mock_reviews[:min(max_reviews, len(mock_reviews))]
        self.logger.info(f"Generated {len(result)} sample Amazon reviews for {product_name}")
        
        return self.validate_data(result)
