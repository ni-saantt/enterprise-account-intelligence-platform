"""
Settings and Scoring Configuration Page for Enterprise GTM Account Intelligence Platform.
Manages ICP weights, recalculations, and validation criteria.
"""

import streamlit as st
import pandas as pd
from database.database import list_batches, delete_batch, set_batch_active_status, load_companies_for_batch
from utils.constants import SVG_ICONS, ICP_FACTOR_MAX_POINTS
from utils.helpers import clean_html

def render_settings_scoring(df: pd.DataFrame) -> None:
    """Renders the ICP weights sliders, recalculation, and database validation configurations."""
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">Settings & Scoring</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Configure scoring sub-weights, modify ABM tier limits, and audit dataset schema rules.</p>', unsafe_allow_html=True)
    
    # Initialize weights session states if not present
    if "wt_ind" not in st.session_state:
        st.session_state.wt_ind = 25
    if "wt_fund" not in st.session_state:
        st.session_state.wt_fund = 25
    if "wt_emp" not in st.session_state:
        st.session_state.wt_emp = 20
    if "wt_hiring" not in st.session_state:
        st.session_state.wt_hiring = 20
    if "wt_loc" not in st.session_state:
        st.session_state.wt_loc = 10
        
    tab_weights, tab_validation, tab_tiers = st.tabs([
        "ICP Weights Manager", 
        "Data Validation Rules", 
        "ABM Tier Configurations"
    ])
    
    with tab_weights:
        st.markdown("### Configure Scoring Weights")
        st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">Manage the percentage weight allocated to each GTM fit parameter. Weights must sum to exactly 100%.</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            wt_ind = st.slider("Industry Match Weight (%)", 0, 50, st.session_state.wt_ind, key="slider_wt_ind")
            wt_fund = st.slider("Funding Stage Weight (%)", 0, 50, st.session_state.wt_fund, key="slider_wt_fund")
            wt_emp = st.slider("Employee Count Weight (%)", 0, 50, st.session_state.wt_emp, key="slider_wt_emp")
            wt_hiring = st.slider("Hiring Activity Weight (%)", 0, 50, st.session_state.wt_hiring, key="slider_wt_hiring")
            wt_loc = st.slider("Location Match Weight (%)", 0, 50, st.session_state.wt_loc, key="slider_wt_loc")
            
            # Sync session states
            st.session_state.wt_ind = wt_ind
            st.session_state.wt_fund = wt_fund
            st.session_state.wt_emp = wt_emp
            st.session_state.wt_hiring = wt_hiring
            st.session_state.wt_loc = wt_loc
            
            sum_wts = wt_ind + wt_fund + wt_emp + wt_hiring + wt_loc
            
        with col2:
            st.markdown(clean_html(f"""
                <div class="saas-card" style="margin-top: 25px;">
                    <div class="saas-card-title">Weights Validation</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF;">Total Configured Sum:</div>
                    <div style="font-size: 3rem; font-weight: 800; color: {'#10B981' if sum_wts == 100 else '#EF4444'}; margin: 10px 0;">
                        {sum_wts}%
                    </div>
                    <div style="font-size: 0.88rem; color: #9CA3AF;">
                        {'✅ Weights are balanced and sum to 100%.' if sum_wts == 100 else '❌ Weights sum must equal exactly 100% to save or recalculate.'}
                    </div>
                </div>
            """), unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Trigger Recalculate Scores
        st.markdown("#### Recalculate Scoring Profile")
        active_batch_id = st.session_state.get("active_batch_id", "None")
        if active_batch_id == "None":
            st.info("No active dataset selected. Select an active dataset in the sidebar or upload one in Data Integration to enable recalculations.")
        else:
            if sum_wts == 100:
                if st.button("🔄 Recalculate Scores for Active Dataset", use_container_width=True):
                    # Circular import resolution
                    from app import process_and_save_data
                    
                    raw_records = load_companies_for_batch(active_batch_id)
                    if raw_records:
                        df_raw = pd.DataFrame(raw_records)
                        
                        # Find the baseline metadata info to preserve name and quality score
                        batches = list_batches(only_active=False)
                        meta = next((b for b in batches if b["batch_id"] == active_batch_id), None)
                        base_name = meta["source_filename"] if meta else "recalculated_dataset.csv"
                        q_score = meta["quality_score"] if meta else 100
                        
                        # Recalculate
                        delete_batch(active_batch_id)
                        new_batch_id, _, _, _ = process_and_save_data(
                            df_raw=df_raw,
                            source_filename=base_name,
                            weights={
                                "industry": wt_ind, "funding": wt_fund, "employee": wt_emp, "hiring": wt_hiring, "location": wt_loc
                            }
                        )
                        set_batch_active_status(new_batch_id, 1)
                        st.session_state.active_batch_id = new_batch_id
                        st.success("Dataset recalculated and saved successfully!")
                        st.rerun()
            else:
                st.button("🔄 Recalculate Scores for Active Dataset", disabled=True, use_container_width=True)
                st.error("Weights must equal 100% to run recalculations.")

    with tab_validation:
        st.markdown("### Data Validation Schema")
        st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">The following required columns are enforced and validated during the ingestion phase.</p>', unsafe_allow_html=True)
        
        validation_data = [
            {"Standard Column": "Company Name", "Data Type": "Text (Normalized)", "Enforce Rule": "Required, Non-Empty"},
            {"Standard Column": "Industry", "Data Type": "Text (Categorized)", "Enforce Rule": "Required, Map to ICP List"},
            {"Standard Column": "Funding Stage", "Data Type": "Text (Categorized)", "Enforce Rule": "Required, Map to Growth Stages"},
            {"Standard Column": "Employee Count", "Data Type": "Integer", "Enforce Rule": "Required, Strip commas/formatters"},
            {"Standard Column": "Location", "Data Type": "Text (Categorized)", "Enforce Rule": "Required, Map to regional HQ codes"},
            {"Standard Column": "Hiring Activity", "Data Type": "Text (Categorized)", "Enforce Rule": "Required, High/Medium/Low/None"},
            {"Standard Column": "Recent Funding", "Data Type": "Text (Boolean)", "Enforce Rule": "Required, Yes/No"},
            {"Standard Column": "Expansion Status", "Data Type": "Text (Categorized)", "Enforce Rule": "Required, Expanding/Stable/Contracting"}
        ]
        
        st.table(pd.DataFrame(validation_data))

    with tab_tiers:
        st.markdown("### Configure ICP Range & ABM Thresholds")
        st.markdown('<p style="font-size:0.88rem; color:#9CA3AF;">Visual representations of the GTM scoring classifications.</p>', unsafe_allow_html=True)
        
        st.markdown(clean_html(f"""
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px; margin-top:20px;">
                <div style="background-color:#111827; border:1px solid #253047; padding:20px; border-radius:8px; border-left:4px solid #22C55E;">
                    <div style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase;">Tier 1 Target Range</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; margin-top:8px;">80 - 100</div>
                    <div style="font-size:0.85rem; color:#9CA3AF; margin-top:4px;">Highly aligned ideal customer profile. High SDR touch.</div>
                </div>
                <div style="background-color:#111827; border:1px solid #253047; padding:20px; border-radius:8px; border-left:4px solid #F59E0B;">
                    <div style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase;">Tier 2 Target Range</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; margin-top:8px;">60 - 79</div>
                    <div style="font-size:0.85rem; color:#9CA3AF; margin-top:4px;">Moderate alignment. Automated and mid-touch sequences.</div>
                </div>
                <div style="background-color:#111827; border:1px solid #253047; padding:20px; border-radius:8px; border-left:4px solid #64748B;">
                    <div style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase;">Tier 3 Target Range</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; margin-top:8px;">0 - 59</div>
                    <div style="font-size:0.85rem; color:#9CA3AF; margin-top:4px;">Low alignment. Low priority monthly sequences.</div>
                </div>
            </div>
        """), unsafe_allow_html=True)
