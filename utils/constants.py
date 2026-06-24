"""
Constants and Configuration for Enterprise GTM Account Intelligence Platform.
Defines scoring options, sub-weights, and CSS theme snippets for SaaS styling.
"""

# Supported Metadata Lists
INDUSTRIES = ["AI", "SaaS", "FinTech", "HR Tech", "Healthcare", "EdTech"]

FUNDING_STAGES = [
    "Seed",
    "Series A",
    "Series B",
    "Series C",
    "Growth",
    "Bootstrapped",
    "IPO-bound"
]

LOCATIONS = ["US", "UK", "Canada", "EU", "APAC", "India", "Middle East", "Latin America"]

HIRING_ACTIVITIES = ["High", "Medium", "Low", "None"]

EXPANSION_STATUSES = ["Expanding", "Stable", "Contracting"]

# Target Categories for Account Segmentation
FIRMOGRAPHIC_SEGMENTS = ["Enterprise", "Mid-Market", "SMB", "Startup"]

# Default Scoring Weights (Must sum to 100)
DEFAULT_WEIGHT_INDUSTRY = 25
DEFAULT_WEIGHT_FUNDING = 25
DEFAULT_WEIGHT_EMPLOYEE = 20
DEFAULT_WEIGHT_HIRING = 20
DEFAULT_WEIGHT_LOCATION = 10

# Dynamic Custom weights configurations
ICP_FACTOR_MAX_POINTS = {
    "industry": 25,
    "funding": 25,
    "employee": 20,
    "hiring": 20,
    "location": 10
}

# Sub-Weight Points Matrix (Out of max points per category)
DEFAULT_SUB_WEIGHTS = {
    "industry": {
        "AI": 25,
        "SaaS": 25,
        "FinTech": 25,
        "HR Tech": 15,
        "Healthcare": 15,
        "EdTech": 5
    },
    "funding": {
        "IPO-bound": 25,
        "Series C": 25,
        "Series B": 25,
        "Series A": 20,
        "Growth": 20,
        "Seed": 12,
        "Bootstrapped": 5
    },
    "employee": {
        # Based on count
        "ideal": 20,      # 50 - 500
        "sub_ideal": 12,  # 10 - 49 or 501 - 1000
        "other": 5        # < 10 or > 1000
    },
    "hiring": {
        "High": 20,
        "Medium": 12,
        "Low": 5,
        "None": 0
    },
    "location": {
        "US": 10,
        "UK": 10,
        "Canada": 10,
        "EU": 7,
        "APAC": 7,
        "India": 8,
        "Middle East": 5,
        "Latin America": 5
    }
}

# Classification Thresholds
ICP_TIER_RULES = {
    "Tier 1": 80,
    "Tier 2": 60,  # 60 to 79
    "Tier 3": 0    # Below 60
}

OPPORTUNITY_TIER_RULES = {
    "Exceptional Opportunity": 90,
    "High Opportunity": 75,
    "Moderate Opportunity": 60,
    "Low Opportunity": 0
}

# Buying Signal Scoring Points
BUYING_SIGNAL_POINTS = {
    "hiring": {
        "High": 35,
        "Medium": 20,
        "Low": 5,
        "None": 0
    },
    "funding": {
        "Yes": 35,
        "No": 0
    },
    "expansion": {
        "Expanding": 30,
        "Stable": 10,
        "Contracting": 0
    }
}

# Premium CSS Theme Styling for Streamlit
SAAS_THEME_CSS = """
<style>
    /* Premium Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Executive Metric Card Styles */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #fcfdfe 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.25s ease-in-out;
        margin-bottom: 15px;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }
    .dark .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-color: #334155;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .dark .metric-value {
        color: #f8fafc;
    }
    .metric-delta {
        font-size: 0.75rem;
        font-weight: 500;
        color: #10b981;
        margin-top: 4px;
        display: flex;
        align-items: center;
    }
    .metric-delta.down {
        color: #ef4444;
    }

    /* Color Code Badges */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .badge-tier1 { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-tier2 { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-tier3 { background-color: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
    
    .badge-high { background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .badge-medium { background-color: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }
    .badge-low { background-color: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }

    .badge-exceptional { background-color: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }
    .badge-high-opp { background-color: #ccfbf1; color: #115e59; border: 1px solid #99f6e4; }
    .badge-mod-opp { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-low-opp { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* Account Detail Info Cards */
    .profile-section {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .dark .profile-section {
        background-color: #0f172a;
        border-color: #1e293b;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 15px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 8px;
    }
    .dark .section-title {
        color: #f8fafc;
        border-bottom-color: #1e293b;
    }
    
    /* Playbook Layout */
    .playbook-step {
        display: flex;
        align-items: flex-start;
        margin-bottom: 12px;
        padding: 10px;
        border-left: 3px solid #6366f1;
        background-color: #f8fafc;
        border-radius: 0 8px 8px 0;
    }
    .dark .playbook-step {
        background-color: #1e293b;
        border-left-color: #818cf8;
    }
    .playbook-num {
        font-weight: 700;
        color: #4f46e5;
        margin-right: 12px;
        min-width: 20px;
    }
    .dark .playbook-num {
        color: #a5b4fc;
    }
    .playbook-text {
        font-size: 0.9rem;
        color: #334155;
    }
    .dark .playbook-text {
        color: #cbd5e1;
    }
</style>
"""

# Plotly styling config matching light/dark modes
PLOTLY_LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_family": "Plus Jakarta Sans",
    "font_color": "#475569",
    "margin": dict(l=40, r=40, t=50, b=40),
}
PLOTLY_DARK_LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_family": "Plus Jakarta Sans",
    "font_color": "#cbd5e1",
    "margin": dict(l=40, r=40, t=50, b=40),
}
