"""
Schema Registry for CSV Ingestion 2.0.
Defines canonical headers, column aliases, and value normalizations.
"""

from typing import Dict, List

# Canonical columns required by the platform
CANONICAL_COLUMNS = [
    "Company Name",
    "Industry",
    "Funding Stage",
    "Employee Count",
    "Location",
    "Hiring Activity",
    "Recent Funding",
    "Expansion Status"
]

# Aliases registry linking raw headers to canonical names
COLUMN_ALIASES: Dict[str, List[str]] = {
    "Company Name": ["company_name", "company name", "companyname", "company", "name", "co"],
    "Industry": ["industry", "sector", "industry_vertical", "vertical", "industry vertical"],
    "Funding Stage": ["funding_stage", "funding stage", "fundingstage", "fundinground", "stage", "funding_round", "round", "funding round"],
    "Employee Count": ["employee_count", "employee count", "employeecount", "employees", "headcount", "size", "emp_count", "staff"],
    "Location": ["location", "country", "city", "region", "hq", "hq_location", "hq location"],
    "Hiring Activity": ["hiring_activity", "hiring activity", "hiringactivity", "hiring", "hiring_status", "open_roles", "hiring status"],
    "Recent Funding": ["recent_funding", "recent funding", "recentfunding", "funding_recent", "recently_funded", "funded_recently", "recently funded"],
    "Expansion Status": ["expansion_status", "expansion status", "expansionstatus", "expansion", "growth_status", "growth", "growth status"]
}

# Normalization maps for raw category cell values
NORMALIZATION_MAPS: Dict[str, Dict[str, str]] = {
    "Funding Stage": {
        "seed": "Seed",
        "seriesa": "Series A",
        "series a": "Series A",
        "seriesb": "Series B",
        "series b": "Series B",
        "seriesc": "Series C",
        "series c": "Series C",
        "growth": "Growth",
        "bootstrapped": "Bootstrapped",
        "bootstrap": "Bootstrapped",
        "ipo-bound": "IPO-bound",
        "ipo bound": "IPO-bound",
        "ipo": "IPO-bound"
    },
    "Location": {
        "usa": "US",
        "united states": "US",
        "us": "US",
        "united kingdom": "UK",
        "uk": "UK",
        "canada": "Canada",
        "india": "India",
        "europe": "EU",
        "eu": "EU",
        "apac": "APAC",
        "middle east": "Middle East",
        "latin america": "Latin America",
        "latam": "Latin America"
    },
    "Hiring Activity": {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "none": "None"
    },
    "Recent Funding": {
        "yes": "Yes",
        "y": "Yes",
        "true": "Yes",
        "no": "No",
        "n": "No",
        "false": "No"
    },
    "Expansion Status": {
        "expanding": "Expanding",
        "expansion": "Expanding",
        "growing": "Expanding",
        "stable": "Stable",
        "constant": "Stable",
        "contracting": "Contracting",
        "shrinking": "Contracting"
    }
}
