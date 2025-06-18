"""
Data Collection Manager - Coordinates all scrapers and manages data collection workflow.
"""
import os
import yaml
import pandas as pd
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging
from .playstore_scraper import PlayStoreScraper
from .reddit_scraper import RedditScraper
from .amazon_scraper import AmazonScraper
from .appstore_scraper import AppStoreScraper

class DataCollectionManager:
    """Manages data collection from multiple sources"""
    
    def __init__(self, config_path: str = None):
        # Setup logger first
        self.logger = self._setup_logger()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize scrapers with config values
        self.scrapers = self._initialize_scrapers()
        
        # Create data directories if they don't exist
        self.raw_data_dir = "data/raw"
        self.processed_data_dir = "data/processed"
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            # Try multiple possible paths
            possible_paths = [
                "config.yaml",
                "../config.yaml", 
                "../../config.yaml",
                os.path.join(os.path.dirname(__file__), "../../config.yaml")
            ]
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                    self.logger.info(f"Loaded config from {config_path}")
                    return config
            except Exception as e:
                self.logger.warning(f"Error loading config from {config_path}: {e}")
        
        self.logger.warning(f"Config file not found, using defaults")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'data_collection': {
                'target_companies': ['McAfee', 'Norton', 'Kaspersky', 'Bitdefender', 'Avast'],
                'max_reviews_per_product': 100,
                'sources': {
                    'app_stores': ['Google Play Store'],
                    'forums': ['Reddit']
                }
            }
        }
    
    def _setup_logger(self):
        """Set up logging"""
        logger = logging.getLogger('DataCollectionManager')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _initialize_scrapers(self) -> Dict:
        """Initialize all available scrapers with config values"""
        # Get scraper config
        scraper_config = self.config.get('scrapers', {})
        
        # Initialize scrapers with config values
        playstore = PlayStoreScraper(delay=scraper_config.get('playstore_delay', 2.0))
        playstore.max_retries = scraper_config.get('max_retries', 3)
        playstore.timeout_seconds = scraper_config.get('timeout_seconds', 15)
        
        reddit = RedditScraper(delay=scraper_config.get('reddit_delay', 1.5))
        reddit.max_retries = scraper_config.get('max_retries', 3)
        reddit.timeout_seconds = scraper_config.get('timeout_seconds', 15)
        
        amazon = AmazonScraper(delay=scraper_config.get('amazon_delay', 2.5))
        amazon.max_retries = scraper_config.get('max_retries', 3)
        amazon.timeout_seconds = scraper_config.get('timeout_seconds', 15)
        
        appstore = AppStoreScraper(delay=scraper_config.get('appstore_delay', 1.5))
        appstore.max_retries = scraper_config.get('max_retries', 3)
        appstore.timeout_seconds = scraper_config.get('timeout_seconds', 15)
        
        return {
            'playstore': playstore,
            'reddit': reddit,
            'amazon': amazon,
            'appstore': appstore
        }
    
    def collect_all_data(self, companies: List[str] = None, max_reviews_per_source: int = None) -> Dict:
        """Collect data from all sources for specified companies"""
        if companies is None:
            companies = self.config['data_collection']['target_companies']
        
        if max_reviews_per_source is None:
            max_reviews_per_source = self.config['data_collection']['max_reviews_per_product']
        
        min_reviews = self.config['data_collection'].get('min_reviews_per_product', 5)
        
        all_data = {
            'companies': companies,
            'collection_date': datetime.now().isoformat(),
            'sources': {},
            'config_used': {
                'max_reviews_per_source': max_reviews_per_source,
                'min_reviews_per_product': min_reviews,
                'total_companies': len(companies)
            }
        }
        
        self.logger.info(f"Starting comprehensive data collection for {len(companies)} companies: {companies}")
        
        for source_name, scraper in self.scrapers.items():
            self.logger.info(f"Collecting data from {source_name} for ALL companies")
            source_data = self._collect_from_source(scraper, companies, max_reviews_per_source, min_reviews)
            all_data['sources'][source_name] = source_data
            
            # Save individual source data
            self._save_source_data(source_data, source_name)
        
        # Combine and save all data
        combined_data = self._combine_all_data(all_data)
        self._save_combined_data(combined_data)
        
        # Generate comprehensive summary
        summary = self._generate_collection_summary(all_data)
        all_data['summary'] = summary
        
        return all_data
    
    def _collect_from_source(self, scraper, companies: List[str], max_reviews: int, min_reviews: int = 5) -> Dict:
        """Collect data from a single source for ALL companies"""
        source_data = {
            'reviews': [],
            'product_info': [],
            'collection_stats': {},
            'companies_processed': [],
            'companies_failed': []
        }
        
        for company in companies:
            self.logger.info(f"Processing {company} from {scraper.__class__.__name__}")
            
            try:
                # Get product information
                product_info = scraper.get_product_info(company)
                if product_info:
                    source_data['product_info'].append(product_info)
                
                # Get reviews
                reviews = scraper.scrape_reviews(company, max_reviews)
                
                if len(reviews) >= min_reviews:
                    source_data['reviews'].extend(reviews)
                    source_data['companies_processed'].append(company)
                    self.logger.info(f"✅ {company}: Collected {len(reviews)} reviews (meets minimum {min_reviews})")
                else:
                    self.logger.warning(f"⚠️ {company}: Only {len(reviews)} reviews (below minimum {min_reviews})")
                    if reviews:  # Still add them if we got some
                        source_data['reviews'].extend(reviews)
                        source_data['companies_processed'].append(company)
                
                source_data['collection_stats'][company] = {
                    'reviews_collected': len(reviews),
                    'has_product_info': bool(product_info),
                    'meets_minimum': len(reviews) >= min_reviews,
                    'status': 'success'
                }
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting data for {company}: {e}")
                source_data['companies_failed'].append(company)
                source_data['collection_stats'][company] = {
                    'reviews_collected': 0,
                    'has_product_info': False,
                    'meets_minimum': False,
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Log final stats for this source
        total_reviews = len(source_data['reviews'])
        successful_companies = len(source_data['companies_processed'])
        self.logger.info(f"📊 {scraper.__class__.__name__} Summary: {total_reviews} reviews from {successful_companies}/{len(companies)} companies")
        
        return source_data
    
    def _save_source_data(self, source_data: Dict, source_name: str):
        """Save data from a single source in both JSON and CSV formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save reviews in JSON format (primary - handles newlines properly)
        if source_data['reviews']:
            reviews_json_file = f"{self.raw_data_dir}/{source_name}_reviews_{timestamp}.json"
            with open(reviews_json_file, 'w', encoding='utf-8') as f:
                json.dump(source_data['reviews'], f, indent=2, ensure_ascii=False)
            self.logger.info(f"📄 Saved {len(source_data['reviews'])} reviews to {reviews_json_file}")
            
            # Also save CSV for compatibility (with escaped newlines)
            reviews_df = pd.DataFrame(source_data['reviews'])
            reviews_csv_file = f"{self.raw_data_dir}/{source_name}_reviews_{timestamp}.csv"
            reviews_df.to_csv(reviews_csv_file, index=False, encoding='utf-8', quoting=1)  # Quote all fields
            self.logger.info(f"📊 Saved CSV backup to {reviews_csv_file}")
        
        # Save product info in JSON format
        if source_data['product_info']:
            info_json_file = f"{self.raw_data_dir}/{source_name}_product_info_{timestamp}.json"
            with open(info_json_file, 'w', encoding='utf-8') as f:
                json.dump(source_data['product_info'], f, indent=2, ensure_ascii=False)
            self.logger.info(f"📄 Saved product info to {info_json_file}")
            
            # CSV backup
            info_df = pd.DataFrame(source_data['product_info'])
            info_csv_file = f"{self.raw_data_dir}/{source_name}_product_info_{timestamp}.csv"
            info_df.to_csv(info_csv_file, index=False, encoding='utf-8', quoting=1)
            self.logger.info(f"📊 Saved product info CSV to {info_csv_file}")
    
    def _combine_all_data(self, all_data: Dict) -> pd.DataFrame:
        """Combine data from all sources into a single DataFrame"""
        all_reviews = []
        
        for source_name, source_data in all_data['sources'].items():
            for review in source_data['reviews']:
                review['collection_source'] = source_name
                all_reviews.append(review)
        
        if all_reviews:
            return pd.DataFrame(all_reviews)
        else:
            return pd.DataFrame()
    
    def _save_combined_data(self, combined_df: pd.DataFrame):
        """Save combined data from all sources in JSON and CSV formats"""
        if combined_df.empty:
            self.logger.warning("⚠️ No data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON (primary format)
        combined_json_file = f"{self.raw_data_dir}/combined_reviews_{timestamp}.json"
        combined_dict = combined_df.to_dict('records')
        with open(combined_json_file, 'w', encoding='utf-8') as f:
            json.dump(combined_dict, f, indent=2, ensure_ascii=False)
        self.logger.info(f"🎯 Saved {len(combined_df)} total reviews to {combined_json_file}")
        
        # Save as CSV (backup)
        combined_csv_file = f"{self.raw_data_dir}/combined_reviews_{timestamp}.csv"
        combined_df.to_csv(combined_csv_file, index=False, encoding='utf-8', quoting=1)
        self.logger.info(f"📊 Saved CSV backup to {combined_csv_file}")
        
        # Save collection metadata
        metadata = {
            'collection_timestamp': timestamp,
            'total_reviews': len(combined_df),
            'sources': combined_df['collection_source'].value_counts().to_dict() if 'collection_source' in combined_df.columns else {},
            'companies': combined_df['product_name'].value_counts().to_dict() if 'product_name' in combined_df.columns else {},
            'date_range': {
                'earliest': combined_df['date'].min() if 'date' in combined_df.columns and not combined_df['date'].isna().all() else None,
                'latest': combined_df['date'].max() if 'date' in combined_df.columns and not combined_df['date'].isna().all() else None
            }
        }
        
        metadata_file = f"{self.raw_data_dir}/collection_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)  # default=str handles datetime objects
        self.logger.info(f"📋 Saved collection metadata to {metadata_file}")
    
    def get_collection_summary(self) -> Dict:
        """Get summary of collected data"""
        summary = {
            'total_files': 0,
            'total_reviews': 0,
            'sources': {},
            'companies': set(),
            'date_range': {'earliest': None, 'latest': None}
        }
        
        # Scan raw data directory
        for filename in os.listdir(self.raw_data_dir):
            if filename.endswith('.csv') and 'reviews' in filename:
                summary['total_files'] += 1
                
                try:
                    df = pd.read_csv(f"{self.raw_data_dir}/{filename}")
                    summary['total_reviews'] += len(df)
                    
                    # Extract source from filename
                    source = filename.split('_')[0]
                    if source not in summary['sources']:
                        summary['sources'][source] = 0
                    summary['sources'][source] += len(df)
                    
                    # Add companies
                    if 'product_name' in df.columns:
                        summary['companies'].update(df['product_name'].unique())
                    
                except Exception as e:
                    self.logger.warning(f"Error reading {filename}: {e}")
        
        summary['companies'] = list(summary['companies'])
        return summary
    
    def _generate_collection_summary(self, all_data: Dict) -> Dict:
        """Generate comprehensive collection summary for all companies"""
        summary = {
            'total_companies_targeted': len(all_data['companies']),
            'companies_with_data': set(),
            'companies_missing_data': [],
            'source_performance': {},
            'total_reviews_by_company': {},
            'recommendations': []
        }
        
        # Analyze each source
        for source_name, source_data in all_data['sources'].items():
            stats = source_data.get('collection_stats', {})
            companies_processed = source_data.get('companies_processed', [])
            
            summary['source_performance'][source_name] = {
                'companies_processed': len(companies_processed),
                'total_reviews': len(source_data.get('reviews', [])),
                'success_rate': len(companies_processed) / len(all_data['companies']) * 100,
                'companies_successful': companies_processed
            }
            
            # Track companies with data
            summary['companies_with_data'].update(companies_processed)
        
        # Calculate per-company totals
        for company in all_data['companies']:
            total_reviews = 0
            for source_data in all_data['sources'].values():
                for review in source_data.get('reviews', []):
                    if review.get('product_name') == company:
                        total_reviews += 1
            
            summary['total_reviews_by_company'][company] = total_reviews
            
            if total_reviews == 0:
                summary['companies_missing_data'].append(company)
        
        # Generate recommendations
        if summary['companies_missing_data']:
            summary['recommendations'].append(f"No data collected for: {', '.join(summary['companies_missing_data'])}")
        
        best_source = max(summary['source_performance'].items(), 
                         key=lambda x: x[1]['total_reviews'])
        summary['recommendations'].append(f"Best performing source: {best_source[0]} ({best_source[1]['total_reviews']} reviews)")
        
        # Convert set to list for JSON serialization
        summary['companies_with_data'] = list(summary['companies_with_data'])
        
        return summary
    
    def test_scrapers(self, test_company: str = "McAfee") -> Dict:
        """Test all scrapers with a single company"""
        test_results = {}
        
        for source_name, scraper in self.scrapers.items():
            self.logger.info(f"Testing {source_name} scraper")
            
            try:
                # Test product info
                product_info = scraper.get_product_info(test_company)
                
                # Test reviews (limited to 5 for testing)
                reviews = scraper.scrape_reviews(test_company, max_reviews=5)
                
                test_results[source_name] = {
                    'status': 'success',
                    'product_info_found': bool(product_info),
                    'reviews_collected': len(reviews),
                    'sample_review': reviews[0] if reviews else None
                }
                
                self.logger.info(f"{source_name} test completed: {len(reviews)} reviews")
                
            except Exception as e:
                test_results[source_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                self.logger.error(f"{source_name} test failed: {e}")
        
        return test_results

# Utility functions for quick data collection
def quick_collect(companies: List[str] = None, max_reviews: int = 50) -> Dict:
    """Quick data collection function"""
    manager = DataCollectionManager()
    
    if companies is None:
        companies = ["McAfee", "Norton", "Avast"]  # Smaller list for testing
    
    return manager.collect_all_data(companies, max_reviews)

def test_all_scrapers() -> Dict:
    """Test all scrapers quickly"""
    manager = DataCollectionManager()
    return manager.test_scrapers()
