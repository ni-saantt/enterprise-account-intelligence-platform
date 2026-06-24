"""
Main Entry Point - Enterprise GTM Account Intelligence Platform.
Handles page routing, custom CSS injection, file uploads, dynamic weight configs,
and database sync.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import database routines
from database.database import init_db, save_company_batch, load_companies_for_batch, list_batches, delete_batch

# Import core scoring engines
from core.icp_scoring import calculate_icp_score
from core.buying_signals import detect_buying_signals
from core.tiering import assign_abm_tier
from core.decision_maker_mapping import map_decision_makers
from core.account_segmentation import segment_account
from core.opportunity_scoring import calculate_opportunity_score
from core.outreach_engine import calculate_outreach_priority
from core.account_summary import generate_account_summary
from core.gtm_playbook_generator import generate_gtm_playbook

# Import UI dashboard pages
from dashboard.gtm_command_center import render_command_center
from dashboard.overview import render_overview
from dashboard.account_analysis import render_account_analysis
from dashboard.revenue_market_intelligence import render_revenue_market_intelligence

# Import styling and helper utilities
from utils.constants import SAAS_THEME_CSS, ICP_FACTOR_MAX_POINTS
from utils.helpers import generate_sample_data

# Page Setup
st.set_page_config(
    page_title="Enterprise GTM Account Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply premium SaaS CSS styles
st.markdown(SAAS_THEME_CSS, unsafe_allow_html=True)

# Ensure database exists
init_db()

# Initialize session states
if "active_batch_id" not in st.session_state:
    st.session_state.active_batch_id = None

def process_and_save_data(df_raw: pd.DataFrame, batch_name: str, weights: dict) -> str:
    """Runs all scoring, segmenting, mapping, and summaries on raw data, then saves to DB."""
    batch_id = f"{batch_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    companies_processed = []
    
    for _, row in df_raw.iterrows():
        company_data = {
            "Company Name": row.get("Company Name", "Unknown"),
            "Industry": row.get("Industry", "SaaS"),
            "Funding Stage": row.get("Funding Stage", "Bootstrapped"),
            "Employee Count": int(row.get("Employee Count", 0)),
            "Location": row.get("Location", "US"),
            "Hiring Activity": row.get("Hiring Activity", "None"),
            "Recent Funding": row.get("Recent Funding", "No"),
            "Expansion Status": row.get("Expansion Status", "Stable")
        }
        
        # Calculate ICP Score
        icp_score = calculate_icp_score(company_data, weights=weights)
        
        # Assign ABM Tier
        abm_tier = assign_abm_tier(icp_score)
        
        # Detect Buying Signals
        buying_score, buying_level = detect_buying_signals(company_data)
        
        # Segment account
        firmographic, industry_val = segment_account(company_data)
        
        # Calculate Opportunity Score
        market_score, opp_score, opp_level = calculate_opportunity_score(icp_score, buying_score, company_data)
        
        # Assign Outreach Priority
        priority, outreach_reason = calculate_outreach_priority(company_data, icp_score, buying_level, opp_score)
        
        # Map Decision Makers
        primary, secondary, contact_reason = map_decision_makers(company_data)
        
        # Generate Playbook
        playbook = generate_gtm_playbook(company_data, priority, primary, secondary)
        
        # Generate AI summary
        summary = generate_account_summary(
            company=company_data,
            icp_score=icp_score,
            abm_tier=abm_tier,
            buying_signal_level=buying_level,
            gtm_opportunity_score=opp_score,
            gtm_opportunity_level=opp_level,
            priority_level=priority,
            primary_contact=primary,
            secondary_contact=secondary
        )
        
        # Combine parameters into record
        record = {**company_data}
        record.update({
            "icp_score": icp_score,
            "abm_tier": abm_tier,
            "buying_signal_score": buying_score,
            "buying_signal_level": buying_level,
            "market_opportunity_score": market_score,
            "gtm_opportunity_score": opp_score,
            "gtm_opportunity_level": opp_level,
            "priority_level": priority,
            "outreach_reasoning": outreach_reason,
            "primary_contact": primary,
            "secondary_contact": secondary,
            "contact_reasoning": contact_reason,
            "account_summary": summary,
            "playbook": playbook,
            "firmographic_segment": firmographic
        })
        
        companies_processed.append(record)
        
    save_company_batch(companies_processed, batch_id)
    return batch_id

# ------------------ SIDEBAR CONTROL PANEL ------------------
st.sidebar.markdown(
    '<div style="text-align: center; margin-bottom: 25px; margin-top: 15px;">'
    '<h2 style="color: #FFFFFF; font-weight: 800; font-size:1.55rem; margin-bottom: 0;">ENTERPRISE GTM</h2>'
    '<p style="color: #64748B; font-size: 0.8rem; margin-top: 3px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Sales Account Intelligence</p>'
    '</div>', 
    unsafe_allow_html=True
)

# 1. Navigation Panel (Pure text-based, styled via saas CSS)
st.sidebar.markdown('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Navigation</p>', unsafe_allow_html=True)
nav_choice = st.sidebar.radio(
    label="Navigation",
    options=[
        "Command Center",
        "Overview Analytics",
        "Account Prioritization",
        "Revenue & Market"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #253047;"></div>', unsafe_allow_html=True)

# 2. Upload / Batch Controls
st.sidebar.markdown('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Data Ingestion</p>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload Company CSV", type=["csv"], label_visibility="collapsed")

# Manage existing batches
batches = list_batches()

# Show dynamic load button if no batches exist
if not batches:
    if st.sidebar.button("Load Demo Dataset", use_container_width=True):
        sample_path = os.path.join("data", "sample_companies.csv")
        if not os.path.exists(sample_path):
            generate_sample_data(sample_path)
            
        df_sample = pd.read_csv(sample_path)
        # Default Weights
        default_weights = {
            "industry": 25,
            "funding": 25,
            "employee": 20,
            "hiring": 20,
            "location": 10
        }
        batch_id = process_and_save_data(df_sample, "sample_companies", default_weights)
        st.session_state.active_batch_id = batch_id
        st.rerun()
else:
    # Dropdown selector for batches
    batch_options = {b["batch_id"]: f"{b['batch_id'].split('_')[0]} ({b['record_count']} acc)" for b in batches}
    selected_batch_id = st.sidebar.selectbox(
        "Active Segment/Batch",
        options=list(batch_options.keys()),
        format_func=lambda x: batch_options.get(x, x)
    )
    
    if st.session_state.active_batch_id is None or st.session_state.active_batch_id not in batch_options:
        st.session_state.active_batch_id = selected_batch_id
    elif selected_batch_id != st.session_state.active_batch_id:
        st.session_state.active_batch_id = selected_batch_id
        
# Process Uploaded CSV
if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        req_cols = ["Company Name", "Industry", "Funding Stage", "Employee Count", "Location", "Hiring Activity", "Recent Funding", "Expansion Status"]
        missing_cols = [c for c in req_cols if c not in df_uploaded.columns]
        
        if not missing_cols:
            if st.sidebar.button("Process & Index CSV", use_container_width=True):
                weights = {
                    "industry": st.session_state.get("wt_ind", 25),
                    "funding": st.session_state.get("wt_fund", 25),
                    "employee": st.session_state.get("wt_emp", 20),
                    "hiring": st.session_state.get("wt_hiring", 20),
                    "location": st.session_state.get("wt_loc", 10)
                }
                new_batch_id = process_and_save_data(df_uploaded, uploaded_file.name.replace(".csv", ""), weights)
                st.session_state.active_batch_id = new_batch_id
                st.sidebar.success("CSV indexed successfully.")
                st.rerun()
        else:
            st.sidebar.error(f"Missing columns: {', '.join(missing_cols)}")
    except Exception as e:
        st.sidebar.error(f"Upload error: {str(e)}")

# Sidebar Delete batch
if st.session_state.active_batch_id:
    if st.sidebar.button("Delete Active Batch", use_container_width=True):
        delete_batch(st.session_state.active_batch_id)
        st.session_state.active_batch_id = None
        st.rerun()

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #253047;"></div>', unsafe_allow_html=True)

# 3. Dynamic ICP Weights Customizer
st.sidebar.markdown('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:5px;">ICP Score Weights</p>', unsafe_allow_html=True)

wt_ind = st.sidebar.slider("Industry Match Weight", 0, 50, 25, key="wt_ind")
wt_fund = st.sidebar.slider("Funding Stage Weight", 0, 50, 25, key="wt_fund")
wt_emp = st.sidebar.slider("Employee Count Weight", 0, 50, 20, key="wt_emp")
wt_hiring = st.sidebar.slider("Hiring Activity Weight", 0, 50, 20, key="wt_hiring")
wt_loc = st.sidebar.slider("Location Match Weight", 0, 50, 10, key="wt_loc")

sum_wts = wt_ind + wt_fund + wt_emp + wt_hiring + wt_loc

if sum_wts == 100:
    st.sidebar.markdown(f'<p style="color:#22C55E; font-weight:600; font-size:0.8rem; margin-top:-5px;">Weights sum: {sum_wts}% (Balanced)</p>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<p style="color:#EF4444; font-weight:600; font-size:0.8rem; margin-top:-5px;">Weights sum: {sum_wts}% (Must equal 100%)</p>', unsafe_allow_html=True)

# Recalculate button for active batch
if st.session_state.active_batch_id and sum_wts == 100:
    if st.sidebar.button("Recalculate Scoring Fits", use_container_width=True):
        raw_records = load_companies_for_batch(st.session_state.active_batch_id)
        if raw_records:
            df_raw = pd.DataFrame(raw_records)
            parts = st.session_state.active_batch_id.split("_")
            base_name = parts[0] if len(parts) > 0 else "recalc_batch"
            
            weights = {
                "industry": wt_ind,
                "funding": wt_fund,
                "employee": wt_emp,
                "hiring": wt_hiring,
                "location": wt_loc
            }
            
            delete_batch(st.session_state.active_batch_id)
            new_batch_id = process_and_save_data(df_raw, base_name, weights)
            st.session_state.active_batch_id = new_batch_id
            st.rerun()

# ------------------ LOAD AND ROUTE PAGE DATA ------------------
# Get active batch data
if st.session_state.active_batch_id:
    batch_records = load_companies_for_batch(st.session_state.active_batch_id)
    df_active = pd.DataFrame(batch_records)
else:
    df_active = pd.DataFrame()

# Page Routing
if nav_choice == "Command Center":
    render_command_center(df_active)
elif nav_choice == "Overview Analytics":
    render_overview(df_active)
elif nav_choice == "Account Prioritization":
    render_account_analysis(df_active)
elif nav_choice == "Revenue & Market":
    render_revenue_market_intelligence(df_active)
