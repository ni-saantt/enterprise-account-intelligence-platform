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
    clone_batch
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
from dashboard.overview import render_overview
from dashboard.account_analysis import render_account_analysis
from dashboard.revenue_market_intelligence import render_revenue_market_intelligence

# Import ingestion 2.0 modules
from utils.schema_registry import CANONICAL_COLUMNS
from utils.column_mapper import map_columns, get_unmapped_required
from utils.csv_validator import normalize_cell_value, audit_dataset_health, validate_scoring_sanity
from utils.duplicate_detector import resolve_duplicates

# Import styling configurations
from utils.constants import SAAS_THEME_CSS, SVG_ICONS, ICP_FACTOR_MAX_POINTS
from utils.helpers import generate_sample_data, to_excel_bytes, to_csv_bytes

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
    st.session_state.active_batch_id = None
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = "idle"  # idle, mapping, audit, progress, summary
if "uploaded_df_raw" not in st.session_state:
    st.session_state.uploaded_df_raw = None
if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {}
if "dedup_strategy" not in st.session_state:
    st.session_state.dedup_strategy = "Keep First"
if "onboarding_filename" not in st.session_state:
    st.session_state.onboarding_filename = ""
if "import_summary" not in st.session_state:
    st.session_state.import_summary = {}
if "nav_override" not in st.session_state:
    st.session_state.nav_override = None

# Redirect callback helper
if st.session_state.nav_override:
    nav_choice_default = st.session_state.nav_override
    st.session_state.nav_override = None
else:
    nav_choice_default = "Command Center"

# ------------------ SIDEBAR CONTROL PANEL ------------------
st.sidebar.markdown(
    '<div style="text-align: center; margin-bottom: 25px; margin-top: 15px;">'
    '<h2 style="color: #FFFFFF; font-weight: 800; font-size:1.55rem; margin-bottom: 0;">ENTERPRISE GTM</h2>'
    '<p style="color: #64748B; font-size: 0.8rem; margin-top: 3px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Sales Account Intelligence</p>'
    '</div>', 
    unsafe_allow_html=True
)

# 1. Navigation Panel
st.sidebar.markdown('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Navigation</p>', unsafe_allow_html=True)
nav_choice = st.sidebar.radio(
    label="Navigation",
    options=[
        "Command Center",
        "Overview Analytics",
        "Account Prioritization",
        "Revenue & Market"
    ],
    index=["Command Center", "Overview Analytics", "Account Prioritization", "Revenue & Market"].index(nav_choice_default),
    label_visibility="collapsed"
)

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #253047;"></div>', unsafe_allow_html=True)

