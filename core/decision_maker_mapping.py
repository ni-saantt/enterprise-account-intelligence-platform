"""
Decision Maker Mapping Engine for Enterprise GTM Account Intelligence Platform.
Identifies and maps key personas based on company firmographics.
"""

from typing import Dict, Any, Tuple

def map_decision_makers(company: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Identifies likely primary and secondary decision makers, and provides the GTM rationale.
    
    Supported Personas:
        Founder, CEO, COO, Head HR, VP People, VP Operations, Talent Acquisition Lead
        
    Args:
        company: Dictionary containing company profile metadata:
            - Company Name
            - Industry
            - Funding Stage
            - Employee Count
            - Hiring Activity
            
    Returns:
        A tuple of (primary_contact, secondary_contact, justification_reason).
    """
    name = company.get("Company Name", "This company")
    industry = company.get("Industry", "SaaS")
    hiring = company.get("Hiring Activity", "None")
    stage = company.get("Funding Stage", "Bootstrapped")
    
    try:
        emp_count = int(company.get("Employee Count", 0))
    except (ValueError, TypeError):
        emp_count = 0
        
    primary = ""
    secondary = ""
    reason = ""
    
    if industry in ["HR Tech", "EdTech"]:
        if emp_count < 100:
            primary = "Founder"
            secondary = "Head HR"
            reason = f"At early-stage ({emp_count} emp), the Founder leads growth strategy. The Head HR manages operations for this {industry} account."
        else:
            primary = "VP People"
            secondary = "Talent Acquisition Lead"
            reason = f"Mid-to-large {industry} team. VP People drives HR software budgets, while TA Lead manages execution under active hiring."
            
    else:  # SaaS, FinTech, AI, Healthcare
        if emp_count < 50:
            primary = "Founder"
            secondary = "COO"
            reason = f"Early stage startup. Founder maps to core GTM, while the COO handles tools and expansion infrastructure."
        elif 50 <= emp_count <= 250:
            primary = "CEO"
            if hiring in ["High", "Medium"]:
                secondary = "Talent Acquisition Lead"
                reason = f"Growing company ({emp_count} emp). CEO evaluates strategic GTM partnerships, and TA Lead is active due to hiring waves."
            else:
                secondary = "VP Operations"
                reason = f"Sizable scaleup ({emp_count} emp). CEO aligns core business decisions; VP Operations coordinates process improvements."
        else:  # > 250 employees (Enterprise / Mid-Market)
            primary = "CEO"
            secondary = "COO"
            if hiring == "High":
                secondary = "VP Operations"
                reason = f"Large enterprise account. CEO sets the vision; VP Operations handles operational tool procurement to support hiring scale."
            else:
                reason = f"Established company. CEO aligns corporate strategy; COO leads resource planning and procurement for tech stacks."
                
    return primary, secondary, reason
