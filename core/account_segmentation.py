"""
Account Segmentation Engine for Enterprise GTM Account Intelligence Platform.
Segments accounts into Enterprise, Mid-Market, SMB, or Startup.
"""

from typing import Dict, Any, Tuple

def segment_account(company: Dict[str, Any]) -> Tuple[str, str]:
    """
    Groups accounts by employee count (firmographics) and industry vertical.
    
    Firmographic Segments:
        - Enterprise: > 500 employees
        - Mid-Market: 101 - 500 employees
        - SMB: 11 - 100 employees
        - Startup: 1 - 10 employees
        
    Args:
        company: Dictionary containing company profile metadata:
            - Employee Count
            - Industry
            
    Returns:
        A tuple of (firmographic_segment, industry_segment).
    """
    try:
        emp_count = int(company.get("Employee Count", 0))
    except (ValueError, TypeError):
        emp_count = 0
        
    # Firmographic segment mapping
    if emp_count > 500:
        firmographic = "Enterprise"
    elif emp_count > 100:
        firmographic = "Mid-Market"
    elif emp_count > 10:
        firmographic = "SMB"
    else:
        firmographic = "Startup"
        
    # Industry mapping
    industry = company.get("Industry", "SaaS")
    
    return firmographic, industry
