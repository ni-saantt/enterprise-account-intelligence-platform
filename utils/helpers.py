"""
Helper utilities for Enterprise GTM Account Intelligence Platform.
Includes dataset generators, export wrappers, and HTML tag formatters.
"""

import os
import io
import random
import csv
import io
import random
from typing import Dict, List, Any
from utils.constants import INDUSTRIES, FUNDING_STAGES, LOCATIONS, HIRING_ACTIVITIES, EXPANSION_STATUSES

def generate_sample_data(filepath: str) -> None:
    """
    Generates a highly realistic, logically consistent dataset of 100 startup companies
    across target GTM segments and saves it to a CSV file.
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Realistic Indian/Global B2B and consumer tech brand names
    company_pool = {
        "AI": [
            "Yellow.ai", "Fractal Analytics", "Quantiphi", "Hevo Data", "Pixis AI",
            "Netradyne", "Haptik", "SigTuple", "Arya.ai", "Vernacular.ai",
            "Myelin Foundry", "Active.ai", "Niki.ai", "Crux Intelligence", 
            "Grep.ai", "Scribble Data", "Observe.ai"
        ],
        "SaaS": [
            "Freshworks", "Zoho", "Chargebee", "BrowserStack", "Postman", "Wingify", 
            "LeadSquared", "WebEngage", "Clevertap", "InVideo", "Exotel", "Amagi", 
            "Icertis", "Druva", "Zenoti", "Keka SaaS", "Facilio", "Darwinbox SaaS",
            "Whatfix", "HighRadius"
        ],
        "FinTech": [
            "Razorpay", "IDfy", "Signzy", "Jupiter Fin", "Fi Money", "Slice", 
            "Cred", "Groww", "INDmoney", "Zerodha", "Upstox", "CoinSwitch", 
            "Pine Labs", "BharatPe", "PhonePe", "Paytm", "M2P Fintech", "OneCard"
        ],
        "HR Tech": [
            "Darwinbox", "Keka", "AuthBridge", "SpringVerify", "GreytHR", "Disprz", 
            "Mercer Mettl", "ZingHR", "Leena AI", "Dockabl", "Belong.co", "HackerEarth",
            "Sense HR", "TurboHire", "Talent500", "Skillate"
        ],
        "Healthcare": [
            "Practo", "Pharmeasy", "Tata 1mg", "MediBuddy", "Cure.fit", "HealthifyMe", 
            "Pristyn Care", "Innovaccer", "Portea Medical", "Netmeds", "MedGenome", 
            "mfine", "Niramai", "Medikabazaar", "BeatO"
        ],
        "EdTech": [
            "Unacademy", "UpGrad", "Simplilearn", "Classplus", "Teachmint", 
            "PhysicsWallah", "Eruditus", "Lead School", "Vedantu", "Doubtnut", 
            "CueMath", "Lido Learning", "Adda247", "Toppr"
        ]
    }
    
    # Fallback pool in case we run out of unique names
    fallback_names = [f"AlphaTech {i}" for i in range(1, 50)]
    
    data: List[Dict[str, Any]] = []
    random.seed(42)  # Seed for deterministic yet realistic generation
    
    used_names = set()
    
    for industry, names in company_pool.items():
        for name in names:
            # Determine profile parameters logically based on stage
            stage = random.choice(FUNDING_STAGES)
            
            # Map size based on funding stage
            if stage == "Bootstrapped":
                emp_count = random.randint(5, 75)
                recent_funding = "No"
                hiring = random.choice(["Low", "None", "Medium"])
                expansion = random.choice(["Stable", "Contracting", "Expanding"])
            elif stage == "Seed":
                emp_count = random.randint(5, 30)
                recent_funding = random.choice(["Yes", "No"])
                hiring = random.choice(["Medium", "Low"])
                expansion = random.choice(["Stable", "Expanding"])
            elif stage in ["Series A", "Series B"]:
                emp_count = random.randint(30, 250)
                recent_funding = random.choice(["Yes", "No"])
                hiring = random.choice(["High", "Medium"])
                expansion = "Expanding" if hiring == "High" else random.choice(["Expanding", "Stable"])
            elif stage in ["Series C", "Growth"]:
                emp_count = random.randint(150, 750)
                recent_funding = random.choice(["Yes", "No"])
                hiring = random.choice(["High", "Medium"])
                expansion = "Expanding"
            else:  # IPO-bound
                emp_count = random.randint(500, 2500)
                recent_funding = random.choice(["Yes", "No"])
                hiring = random.choice(["High", "Medium", "Low"])
                expansion = random.choice(["Expanding", "Stable"])
                
            location = random.choice(LOCATIONS)
            
            used_names.add(name)
            data.append({
                "Company Name": name,
                "Industry": industry,
                "Funding Stage": stage,
                "Employee Count": emp_count,
                "Location": location,
                "Hiring Activity": hiring,
                "Recent Funding": recent_funding,
                "Expansion Status": expansion
            })
            
    # If we need exactly 100 rows, fill or truncate
    while len(data) < 100:
        name = fallback_names.pop(0)
        ind = random.choice(INDUSTRIES)
        stage = random.choice(FUNDING_STAGES)
        emp = random.randint(10, 800)
        hiring = random.choice(HIRING_ACTIVITIES)
        expansion = random.choice(EXPANSION_STATUSES)
        data.append({
            "Company Name": name,
            "Industry": ind,
            "Funding Stage": stage,
            "Employee Count": emp,
            "Location": random.choice(LOCATIONS),
            "Hiring Activity": hiring,
            "Recent Funding": random.choice(["Yes", "No"]),
            "Expansion Status": expansion
        })
        
    fields = ["Company Name", "Industry", "Funding Stage", "Employee Count", "Location", "Hiring Activity", "Recent Funding", "Expansion Status"]
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data[:100])


# UI Badge Helpers
def get_tier_badge(tier: str) -> str:
    """Returns CSS badge for ABM Tiers."""
    tier_class = "badge-tier3"
    if tier == "Tier 1":
        tier_class = "badge-tier1"
    elif tier == "Tier 2":
        tier_class = "badge-tier2"
    return f'<span class="saas-badge {tier_class}">{tier}</span>'


def get_priority_badge(priority: str) -> str:
    """Returns CSS badge for outreach priority."""
    p_class = "badge-low"
    if priority.upper() == "HIGH":
        p_class = "badge-high"
    elif priority.upper() == "MEDIUM":
        p_class = "badge-medium"
    return f'<span class="saas-badge {p_class}">{priority}</span>'


def get_opportunity_badge(level: str) -> str:
    """Returns CSS badge for GTM opportunity levels."""
    o_class = "badge-low-opp"
    if level == "Exceptional Opportunity":
        o_class = "badge-exceptional"
    elif level == "High Opportunity":
        o_class = "badge-high-opp"
    elif level == "Moderate Opportunity":
        o_class = "badge-mod-opp"
    return f'<span class="saas-badge {o_class}">{level}</span>'


def get_buying_signal_badge(level: str) -> str:
    """Returns CSS badge for buying signals."""
    b_class = "badge-low"
    if level.upper() == "HIGH":
        b_class = "badge-high"
    elif level.upper() == "MEDIUM":
        b_class = "badge-medium"
    return f'<span class="saas-badge {b_class}">{level}</span>'


def to_excel_bytes(df: Any) -> bytes:
    """Converts a pandas DataFrame into a bytes buffer formatted as an Excel spreadsheet."""
    import pandas as pd
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='GTM Account Intelligence')
    return output.getvalue()


def to_csv_bytes(df: Any) -> bytes:
    """Converts a pandas DataFrame into a bytes buffer formatted as CSV."""
    import pandas as pd
    return df.to_csv(index=False).encode('utf-8')


def clean_html(html_str: str) -> str:
    """Strips leading/trailing whitespace from each line of HTML strings to prevent code block escaping."""
    if not html_str:
        return ""
    return "\n".join(line.strip() for line in html_str.split("\n"))


def get_icp_score_breakdown(company: dict, weights: dict = None) -> dict:
    """Returns factor contributions for explainability of the ICP score."""
    from utils.constants import DEFAULT_SUB_WEIGHTS, ICP_FACTOR_MAX_POINTS
    if weights is None:
        weights = {"industry": 25, "funding": 25, "employee": 20, "hiring": 20, "location": 10}
        
    sub_weights = DEFAULT_SUB_WEIGHTS
    
    # 1. Industry
    industry = company.get("Industry", "Other")
    ind_points = sub_weights.get("industry", {}).get(industry, 5)
    max_ind_points = ICP_FACTOR_MAX_POINTS.get("industry", 25)
    industry_contrib = (ind_points / max_ind_points) * weights.get("industry", 25)
    
    # 2. Funding
    funding = company.get("Funding Stage", "Other")
    funding_points = sub_weights.get("funding", {}).get(funding, 5)
    max_fund_points = ICP_FACTOR_MAX_POINTS.get("funding", 25)
    funding_contrib = (funding_points / max_fund_points) * weights.get("funding", 25)
    
    # 3. Employee
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
    
    # 4. Hiring
    hiring = company.get("Hiring Activity", "None")
    hiring_points = sub_weights.get("hiring", {}).get(hiring, 0)
    max_hiring_points = ICP_FACTOR_MAX_POINTS.get("hiring", 20)
    hiring_contrib = (hiring_points / max_hiring_points) * weights.get("hiring", 20)
    
    # 5. Location
    location = company.get("Location", "Other")
    loc_points = sub_weights.get("location", {}).get(location, 2)
    max_loc_points = ICP_FACTOR_MAX_POINTS.get("location", 10)
    location_contrib = (loc_points / max_loc_points) * weights.get("location", 10)
    
    return {
        "Industry Match": round(industry_contrib, 1),
        "Funding Stage Match": round(funding_contrib, 1),
        "Employee Count Match": round(employee_contrib, 1),
        "Hiring Activity Match": round(hiring_contrib, 1),
        "Location Match": round(location_contrib, 1)
    }


def get_next_batch_version_name(filename: str, db_path: str = None) -> str:
    """Calculates auto-incrementing file suffix versions to prevent silent overwrites."""
    from database.database import list_batches
    try:
        batches = list_batches(only_active=False, db_path=db_path)
    except Exception:
        return filename
        
    base_name = filename.replace(".csv", "")
    
    # Find existing versions
    existing_versions = []
    for b in batches:
        b_file = b.get("source_filename", "")
        b_name = b_file.replace(".csv", "")
        if b_name == base_name:
            existing_versions.append(1)
        elif b_name.startswith(f"{base_name}_v"):
            try:
                v_num = int(b_name.split("_v")[-1])
                existing_versions.append(v_num)
            except ValueError:
                pass
                
    if existing_versions:
        next_v = max(existing_versions) + 1
        return f"{base_name}_v{next_v}.csv"
        
    return filename
