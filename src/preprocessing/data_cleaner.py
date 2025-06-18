"""
Data Cleaner Module - Clean and standardize review data from multiple sources.
"""

import pandas as pd
import numpy as np
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import warnings

warnings.filterwarnings('ignore')

class DataCleaner:
    """Comprehensive data cleaning pipeline for multi-source consumer security reviews"""
    
    def __init__(self, config: Dict = None):
        self.logger = self._setup_logger()
        self.config = config or self._get_default_config()
        self.cleaning_stats = {}
        
    def _setup_logger(self):
        """Setup logging for data cleaning operations"""
        logger = logging.getLogger('DataCleaner')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _get_default_config(self) -> Dict:
        """Default configuration for data cleaning"""
        return {
            'min_review_length': 10,
            'max_review_length': 10000,
            'remove_duplicates': True,
            'standardize_ratings': True,
            'clean_text': True,
            'filter_languages': ['en'],
            'remove_spam': True,
            'normalize_dates': True
        }
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from JSON or CSV file"""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                raise ValueError("Unsupported file format. Use .json or .csv")
                
            self.logger.info(f"📄 Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error loading data: {e}")
            raise
    
    def clean_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete data cleaning pipeline"""
        self.logger.info("🧹 Starting comprehensive data cleaning pipeline...")
        
        original_count = len(df)
        self.cleaning_stats = {'original_count': original_count}
        
        # Step 1: Remove completely empty records
        df = self._remove_empty_records(df)
        
        # Step 2: Standardize column names and types
        df = self._standardize_columns(df)
        
        # Step 3: Clean and validate review text
        df = self._clean_review_text(df)
        
        # Step 4: Standardize ratings across sources
        df = self._standardize_ratings(df)
        
        # Step 5: Clean and normalize dates
        df = self._clean_dates(df)
        
        # Step 6: Remove duplicates
        if self.config['remove_duplicates']:            
            df = self._remove_duplicates(df)
        
        # Step 7: Filter by quality metrics
        df = self._filter_by_quality(df)
        
        # Step 8: Add derived features
        df = self._add_derived_features(df)
        
        # Step 9: Final validation
        df = self._final_validation(df)
        
        # Generate cleaning report
        self._generate_cleaning_report(original_count, len(df))
        
        return df
    
    def _remove_empty_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records missing critical information."""

        # Create mask: require (non-empty review_text OR non-empty title) AND non-null product_name
        mask = (
            ((df['review_text'].notna()) & (df['review_text'].str.len() > 0))
            | ((df['title'].notna()) & (df['title'].str.len() > 0))
        ) & df['product_name'].notna()

        # Apply filter
        df_clean = df[mask].copy()
        removed = len(df) - len(df_clean)

        if removed > 0:
            self.logger.info(f"🗑️  Removed {removed} empty records")

        self.cleaning_stats['empty_records_removed'] = removed
        return df_clean


    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and data types"""
        # Create unified review text from multiple sources
        df['review_text_unified'] = ''
        
        # Combine title and review text for Reddit posts
        for idx, row in df.iterrows():
            text_parts = []
            
            if pd.notna(row.get('title')) and str(row['title']).strip():
                text_parts.append(str(row['title']).strip())
            
            if pd.notna(row.get('review_text')) and str(row['review_text']).strip():
                text_parts.append(str(row['review_text']).strip())
            
            if pd.notna(row.get('selftext')) and str(row['selftext']).strip():
                selftext = str(row['selftext']).strip()
                if selftext not in text_parts:  # Avoid duplication
                    text_parts.append(selftext)
            
            df.loc[idx, 'review_text_unified'] = ' '.join(text_parts)
        
        # Standardize product names
        df['product_name'] = df['product_name'].str.strip().str.title()
        
        # Create unified rating (handle different rating systems)
        df['rating_unified'] = df['rating']
        
        # Standardize source information
        df['data_source'] = df['collection_source'].fillna('unknown')
        df['original_source'] = df['source'].fillna('unknown')
        
        # Convert dates to datetime
        if 'created_utc' in df.columns:
            df['created_utc'] = pd.to_numeric(df['created_utc'], errors='coerce')
            df['date_from_utc'] = pd.to_datetime(df['created_utc'], unit='s', errors='coerce')
        
        self.logger.info("✅ Standardized columns and data types")
        return df
    
    import re
import pandas as pd

