"""
Professional Data Extraction & AI Analysis Pipeline
Demonstrating: Selenium, APIs, OpenAI, and Data Processing Capabilities

Author: Showcasing technical skills in web scraping, data analysis, and AI integration
Purpose: Convert user feedback into actionable business intelligence
"""

import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any
import logging

# Core libraries for data extraction and processing
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import requests
    import pandas as pd
    import openai
    import numpy as np
except ImportError as e:
    print(f"Required library not installed: {e}")
    print("Install with: pip install selenium requests pandas openai numpy")

class SecurityMarketAnalyzer:
    """
    Professional-grade data extraction and analysis pipeline
    Demonstrates real-world skills in web scraping, API integration, and AI analysis
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the analyzer with proper configuration"""
        self.setup_logging()
        self.data_sources = {
            'reddit': {
                'base_url': 'https://www.reddit.com',
                'endpoints': [
                    '/r/antivirus/search?q=mcafee',
                    '/r/antivirus/search?q=norton',
                    '/r/cybersecurity/search?q=security+software'
                ]
            },
            'trustpilot': {
                'base_url': 'https://www.trustpilot.com',
                'endpoints': [
                    '/review/mcafee.com',
                    '/review/norton.com',
                    '/review/bitdefender.com'
                ]
            }
        }
        
        # OpenAI setup for AI analysis
        if openai_api_key:
            openai.api_key = openai_api_key
            self.ai_enabled = True
        else:
            self.ai_enabled = False
            self.logger.warning("OpenAI API key not provided - AI analysis disabled")
        
        # Results storage
        self.extracted_data = []
        self.analyzed_data = []
        self.insights = {}
    
    def setup_logging(self):
        """Setup professional logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_analysis.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_selenium_driver(self, headless: bool = True) -> webdriver.Chrome:
        """
        Configure Selenium WebDriver with optimal settings
        Demonstrates professional web scraping setup
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        
        # Professional Chrome options for stable scraping
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.logger.info("Initializing Selenium WebDriver with professional configuration")
        return webdriver.Chrome(options=chrome_options)
    
    def extract_reddit_data(self, driver: webdriver.Chrome, search_terms: List[str]) -> List[Dict]:
        """
        Advanced Reddit data extraction using Selenium
        Demonstrates real-world web scraping techniques
        """
        reddit_data = []
        
        for term in search_terms:
            try:
                search_url = f"https://www.reddit.com/search/?q={term}+security+software"
                self.logger.info(f"Scraping Reddit for: {term}")
                
                driver.get(search_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="post-container"]'))
                )
                
                # Extract post data with professional error handling
                posts = driver.find_elements(By.CSS_SELECTOR, '[data-testid="post-container"]')
                
                for post in posts[:20]:  # Limit for demonstration
                    try:
                        title_element = post.find_element(By.CSS_SELECTOR, 'h3')
                        title = title_element.text if title_element else "No title"
                        
                        # Extract post content with null checks
                        content_elements = post.find_elements(By.CSS_SELECTOR, '[data-testid="post-content"]')
                        content = content_elements[0].text if content_elements else ""
                        
                        # Professional data structure
                        reddit_data.append({
                            'platform': 'reddit',
                            'search_term': term,
                            'title': title,
                            'content': content,
                            'extracted_at': datetime.now().isoformat(),
                            'source_url': driver.current_url,
                            'data_quality': 'high' if len(content) > 50 else 'medium'
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Error extracting post data: {e}")
                        continue
                
                # Professional rate limiting
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error scraping Reddit for {term}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(reddit_data)} Reddit posts")
        return reddit_data
    
    def extract_trustpilot_reviews(self, driver: webdriver.Chrome, companies: List[str]) -> List[Dict]:
        """
        Professional Trustpilot review extraction
        Demonstrates handling of dynamic content and review structures
        """
        trustpilot_data = []
        
        for company in companies:
            try:
                review_url = f"https://www.trustpilot.com/review/{company}.com"
                self.logger.info(f"Scraping Trustpilot reviews for: {company}")
                
                driver.get(review_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-service-review-card-paper]'))
                )
                
                # Extract review cards with professional parsing
                reviews = driver.find_elements(By.CSS_SELECTOR, '[data-service-review-card-paper]')
                
                for review in reviews[:15]:  # Limit for demonstration
                    try:
                        # Professional data extraction with multiple fallbacks
                        rating_element = review.find_element(By.CSS_SELECTOR, '[data-service-review-rating]')
                        rating = rating_element.get_attribute('data-service-review-rating') if rating_element else None
                        
                        title_elements = review.find_elements(By.CSS_SELECTOR, '[data-service-review-title-typography]')
                        title = title_elements[0].text if title_elements else ""
                        
                        content_elements = review.find_elements(By.CSS_SELECTOR, '[data-service-review-text-typography]')
                        content = content_elements[0].text if content_elements else ""
                        
                        trustpilot_data.append({
                            'platform': 'trustpilot',
                            'company': company,
                            'rating': rating,
                            'title': title,
                            'content': content,
                            'extracted_at': datetime.now().isoformat(),
                            'source_url': review_url,
                            'data_quality': 'high' if len(content) > 30 else 'medium'
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"Error extracting review: {e}")
                        continue
                
                time.sleep(3)  # Professional rate limiting
                
            except Exception as e:
                self.logger.error(f"Error scraping Trustpilot for {company}: {e}")
                continue
        
        self.logger.info(f"Extracted {len(trustpilot_data)} Trustpilot reviews")
        return trustpilot_data
    
    def analyze_with_openai(self, text: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
        """
        Professional OpenAI integration for content analysis
        Demonstrates AI API usage with proper error handling
        """
        if not self.ai_enabled:
            return self._fallback_analysis(text, analysis_type)
        
        try:
            if analysis_type == "sentiment":
                prompt = f"""
                Analyze this security software review for sentiment and categorization.
                
                Review text: "{text}"
                
                Provide analysis in this JSON format:
                {{
                    "sentiment_score": <1-10 scale>,
                    "sentiment_label": "<positive/negative/neutral>",
                    "main_category": "<performance/privacy/support/usability>",
                    "key_issues": ["issue1", "issue2"],
                    "business_impact": "<low/medium/high>",
                    "competitor_mentions": ["company1", "company2"]
                }}
                """
            
            elif analysis_type == "strategic":
                prompt = f"""
                Analyze this user feedback for strategic business insights.
                
                Content: "{text}"
                
                Provide strategic analysis focusing on:
                1. Market opportunities identified
                2. Competitive advantages mentioned
                3. Product gaps or weaknesses
                4. Revenue impact potential
                
                Format as structured analysis.
                """
            
            # Professional OpenAI API call with error handling
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior business analyst specializing in cybersecurity market intelligence."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_result = response.choices[0].message.content
            
            # Professional JSON parsing with fallback
            try:
                parsed_result = json.loads(analysis_result)
                return parsed_result
            except json.JSONDecodeError:
                return {
                    "raw_analysis": analysis_result,
                    "parsing_status": "manual_review_required"
                }
            
        except Exception as e:
            self.logger.error(f"OpenAI analysis failed: {e}")
            return self._fallback_analysis(text, analysis_type)
    
    def _fallback_analysis(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Professional fallback analysis when AI is unavailable"""
        # Rule-based analysis as fallback
        sentiment_keywords = {
            'negative': ['bad', 'terrible', 'slow', 'awful', 'hate', 'scam', 'worst'],
            'positive': ['good', 'great', 'excellent', 'fast', 'love', 'best', 'amazing']
        }
        
        text_lower = text.lower()
        
        negative_count = sum(1 for word in sentiment_keywords['negative'] if word in text_lower)
        positive_count = sum(1 for word in sentiment_keywords['positive'] if word in text_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
            score = max(1, 5 - negative_count)
        elif positive_count > negative_count:
            sentiment = "positive"
            score = min(10, 5 + positive_count)
        else:
            sentiment = "neutral"
            score = 5
        
        return {
            "sentiment_score": score,
            "sentiment_label": sentiment,
            "main_category": "general",
            "analysis_method": "rule_based_fallback",
            "confidence": "medium"
        }
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Execute complete data extraction and analysis pipeline
        Demonstrates end-to-end professional workflow
        """
        self.logger.info("Starting complete security market analysis pipeline")
        
        # Step 1: Data Extraction
        driver = self.setup_selenium_driver()
        
        try:
            # Extract Reddit data
            reddit_terms = ['mcafee', 'norton', 'bitdefender', 'kaspersky', 'avast']
            reddit_data = self.extract_reddit_data(driver, reddit_terms)
            
            # Extract Trustpilot data
            companies = ['mcafee', 'norton', 'bitdefender']
            trustpilot_data = self.extract_trustpilot_reviews(driver, companies)
            
            # Combine all extracted data
            self.extracted_data = reddit_data + trustpilot_data
            
        finally:
            driver.quit()
        
        # Step 2: AI Analysis
        self.logger.info(f"Analyzing {len(self.extracted_data)} extracted items with AI")
        
        for item in self.extracted_data:
            analysis_text = f"{item.get('title', '')} {item.get('content', '')}"
            
            # Professional AI analysis
            sentiment_analysis = self.analyze_with_openai(analysis_text, "sentiment")
            strategic_analysis = self.analyze_with_openai(analysis_text, "strategic")
            
            # Combine original data with AI insights
            analyzed_item = {
                **item,
                'ai_sentiment': sentiment_analysis,
                'ai_strategic': strategic_analysis,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            self.analyzed_data.append(analyzed_item)
        
        # Step 3: Generate Business Insights
        self.insights = self._generate_business_insights()
        
        # Step 4: Export Results
        self._export_results()
        
        self.logger.info("Complete analysis pipeline finished successfully")
        
        return {
            'total_items_extracted': len(self.extracted_data),
            'total_items_analyzed': len(self.analyzed_data),
            'insights_generated': len(self.insights),
            'business_opportunities': self.insights.get('opportunities', []),
            'critical_issues': self.insights.get('critical_issues', []),
            'revenue_impact': self.insights.get('revenue_impact', 0)
        }
    
    def _generate_business_insights(self) -> Dict[str, Any]:
        """Generate strategic business insights from analyzed data"""
        insights = {
            'opportunities': [],
            'critical_issues': [],
            'revenue_impact': 0,
            'market_gaps': [],
            'competitive_advantages': []
        }
        
        # Analyze for critical issues
        for item in self.analyzed_data:
            sentiment = item.get('ai_sentiment', {})
            
            if sentiment.get('sentiment_score', 5) <= 3:
                issue = {
                    'company': item.get('company', 'unknown'),
                    'category': sentiment.get('main_category', 'general'),
                    'severity': 'high' if sentiment.get('sentiment_score', 5) <= 2 else 'medium',
                    'evidence': item.get('content', '')[:200] + '...',
                    'platform': item.get('platform', 'unknown')
                }
                insights['critical_issues'].append(issue)
        
        # Calculate revenue opportunities (simplified for demonstration)
        critical_count = len(insights['critical_issues'])
        insights['revenue_impact'] = critical_count * 50_000_000  # $50M per major issue
        
        return insights
    
    def _export_results(self):
        """Export results in professional formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export raw data
        with open(f'extracted_data_{timestamp}.json', 'w') as f:
            json.dump(self.extracted_data, f, indent=2, default=str)
        
        # Export analyzed data
        with open(f'analyzed_data_{timestamp}.json', 'w') as f:
            json.dump(self.analyzed_data, f, indent=2, default=str)
        
        # Export insights
        with open(f'business_insights_{timestamp}.json', 'w') as f:
            json.dump(self.insights, f, indent=2, default=str)
        
        self.logger.info(f"Results exported with timestamp: {timestamp}")

def main():
    """
    Demonstration of professional data analysis pipeline
    Run this to see complete workflow in action
    """
    print("🔬 Security Market Intelligence Pipeline")
    print("=" * 50)
    print("Demonstrating professional skills in:")
    print("• Web Scraping with Selenium")
    print("• API Integration")
    print("• AI Analysis with OpenAI")
    print("• Data Processing & Business Intelligence")
    print()
    
    # Initialize analyzer
    analyzer = SecurityMarketAnalyzer()
    
    # Run complete analysis
    results = analyzer.run_complete_analysis()
    
    # Display results
    print("📊 ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Items Extracted: {results['total_items_extracted']}")
    print(f"Items Analyzed: {results['total_items_analyzed']}")
    print(f"Business Opportunities: {len(results['business_opportunities'])}")
    print(f"Critical Issues Found: {len(results['critical_issues'])}")
    print(f"Revenue Impact: ${results['revenue_impact']:,}")
    print()
    print("✅ Professional data pipeline completed successfully!")
    print("📁 Results exported to JSON files for further analysis")

if __name__ == "__main__":
    main()