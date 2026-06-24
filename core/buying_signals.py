"""
Buying Signal Engine for Enterprise GTM Account Intelligence Platform.
Detects growth indicators and evaluates transaction likelihood.
"""

from typing import Dict, Any, Tuple
from utils.constants import BUYING_SIGNAL_POINTS

def detect_buying_signals(company: Dict[str, Any]) -> Tuple[int, str]:
    """
    Computes a buying signal score (0-100) and assigns a signal level (High, Medium, Low).
    
    Args:
        company: Dictionary containing company profile metadata:
            - Hiring Activity
            - Recent Funding
            - Expansion Status
            
    Returns:
        A tuple of (buying_signal_score, buying_signal_level).
    """
    score = 0
    
    # 1. Hiring Activity Points (Max 35)
    hiring = company.get("Hiring Activity", "None")
    hiring_pts = BUYING_SIGNAL_POINTS.get("hiring", {}).get(hiring, 0)
    score += hiring_pts
    
    # 2. Recent Funding Points (Max 35)
    funding = company.get("Recent Funding", "No")
    funding_pts = BUYING_SIGNAL_POINTS.get("funding", {}).get(funding, 0)
    score += funding_pts
    
    # 3. Expansion Status Points (Max 30)
    expansion = company.get("Expansion Status", "Stable")
    expansion_pts = BUYING_SIGNAL_POINTS.get("expansion", {}).get(expansion, 10)
    score += expansion_pts
    
    # Categorize signal strength
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"
        
    return score, level