def _clean_review_text(self, df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize review text."""
    if not self.config.get('clean_text', False):
        return df

    original_len = len(df)

    # Pre-compile regex patterns for performance
    ws_pattern = re.compile(r'\s+')
    url_pattern = re.compile(r'http[s]?://\S+')
    # Keep word chars, whitespace, and common punctuation
    nice_pattern = re.compile(r'[^\w\s\.,!?;:()\-"\'’]')

    def clean_text(text):
        if pd.isna(text):
            return ''
        text = str(text)
        text = ws_pattern.sub(' ', text)
        text = url_pattern.sub('', text)
        text = nice_pattern.sub(' ', text)
        # Collapse repeated punctuation
        text = re.sub(r'\.{3,}', '...', text)
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        # Trim whitespace
        return ' '.join(text.split()).strip()

    df['review_text_unified'] = df['review_text_unified'].apply(clean_text)

    # Filter by length constraints
    min_len = self.config.get('min_review_length', 0)
    max_len = self.config.get('max_review_length', float('inf'))
    length_mask = df['review_text_unified'].str.len().between(min_len, max_len)
    df_clean = df[length_mask].copy()

    removed = original_len - len(df_clean)
    if removed > 0:
        self.logger.info(f"📝 Removed {removed} records during text cleaning")
    self.cleaning_stats['text_length_filtered'] = removed

    return df_clean
    
    def _standardize_ratings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize ratings to 1-5 scale"""
        if not self.config['standardize_ratings']:
            return df
        
        def standardize_rating(rating, source):
            if pd.isna(rating):
                return np.nan
            
            rating = float(rating)
            
            # Reddit scores can be large - convert to 1-5 scale
            if source == 'reddit':
                if rating >= 100:
                    return 5
                elif rating >= 50:
                    return 4
                elif rating >= 10:
                    return 3
                elif rating >= 0:
                    return 2
                else:
                    return 1
            
            # App store ratings are already 1-5
            elif source in ['playstore', 'appstore']:
                return max(1, min(5, rating))
            
            # Default: assume 1-5 scale
            return max(1, min(5, rating))
        
        df['rating_standardized'] = df.apply(
            lambda row: standardize_rating(row['rating_unified'], row['data_source']), 
            axis=1
        )
        
        self.logger.info("⭐ Standardized ratings to 1-5 scale")
        return df
    
    def _clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize dates"""
        if not self.config['normalize_dates']:
            return df
        
        # Create unified date column
        df['date_unified'] = pd.NaT
        
        # Use date column first
        if 'date' in df.columns:
            df['date_unified'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Fill missing with UTC dates for Reddit
        mask = df['date_unified'].isna() & df['date_from_utc'].notna()
        df.loc[mask, 'date_unified'] = df.loc[mask, 'date_from_utc']
        
        # Add date features
        df['year'] = df['date_unified'].dt.year
        df['month'] = df['date_unified'].dt.month
        df['quarter'] = df['date_unified'].dt.quarter
        
        # Calculate days since collection
        if 'scraped_at' in df.columns:
            df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
            df['days_old'] = (df['scraped_at'] - df['date_unified']).dt.days
        
        self.logger.info("📅 Normalized dates and added temporal features")
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate reviews"""
        original_count = len(df)
        
        # Remove exact duplicates based on text and product
        df = df.drop_duplicates(subset=['product_name', 'review_text_unified'], keep='first')
        
        # Remove near-duplicates (same reviewer, same product, similar date)
        def identify_near_duplicates():
            duplicates = []
            
            for product in df['product_name'].unique():
                product_df = df[df['product_name'] == product]
                
                # Group by reviewer if available
                if 'reviewer_name' in product_df.columns:
                    for reviewer in product_df['reviewer_name'].dropna().unique():
                        reviewer_reviews = product_df[product_df['reviewer_name'] == reviewer]
                        
                        if len(reviewer_reviews) > 1:
                            # Keep only the most recent review
                            if 'date_unified' in reviewer_reviews.columns:
                                to_remove = reviewer_reviews.nsmallest(len(reviewer_reviews) - 1, 'date_unified')
                                duplicates.extend(to_remove.index.tolist())
            
            return duplicates
        
        near_dupe_indices = identify_near_duplicates()
        if near_dupe_indices:
            df = df.drop(near_dupe_indices)
        
        removed = original_count - len(df)
        if removed > 0:
            self.logger.info(f"🔄 Removed {removed} duplicate reviews")
        
        self.cleaning_stats['duplicates_removed'] = removed
        return df
    
    def _filter_by_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter reviews by quality metrics"""
        original_count = len(df)
        
        # Remove likely spam (very short, repetitive text)
        def is_spam(text):
            if pd.isna(text) or len(text) < 20:
                return True
            
            words = text.lower().split()
            if len(words) < 5:
                return True
            
            # Check for excessive repetition
            unique_words = len(set(words))
            if unique_words / len(words) < 0.3:  # Less than 30% unique words
                return True
            
            return False
        
        if self.config['remove_spam']:
            spam_mask = df['review_text_unified'].apply(is_spam)
            df = df[~spam_mask].copy()
        
        removed = original_count - len(df)
        if removed > 0:
            self.logger.info(f"🚫 Removed {removed} low-quality/spam reviews")
        
        self.cleaning_stats['quality_filtered'] = removed
        return df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for analysis"""
        # Text length features
        df['text_length'] = df['review_text_unified'].str.len()
        df['word_count'] = df['review_text_unified'].str.split().str.len()
        
        # Sentiment indicators (basic)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'useless', 'garbage']
        
        df['positive_words'] = df['review_text_unified'].str.lower().apply(
            lambda x: sum(1 for word in positive_words if word in str(x))
        )
        df['negative_words'] = df['review_text_unified'].str.lower().apply(
            lambda x: sum(1 for word in negative_words if word in str(x))
        )
        
        # Basic sentiment score
        df['sentiment_score'] = (df['positive_words'] - df['negative_words']) / (df['word_count'] + 1)
        
        # Source credibility features
        df['has_rating'] = df['rating_standardized'].notna()
        df['has_reviewer_name'] = df['reviewer_name'].notna() if 'reviewer_name' in df.columns else False
        
        # Engagement features for Reddit
        if 'score' in df.columns:
            df['reddit_engagement'] = df['score'].fillna(0) + df['num_comments'].fillna(0)
        
        self.logger.info("📊 Added derived features for analysis")
        return df
    
    def _final_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final validation and cleanup"""
        # Ensure required columns exist
        required_columns = ['product_name', 'review_text_unified', 'data_source']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Add unique ID
        df['clean_id'] = range(len(df))
        
        self.logger.info("✅ Completed final validation")
        return df
    
    def _generate_cleaning_report(self, original_count: int, final_count: int):
        """Generate comprehensive cleaning report"""
        total_removed = original_count - final_count
        retention_rate = (final_count / original_count) * 100 if original_count > 0 else 0
        
        report = {
            'original_count': original_count,
            'final_count': final_count,
            'total_removed': total_removed,
            'retention_rate': retention_rate,
            'cleaning_steps': self.cleaning_stats
        }
        
        self.logger.info(f"""
📈 DATA CLEANING REPORT 📈
========================
Original records: {original_count:,}
Final records: {final_count:,}
Total removed: {total_removed:,}
Retention rate: {retention_rate:.1f}%
========================
        """)
        
        return report
    
    def save_cleaned_data(self, df: pd.DataFrame, output_path: str, metadata: Dict = None):
        """Save cleaned data with metadata"""
        # Save main data
        if output_path.endswith('.json'):
            df.to_json(output_path, orient='records', indent=2, force_ascii=False)
        else:
            df.to_csv(output_path, index=False, encoding='utf-8')
        
        # Save metadata
        if metadata:
            metadata_path = output_path.replace('.json', '_metadata.json').replace('.csv', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
        
        self.logger.info(f"💾 Saved cleaned data to {output_path}")

# Quick utility functions
def quick_clean(file_path: str, output_path: str = None) -> pd.DataFrame:
    """Quick data cleaning with default settings"""
    cleaner = DataCleaner()
    df = cleaner.load_data(file_path)
    df_clean = cleaner.clean_pipeline(df)
    
    if output_path:
        cleaner.save_cleaned_data(df_clean, output_path)
    
    return df_clean

def get_data_quality_summary(df: pd.DataFrame) -> Dict:
    """Get data quality summary statistics"""
    return {
        'total_records': len(df),
        'products': df['product_name'].nunique() if 'product_name' in df.columns else 0,
        'sources': df['data_source'].nunique() if 'data_source' in df.columns else 0,
        'date_range': {
            'earliest': df['date_unified'].min() if 'date_unified' in df.columns else None,
            'latest': df['date_unified'].max() if 'date_unified' in df.columns else None
        },
        'text_stats': {
            'avg_length': df['text_length'].mean() if 'text_length' in df.columns else 0,
            'avg_words': df['word_count'].mean() if 'word_count' in df.columns else 0
        },
        'missing_data': df.isnull().sum().to_dict()
    }
