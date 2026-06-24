"""
ABM Tiering Engine for Enterprise GTM Account Intelligence Platform.
Classifies accounts into target groups (Tier 1, Tier 2, Tier 3).
"""

from utils.constants import ICP_TIER_RULES

def assign_abm_tier(icp_score: int) -> str:
    """
    Categorizes a company into an ABM Tier based on its ICP Score.
    
    Rules:
        ICP Score >= 80: Tier 1
        ICP Score 60-79: Tier 2
        ICP Score < 60: Tier 3
        
    Args:
        icp_score: The calculated ICP score (0-100).
        
    Returns:
        A string tier: "Tier 1", "Tier 2", or "Tier 3".
    """
    if icp_score >= ICP_TIER_RULES.get("Tier 1", 80):
        return "Tier 1"
    elif icp_score >= ICP_TIER_RULES.get("Tier 2", 60):
        return "Tier 2"
    else:
        return "Tier 3"
