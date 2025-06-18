"""
Reddit scraper for security product discussions and reviews.
"""
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlencode

class RedditScraper(BaseScraper):
    """Scraper for Reddit posts and comments about security products"""
    
    def __init__(self, delay: float = 2.0, headless: bool = True):
        super().__init__(delay, headless)
        self.base_url = "https://www.reddit.com"
        # Add Reddit-specific headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_product_info(self, product_name: str) -> Dict:
        """Get basic information about product discussions on Reddit"""
        search_results = self.search_posts(product_name, limit=5)
        
        if not search_results:
            return {}
        
        return {
            'name': product_name,
            'source': 'Reddit',
            'total_posts_found': len(search_results),
            'scraped_at': datetime.now().isoformat(),
            'subreddits': list(set([post.get('subreddit', '') for post in search_results]))
        }
    
    def search_posts(self, query: str, subreddits: List[str] = None, limit: int = 100) -> List[Dict]:
        """Search for posts containing the query"""
        if subreddits is None:
            # Get subreddits from config if available, otherwise use defaults
            try:
                # Try to load config to get subreddits
                import yaml
                import os
                config_paths = ["config.yaml", "../config.yaml", "../../config.yaml"]
                subreddits = ['antivirus', 'cybersecurity', 'techsupport', 'security', 'privacy']  # fallback
                
                for config_path in config_paths:
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = yaml.safe_load(f)
                            reddit_subreddits = config.get('data_collection', {}).get('reddit_subreddits')
                            if reddit_subreddits:
                                subreddits = reddit_subreddits
                                self.logger.info(f"Using {len(subreddits)} subreddits from config: {subreddits}")
                                break
            except Exception as e:
                self.logger.debug(f"Could not load config, using defaults: {e}")
                subreddits = ['antivirus', 'cybersecurity', 'techsupport', 'security', 'privacy']
        
        all_posts = []
        
        for subreddit in subreddits:
            posts = self._search_subreddit(query, subreddit, limit // len(subreddits))
            all_posts.extend(posts)
            
            if len(all_posts) >= limit:
                break
        
        return all_posts[:limit]
    
    def _search_subreddit(self, query: str, subreddit: str, limit: int = 25) -> List[Dict]:
        """Search for posts in a specific subreddit"""
        search_url = f"{self.base_url}/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'sort': 'relevance',
            'limit': min(limit, 25),  # Reddit API limit
            't': 'year'  # Posts from the last year
        }
        
        full_url = f"{search_url}?{urlencode(params)}"
        response = self.safe_request(full_url)
        
        if not response:
            # Try alternative approach for restricted subreddits
            try:
                # Use hot posts instead of search for restricted subreddits
                hot_url = f"{self.base_url}/r/{subreddit}/hot.json"
                hot_params = {'limit': min(limit, 10)}
                hot_full_url = f"{hot_url}?{urlencode(hot_params)}"
                response = self.safe_request(hot_full_url)
                
                if response:
                    self.logger.info(f"Using hot posts from r/{subreddit} instead of search")
            except:
                pass
        
        if not response:
            self.logger.warning(f"Could not access r/{subreddit} - skipping")
            return []
        
        try:
            data = response.json()
            posts = []
            
            for post_data in data.get('data', {}).get('children', []):
                post = self._extract_post_data(post_data['data'], subreddit)
                if post:
                    # Filter for relevance if we used hot posts
                    if query.lower() in post.get('review_text', '').lower():
                        posts.append(post)
            
            self.logger.info(f"Found {len(posts)} relevant posts in r/{subreddit}")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error parsing Reddit data from r/{subreddit}: {e}")
            return []
    
    def _extract_post_data(self, post_data: Dict, subreddit: str) -> Dict:
        """Extract relevant data from a Reddit post"""
        try:
            # Basic post information
            post = {
                'id': post_data.get('id'),
                'title': post_data.get('title', ''),
                'selftext': post_data.get('selftext', ''),
                'score': post_data.get('score', 0),
                'num_comments': post_data.get('num_comments', 0),
                'created_utc': post_data.get('created_utc'),
                'author': post_data.get('author', 'deleted'),
                'subreddit': subreddit,
                'url': f"{self.base_url}{post_data.get('permalink', '')}",
                'source': 'Reddit',
                'scraped_at': datetime.now().isoformat()
            }
            
            # Convert timestamp to readable date
            if post['created_utc']:
                post['date'] = datetime.fromtimestamp(post['created_utc']).strftime('%Y-%m-%d')
            
            # Combine title and text for full content
            full_text = f"{post['title']} {post['selftext']}".strip()
            post['review_text'] = full_text
            
            # Assign a rating based on score (normalized to 1-5 scale)
            # This is approximate since Reddit doesn't have traditional ratings
            if post['score'] >= 50:
                post['rating'] = 5
            elif post['score'] >= 20:
                post['rating'] = 4
            elif post['score'] >= 5:
                post['rating'] = 3
            elif post['score'] >= 0:
                post['rating'] = 2
            else:
                post['rating'] = 1
            
            return post
            
        except Exception as e:
            self.logger.warning(f"Error extracting post data: {e}")
            return None
    
    def scrape_reviews(self, product_name: str, max_reviews: int = 100) -> List[Dict]:
        """Scrape posts/discussions about a security product"""
        # Search for posts mentioning the product
        posts = self.search_posts(product_name, limit=max_reviews)
        
        # Filter posts that actually discuss the product meaningfully
        filtered_posts = []
        product_keywords = product_name.lower().split()
        
        for post in posts:
            text_lower = post['review_text'].lower()
            
            # Check if product is mentioned meaningfully (not just in passing)
            keyword_count = sum(1 for keyword in product_keywords if keyword in text_lower)
            
            if keyword_count > 0 and len(post['review_text']) > 50:
                post['product_name'] = product_name
                filtered_posts.append(post)
        
        self.logger.info(f"Filtered to {len(filtered_posts)} relevant posts for {product_name}")
        
        return self.validate_data(filtered_posts)
    
    def get_comments(self, post_id: str, subreddit: str) -> List[Dict]:
        """Get comments for a specific post (optional for deeper analysis)"""
        comments_url = f"{self.base_url}/r/{subreddit}/comments/{post_id}.json"
        response = self.safe_request(comments_url)
        
        if not response:
            return []
        
        try:
            data = response.json()
            comments = []
            
            # Reddit returns post + comments, comments are in data[1]
            if len(data) > 1:
                comments_data = data[1].get('data', {}).get('children', [])
                
                for comment_data in comments_data:
                    comment = self._extract_comment_data(comment_data['data'])
                    if comment:
                        comments.append(comment)
            
            return comments
            
        except Exception as e:
            self.logger.error(f"Error getting comments for post {post_id}: {e}")
            return []
    
    def _extract_comment_data(self, comment_data: Dict) -> Dict:
        """Extract data from a Reddit comment"""
        try:
            if comment_data.get('body') in ['[deleted]', '[removed]', '']:
                return None
            
            return {
                'id': comment_data.get('id'),
                'body': comment_data.get('body', ''),
                'score': comment_data.get('score', 0),
                'created_utc': comment_data.get('created_utc'),
                'author': comment_data.get('author', 'deleted'),
                'date': datetime.fromtimestamp(comment_data.get('created_utc', 0)).strftime('%Y-%m-%d') if comment_data.get('created_utc') else None,
                'source': 'Reddit Comment',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting comment data: {e}")
            return None
