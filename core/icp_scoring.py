"""
ICP Scoring Engine for Enterprise GTM Account Intelligence Platform.
Computes a weighted customer fit score based on firmographic parameters.
"""

from typing import Dict, Any
from utils.constants import DEFAULT_SUB_WEIGHTS, ICP_FACTOR_MAX_POINTS

def calculate_icp_score(
    company: Dict[str, Any],
    weights: Dict[str, int] = None,
    sub_weights: Dict[str, Dict[str, int]] = None
) -> int:
    """
    Calculates the Ideal Customer Profile (ICP) score (0-100) for a company profile.
    
    Args:
        company: Dictionary containing company profile metadata:
            - Industry
            - Funding Stage
            - Employee Count
            - Hiring Activity
            - Location
        weights: Dictionary of weight points allocated to each metric (must sum to 100).
        sub_weights: Points allocation map for options within each metric.
        
    Returns:
        An integer ICP score bounded between 0 and 100.
    """
    if weights is None:
        weights = ICP_FACTOR_MAX_POINTS
    if sub_weights is None:
        sub_weights = DEFAULT_SUB_WEIGHTS

    score = 0.0

    # 1. Industry Match Score (Max weights['industry'])
    industry = company.get("Industry", "Other")
    ind_points = sub_weights.get("industry", {}).get(industry, 5)
    # Scale points based on the max possible points allocated to industry in weights
    max_ind_points = ICP_FACTOR_MAX_POINTS.get("industry", 25)
    industry_contrib = (ind_points / max_ind_points) * weights.get("industry", 25)
    score += industry_contrib

    # 2. Funding Stage Match Score (Max weights['funding'])
    funding = company.get("Funding Stage", "Other")
    funding_points = sub_weights.get("funding", {}).get(funding, 5)
    max_fund_points = ICP_FACTOR_MAX_POINTS.get("funding", 25)
    funding_contrib = (funding_points / max_fund_points) * weights.get("funding", 25)
    score += funding_contrib

    # 3. Employee Count Match Score (Max weights['employee'])
    try:
        emp_count = int(company.get("Employee Count", 0))
    except (ValueError, TypeError):
        emp_count = 0

    emp_sub_weights = sub_weights.get("employee", {})
    if 50 <= emp_count <= 500:
        emp_points = emp_sub_weights.get("ideal", 20)
    elif 10 <= emp_count < 50 or 501 <= emp_count <= 1000:
        emp_points = emp_sub_weights.get("sub_ideal", 12)
    else:
        emp_points = emp_sub_weights.get("other", 5)

    max_emp_points = ICP_FACTOR_MAX_POINTS.get("employee", 20)
    employee_contrib = (emp_points / max_emp_points) * weights.get("employee", 20)
    score += employee_contrib

    # 4. Hiring Activity Match Score (Max weights['hiring'])
    hiring = company.get("Hiring Activity", "None")
    hiring_points = sub_weights.get("hiring", {}).get(hiring, 0)
    max_hiring_points = ICP_FACTOR_MAX_POINTS.get("hiring", 20)
    hiring_contrib = (hiring_points / max_hiring_points) * weights.get("hiring", 20)
    score += hiring_contrib

    # 5. Location Match Score (Max weights['location'])
    location = company.get("Location", "Other")
    loc_points = sub_weights.get("location", {}).get(location, 2)
    max_loc_points = ICP_FACTOR_MAX_POINTS.get("location", 10)
    location_contrib = (loc_points / max_loc_points) * weights.get("location", 10)
    score += location_contrib

    # Ensure result is integer bounded 0-100
    return min(100, max(0, int(round(score))))
