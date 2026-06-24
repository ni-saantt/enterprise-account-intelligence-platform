"""
Constants and Configuration for Enterprise GTM Account Intelligence Platform.
Defines scoring options, sub-weights, raw SVG icons, and a premium B2B SaaS dark design system.
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

# GTM Opportunity thresholds
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

# ------------------ RAW SVG ICON LIBRARY (Lucide Replacements) ------------------
SVG_ICONS = {
    "rocket": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4.5 16.5c-1.5 1.26-2.5 3.19-2.5 5.5s1 4.24 2.5 5.5"/>'
        '<path d="M12 2L2 22l10-6 10 6-10-22z"/></svg>'
    ),
    "briefcase": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>'
        '<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
    ),
    "building": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="4" y="2" width="16" height="20" rx="2" ry="2"/>'
        '<line x1="9" y1="22" x2="9" y2="16"/>'
        '<line x1="15" y1="22" x2="15" y2="16"/>'
        '<line x1="9" y1="16" x2="15" y2="16"/>'
        '<path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M12 6h.01M12 10h.01"/></svg>'
    ),
    "target": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/></svg>'
    ),
    "users": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    ),
    "search": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
    ),
    "trending-up": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>'
        '<polyline points="17 6 23 6 23 12"/></svg>'
    ),
    "bar-chart": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="18" y1="20" x2="18" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/></svg>'
    ),
    "dollar-sign": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="12" y1="1" x2="12" y2="23"/>'
        '<path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
    ),
    "activity": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    ),
    "brain": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1 0-3.12 3.01 3.01 0 0 1 0-4.88 '
        '2.5 2.5 0 0 1 0-3.12A2.5 2.5 0 0 1 9.5 2zM14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 '
        '2.5 2.5 0 0 0 0-3.12 3.01 3.01 0 0 0 0-4.88 2.5 2.5 0 0 0 0-3.12A2.5 2.5 0 0 0 14.5 2z"/></svg>'
    ),
    "database": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'
        '<path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>'
    ),
    "globe": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="2" y1="12" x2="22" y2="12"/>'
        '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'
    ),
    "mail": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>'
        '<polyline points="22,6 12,13 2,6"/></svg>'
    ),
    "settings": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33'
        ' 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06'
        'a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09'
        'A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 '
        '1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33'
        'l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 '
        '0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    ),
    "user": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/></svg>'
    ),
    "user-check": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<polyline points="16 11 18 13 22 9"/></svg>'
    ),
    "check-circle": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/></svg>'
    )
}

# ------------------ PREMIUM B2B SAAS DARK SYSTEM CSS ------------------
SAAS_THEME_CSS = """
<style>
    /* Google Font Import - Plus Jakarta Sans */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0B1220 !important;
        color: #F3F4F6 !important;
    }
    
    /* Main Streamlit App background override */
    .stApp {
        background-color: #0B1220 !important;
    }
    
    /* Hide default Streamlit decoration header line */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Sidebar Custom Skinning */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #253047 !important;
    }
    
    /* Navigation Sidebar styling */
    div.row-widget.stRadio > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Custom style for radio choices in sidebar to look like Apollo menu items */
    div.row-widget.stRadio label {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 10px 14px !important;
        margin-bottom: 6px !important;
        cursor: pointer;
        display: flex !important;
        align-items: center;
        gap: 12px;
        transition: all 0.2s ease-in-out;
        color: #9CA3AF !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
    }
    div.row-widget.stRadio label:hover {
        background-color: #1A2235 !important;
        color: #FFFFFF !important;
    }
    div.row-widget.stRadio label[data-checked="true"] {
        background-color: #1A2235 !important;
        border-left: 3px solid #3B82F6 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    /* Input field styling overrides (Streamlit Inputs) */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #1A2235 !important;
        border: 1px solid #253047 !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }
    
    /* Form headers, text inputs */
    label, p, span {
        color: #D1D5DB !important;
    }
    
    /* Custom Enterprise Metric Card */
    .saas-metric-card {
        background-color: #1A2235 !important;
        border: 1px solid #253047 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        position: relative !important;
        overflow: hidden !important;
        display: flex !important;
        flex-direction: column !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 16px;
    }
    .saas-metric-card:hover {
        transform: translateY(-2px);
        border-color: #3B82F6 !important;
    }
    .saas-metric-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin-bottom: 10px !important;
        color: #64748B !important;
    }
    .saas-metric-label {
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #9CA3AF !important;
        font-weight: 600 !important;
    }
    .saas-metric-value-row {
        display: flex !important;
        align-items: baseline !important;
        justify-content: space-between !important;
    }
    .saas-metric-value {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        margin: 0 !important;
    }
    .saas-metric-delta {
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        gap: 3px !important;
    }
    .delta-up { color: #22C55E !important; }
    .delta-down { color: #EF4444 !important; }
    
    /* Sparkline containers */
    .sparkline-container {
        margin-top: 10px;
        display: flex;
        justify-content: flex-end;
    }

    /* Color Badges */
    .saas-badge {
        display: inline-flex !important;
        align-items: center !important;
        padding: 4px 8px !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
        border: 1px solid transparent !important;
    }
    .badge-tier1 { background-color: rgba(34, 197, 94, 0.1) !important; color: #22C55E !important; border-color: rgba(34, 197, 94, 0.2) !important; }
    .badge-tier2 { background-color: rgba(245, 158, 11, 0.1) !important; color: #F59E0B !important; border-color: rgba(245, 158, 11, 0.2) !important; }
    .badge-tier3 { background-color: rgba(100, 116, 139, 0.1) !important; color: #9CA3AF !important; border-color: rgba(100, 116, 139, 0.2) !important; }
    
    .badge-high { background-color: rgba(239, 68, 68, 0.1) !important; color: #EF4444 !important; border-color: rgba(239, 68, 68, 0.2) !important; }
    .badge-medium { background-color: rgba(245, 158, 11, 0.1) !important; color: #F59E0B !important; border-color: rgba(245, 158, 11, 0.2) !important; }
    .badge-low { background-color: rgba(100, 116, 139, 0.1) !important; color: #9CA3AF !important; border-color: rgba(100, 116, 139, 0.2) !important; }

    .badge-exceptional { background-color: rgba(59, 130, 246, 0.15) !important; color: #3B82F6 !important; border-color: rgba(59, 130, 246, 0.25) !important; }
    .badge-high-opp { background-color: rgba(20, 184, 166, 0.15) !important; color: #14B8A6 !important; border-color: rgba(20, 184, 166, 0.25) !important; }
    .badge-mod-opp { background-color: rgba(245, 158, 11, 0.1) !important; color: #F59E0B !important; border-color: rgba(245, 158, 11, 0.2) !important; }
    .badge-low-opp { background-color: rgba(100, 116, 139, 0.1) !important; color: #9CA3AF !important; border-color: rgba(100, 116, 139, 0.2) !important; }

    /* Custom Cards and native container overrides */
    .saas-card, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1A2235 !important;
        border: 1px solid #253047 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Specific Container Key Modifiers */
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-tab-container {
        border-top: none !important;
        border-top-left-radius: 0 !important;
        border-top-right-radius: 0 !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-height380 {
        height: 380px !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-minheight360 {
        min-height: 360px !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"].st-key-progress-card {
        text-align: center !important;
        padding: 40px 20px !important;
    }
    
    .saas-card-title {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        margin-top: 0 !important;
        margin-bottom: 16px !important;
        border-bottom: 1px solid #253047 !important;
        padding-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    /* Custom Table for lists (if used) */
    .saas-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        background-color: #1A2235;
    }
    .saas-table th {
        background-color: #111827;
        border-bottom: 2px solid #253047;
        color: #9CA3AF;
        font-weight: 600;
        padding: 12px;
    }
    .saas-table td {
        border-bottom: 1px solid #253047;
        padding: 12px;
        color: #E5E7EB;
    }
    
    /* Playbook Timeline Design */
    .timeline-container {
        position: relative;
        padding-left: 32px;
        border-left: 2px solid #253047;
        margin-left: 10px;
        margin-top: 15px;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 20px;
    }
    .timeline-badge {
        position: absolute;
        left: -43px;
        top: 0;
        background-color: #3B82F6;
        color: #FFFFFF;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 700;
        border: 2px solid #1A2235;
    }
    .timeline-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .timeline-desc {
        font-size: 0.85rem;
        color: #9CA3AF;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-weight: 500 !important;
        border-bottom-color: transparent !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom-color: #3B82F6 !important;
        font-weight: 600 !important;
    }
    
    /* Button Custom overrides */
    .stButton > button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2563EB !important;
        border-color: #2563EB !important;
    }
    
    /* Progress Bars styling */
    .saas-progress-bar {
        background-color: #253047;
        border-radius: 10px;
        height: 8px;
        width: 100%;
        overflow: hidden;
        margin-top: 4px;
        margin-bottom: 12px;
    }
    .saas-progress-value {
        height: 100%;
        border-radius: 10px;
    }

    /* Typographical sizing override */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
        margin-top: 20px !important;
    }
    h2 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.01em !important;
    }
    h3 {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
    }
</style>
"""

# Plotly styling config matching light/dark modes
PLOTLY_LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_family": "Plus Jakarta Sans",
    "font_color": "#D1D5DB",
    "margin": dict(l=40, r=40, t=50, b=40),
    "xaxis": {
        "gridcolor": "#253047",
        "linecolor": "#253047",
        "zerolinecolor": "#253047",
        "tickfont": {"color": "#9CA3AF"}
    },
    "yaxis": {
        "gridcolor": "#253047",
        "linecolor": "#253047",
        "zerolinecolor": "#253047",
        "tickfont": {"color": "#9CA3AF"}
    }
}
PLOTLY_DARK_LAYOUT_DEFAULTS = PLOTLY_LAYOUT_DEFAULTS
