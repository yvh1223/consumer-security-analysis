"""
Data Validator Module - Validate and ensure data quality for analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

class DataValidator:
    """Simple data validation for processed reviews"""
    
    def __init__(self):
        self.logger = logging.getLogger('DataValidator')
    
    def validate_dataset(self, df: pd.DataFrame) -> Dict:
        """Validate dataset quality and completeness"""
        
        validation_report = {
            'total_records': len(df),
            'required_columns_present': True,
            'data_quality_issues': [],
            'summary': {}
        }
        
        # Check required columns
        required_cols = ['product_name', 'review_text_unified', 'data_source']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            validation_report['required_columns_present'] = False
            validation_report['data_quality_issues'].append(f"Missing columns: {missing_cols}")
        
        # Check data completeness
        if 'review_text_unified' in df.columns:
            empty_text = df['review_text_unified'].isna().sum() + (df['review_text_unified'] == '').sum()
            if empty_text > 0:
                validation_report['data_quality_issues'].append(f"{empty_text} records with empty text")
        
        # Summary statistics
        validation_report['summary'] = {
            'products': df['product_name'].nunique() if 'product_name' in df.columns else 0,
            'sources': df['data_source'].nunique() if 'data_source' in df.columns else 0,
            'avg_text_length': df['review_text_unified'].str.len().mean() if 'review_text_unified' in df.columns else 0
        }
        
        return validation_report
