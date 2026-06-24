"""
Main Entry Point - Enterprise GTM Account Intelligence Platform.
Handles onboarding wizard stages, custom weight sliders, page routing,
and advanced batch workspace management (renaming, cloning, exports).
"""

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from collections import Counter

# Import database routines
from database.database import (
    init_db, 
    save_company_batch, 
    load_companies_for_batch, 
    list_batches, 
    delete_batch, 
    rename_batch, 
    clone_batch,
    set_batch_active_status
)

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
from dashboard.overview import render_analytics
from dashboard.account_analysis import render_account_analysis
from dashboard.revenue_market_intelligence import render_market_intelligence
from dashboard.settings_scoring import render_settings_scoring

# Import ingestion 2.0 modules
from utils.schema_registry import CANONICAL_COLUMNS
from utils.column_mapper import map_columns, get_unmapped_required
from utils.csv_validator import normalize_cell_value, audit_dataset_health, validate_scoring_sanity
from utils.duplicate_detector import resolve_duplicates

# Import styling configurations
from utils.constants import SAAS_THEME_CSS, SVG_ICONS, ICP_FACTOR_MAX_POINTS
from utils.helpers import (
    generate_sample_data, 
    to_excel_bytes, 
    to_csv_bytes,
    clean_html,
    get_next_batch_version_name,
    get_icp_score_breakdown
)

def process_and_save_data(df_raw: pd.DataFrame, source_filename: str, weights: dict, column_mapping: dict = None, dedup_strategy: str = "Keep First") -> tuple:
    """
    Deduplicates, normalizes, scores, and saves a dataset to the database.
    Returns (new_batch_id, processed_count, duplicate_count, normalizations_count).
    """
    if column_mapping is None:
        # Generate mapping mapping standard columns to themselves or using helper
        column_mapping = {col: col for col in df_raw.columns if col in CANONICAL_COLUMNS}
        if not column_mapping:
            column_mapping = map_columns(df_raw.columns)
            
    # Get raw company column name
    raw_company_col = next((r for r, c in column_mapping.items() if c == "Company Name"), None)
    if not raw_company_col:
        raw_company_col = df_raw.columns[0]
        
    # Deduplicate
    df_dedup = resolve_duplicates(df_raw, raw_company_col, dedup_strategy)
    
    # Process and normalize value records
    processed = []
    normalizations_run = 0
    
    for _, row in df_dedup.iterrows():
        c_dict = {}
        for raw, canon in column_mapping.items():
            if canon in CANONICAL_COLUMNS:
                val = row.get(raw)
                cleaned = normalize_cell_value(val, canon)
                if cleaned != val:
                    normalizations_run += 1
                c_dict[canon] = cleaned
                
        # Set default keys if missing
        for canon in CANONICAL_COLUMNS:
            if canon not in c_dict:
                c_dict[canon] = 0 if canon == "Employee Count" else "Unknown"
                
        # Calculate metrics
        icp = calculate_icp_score(c_dict, weights)
        abm = assign_abm_tier(icp)
        bs_score, bs_lvl = detect_buying_signals(c_dict)
        firm, ind = segment_account(c_dict)
        ms, opp, opp_lvl = calculate_opportunity_score(icp, bs_score, c_dict)
        pri, out_reason = calculate_outreach_priority(c_dict, icp, bs_lvl, opp)
        prim, sec, con_reason = map_decision_makers(c_dict)
        play = generate_gtm_playbook(c_dict, pri, prim, sec)
        sum_narrative = generate_account_summary(c_dict, icp, abm, bs_lvl, opp, opp_lvl, pri, prim, sec)
        
        rec = {**c_dict}
        rec.update({
            "icp_score": icp,
            "abm_tier": abm,
            "buying_signal_score": bs_score,
            "buying_signal_level": bs_lvl,
            "market_opportunity_score": ms,
            "gtm_opportunity_score": opp,
            "gtm_opportunity_level": opp_lvl,
            "priority_level": pri,
            "outreach_reasoning": out_reason,
            "primary_contact": prim,
            "secondary_contact": sec,
            "contact_reasoning": con_reason,
            "account_summary": sum_narrative,
            "playbook": play,
            "firmographic_segment": firm
        })
        
        # Assert scoring sanity checks (Boundary validation layer)
        validate_scoring_sanity(rec)
        processed.append(rec)
        
    clean_filename = source_filename.replace(".csv", "")
    new_batch_id = f"{clean_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Calculate Data Quality Score
    audit = audit_dataset_health(df_raw, column_mapping)
    q_score = audit["quality_score"]
    
    save_company_batch(processed, new_batch_id, source_filename=source_filename, quality_score=q_score)
    
    return new_batch_id, len(processed), len(df_raw) - len(df_dedup), normalizations_run

