"""
AI Account Summary Engine for Enterprise GTM Account Intelligence Platform.
Generates concise, narrative account intelligence summaries.
"""

from typing import Dict, Any

def generate_account_summary(
    company: Dict[str, Any],
    icp_score: int,
    abm_tier: str,
    buying_signal_level: str,
    gtm_opportunity_score: int,
    gtm_opportunity_level: str,
    priority_level: str,
    primary_contact: str,
    secondary_contact: str
) -> str:
    """
    Generates a natural-language GTM intelligence brief for an account.
    
    Args:
        company: Dictionary of company attributes.
        icp_score: Calculated ICP Score.
        abm_tier: Assigned ABM Tier.
        buying_signal_level: Signal Level ("High", "Medium", "Low").
        gtm_opportunity_score: Calculated GTM Opportunity Score.
        gtm_opportunity_level: Opportunity Level (Exceptional, High, Moderate, Low).
        priority_level: Outreach Priority (High, Medium, Low).
        primary_contact: Primary executive contact role.
        secondary_contact: Secondary executive contact role.
        
    Returns:
        A string narrative summary.
    """
    name = company.get("Company Name", "This company")
    industry = company.get("Industry", "SaaS")
    stage = company.get("Funding Stage", "Bootstrapped")
    emp_count = company.get("Employee Count", 0)
    location = company.get("Location", "US")
    hiring = company.get("Hiring Activity", "None")
    funding = company.get("Recent Funding", "No")
    expansion = company.get("Expansion Status", "Stable")
    
    # Constructing narrative
    sentence1 = f"{name} is a {abm_tier} {industry} account located in {location} with strong ICP alignment (Score: {icp_score}/100)."
    
    # Growth metrics
    funding_phrase = "recently secured funding" if funding == "Yes" else "operates with a steady capital base"
    hiring_phrase = "actively hiring" if hiring in ["High", "Medium"] else "maintaining stable headcount"
    expansion_phrase = "recently expanded operations" if expansion == "Expanding" else "focusing on operational efficiency"
    
    sentence2 = f"At the {stage} stage with {emp_count} employees, the company {funding_phrase}, is {hiring_phrase}, and has {expansion_phrase}."
    
    sentence3 = f"Buying signals are evaluated as {buying_signal_level.upper()} with a GTM Opportunity Score of {gtm_opportunity_score}/100 ({gtm_opportunity_level})."
    
    sentence4 = f"Recommended outreach priority is **{priority_level.upper()}**. Suggested target personas for outreach sequences are the **{primary_contact}** (Primary Contact) and **{secondary_contact}** (Secondary Contact)."
    
    summary = f"{sentence1}\n\n{sentence2}\n\n{sentence3}\n\n{sentence4}"
    return summary
