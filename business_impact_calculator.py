"""
Business Impact Calculator for Security Market Strategy
Module 4: ROI and Revenue Projections
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict
import json

class BusinessImpactCalculator:
    """Calculate business impact and ROI for security market strategies"""
    
    def __init__(self):
        # Market data and assumptions
        self.market_data = {
            "total_market_size": 15.6e9,  # $15.6B global consumer security market
            "average_customer_value": 45,   # $45 annual subscription
            "customer_acquisition_cost": 25,  # $25 CAC
            "churn_rate": 0.15,  # 15% annual churn
        }
        
        # Strategic scenarios and their impacts
        self.scenarios = {
            "norton_recovery": {
                "description": "Norton reputation recovery strategy",
                "investment": 20e6,  # $20M investment
                "timeline_months": 12,
                "market_share_change": 2.5,  # Gain 2.5% market share
                "customer_retention_improvement": 0.25,  # 25% better retention
                "success_probability": 0.7
            },
            "mcafee_gdpr_fix": {
                "description": "McAfee GDPR compliance and privacy leadership",
                "investment": 15e6,  # $15M investment
                "timeline_months": 8,
                "market_share_change": 3.2,  # Gain 3.2% market share
                "fine_avoidance": 50e6,  # Avoid $50M GDPR fines
                "success_probability": 0.85
            },
            "bitdefender_linux": {
                "description": "Bitdefender Linux market expansion",
                "investment": 10e6,  # $10M investment
                "timeline_months": 18,
                "new_market_segment": 2.1,  # 2.1% of total market as new segment
                "success_probability": 0.6
            }
        }
    
    def calculate_revenue_impact(self, scenario_name: str) -> Dict:
        """Calculate revenue impact for a specific scenario"""
        scenario = self.scenarios[scenario_name]
        market_size = self.market_data["total_market_size"]
        customer_value = self.market_data["average_customer_value"]
        
        # Calculate potential customer base
        if "market_share_change" in scenario:
            market_share_gain = scenario["market_share_change"] / 100
            new_customers = (market_size * market_share_gain) / customer_value
            annual_revenue_increase = new_customers * customer_value
        elif "new_market_segment" in scenario:
            segment_size = scenario["new_market_segment"] / 100
            new_customers = (market_size * segment_size) / customer_value
            annual_revenue_increase = new_customers * customer_value
        else:
            annual_revenue_increase = 0
            new_customers = 0
        
        # Calculate ROI components
        investment = scenario["investment"]
        timeline_months = scenario["timeline_months"]
        
        # Additional benefits
        fine_avoidance = scenario.get("fine_avoidance", 0)
        retention_improvement = scenario.get("customer_retention_improvement", 0)
        
        # Calculate retention revenue impact
        if retention_improvement > 0:
            current_customers = (market_size * 12.8 / 100) / customer_value  # McAfee market share
            retained_revenue = current_customers * customer_value * retention_improvement
        else:
            retained_revenue = 0
        
        # Total financial impact
        total_revenue_impact = annual_revenue_increase + retained_revenue + fine_avoidance
        net_benefit = total_revenue_impact - investment
        roi_percentage = (net_benefit / investment) * 100 if investment > 0 else 0
        payback_months = (investment / (annual_revenue_increase / 12)) if annual_revenue_increase > 0 else timeline_months
        
        return {
            "scenario": scenario_name,
            "description": scenario["description"],
            "investment": investment,
            "timeline_months": timeline_months,
            "new_customers": int(new_customers),
            "annual_revenue_increase": annual_revenue_increase,
            "retained_revenue": retained_revenue,
            "fine_avoidance": fine_avoidance,
            "total_revenue_impact": total_revenue_impact,
            "net_benefit": net_benefit,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "success_probability": scenario["success_probability"]
        }
    
    def calculate_all_scenarios(self) -> Dict:
        """Calculate impact for all scenarios"""
        results = {}
        for scenario_name in self.scenarios.keys():
            results[scenario_name] = self.calculate_revenue_impact(scenario_name)
        return results
    
    def create_executive_summary(self, results: Dict) -> str:
        """Create executive summary of business impact"""
        total_investment = sum([r["investment"] for r in results.values()])
        total_revenue_impact = sum([r["total_revenue_impact"] for r in results.values()])
        
        summary = f"""
EXECUTIVE BUSINESS IMPACT SUMMARY
=================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

💰 FINANCIAL OVERVIEW
Total Investment Required: ${total_investment/1e6:.1f}M
Total Revenue Opportunity: ${total_revenue_impact/1e6:.1f}M
Net Benefit: ${(total_revenue_impact - total_investment)/1e6:.1f}M

🎯 STRATEGIC RECOMMENDATIONS
1. Prioritize McAfee GDPR compliance (highest ROI)
2. Execute Norton reputation recovery in parallel
3. Develop Bitdefender Linux expansion as growth driver
"""
        return summary

if __name__ == "__main__":
    calculator = BusinessImpactCalculator()
    results = calculator.calculate_all_scenarios()
    
    print("📊 BUSINESS IMPACT CALCULATOR")
    print("=" * 50)
    
    for scenario_name, result in results.items():
        print(f"\n🎯 {result['description'].upper()}")
        print(f"Investment: ${result['investment']/1e6:.1f}M")
        print(f"Revenue Impact: ${result['total_revenue_impact']/1e6:.1f}M")
        print(f"ROI: {result['roi_percentage']:.1f}%")
    
    summary = calculator.create_executive_summary(results)
    print(summary)