"""
Data collection module for Consumer Security Product Analysis.
"""
from .collection_manager import DataCollectionManager, quick_collect, test_all_scrapers
from .base_scraper import BaseScraper
from .playstore_scraper import PlayStoreScraper
from .reddit_scraper import RedditScraper
from .amazon_scraper import AmazonScraper
from .appstore_scraper import AppStoreScraper

__all__ = [
    'DataCollectionManager',
    'BaseScraper', 
    'PlayStoreScraper',
    'RedditScraper',
    'AmazonScraper',
    'AppStoreScraper',
    'quick_collect',
    'test_all_scrapers'
]
