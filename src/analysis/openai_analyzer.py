"""
OpenAI Analysis Module - Use OpenAI API for sentiment analysis and insights.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Optional
import logging
from datetime import datetime
import openai
from openai import OpenAI

class OpenAIAnalyzer:
    """OpenAI-powered analysis for consumer security reviews"""
    
    def __init__(self, config: Dict = None):
        self.logger = self._setup_logger()
        self.config = config or self._load_config()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = self.config.get('openai', {}).get('model', 'gpt-4o-mini')
        
    def _setup_logger(self):
        logger = logging.getLogger('OpenAIAnalyzer')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _load_config(self):
        """Load configuration from config.yaml"""
        try:
            import yaml
            with open('config.yaml', 'r') as f:
                return yaml.safe_load(f)
        except:
            return {'openai': {'model': 'gpt-4o-mini', 'max_tokens': 1500, 'temperature': 0.1}}
    
    def analyze_batch_sentiment(self, df: pd.DataFrame, batch_size: int = 10) -> pd.DataFrame:
        """Analyze sentiment using OpenAI API in batches"""
        self.logger.info(f"🤖 Starting OpenAI sentiment analysis for {len(df)} reviews...")
        
        results = []
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")
            
            for idx, row in batch.iterrows():
                try:
                    analysis = self._analyze_single_review(row['review_text_unified'], row['product_name'])
                    results.append({
                        'index': idx,
                        'ai_sentiment': analysis.get('sentiment', 'neutral'),
                        'ai_sentiment_score': analysis.get('score', 0.0),
                        'ai_key_points': analysis.get('key_points', []),
                        'ai_features': analysis.get('features', []),
                        'ai_summary': analysis.get('summary', '')
                    })
                except Exception as e:
                    self.logger.error(f"Error analyzing review {idx}: {e}")
                    results.append({
                        'index': idx,
                        'ai_sentiment': 'neutral',
                        'ai_sentiment_score': 0.0,
                        'ai_key_points': [],
                        'ai_features': [],
                        'ai_summary': 'Analysis failed'
                    })
        
        # Merge results back to dataframe
        results_df = pd.DataFrame(results).set_index('index')
        df = df.join(results_df, how='left')
        
        self.logger.info(f"✅ Completed OpenAI analysis for {len(df)} reviews")
        return df
    
    def _analyze_single_review(self, review_text: str, product_name: str) -> Dict:
        """Analyze a single review using OpenAI"""
        
        prompt = f"""Analyze this security software review for {product_name}:

"{review_text}"

Return ONLY a JSON object with:
{{
  "sentiment": "positive", "negative", or "neutral",
  "score": float between -1 and 1,
  "key_points": ["list of main points mentioned"],
  "features": ["security features discussed"],
  "summary": "brief 1-sentence summary"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure valid JSON
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(result_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return self._get_fallback_analysis(review_text)
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_analysis(review_text)
    
    def _get_fallback_analysis(self, review_text: str) -> Dict:
        """Fallback analysis if OpenAI fails"""
        # Simple keyword-based fallback
        positive_words = ['good', 'great', 'excellent', 'recommend', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'useless']
        
        text_lower = review_text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = 'positive'
            score = 0.6
        elif neg_count > pos_count:
            sentiment = 'negative'
            score = -0.6
        else:
            sentiment = 'neutral'
            score = 0.0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'key_points': ['Analysis unavailable'],
            'features': [],
            'summary': 'Fallback analysis used'
        }
    
    def generate_product_insights(self, df: pd.DataFrame) -> Dict:
        """Generate insights by product using OpenAI"""
        self.logger.info("🔍 Generating product insights...")
        
        insights = {}
        
        for product in df['product_name'].unique():
            product_reviews = df[df['product_name'] == product]
            
            # Sample reviews for analysis (max 20 for cost efficiency)
            sample_reviews = product_reviews.sample(min(20, len(product_reviews)))
            
            # Combine review texts
            combined_text = ' '.join(sample_reviews['review_text_unified'].astype(str))
            
            try:
                insight = self._get_product_insight(product, combined_text, len(product_reviews))
                insights[product] = insight
            except Exception as e:
                self.logger.error(f"Error generating insight for {product}: {e}")
                insights[product] = {
                    'summary': f'Analysis unavailable for {product}',
                    'strengths': [],
                    'weaknesses': [],
                    'recommendations': []
                }
        
        return insights
    
    def _get_product_insight(self, product: str, combined_text: str, total_reviews: int) -> Dict:
        """Get insights for a specific product"""
        
        prompt = f"""Analyze these {total_reviews} reviews for {product} security software:

{combined_text[:4000]}...

Return ONLY a JSON object with:
{{
  "summary": "2-sentence overall assessment",
  "strengths": ["top 3 strengths mentioned"],
  "weaknesses": ["top 3 weaknesses mentioned"],
  "recommendations": ["2-3 recommendations for improvement"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            self.logger.error(f"Error in product insight: {e}")
            return {
                'summary': f'Analysis unavailable for {product}',
                'strengths': [],
                'weaknesses': [],
                'recommendations': []
            }
    
    def save_analysis_results(self, df: pd.DataFrame, insights: Dict, output_dir: str = 'data/processed'):
        """Save analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save analyzed dataframe
        df_path = f"{output_dir}/analyzed_reviews_{timestamp}.json"
        df.to_json(df_path, orient='records', indent=2, force_ascii=False)
        
        # Save insights
        insights_path = f"{output_dir}/product_insights_{timestamp}.json"
        with open(insights_path, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Saved analysis results to {output_dir}")
        
        return df_path, insights_path

# Quick analysis function
def quick_openai_analysis(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Quick OpenAI analysis of reviews"""
    analyzer = OpenAIAnalyzer()
    
    # Analyze sentiment
    df_analyzed = analyzer.analyze_batch_sentiment(df)
    
    # Generate insights
    insights = analyzer.generate_product_insights(df_analyzed)
    
    # Save results
    analyzer.save_analysis_results(df_analyzed, insights)
    
    return df_analyzed, insights
