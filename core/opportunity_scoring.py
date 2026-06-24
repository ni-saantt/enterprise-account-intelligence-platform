"""
GTM Opportunity Scoring Engine for Enterprise GTM Account Intelligence Platform.
Computes a unified scoring index by blending ICP, Buying Signal, and Market Trend factors.
"""

from typing import Dict, Any, Tuple
from utils.constants import OPPORTUNITY_TIER_RULES

def calculate_market_opportunity_score(company: Dict[str, Any]) -> int:
    """
    Computes a market opportunity score (0-100) based on industry trends,
    funding stage velocity, and location premium.
    """
    industry = company.get("Industry", "SaaS")
    funding = company.get("Funding Stage", "Bootstrapped")
    location = company.get("Location", "Other")
    
    # 1. Industry Premium (Max 100)
    industry_scores = {
        "AI": 100,
        "SaaS": 90,
        "FinTech": 85,
        "Healthcare": 80,
        "HR Tech": 70,
        "EdTech": 55
    }
    ind_score = industry_scores.get(industry, 50)
    
    # 2. Funding Stage Velocity (Max 100)
    funding_scores = {
        "IPO-bound": 100,
        "Series C": 100,
        "Series B": 95,
        "Series A": 85,
        "Growth": 80,
        "Seed": 60,
        "Bootrapped": 40,
        "Bootstrapped": 40
    }
    fund_score = funding_scores.get(funding, 50)
    
    # 3. Location Premium (Max 100)
    location_scores = {
        "US": 100,
        "UK": 95,
        "Canada": 95,
        "India": 90,
        "EU": 85,
        "APAC": 80,
        "Middle East": 65,
        "Latin America": 60
    }
    loc_score = location_scores.get(location, 50)
    
    # Combined formula
    market_score = (0.4 * ind_score) + (0.3 * fund_score) + (0.3 * loc_score)
    return int(round(market_score))


def calculate_opportunity_score(
    icp_score: int,
    buying_signal_score: int,
    company: Dict[str, Any]
) -> Tuple[int, int, str]:
    """
    Computes a unified GTM Opportunity Score (0-100) and opportunity category.
    
    Formula:
        40% ICP Score + 40% Buying Signal Score + 20% Market Opportunity Score
        
    Category thresholds:
        90+   = Exceptional Opportunity
        75-89 = High Opportunity
        60-74 = Moderate Opportunity
        < 60  = Low Opportunity
        
    Returns:
        A tuple of (market_opp_score, gtm_opportunity_score, gtm_opportunity_level).
    """
    market_score = calculate_market_opportunity_score(company)
    
    # GTM Opportunity Score formula
    gtm_score = (0.4 * icp_score) + (0.4 * buying_signal_score) + (0.2 * market_score)
    final_score = min(100, max(0, int(round(gtm_score))))
    
    # Categorization
    if final_score >= OPPORTUNITY_TIER_RULES.get("Exceptional Opportunity", 90):
        level = "Exceptional Opportunity"
    elif final_score >= OPPORTUNITY_TIER_RULES.get("High Opportunity", 75):
        level = "High Opportunity"
    elif final_score >= OPPORTUNITY_TIER_RULES.get("Moderate Opportunity", 60):
        level = "Moderate Opportunity"
    else:
        level = "Low Opportunity"
        
    return market_score, final_score, level