# 2. Upload / Ingestion Section
st.sidebar.markdown('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">Data Ingestion</p>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload Company CSV", type=["csv"], label_visibility="collapsed")

# Manage upload file triggers
if uploaded_file is not None and st.session_state.onboarding_step == "idle":
    try:
        # Load CSV into state
        df_raw = pd.read_csv(uploaded_file)
        st.session_state.uploaded_df_raw = df_raw
        st.session_state.onboarding_filename = uploaded_file.name
        # Run auto mapper
        st.session_state.column_mapping = map_columns(df_raw.columns)
        st.session_state.onboarding_step = "mapping"
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to parse CSV: {str(e)}")

# Active Batch Management controls
batches = list_batches()

if not batches:
    # If database is completely empty, let them load default sample startups
    if st.sidebar.button("Load Demo Dataset", use_container_width=True):
        sample_path = os.path.join("data", "sample_companies.csv")
        if not os.path.exists(sample_path):
            generate_sample_data(sample_path)
            
        df_sample = pd.read_csv(sample_path)
        default_weights = {"industry": 25, "funding": 25, "employee": 20, "hiring": 20, "location": 10}
        
        # In demo mode, skip onboarding steps
        processed = []
        for _, row in df_sample.iterrows():
            c = {
                "Company Name": row["Company Name"], "Industry": row["Industry"],
                "Funding Stage": row["Funding Stage"], "Employee Count": int(row["Employee Count"]),
                "Location": row["Location"], "Hiring Activity": row["Hiring Activity"],
                "Recent Funding": row["Recent Funding"], "Expansion Status": row["Expansion Status"]
            }
            # Calculate metrics
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
        save_company_batch(processed, demo_id, source_filename="sample_companies.csv")
        st.session_state.active_batch_id = demo_id
        st.rerun()
else:
    # Select active segment
    batch_options = {b["batch_id"]: f"{b['source_filename']} ({b['record_count']} acc)" for b in batches}
    selected_batch_id = st.sidebar.selectbox(
        "Active Segment/Batch",
        options=list(batch_options.keys()),
        format_func=lambda x: batch_options.get(x, x)
    )
    
    if st.session_state.active_batch_id is None or st.session_state.active_batch_id not in batch_options:
        st.session_state.active_batch_id = selected_batch_id
    elif selected_batch_id != st.session_state.active_batch_id:
        st.session_state.active_batch_id = selected_batch_id
        
    # Active Batch Stats Card in Sidebar
    active_meta = next((b for b in batches if b["batch_id"] == st.session_state.active_batch_id), None)
    if active_meta:
        st.sidebar.markdown(f"""
            <div style="background-color:#1A2235; border:1px solid #253047; padding:12px; border-radius:8px; margin-top:8px;">
                <div style="font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.03em;">Active Segment Audit</div>
                <div style="font-size:0.85rem; color:#FFFFFF; font-weight:700; margin-top:4px;">{active_meta['source_filename']}</div>
                <div style="font-size:0.8rem; color:#9CA3AF; margin-top:6px;">
                    • <b>Accounts:</b> {active_meta['record_count']}<br>
                    • <b>Avg ICP:</b> {active_meta['average_icp']:.1f}<br>
                    • <b>Avg Opportunity:</b> {active_meta['average_opp_score']:.1f}<br>
                    • <b>Top Segment:</b> {active_meta['top_industry']}<br>
                    • <b>Imported:</b> {active_meta['created_at'].split()[0]}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. Batch Workspace Manager Actions
    st.sidebar.markdown('<p style="font-weight:700; font-size:0.75rem; color:#4B5563; text-transform:uppercase; letter-spacing:0.05em; margin-top:15px; margin-bottom:5px;">Batch Workspace Actions</p>', unsafe_allow_html=True)
    with st.sidebar.expander("Workspace Actions"):
        # Rename Batch
        new_batch_name = st.text_input("New Batch Name", placeholder="Enter name...")
        if st.button("Rename Batch", use_container_width=True) and new_batch_name:
            new_id = rename_batch(st.session_state.active_batch_id, new_batch_name)
            st.session_state.active_batch_id = new_id
            st.rerun()
            
        # Clone Batch
        clone_name_input = st.text_input("Clone Name", placeholder="Enter clone name...")
        if st.button("Clone Batch", use_container_width=True) and clone_name_input:
            new_clone_id = clone_batch(st.session_state.active_batch_id, clone_name_input)
            st.session_state.active_batch_id = new_clone_id
            st.rerun()
            
        # Export Active Batch
        st.markdown('<div style="margin: 8px 0; border-top:1px solid #253047;"></div>', unsafe_allow_html=True)
        active_records = load_companies_for_batch(st.session_state.active_batch_id)
        if active_records:
            df_active_export = pd.DataFrame(active_records)
            st.download_button(
                label="Export Batch (Excel)",
                data=to_excel_bytes(df_active_export),
                file_name=f"{active_meta['source_filename']}_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        # Delete Batch
        if st.button("Delete Active Batch", use_container_width=True):
            delete_batch(st.session_state.active_batch_id)
            st.session_state.active_batch_id = None
            st.rerun()

st.sidebar.markdown('<div style="margin: 20px 0; border-top: 1px solid #253047;"></div>', unsafe_allow_html=True)

# 4. Dynamic ICP Weights Customizer
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
                "industry": wt_ind, "funding": wt_fund, "employee": wt_emp, "hiring": wt_hiring, "location": wt_loc
            }
            
            delete_batch(st.session_state.active_batch_id)
            new_batch_id = process_and_save_data(df_raw, base_name, weights)
            st.session_state.active_batch_id = new_batch_id
            st.rerun()


# ------------------ LOAD AND ROUTE PAGE DATA ------------------
if st.session_state.active_batch_id:
    batch_records = load_companies_for_batch(st.session_state.active_batch_id)
    df_active = pd.DataFrame(batch_records)
else:
    df_active = pd.DataFrame()

# ------------------ MAIN CONTAINER ROUTING & ONBOARDING WIZARD ------------------
if st.session_state.onboarding_step != "idle":
    st.markdown('<h1 style="color:#FFFFFF;">Data Onboarding Wizard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:#64748B; font-size:1rem; margin-top:2px;">Configuring ingestion mapping and auditing dataset quality for <b>{st.session_state.onboarding_filename}</b>.</p>', unsafe_allow_html=True)
    
    # ------------------ STEP 1: COLUMN MAPPING ------------------
    if st.session_state.onboarding_step == "mapping":
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-card-title">Column Mapping Setup</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">Validate and edit column mapping parameters. Standard columns must map to raw CSV headers.</p>', unsafe_allow_html=True)
        
        # Draw columns matching config
        raw_cols = st.session_state.uploaded_df_raw.columns.tolist()
        mapping = st.session_state.column_mapping.copy()
        
        col_left_map, col_right_map = st.columns(2)
        
        with col_left_map:
            st.markdown('<div style="font-weight:700; font-size:0.85rem; color:#9CA3AF; margin-bottom:10px;">Raw CSV Header</div>', unsafe_allow_html=True)
            for idx, raw in enumerate(raw_cols):
                # Calculate default selection
                default_canon = mapping.get(raw)
                st.text(f"• {raw}")
                
        with col_right_map:
            st.markdown('<div style="font-weight:700; font-size:0.85rem; color:#9CA3AF; margin-bottom:10px;">Maps to Standard Header</div>', unsafe_allow_html=True)
            for idx, raw in enumerate(raw_cols):
                default_canon = mapping.get(raw)
                options = ["None"] + CANONICAL_COLUMNS
                sel_idx = options.index(default_canon) if default_canon in options else 0
                
                selected = st.selectbox(
                    label=f"Map {raw}",
                    options=options,
                    index=sel_idx,
                    key=f"map_sel_{raw}",
                    label_visibility="collapsed"
                )
                
                # Save override
                st.session_state.column_mapping[raw] = selected if selected != "None" else None
                
        # Validate Required Columns
        unmapped = get_unmapped_required(st.session_state.column_mapping)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if unmapped:
            st.markdown(f"""
                <div style="background-color:rgba(239, 68, 68, 0.1); border:1px solid #EF4444; border-radius:8px; padding:16px; margin-bottom:20px; color:#EF4444; font-size:0.9rem;">
                    <div style="font-weight:700; margin-bottom:5px;">We couldn't map the following required fields:</div>
                    <ul style="margin:5px 0 10px 20px;">
                        {"".join([f"<li>{c}</li>" for c in unmapped])}
                    </ul>
                    <b>Detected columns:</b> {', '.join([f"'{c}'" for c in raw_cols])}<br>
                    Please map these required fields manually using the dropdowns above.
                </div>
            """, unsafe_allow_html=True)
            
            st.button("Next: Audit Dataset", disabled=True)
        else:
            st.markdown(f"""
                <div style="background-color:rgba(34, 197, 94, 0.1); border:1px solid #22C55E; border-radius:8px; padding:16px; margin-bottom:20px; color:#22C55E; font-size:0.9rem;">
                    All required GTM columns mapped successfully. Click below to review the data quality report.
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Next: Audit Dataset"):
                st.session_state.onboarding_step = "audit"
                st.rerun()
                
        if st.button("Cancel Import"):
            st.session_state.onboarding_step = "idle"
            st.session_state.uploaded_df_raw = None
            st.rerun()

    # ------------------ STEP 2: DATASET HEALTH AUDIT ------------------
    elif st.session_state.onboarding_step == "audit":
        audit = audit_dataset_health(st.session_state.uploaded_df_raw, st.session_state.column_mapping)
        
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-card-title">Dataset Health Report</div>', unsafe_allow_html=True)
        
        score = audit["quality_score"]
        score_color = "#22C55E" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
        
        col_l_aud, col_r_aud = st.columns([1, 2])
        
        with col_l_aud:
            st.markdown(f"""
                <div style="text-align:center; padding:20px; border:1px solid #253047; border-radius:10px; background-color:#111827;">
                    <div style="font-size:0.8rem; color:#64748B; font-weight:700; text-transform:uppercase;">Data Quality Score</div>
                    <div style="font-size:3.5rem; font-weight:800; color:{score_color}; margin:10px 0;">{score}%</div>
                    <div style="font-size:0.85rem; color:#E5E7EB;"><b>{audit['total_records']}</b> total rows evaluated</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_r_aud:
            st.markdown('<div style="font-weight:600; color:#FFFFFF; margin-bottom:8px;">Quality Metrics Summary:</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <table style="width:100%; font-size:0.88rem; border-collapse:collapse; color:#9CA3AF;">
                    <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Duplicate Companies</td><td style="padding:6px 0; color:#EF4444;">{audit['duplicate_count']} matches flagged</td></tr>
                    <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Employee Counts</td><td style="padding:6px 0;">{audit['missing_counts'].get('Employee Count', 0)} rows</td></tr>
                    <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Industries</td><td style="padding:6px 0;">{audit['missing_counts'].get('Industry', 0)} rows</td></tr>
                    <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Funding Stages</td><td style="padding:6px 0;">{audit['missing_counts'].get('Funding Stage', 0)} rows</td></tr>
                    <tr style="border-bottom:1px solid #253047;"><td style="padding:6px 0; font-weight:600; color:#FFFFFF;">Missing Locations</td><td style="padding:6px 0;">{audit['missing_counts'].get('Location', 0)} rows</td></tr>
                </table>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Duplicate Resolution Settings
        st.markdown('<div class="saas-card">', unsafe_allow_html=True)
        st.markdown('<div class="saas-card-title">Duplicate Resolution Strategy</div>', unsafe_allow_html=True)
        st.session_state.dedup_strategy = st.selectbox(
            "Select Resolution Logic",
            options=["Keep First", "Keep Latest", "Merge Records"],
            help="Keep First retains the first row. Keep Latest takes the last row. Merge Records merges duplicates by taking the maximum size and non-empty parameters."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Health Warnings list
        if audit["warnings"]:
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            st.markdown('<div class="saas-card-title">Data Quality Alerts</div>', unsafe_allow_html=True)
            for w in audit["warnings"][:6]: # Limit warnings view
                st.markdown(f'<div style="font-size:0.85rem; color:#F59E0B; margin-bottom:5px;">⚠ {w}</div>', unsafe_allow_html=True)
            if len(audit["warnings"]) > 6:
                st.text(f"...and {len(audit['warnings']) - 6} other minor missing fields.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Ingestion triggers
        col_b1, col_b2 = st.columns([1, 10])
        with col_b1:
            if st.button("Import & Score"):
                st.session_state.onboarding_step = "progress"
                st.rerun()
        with col_b2:
            if st.button("Back to Mapping"):
                st.session_state.onboarding_step = "mapping"
                st.rerun()

    # ------------------ STEP 3: PROGRESS TRACKER ------------------
    elif st.session_state.onboarding_step == "progress":
        st.markdown('<div class="saas-card" style="text-align:center; padding:40px 20px;">', unsafe_allow_html=True)
        progress_text = st.empty()
        bar = st.progress(0)
        
        # Steps simulation + processing
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
            time.sleep(0.3)  # Visually smooth transitions
            
        # Running Ingestion 2.0 deduplication and normalizations
        df_raw = st.session_state.uploaded_df_raw
        mapping = st.session_state.column_mapping
        
        # Get raw company column name
        raw_company_col = next((r for r, c in mapping.items() if c == "Company Name"), None)
        
        # Deduplicate
        df_dedup = resolve_duplicates(df_raw, raw_company_col, st.session_state.dedup_strategy)
        
        # Process and normalize value records
        weights = {"industry": wt_ind, "funding": wt_fund, "employee": wt_emp, "hiring": wt_hiring, "location": wt_loc}
        processed = []
        normalizations_run = 0
        
        for _, row in df_dedup.iterrows():
            # Build clean dictionary matching standard headers
            c_dict = {}
            for raw, canon in mapping.items():
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
            
        # Save to SQLite
        clean_filename = st.session_state.onboarding_filename.replace(".csv", "")
        new_batch_id = f"{clean_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        save_company_batch(processed, new_batch_id, source_filename=uploaded_file.name)
        
        # Save summary details to session state
        st.session_state.import_summary = {
            "batch_id": new_batch_id,
            "filename": uploaded_file.name,
            "raw_count": len(df_raw),
            "final_count": len(processed),
            "dedup_count": len(df_raw) - len(df_dedup),
            "normalizations": normalizations_run,
            "avg_icp": sum(c["icp_score"] for c in processed) / len(processed) if processed else 0,
            "avg_opp": sum(c["gtm_opportunity_score"] for c in processed) / len(processed) if processed else 0,
            "top_ind": Counter([c["Industry"] for c in processed]).most_common(1)[0][0] if processed else "None"
        }
        
        bar.progress(100)
        progress_text.write("**Complete!** Segment generated.")
        
        # Automatically update active batch
        st.session_state.active_batch_id = new_batch_id
        st.session_state.onboarding_step = "summary"
        st.rerun()

    # ------------------ STEP 4: IMPORT SUMMARY REPORT CARD ------------------
    elif st.session_state.onboarding_step == "summary":
        summary = st.session_state.import_summary
        
        st.markdown(f"""
            <div class="saas-card" style="border-top: 3px solid #22C55E;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:15px;">
                    <span style="color:#22C55E;">{SVG_ICONS['check-circle']}</span>
                    <span style="font-size:1.25rem; font-weight:700; color:#FFFFFF;">Dataset Imported Successfully</span>
                </div>
                <div style="font-size:0.9rem; color:#9CA3AF; margin-bottom:20px;">
                    Segment batch is fully calculated, indexed, and cached in the persistence SQLite database.
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:25px;">
                    <table style="width:100%; font-size:0.9rem; border-collapse:collapse; color:#D1D5DB;">
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Dataset Name</td><td style="padding:8px 0; font-weight:600; color:#FFFFFF;">{summary['filename']}</td></tr>
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Total Records Imported</td><td style="padding:8px 0; font-weight:600; color:#FFFFFF;">{summary['final_count']} companies</td></tr>
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Duplicates Removed</td><td style="padding:8px 0; color:#EF4444;">{summary['dedup_count']} rows cleaned</td></tr>
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Value Normalizations</td><td style="padding:8px 0; color:#F59E0B;">{summary['normalizations']} cells corrected</td></tr>
                    </table>
                    <table style="width:100%; font-size:0.9rem; border-collapse:collapse; color:#D1D5DB;">
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Average ICP Fit</td><td style="padding:8px 0; font-weight:600; color:#3B82F6;">{summary['avg_icp']:.1f}/100</td></tr>
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Average GTM Index</td><td style="padding:8px 0; font-weight:600; color:#22C55E;">{summary['avg_opp']:.1f}/100</td></tr>
                        <tr style="border-bottom:1px solid #253047;"><td style="padding:8px 0; color:#9CA3AF;">Top Industry Segment</td><td style="padding:8px 0; font-weight:600; color:#FFFFFF;">{summary['top_ind']}</td></tr>
                    </table>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Imported Accounts"):
            # Clear onboarding states and redirect
            st.session_state.onboarding_step = "idle"
            st.session_state.uploaded_df_raw = None
            st.session_state.nav_override = "Account Prioritization"
            st.rerun()

else:
    # ------------------ STANDARD SAAS NAVIGATION ROUTER ------------------
    if nav_choice == "Command Center":
        render_command_center(df_active)
    elif nav_choice == "Overview Analytics":
        render_overview(df_active)
    elif nav_choice == "Account Prioritization":
        render_account_analysis(df_active)
    elif nav_choice == "Revenue & Market":
        render_revenue_market_intelligence(df_active)
