"""
Outreach Priority Engine for Enterprise GTM Account Intelligence Platform.
Prioritizes sales outreach and compiles data-driven target justifications.
"""

from typing import Dict, Any, Tuple, List

def calculate_outreach_priority(
    company: Dict[str, Any],
    icp_score: int,
    buying_signal_level: str,
    gtm_opportunity_score: int
) -> Tuple[str, str]:
    """
    Determines outreach priority level (High, Medium, Low) and generates B2B reasoning.
    
    Args:
        company: Dictionary containing company profile metadata.
        icp_score: Calculated ICP Score (0-100).
        buying_signal_level: Buying signal level ("High", "Medium", "Low").
        gtm_opportunity_score: Calculated combined GTM Opportunity Score (0-100).
        
    Returns:
        A tuple of (priority_level, reasoning_bullet_string).
    """
    hiring = company.get("Hiring Activity", "None")
    funding = company.get("Recent Funding", "No")
    expansion = company.get("Expansion Status", "Stable")
    
    # 1. Determine priority level
    if gtm_opportunity_score >= 75 and buying_signal_level in ["High", "Medium"]:
        priority = "High"
    elif gtm_opportunity_score >= 60 and buying_signal_level in ["High", "Medium"]:
        priority = "Medium"
    elif icp_score >= 80 and buying_signal_level == "Low":
        priority = "Medium"  # Tier 1 account, worth monitoring despite low signals
    else:
        priority = "Low"
        
    # 2. Build B2B reasoning dynamically
    reasons: List[str] = []
    
    if icp_score >= 80:
        reasons.append(f"Strong ICP alignment (ICP: {icp_score}/100)")
    elif icp_score >= 60:
        reasons.append("Moderate ICP alignment")
        
    if funding == "Yes":
        reasons.append("Recently funded indicating available budget")
        
    if hiring == "High":
        reasons.append("Hiring aggressively for open positions")
    elif hiring == "Medium":
        reasons.append("Moderate active hiring detected")
        
    if expansion == "Expanding":
        reasons.append("Expanding operations and/or team size")
        
    if gtm_opportunity_score >= 90:
        reasons.append("Exceptional overall GTM opportunity value")
        
    if not reasons:
        if priority == "Low":
            reason_str = "Limited buying signal velocity and low ICP alignment indicators."
        else:
            reason_str = "Steady operations with moderate ICP fit indicators."
    else:
        reason_str = ", ".join(reasons) + "."
        
    return priority, reason_str