# Page Setup
st.set_page_config(
    page_title="Enterprise GTM Account Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS theme
st.markdown(SAAS_THEME_CSS, unsafe_allow_html=True)

# Ensure database tables exist
init_db()

# Initialize session states
if "active_batch_id" not in st.session_state:
    st.session_state.active_batch_id = "None"
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = "idle"  # idle, mapping, validation, scoring, activation
if "uploaded_df_raw" not in st.session_state:
    st.session_state.uploaded_df_raw = None
if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {}
if "dedup_strategy" not in st.session_state:
    st.session_state.dedup_strategy = "Keep First"
if "onboarding_filename" not in st.session_state:
    st.session_state.onboarding_filename = ""
if "onboarding_filesize" not in st.session_state:
    st.session_state.onboarding_filesize = 0
if "import_summary" not in st.session_state:
    st.session_state.import_summary = {}
if "nav_override" not in st.session_state:
    st.session_state.nav_override = None
if "active_page" not in st.session_state:
    st.session_state.active_page = "Data Integration"

# Redirect callback helper
if st.session_state.nav_override:
    st.session_state.active_page = st.session_state.nav_override
    st.session_state.nav_override = None

nav_choice_default = st.session_state.active_page

# ------------------ SIDEBAR CONTROL PANEL ------------------
st.sidebar.markdown(
    clean_html('<div style="text-align: center; margin-bottom: 25px; margin-top: 15px;">'
    '<h2 style="color: #FFFFFF; font-weight: 800; font-size:1.55rem; margin-bottom: 0;">ENTERPRISE GTM</h2>'
    '<p style="color: #64748B; font-size: 0.8rem; margin-top: 3px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0;">Sales Account Intelligence</p>'
    '</div>'), 
    unsafe_allow_html=True
)

# 1. Navigation Panel
st.sidebar.markdown(clean_html('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Navigation</p>'), unsafe_allow_html=True)

nav_options = [
    "Data Integration",
    "Command Center",
    "Analytics",
    "Account Prioritization",
    "Market Intelligence",
    "Settings & Scoring"
]

if st.session_state.onboarding_step != "idle":
    # Navigation remains visible but they are reminded onboarding is in progress
    nav_choice = st.sidebar.radio(
        label="Navigation",
        options=nav_options,
        index=nav_options.index(nav_choice_default),
        label_visibility="collapsed"
    )
    st.sidebar.markdown(
        clean_html(f"""
            <div style="background-color:rgba(239,68,68,0.1); border:1px solid #EF444450; padding:12px; border-radius:8px; margin-top:10px;">
                <div style="font-size:0.75rem; color:#EF4444; font-weight:700; text-transform:uppercase;">⚠️ Wizard Active</div>
                <div style="font-size:0.8rem; color:#FFFFFF; margin-top:4px;">
                    Onboarding <b>{st.session_state.onboarding_filename}</b>. Complete mapping/validation in Data Integration to unlock dashboards.
                </div>
            </div>
        """),
        unsafe_allow_html=True
    )
else:
    nav_choice = st.sidebar.radio(
        label="Navigation",
        options=nav_options,
        index=nav_options.index(nav_choice_default),
        label_visibility="collapsed"
    )
    
st.session_state.active_page = nav_choice
st.sidebar.markdown(clean_html('<div style="margin: 20px 0; border-top: 1px solid #253047;"></div>'), unsafe_allow_html=True)

# 2. Active Batch Management
batches = list_batches(only_active=True)

if batches and st.session_state.onboarding_step == "idle":
    st.sidebar.markdown(clean_html('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Active Dataset</p>'), unsafe_allow_html=True)
    
    # Select active segment
    batch_options = {"None": "None Selected"}
    for b in batches:
        batch_options[b["batch_id"]] = f"{b['source_filename']} ({b['record_count']} acc)"
        
    options_keys = list(batch_options.keys())
    if st.session_state.active_batch_id in batch_options:
        default_idx = options_keys.index(st.session_state.active_batch_id)
    else:
        default_idx = 0
        
    selected_batch_id = st.sidebar.selectbox(
        "Active Segment/Batch",
        options=options_keys,
        index=default_idx,
        format_func=lambda x: batch_options.get(x, x),
        label_visibility="collapsed"
    )
    
    if selected_batch_id != st.session_state.active_batch_id:
        st.session_state.active_batch_id = selected_batch_id
        st.session_state.confirm_clear_active = False
        st.rerun()
        
    # Reset / Clear Active Batch
    if st.sidebar.button("🗑 Deactivate Current Dataset", use_container_width=True):
        st.session_state.confirm_clear_active = True
        
    if st.session_state.get("confirm_clear_active", False):
        st.sidebar.warning("Deactivate selection?")
        col_clear_yes, col_clear_no = st.sidebar.columns(2)
        with col_clear_yes:
            if st.sidebar.button("Yes", key="clear_active_confirm_yes", use_container_width=True):
                if st.session_state.active_batch_id and st.session_state.active_batch_id != "None":
                    set_batch_active_status(st.session_state.active_batch_id, 0)
                st.session_state.active_batch_id = "None"
                st.session_state.confirm_clear_active = False
                st.session_state.active_page = "Data Integration"
                st.rerun()
        with col_clear_no:
            if st.sidebar.button("No", key="clear_active_confirm_no", use_container_width=True):
                st.session_state.confirm_clear_active = False
                st.rerun()
                
    # Active Batch Stats Card in Sidebar
    active_meta = next((b for b in batches if b["batch_id"] == st.session_state.active_batch_id), None)
    if active_meta:
        st.sidebar.markdown(clean_html(f"""
            <div style="background-color:#1A2235; border:1px solid #253047; padding:12px; border-radius:8px; margin-top:8px;">
                <div style="font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.03em;">Active Dataset KPI</div>
                <div style="font-size:0.85rem; color:#FFFFFF; font-weight:700; margin-top:4px;">{active_meta['source_filename']}</div>
                <div style="font-size:0.8rem; color:#9CA3AF; margin-top:6px;">
                    • <b>Accounts:</b> {active_meta['record_count']}<br>
                    • <b>Avg ICP:</b> {active_meta['average_icp']:.1f}<br>
                    • <b>Quality:</b> {active_meta.get('quality_score', 100)}%<br>
                    • <b>Top Segment:</b> {active_meta['top_industry']}<br>
                    • <b>Imported:</b> {active_meta['created_at'].split()[0]}
                </div>
            </div>
        """), unsafe_allow_html=True)
        
        # Recalculate weights button in settings, but we can add Refresh here too
        if st.sidebar.button("🔄 Refresh & Recalculate", use_container_width=True):
            raw_records = load_companies_for_batch(st.session_state.active_batch_id)
            if raw_records:
                df_raw = pd.DataFrame(raw_records)
                base_name = active_meta["source_filename"]
                weights = {
                    "industry": st.session_state.get("wt_ind", 25),
                    "funding": st.session_state.get("wt_fund", 25),
                    "employee": st.session_state.get("wt_emp", 20),
                    "hiring": st.session_state.get("wt_hiring", 20),
                    "location": st.session_state.get("wt_loc", 10)
                }
                
                # Retrieve existing Quality Score
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT quality_score FROM batches WHERE batch_id = ?", (st.session_state.active_batch_id,))
                row = cursor.fetchone()
                q_score = row["quality_score"] if row else 100
                conn.close()
                
                delete_batch(st.session_state.active_batch_id)
                new_batch_id, _, _, _ = process_and_save_data(
                    df_raw=df_raw,
                    source_filename=base_name,
                    weights=weights
                )
                set_batch_active_status(new_batch_id, 1)
                # Keep active
                st.session_state.active_batch_id = new_batch_id
                st.success("Recalculated scores!")
                st.rerun()

# ------------------ LOAD ACTIVE DATA ------------------
if st.session_state.active_batch_id and st.session_state.active_batch_id != "None":
    batch_records = load_companies_for_batch(st.session_state.active_batch_id)
    df_active = pd.DataFrame(batch_records)
    active_meta = next((b for b in list_batches(only_active=False) if b["batch_id"] == st.session_state.active_batch_id), None)
else:
    df_active = pd.DataFrame()
    active_meta = None

# Helper to render the active dataset header on pages
def render_active_dataset_header(active_meta: dict) -> None:
    if active_meta:
        dt_str = active_meta.get("created_at", "")
        st.markdown(clean_html(f"""
            <div style="background-color:#1A2235; border:1px solid #253047; padding:10px 16px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#10B981; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; background-color:rgba(16, 185, 129, 0.1); padding:2px 6px; border-radius:4px;">Active</span>
                    <span style="font-size:0.9rem; color:#FFFFFF; font-weight:600;">Currently Active Dataset:</span>
                    <span style="font-size:0.9rem; color:#3B82F6; font-weight:700;">{active_meta['source_filename']}</span>
                </div>
                <div style="display:flex; align-items:center; gap:16px; font-size:0.85rem; color:#9CA3AF;">
                    <div>• <b>Rows:</b> {active_meta['record_count']}</div>
                    <div>• <b>Data Quality:</b> {active_meta.get('quality_score', 100)}%</div>
                    <div>• <b>Last Updated:</b> {dt_str}</div>
                </div>
            </div>
        """), unsafe_allow_html=True)
    else:
        st.markdown(clean_html("""
            <div style="background-color:rgba(239, 68, 68, 0.08); border:1px solid #EF444450; padding:10px 16px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#EF4444; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; background-color:rgba(239, 68, 68, 0.15); padding:2px 6px; border-radius:4px;">No Active Dataset</span>
                    <span style="font-size:0.9rem; color:#E5E7EB;">No active dataset is selected. Access configuration metrics in the Data Integration tab.</span>
                </div>
            </div>
        """), unsafe_allow_html=True)


# ------------------ WIZARD IMPLEMENTATION ------------------
def render_data_integration_wizard() -> None:
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">Data Integration Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Upload new datasets, run mapping wizards, and audit historical GTM runs.</p>', unsafe_allow_html=True)
    
    tab_wizard, tab_manager, tab_compare = st.tabs([
        "Import Wizard", 
        "Dataset Manager", 
        "Dataset Comparison"
    ])
    
    with tab_wizard:
        if st.session_state.onboarding_step == "idle":
            st.markdown("### Upload New Dataset (Phase 1)")
            st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">Drag and drop your accounts CSV file to initiate the enterprise onboarding flow.</p>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Upload Company CSV", type=["csv"], key="wizard_uploader", label_visibility="collapsed")
            
            if uploaded_file is not None:
                try:
                    df_raw = pd.read_csv(uploaded_file)
                    st.session_state.uploaded_df_raw = df_raw
                    # Auto version name
                    versioned_filename = get_next_batch_version_name(uploaded_file.name)
                    st.session_state.onboarding_filename = versioned_filename
                    st.session_state.onboarding_filesize = len(uploaded_file.getvalue())
                    st.session_state.column_mapping = map_columns(df_raw.columns)
                    st.session_state.onboarding_step = "mapping"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to parse CSV: {str(e)}")
                    
            # Option to load demo dataset if db is empty
            batches_check = list_batches(only_active=False)
            if not batches_check:
                st.markdown("---")
                st.markdown("#### No Datasets Found")
                if st.button("Load Demo Dataset", use_container_width=True):
                    sample_path = os.path.join("data", "sample_companies.csv")
                    if not os.path.exists(sample_path):
                        generate_sample_data(sample_path)
                        
                    df_sample = pd.read_csv(sample_path)
                    default_weights = {"industry": 25, "funding": 25, "employee": 20, "hiring": 20, "location": 10}
                    
                    processed = []
                    for _, row in df_sample.iterrows():
                        c = {
                            "Company Name": row["Company Name"], "Industry": row["Industry"],
                            "Funding Stage": row["Funding Stage"], "Employee Count": int(row["Employee Count"]),
                            "Location": row["Location"], "Hiring Activity": row["Hiring Activity"],
                            "Recent Funding": row["Recent Funding"], "Expansion Status": row["Expansion Status"]
                        }
                        icp = calculate_icp_score(c, default_weights)
                        abm = assign_abm_tier(icp)
                        bs_score, bs_lvl = detect_buying_signals(c)
                        firm, ind = segment_account(c)
                        ms, opp, opp_lvl = calculate_opportunity_score(icp, bs_score, c)
                        pri, out_reason = calculate_outreach_priority(c, icp, bs_lvl, opp)
                        prim, sec, con_reason = map_decision_makers(c)
                        play = generate_gtm_playbook(c, pri, prim, sec)
                        sum_narrative = generate_account_summary(c, icp, abm, bs_lvl, opp, opp_lvl, pri, prim, sec)
                        
                        rec = {**c}
                        rec.update({
                            "icp_score": icp, "abm_tier": abm, "buying_signal_score": bs_score, "buying_signal_level": bs_lvl,
                            "market_opportunity_score": ms, "gtm_opportunity_score": opp, "gtm_opportunity_level": opp_lvl,
                            "priority_level": pri, "outreach_reasoning": out_reason, "primary_contact": prim, "secondary_contact": sec,
                            "contact_reasoning": con_reason, "account_summary": sum_narrative, "playbook": play, "firmographic_segment": firm
                        })
                        processed.append(rec)
                        
                    demo_id = f"sample_companies_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    save_company_batch(processed, demo_id, source_filename="sample_companies.csv", quality_score=95)
                    st.session_state.active_batch_id = demo_id
                    st.rerun()
                    
        elif st.session_state.onboarding_step == "mapping":
            st.markdown("### Column Mapping Setup (Phase 2)")
            with st.container(border=True):
                st.markdown('<div class="saas-card-title">Column Mapping Setup</div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">Validate and edit column mapping parameters. Standard columns must map to raw CSV headers.</p>', unsafe_allow_html=True)
                
                raw_cols = st.session_state.uploaded_df_raw.columns.tolist()
                mapping = st.session_state.column_mapping.copy()
                
                h_col1, h_col2 = st.columns([1, 1])
                with h_col1:
                    st.markdown('<div style="font-weight:700; font-size:0.85rem; color:#9CA3AF; margin-bottom:15px; text-transform:uppercase; letter-spacing:0.05em;">Raw CSV Header</div>', unsafe_allow_html=True)
                with h_col2:
                    st.markdown('<div style="font-weight:700; font-size:0.85rem; color:#9CA3AF; margin-bottom:15px; text-transform:uppercase; letter-spacing:0.05em;">Maps to Standard Header</div>', unsafe_allow_html=True)
                    
                for idx, raw in enumerate(raw_cols):
                    r_col1, r_col2 = st.columns([1, 1])
                    default_canon = mapping.get(raw)
                    options = ["None"] + CANONICAL_COLUMNS
                    sel_idx = options.index(default_canon) if default_canon in options else 0
                    
                    with r_col1:
                        st.markdown(f'<div style="padding-top: 10px; font-weight: 600; color: #FFFFFF; font-size: 0.95rem;">• {raw}</div>', unsafe_allow_html=True)
                    with r_col2:
                        selected = st.selectbox(
                            label=f"Map {raw}",
                            options=options,
                            index=sel_idx,
                            key=f"map_sel_{raw}",
                            label_visibility="collapsed"
                        )
                        st.session_state.column_mapping[raw] = selected if selected != "None" else None
                        
                unmapped = get_unmapped_required(st.session_state.column_mapping)
                
            if unmapped:
                st.markdown(clean_html(f"""
                    <div style="background-color:rgba(239, 68, 68, 0.1); border:1px solid #EF4444; border-radius:8px; padding:16px; margin-bottom:20px; color:#EF4444; font-size:0.9rem;">
                        <div style="font-weight:700; margin-bottom:5px;">We couldn't map the following required fields:</div>
                        <ul style="margin:5px 0 10px 20px;">
                            {"".join([f"<li>{c}</li>" for c in unmapped])}
                        </ul>
                        Please map these required fields manually using the dropdowns above.
                    </div>
                """), unsafe_allow_html=True)
                st.button("Next: Audit Dataset", disabled=True)
            else:
                st.markdown(clean_html("""
                    <div style="background-color:rgba(34, 197, 94, 0.1); border:1px solid #22C55E; border-radius:8px; padding:16px; margin-bottom:20px; color:#22C55E; font-size:0.9rem;">
                        All required GTM columns mapped successfully. Click below to review the data quality report.
                    </div>
                """), unsafe_allow_html=True)
                if st.button("Next: Audit Dataset"):
                    st.session_state.onboarding_step = "validation"
                    st.rerun()
                    
            if st.button("Cancel Import"):
                st.session_state.onboarding_step = "idle"
                st.session_state.uploaded_df_raw = None
                st.rerun()
                
        elif st.session_state.onboarding_step == "validation":
            st.markdown("### Data Validation (Phase 3)")
            audit = audit_dataset_health(st.session_state.uploaded_df_raw, st.session_state.column_mapping)
            score = audit["quality_score"]
            score_color = "#22C55E" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
            
            with st.container(border=True):
                st.markdown('<div class="saas-card-title">Dataset Health Report</div>', unsafe_allow_html=True)
                col_l_aud, col_r_aud = st.columns([1, 2])
                with col_l_aud:
                    st.markdown(clean_html(f"""
                        <div style="text-align:center; padding:20px; border:1px solid #253047; border-radius:10px; background-color:#111827;">
                            <div style="font-size:0.8rem; color:#64748B; font-weight:700; text-transform:uppercase;">Data Quality Score</div>
                            <div style="font-size:3.5rem; font-weight:800; color:{score_color}; margin:10px 0;">{score}%</div>
                            <div style="font-size:0.85rem; color:#E5E7EB;"><b>{audit['total_records']}</b> total rows evaluated</div>
                        </div>
                    """), unsafe_allow_html=True)
                with col_r_aud:
                    st.markdown('<div style="font-weight:600; color:#FFFFFF; margin-bottom:8px;">Quality Metrics Summary:</div>', unsafe_allow_html=True)
                    st.markdown(clean_html(f"""
                        <table style="width:100%; font-size:0.88rem; border-collapse:collapse; color:#9CA3AF;">
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Duplicate Companies</td><td style="padding:6px 0; color:#EF4444;">{audit['duplicate_count']} matches flagged</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Employee Counts</td><td style="padding:6px 0;">{audit['missing_counts'].get('Employee Count', 0)} rows</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Industries</td><td style="padding:6px 0;">{audit['missing_counts'].get('Industry', 0)} rows</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Funding Stages</td><td style="padding:6px 0;">{audit['missing_counts'].get('Funding Stage', 0)} rows</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Locations</td><td style="padding:6px 0;">{audit['missing_counts'].get('Location', 0)} rows</td></tr>
                        </table>
                    """), unsafe_allow_html=True)
                    
            # Duplicate Resolution
            with st.container(border=True):
                st.markdown('<div class="saas-card-title">Duplicate Resolution Strategy</div>', unsafe_allow_html=True)
                st.session_state.dedup_strategy = st.selectbox(
                    "Select Resolution Logic",
                    options=["Keep First", "Keep Latest", "Merge Records"]
                )
                
            # Error Report Download logic
            df_raw = st.session_state.uploaded_df_raw
            mapping = st.session_state.column_mapping
            error_records = []
            for idx, row in df_raw.iterrows():
                reasons = []
                for raw, canon in mapping.items():
                    if canon in CANONICAL_COLUMNS:
                        val = row.get(raw)
                        if pd.isna(val) or str(val).strip() == "":
                            reasons.append(f"Missing '{canon}'")
                if reasons:
                    rec = dict(row)
                    rec["Validation Errors"] = "; ".join(reasons)
                    error_records.append(rec)
                    
            if error_records:
                st.markdown("### Validation Warnings & Errors")
                df_errors = pd.DataFrame(error_records)
                st.download_button(
                    label="📥 Download Error Report (CSV)",
                    data=df_errors.to_csv(index=False).encode('utf-8'),
                    file_name=f"{st.session_state.onboarding_filename}_error_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            if audit["warnings"]:
                with st.container(border=True):
                    st.markdown('<div class="saas-card-title">Data Quality Alerts</div>', unsafe_allow_html=True)
                    for w in audit["warnings"][:6]:
                        st.markdown(f'<div style="font-size:0.85rem; color:#F59E0B; margin-bottom:5px;">⚠ {w}</div>', unsafe_allow_html=True)
                    if len(audit["warnings"]) > 6:
                        st.text(f"...and {len(audit['warnings']) - 6} other minor alerts.")
                        
            col_b1, col_b2 = st.columns([1, 10])
            with col_b1:
                if st.button("Score Accounts"):
                    st.session_state.onboarding_step = "scoring"
                    st.rerun()
            with col_b2:
                if st.button("Back to Mapping"):
                    st.session_state.onboarding_step = "mapping"
                    st.rerun()
                    
        elif st.session_state.onboarding_step == "scoring":
            st.markdown("### Account Scoring (Phase 4)")
            with st.container(border=True, key="progress-card"):
                progress_text = st.empty()
                bar = st.progress(0)
                steps = [
                    ("Validating mapping structures...", 15),
                    ("Deduplicating fuzzy accounts...", 35),
                    ("Normalizing cell categories...", 55),
                    ("Calculating GTM scoring profiles...", 75),
                    ("Saving and indexing batch in SQLite database...", 95)
                ]
                for idx, (label, pct) in enumerate(steps):
                    progress_text.write(f"**Step {idx+1}/5:** {label}")
                    bar.progress(pct)
                    time.sleep(0.3)
                    
            df_raw = st.session_state.uploaded_df_raw
            mapping = st.session_state.column_mapping
            dedup_strategy = st.session_state.dedup_strategy
            weights = {
                "industry": st.session_state.get("wt_ind", 25),
                "funding": st.session_state.get("wt_fund", 25),
                "employee": st.session_state.get("wt_emp", 20),
                "hiring": st.session_state.get("wt_hiring", 20),
                "location": st.session_state.get("wt_loc", 10)
            }
            
            new_batch_id, final_count, dedup_count, normalizations_run = process_and_save_data(
                df_raw=df_raw,
                source_filename=st.session_state.onboarding_filename,
                weights=weights,
                column_mapping=mapping,
                dedup_strategy=dedup_strategy
            )
            
            # Deactivate immediately until activated in Phase 5
            set_batch_active_status(new_batch_id, 0)
            
            processed_records = load_companies_for_batch(new_batch_id)
            
            st.session_state.import_summary = {
                "batch_id": new_batch_id,
                "filename": st.session_state.onboarding_filename,
                "raw_count": len(df_raw),
                "final_count": final_count,
                "dedup_count": dedup_count,
                "normalizations": normalizations_run,
                "avg_icp": sum(c["icp_score"] for c in processed_records) / final_count if final_count > 0 else 0,
                "avg_opp": sum(c["gtm_opportunity_score"] for c in processed_records) / final_count if final_count > 0 else 0,
                "top_ind": Counter([c["Industry"] for c in processed_records]).most_common(1)[0][0] if final_count > 0 else "None",
                "quality_score": audit_dataset_health(df_raw, mapping)["quality_score"]
            }
            
            bar.progress(100)
            progress_text.write("**Complete!** Scoring complete.")
            st.session_state.onboarding_step = "activation"
            st.rerun()
            
        elif st.session_state.onboarding_step == "activation":
            st.markdown("### Dataset Activation (Phase 5)")
            summary = st.session_state.import_summary
            
            st.markdown(clean_html(f"""
                <div class="saas-card" style="border-top: 3px solid #22C55E;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:15px;">
                        <span style="color:#22C55E;">{SVG_ICONS['check-circle']}</span>
                        <span style="font-size:1.25rem; font-weight:700; color:#FFFFFF;">Dataset Processed Successfully</span>
                    </div>
                    <div style="font-size:0.9rem; color:#9CA3AF; margin-bottom:20px;">
                        Scoring, segmentation, and outreach recommendations have been calculated. Verify parameters below to activate this dataset.
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:25px;">
                        <table style="width:100%; font-size:0.9rem; border-collapse:collapse; color:#D1D5DB;">
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Dataset Version Name</td><td style="padding:8px 0; font-weight:600; color:#FFFFFF;">{summary['filename']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Accounts Processed</td><td style="padding:8px 0; font-weight:600; color:#FFFFFF;">{summary['final_count']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Data Quality Score</td><td style="padding:8px 0; font-weight:600; color:#10B981;">{summary['quality_score']}%</td></tr>
                        </table>
                        <table style="width:100%; font-size:0.9rem; border-collapse:collapse; color:#D1D5DB;">
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Average ICP Fit</td><td style="padding:8px 0; font-weight:600; color:#3B82F6;">{summary['avg_icp']:.1f}/100</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Average Opportunity Index</td><td style="padding:8px 0; font-weight:600; color:#22C55E;">{summary['avg_opp']:.1f}/100</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Top Industry Segment</td><td style="padding:8px 0; font-weight:600; color:#FFFFFF;">{summary['top_ind']}</td></tr>
                        </table>
                    </div>
                </div>
            """), unsafe_allow_html=True)
            
            st.markdown("#### Sample Account Scoring Preview")
            rec_id = summary['batch_id']
            preview_rec = load_companies_for_batch(rec_id)[:3]
            for r in preview_rec:
                st.markdown(f"- **{r['Company Name']}**: ICP Score: `{r['icp_score']}`, Intent Score: `{r['buying_signal_score']}`, Growth Score: `{r['market_opportunity_score']}`, Unified GTM Opportunity Score: `{r['gtm_opportunity_score']}` ({r['abm_tier']})")
                
            st.markdown("---")
            
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("Activate Dataset", use_container_width=True):
                    set_batch_active_status(summary['batch_id'], 1)
                    st.session_state.active_batch_id = summary['batch_id']
                    st.session_state.onboarding_step = "idle"
                    st.session_state.uploaded_df_raw = None
                    st.success("Dataset successfully activated!")
                    st.rerun()
            with col_act2:
                if st.button("Go to Command Center", use_container_width=True):
                    set_batch_active_status(summary['batch_id'], 1)
                    st.session_state.active_batch_id = summary['batch_id']
                    st.session_state.onboarding_step = "idle"
                    st.session_state.uploaded_df_raw = None
                    st.session_state.active_page = "Command Center"
                    st.rerun()
                    
    with tab_manager:
        st.markdown("### Dataset Manager")
        st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">Review and control activation states for all historical GTM runs stored in the SQLite database.</p>', unsafe_allow_html=True)
        
        all_batches = list_batches(only_active=False)
        if not all_batches:
            st.info("No datasets loaded in the database.")
        else:
            for b in all_batches:
                with st.container(border=True):
                    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns([3, 1, 1, 2, 2])
                    with m_col1:
                        st.markdown(f"**{b['source_filename']}**")
                        st.markdown(f"<span style='font-size:0.75rem; color:#64748B;'>ID: {b['batch_id']}</span>", unsafe_allow_html=True)
                    with m_col2:
                        status_label = "🟢 Active" if b["is_active"] == 1 else "🔴 Inactive"
                        st.write(status_label)
                    with m_col3:
                        st.write(f"{b['record_count']} accounts")
                    with m_col4:
                        st.write(f"Quality Score: **{b.get('quality_score', 100)}%**")
                        st.write(f"ICP: {b['average_icp']:.1f} | Opp: {b['average_opp_score']:.1f}")
                    with m_col5:
                        btn_lbl = "Deactivate" if b["is_active"] == 1 else "Activate"
                        if st.button(btn_lbl, key=f"mgr_tgl_{b['batch_id']}", use_container_width=True):
                            set_batch_active_status(b["batch_id"], 0 if b["is_active"] == 1 else 1)
                            if b["is_active"] == 1 and st.session_state.active_batch_id == b["batch_id"]:
                                st.session_state.active_batch_id = "None"
                            st.rerun()
                        if st.button("Delete", key=f"mgr_del_{b['batch_id']}", use_container_width=True):
                            delete_batch(b["batch_id"])
                            if st.session_state.active_batch_id == b["batch_id"]:
                                st.session_state.active_batch_id = "None"
                            st.rerun()
                            
    with tab_compare:
        st.markdown("### Compare Datasets")
        all_batches_comp = list_batches(only_active=False)
        if len(all_batches_comp) < 2:
            st.info("Please import at least 2 datasets to enable side-by-side comparison.")
        else:
            col_comp1, col_comp2 = st.columns(2)
            with col_comp1:
                dataset_a_id = st.selectbox(
                    "Select Baseline Dataset (A)", 
                    options=[b["batch_id"] for b in all_batches_comp], 
                    format_func=lambda x: next(b["source_filename"] for b in all_batches_comp if b["batch_id"] == x)
                )
            with col_comp2:
                dataset_b_id = st.selectbox(
                    "Select Comparison Dataset (B)", 
                    options=[b["batch_id"] for b in all_batches_comp], 
                    format_func=lambda x: next(b["source_filename"] for b in all_batches_comp if b["batch_id"] == x)
                )
                
            if dataset_a_id == dataset_b_id:
                st.warning("Please select two different datasets to compare.")
            else:
                df_a = pd.DataFrame(load_companies_for_batch(dataset_a_id))
                df_b = pd.DataFrame(load_companies_for_batch(dataset_b_id))
                
                meta_a = next(b for b in all_batches_comp if b["batch_id"] == dataset_a_id)
                meta_b = next(b for b in all_batches_comp if b["batch_id"] == dataset_b_id)
                
                count_a, count_b = len(df_a), len(df_b)
                icp_a, icp_b = df_a["icp_score"].mean(), df_b["icp_score"].mean()
                opp_a, opp_b = df_a["gtm_opportunity_score"].mean(), df_b["gtm_opportunity_score"].mean()
                q_a, q_b = meta_a.get("quality_score", 100), meta_b.get("quality_score", 100)
                
                diff_count = count_b - count_a
                diff_icp = icp_b - icp_a
                diff_opp = opp_b - opp_a
                diff_q = q_b - q_a
                
                st.markdown("#### Key Metrics Comparison")
                c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                with c_m1:
                    st.metric("Accounts Count", f"{count_b}", delta=f"{diff_count:+d}")
                with c_m2:
                    st.metric("Avg ICP Fit", f"{icp_b:.1f}", delta=f"{diff_icp:+.1f}")
                with c_m3:
                    st.metric("Avg Opportunity Index", f"{opp_b:.1f}", delta=f"{diff_opp:+.1f}")
                with c_m4:
                    st.metric("Data Quality Score", f"{q_b}%", delta=f"{diff_q:+.1f}%")
                    
                st.markdown("---")
                
                # Import Plotly Graph Objects for compare charts
                import plotly.graph_objects as go
                
                # Industry Sector Shift
                st.markdown("#### Industry Sector Distribution Shift (%)")
                ind_a = df_a["Industry"].value_counts(normalize=True).reset_index()
                ind_a.columns = ["Industry", "Baseline (A)"]
                ind_b = df_b["Industry"].value_counts(normalize=True).reset_index()
                ind_b.columns = ["Industry", "Comparison (B)"]
                ind_comp = pd.merge(ind_a, ind_b, on="Industry", how="outer").fillna(0)
                ind_comp["Baseline (A)"] *= 100
                ind_comp["Comparison (B)"] *= 100
                
                fig_ind_comp = go.Figure()
                fig_ind_comp.add_trace(go.Bar(x=ind_comp["Industry"], y=ind_comp["Baseline (A)"], name=f"{meta_a['source_filename']} (A)", marker_color="#3B82F6"))
                fig_ind_comp.add_trace(go.Bar(x=ind_comp["Industry"], y=ind_comp["Comparison (B)"], name=f"{meta_b['source_filename']} (B)", marker_color="#10B981"))
                fig_ind_comp.update_layout(barmode="group", height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#D1D5DB")
                st.plotly_chart(fig_ind_comp, use_container_width=True)
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown("#### Geographic Distribution Shift (%)")
                    loc_a = df_a["Location"].value_counts(normalize=True).reset_index()
                    loc_a.columns = ["Location", "Baseline (A)"]
                    loc_b = df_b["Location"].value_counts(normalize=True).reset_index()
                    loc_b.columns = ["Location", "Comparison (B)"]
                    loc_comp = pd.merge(loc_a, loc_b, on="Location", how="outer").fillna(0)
                    loc_comp["Baseline (A)"] *= 100
                    loc_comp["Comparison (B)"] *= 100
                    
                    fig_loc_comp = go.Figure()
                    fig_loc_comp.add_trace(go.Bar(x=loc_comp["Location"], y=loc_comp["Baseline (A)"], name="A (%)", marker_color="#3B82F6"))
                    fig_loc_comp.add_trace(go.Bar(x=loc_comp["Location"], y=loc_comp["Comparison (B)"], name="B (%)", marker_color="#10B981"))
                    fig_loc_comp.update_layout(barmode="group", height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#D1D5DB")
                    st.plotly_chart(fig_loc_comp, use_container_width=True)
                    
                with col_s2:
                    st.markdown("#### ABM Tier Shift (%)")
                    tier_a = df_a["abm_tier"].value_counts(normalize=True).reset_index()
                    tier_a.columns = ["Tier", "Baseline (A)"]
                    tier_b = df_b["abm_tier"].value_counts(normalize=True).reset_index()
                    tier_b.columns = ["Tier", "Comparison (B)"]
                    tier_comp = pd.merge(tier_a, tier_b, on="Tier", how="outer").fillna(0)
                    tier_comp["Baseline (A)"] *= 100
                    tier_comp["Comparison (B)"] *= 100
                    
                    fig_tier_comp = go.Figure()
                    fig_tier_comp.add_trace(go.Bar(x=tier_comp["Tier"], y=tier_comp["Baseline (A)"], name="A (%)", marker_color="#3B82F6"))
                    fig_tier_comp.add_trace(go.Bar(x=tier_comp["Tier"], y=tier_comp["Comparison (B)"], name="B (%)", marker_color="#10B981"))
                    fig_tier_comp.update_layout(barmode="group", height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#D1D5DB")
                    st.plotly_chart(fig_tier_comp, use_container_width=True)

# ------------------ NAVIGATION CONTROL & ONBOARDING LOCK ------------------
if st.session_state.onboarding_step != "idle" and nav_choice != "Data Integration":
    # Show warning redirect overlay
    st.markdown(clean_html(f"""
        <div style="background-color:rgba(239, 68, 68, 0.08); border:1px solid #EF444450; padding:32px; border-radius:12px; margin-top:20px; text-align:center;">
            <div style="font-size:2rem; margin-bottom:10px; color:#EF4444; font-weight:700;">⚠️ Onboarding In Progress</div>
            <div style="font-size:1.15rem; color:#E5E7EB; margin-bottom:15px;">
                **Current Step:** {st.session_state.onboarding_step.title()}
            </div>
            <div style="font-size:0.95rem; color:#9CA3AF; margin-bottom:20px; max-width:600px; margin-left:auto; margin-right:auto;">
                Please complete the dataset import mapping and validation steps in the <b>Data Integration</b> tab before attempting to access other analytics dashboards.
            </div>
        </div>
    """), unsafe_allow_html=True)
    
    if st.button("Go to Data Integration", use_container_width=True):
        st.session_state.active_page = "Data Integration"
        st.rerun()
else:
    # Router logic
    if nav_choice == "Data Integration":
        render_data_integration_wizard()
    elif nav_choice == "Command Center":
        render_active_dataset_header(active_meta)
        render_command_center(df_active)
    elif nav_choice == "Analytics":
        render_active_dataset_header(active_meta)
        render_analytics(df_active)
    elif nav_choice == "Account Prioritization":
        render_active_dataset_header(active_meta)
        # Pass weights configuration
        weights = {
            "industry": st.session_state.get("wt_ind", 25),
            "funding": st.session_state.get("wt_fund", 25),
            "employee": st.session_state.get("wt_emp", 20),
            "hiring": st.session_state.get("wt_hiring", 20),
            "location": st.session_state.get("wt_loc", 10)
        }
        render_account_analysis(df_active, weights)
    elif nav_choice == "Market Intelligence":
        render_active_dataset_header(active_meta)
        render_market_intelligence(df_active)
    elif nav_choice == "Settings & Scoring":
        render_active_dataset_header(active_meta)
        render_settings_scoring(df_active)
