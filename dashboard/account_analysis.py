"""
Account Analysis Page for Enterprise GTM Account Intelligence Platform.
Implements the interactive prioritization table and the tabbed account deep-dive profile inspector.
Removes all raw HTML tables in the main list to prevent search block overlay bugs.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from utils.constants import SVG_ICONS
from utils.helpers import to_excel_bytes, to_csv_bytes

def render_account_analysis(df: pd.DataFrame) -> None:
    """Renders the account prioritization grid and detail tab-viewer."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">Account Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Filter, segment, export, and audit detailed account execution playbooks.</p>', unsafe_allow_html=True)
    
    # ------------------ SAAS FILTERS BLOCK ------------------
    with st.container(border=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        with f_col1:
            # Search Box - single text input, styled via dark CSS
            search_query = st.text_input("Search Company", value="", placeholder="Search by name...", label_visibility="collapsed")
        with f_col2:
            selected_tiers = st.multiselect("ABM Tier", options=["Tier 1", "Tier 2", "Tier 3"])
        with f_col3:
            selected_industries = st.multiselect("Industry Vertical", options=sorted(df["Industry"].unique()))
        with f_col4:
            selected_priorities = st.multiselect("Outreach Priority", options=["High", "Medium", "Low"])
    
    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df["Company Name"].str.contains(search_query, case=False, na=False)]
    if selected_tiers:
        filtered_df = filtered_df[filtered_df["abm_tier"].isin(selected_tiers)]
    if selected_industries:
        filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]
    if selected_priorities:
        filtered_df = filtered_df[filtered_df["priority_level"].isin(selected_priorities)]
        
    # Active filter information
    active_filters_count = (1 if search_query else 0) + len(selected_tiers) + len(selected_industries) + len(selected_priorities)
    
    # Grid metrics summary row
    act_col1, act_col2 = st.columns([8, 4])
    with act_col1:
        st.markdown(
            f'<div style="font-size: 0.9rem; color: #9CA3AF; margin-top: 10px;">'
            f'Showing <b>{len(filtered_df)}</b> of <b>{len(df)}</b> accounts. Active filters: <b>{active_filters_count}</b>'
            f'</div>', 
            unsafe_allow_html=True
        )
    with act_col2:
        # Excel/CSV download buttons
        dl_col1, dl_col2 = st.columns(2)
        
        export_df = filtered_df[[
            "Company Name", "Industry", "Funding Stage", "Employee Count", "Location", 
            "Hiring Activity", "Recent Funding", "Expansion Status", "icp_score", 
            "abm_tier", "buying_signal_score", "buying_signal_level", "market_opportunity_score",
            "gtm_opportunity_score", "gtm_opportunity_level", "priority_level", 
            "primary_contact", "secondary_contact"
        ]].copy()
        
        with dl_col1:
            st.download_button(
                label="Export Excel",
                data=to_excel_bytes(export_df),
                file_name="gtm_intelligence_accounts.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="Export CSV",
                data=to_csv_bytes(export_df),
                file_name="gtm_intelligence_accounts.csv",
                mime="text/csv",
                use_container_width=True
            )

    # ------------------ NATIVE ENTERPRISE DATAFRAME ------------------
    # Pre-formatting dataframe for native rendering (no HTML raw tags visible!)
    grid_df = filtered_df[[
        "Company Name", "Industry", "icp_score", "buying_signal_score", 
        "gtm_opportunity_score", "abm_tier", "priority_level", "primary_contact"
    ]].copy()
    
    # Rename columns for presentation
    grid_df.columns = [
        "Company", "Industry", "ICP Fit", "Buying Signal Score", 
        "Opportunity Score", "ABM Tier", "Outreach Priority", "Primary Target Contact"
    ]
    
    # Render interactive st.dataframe with custom configs (progress bars for scores!)
    st.dataframe(
        grid_df,
        column_config={
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "Industry": st.column_config.TextColumn("Industry", width="small"),
            "ICP Fit": st.column_config.ProgressColumn("ICP Fit Score", min_value=0, max_value=100, format="%d"),
            "Buying Signal Score": st.column_config.ProgressColumn("Buying Signal", min_value=0, max_value=100, format="%d"),
            "Opportunity Score": st.column_config.ProgressColumn("GTM Opportunity Score", min_value=0, max_value=100, format="%d"),
            "ABM Tier": st.column_config.TextColumn("ABM Tier", width="small"),
            "Outreach Priority": st.column_config.TextColumn("Outreach Priority", width="small"),
            "Primary Target Contact": st.column_config.TextColumn("Target Contact", width="medium")
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")

    # ------------------ TABBED DEEP DIVE AUDITOR ------------------
    st.markdown('<h2 style="color:#FFFFFF; margin-top:10px; margin-bottom:12px;">Account Auditor</h2>', unsafe_allow_html=True)
    
    company_options = sorted(df["Company Name"].unique())
    selected_company_name = st.selectbox("Select Target Account to Audit", options=company_options, label_visibility="collapsed")
    
    if selected_company_name:
        company_row = df[df["Company Name"] == selected_company_name].iloc[0]
        
        # Tabs for Inspector: Overview, Scoring, Decision Makers, Playbook, Signals, Summary
        tab_overview, tab_scoring, tab_contacts, tab_playbook, tab_signals, tab_summary = st.tabs([
            "Overview", "Scoring", "Decision Makers", "Playbook", "Signals", "Summary"
        ])
        
        # Tab 1: Overview
        with tab_overview:
            with st.container(border=True, key="tab-container"):
                col_l, col_r = st.columns(2)
                with col_l:
                    st.markdown(f"""
                        <table style="width:100%; font-size:0.92rem; border-collapse:collapse; color:#E5E7EB;">
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF; width:40%;">Company Name</td><td style="padding:10px 0; font-weight:700; color:#FFFFFF;">{company_row['Company Name']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF;">Industry Vertical</td><td style="padding:10px 0;">{company_row['Industry']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF;">HQ Location</td><td style="padding:10px 0;">{company_row['Location']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF;">Firmographic Size</td><td style="padding:10px 0;">{company_row['Employee Count']} ({company_row['firmographic_segment']})</td></tr>
                        </table>
                    """, unsafe_allow_html=True)
                with col_r:
                    st.markdown(f"""
                        <table style="width:100%; font-size:0.92rem; border-collapse:collapse; color:#E5E7EB;">
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF; width:40%;">Funding Stage</td><td style="padding:10px 0;">{company_row['Funding Stage']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF;">Hiring Intensity</td><td style="padding:10px 0;">{company_row['Hiring Activity']}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF;">Funding Velocity</td><td style="padding:10px 0;">{company_row['Recent Funding'] == 'Yes' and 'Recently Funded' or 'Stable'}</td></tr>
                            <tr style="border-bottom:1px solid #253047;"><td style="padding:10px 0; font-weight:600; color:#9CA3AF;">Expansion Status</td><td style="padding:10px 0;">{company_row['Expansion Status']}</td></tr>
                        </table>
                    """, unsafe_allow_html=True)
            
        # Tab 2: Scoring
        with tab_scoring:
            with st.container(border=True, key="tab-container"):
                sc_col1, sc_col2 = st.columns(2)
                with sc_col1:
                    icp = company_row['icp_score']
                    bs = company_row['buying_signal_score']
                    mo = company_row['market_opportunity_score']
                    gtm = company_row['gtm_opportunity_score']
                    
                    # Visual score progress bars
                    st.markdown(f"""
                        <div style="margin-bottom:18px;">
                            <div style="display:flex; justify-content:between; align-items:center; font-size:0.85rem; margin-bottom:5px;">
                                <span style="font-weight:600; color:#FFFFFF;">ICP Fit Score</span>
                                <span style="font-weight:700; color:#3B82F6; margin-left:auto;">{icp}/100</span>
                            </div>
                            <div class="saas-progress-bar"><div class="saas-progress-value" style="width:{icp}%; background-color:#3B82F6;"></div></div>
                        </div>
                        
                        <div style="margin-bottom:18px;">
                            <div style="display:flex; justify-content:between; align-items:center; font-size:0.85rem; margin-bottom:5px;">
                                <span style="font-weight:600; color:#FFFFFF;">Buying Intent Score</span>
                                <span style="font-weight:700; color:#F59E0B; margin-left:auto;">{bs}/100</span>
                            </div>
                            <div class="saas-progress-bar"><div class="saas-progress-value" style="width:{bs}%; background-color:#F59E0B;"></div></div>
                        </div>
                        
                        <div style="margin-bottom:18px;">
                            <div style="display:flex; justify-content:between; align-items:center; font-size:0.85rem; margin-bottom:5px;">
                                <span style="font-weight:600; color:#FFFFFF;">Market Opportunity Score</span>
                                <span style="font-weight:700; color:#8B5CF6; margin-left:auto;">{mo}/100</span>
                            </div>
                            <div class="saas-progress-bar"><div class="saas-progress-value" style="width:{mo}%; background-color:#8B5CF6;"></div></div>
                        </div>
                        
                        <div style="margin-bottom:5px;">
                            <div style="display:flex; justify-content:between; align-items:center; font-size:0.88rem; margin-bottom:5px;">
                                <span style="font-weight:700; color:#FFFFFF;">Unified GTM Opportunity Score</span>
                                <span style="font-weight:800; color:#22C55E; margin-left:auto;">{gtm}/100</span>
                            </div>
                            <div class="saas-progress-bar" style="height:10px;"><div class="saas-progress-value" style="width:{gtm}%; background-color:#22C55E;"></div></div>
                        </div>
                    """, unsafe_allow_html=True)
                with sc_col2:
                    st.markdown(f"""
                        <div style="padding:16px; background-color:#111827; border:1px solid #253047; border-radius:8px; font-size:0.88rem; color:#9CA3AF; height: 100%;">
                            <strong style="color:#FFFFFF; display:block; margin-bottom:8px;">GTM Index Rationale:</strong>
                            The unified GTM Opportunity Score represents a weighted distribution of the customer fit:
                            <ul style="margin-top:6px; padding-left:20px;">
                                <li><b>ICP Fit (40%):</b> Measures firmographic compatibility with ideal B2B profiles.</li>
                                <li><b>Intent Signal (40%):</b> Evaluates real-time buying signs (hiring waves, funding velocity).</li>
                                <li><b>Market Opportunity (20%):</b> Evaluates industry and geographical momentum.</li>
                            </ul>
                            <div style="margin-top:12px; border-top:1px solid #253047; padding-top:10px; font-weight:600; color:#FFFFFF;">
                                Opportunity Level: <span style="color: #3B82F6;">{company_row['gtm_opportunity_level']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
        # Tab 3: Decision Makers
        with tab_contacts:
            # Roles details builder
            primary_role = company_row['primary_contact']
            secondary_role = company_row['secondary_contact']
            
            # Dynamic mock pain points based on persona role
            pain_points_map = {
                "Founder": "Scaling early B2B pipelines, tooling overhead, finding repeatable channels.",
                "CEO": "Corporate growth margins, pipeline predictability, macro industry shifts.",
                "COO": "Operational bottlenecks, tooling consolidation, budget distributions.",
                "VP People": "Recruiting velocity, employee retention, HR tool stack efficiency.",
                "Head HR": "Hiring operational friction, compliance, scaling administrative processes.",
                "VP Operations": "Systems efficiency, sales/RevOps automation, contract overheads.",
                "Talent Acquisition Lead": "Sourcing qualified technical talent, high agency spend, screening tools."
            }
            
            primary_pain = pain_points_map.get(primary_role, "Sourcing reliable vendors, system integration.")
            secondary_pain = pain_points_map.get(secondary_role, "Operational scalability, data transparency.")
            
            st.markdown(f"""
                <div class="saas-card" style="border-top:none; border-radius:0 0 12px 12px;">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                        <!-- Primary contact card -->
                        <div style="background-color:#111827; border:1px solid #253047; border-radius:8px; padding:20px; display:flex; gap:16px;">
                            <div style="width:48px; height:48px; border-radius:50%; background-color:#3B82F6; display:flex; align-items:center; justify-content:center; color:#FFFFFF; flex-shrink:0;">
                                {SVG_ICONS['user-check']}
                            </div>
                            <div>
                                <span style="font-size:0.75rem; background-color:rgba(59, 130, 246, 0.15); color:#3B82F6; padding:2px 6px; border-radius:4px; font-weight:600;">Primary Target Contact</span>
                                <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF; margin-top:3px; margin-bottom:5px;">{primary_role}</div>
                                <div style="font-size:0.85rem; color:#E5E7EB; margin-bottom:8px;"><b>Responsibility:</b> Core purchasing logic, tooling budget authorization.</div>
                                <div style="font-size:0.82rem; color:#EF4444; margin-bottom:8px;"><b>Pain Point:</b> {primary_pain}</div>
                                <div style="font-size:0.82rem; color:#22C55E; font-weight:600; padding:8px; background-color:#1A2235; border-radius:6px;">
                                    <b>Outreach Angle:</b> Present ROI and operational speed improvements.
                                </div>
                            </div>
                        </div>
                        
                        <!-- Secondary contact card -->
                        <div style="background-color:#111827; border:1px solid #253047; border-radius:8px; padding:20px; display:flex; gap:16px;">
                            <div style="width:48px; height:48px; border-radius:50%; background-color:#10B981; display:flex; align-items:center; justify-content:center; color:#FFFFFF; flex-shrink:0;">
                                {SVG_ICONS['user']}
                            </div>
                            <div>
                                <span style="font-size:0.75rem; background-color:rgba(16, 185, 129, 0.15); color:#10B981; padding:2px 6px; border-radius:4px; font-weight:600;">Secondary Target Contact</span>
                                <div style="font-size:1.15rem; font-weight:700; color:#FFFFFF; margin-top:3px; margin-bottom:5px;">{secondary_role}</div>
                                <div style="font-size:0.85rem; color:#E5E7EB; margin-bottom:8px;"><b>Responsibility:</b> Tooling evaluation, daily operational execution.</div>
                                <div style="font-size:0.82rem; color:#EF4444; margin-bottom:8px;"><b>Pain Point:</b> {secondary_pain}</div>
                                <div style="font-size:0.82rem; color:#22C55E; font-weight:600; padding:8px; background-color:#1A2235; border-radius:6px;">
                                    <b>Outreach Angle:</b> Highlight user adoption and frictionless workflows.
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="font-size:0.88rem; color:#9CA3AF; padding:12px; background-color:#111827; border-radius:8px; border: 1px solid #253047; border-left:4px solid #3B82F6; margin-top:20px;">
                        <b>Executive Mapping Justification:</b> {company_row['contact_reasoning']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Tab 4: Playbook
        with tab_playbook:
            playbook_steps = company_row["playbook"]
            day_labels = ["Day 1", "Day 3", "Day 7", "Day 14", "Day 21"]
            
            timeline_items = []
            for idx, step in enumerate(playbook_steps):
                clean_text = step.split(".", 1)[1].strip() if "." in step else step
                timeline_items.append(f"""
                    <div class="timeline-item">
                        <div class="timeline-badge">{idx + 1}</div>
                        <div class="timeline-title" style="color: #FFFFFF; font-weight:600;">{day_labels[idx] if idx < len(day_labels) else "Follow-up"} - {clean_text.split(':')[0]}</div>
                        <div class="timeline-desc">{clean_text.split(':')[-1] if ':' in clean_text else clean_text}</div>
                    </div>
                """)
                
            st.markdown(f"""
                <div class="saas-card" style="border-top:none; border-radius:0 0 12px 12px;">
                    <div class="timeline-container">
                        {"".join(timeline_items)}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Tab 5: Signals
        with tab_signals:
            # Format custom signal checkboxes
            hiring_val = company_row["Hiring Activity"]
            funding_val = company_row["Recent Funding"]
            expansion_val = company_row["Expansion Status"]
            
            st.markdown(f"""
                <div class="saas-card" style="border-top:none; border-radius:0 0 12px 12px;">
                    <div style="font-size:0.92rem; color:#D1D5DB;">
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                            <span style="color:#22C55E;">{SVG_ICONS['check-circle']}</span>
                            <span><b>Hiring Waves:</b> Detected <b>{hiring_val}</b> hiring activity.</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                            <span style="color:#22C55E;">{SVG_ICONS['check-circle']}</span>
                            <span><b>Funding Velocity:</b> Recent Funding is <b>{funding_val == 'Yes' and 'ACTIVE' or 'STABLE'}</b> (Stage: {company_row['Funding Stage']}).</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                            <span style="color:#22C55E;">{SVG_ICONS['check-circle']}</span>
                            <span><b>Expansion signals:</b> Team footprint is <b>{expansion_val.upper()}</b>.</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="color:#22C55E;">{SVG_ICONS['check-circle']}</span>
                            <span><b>Market Trend Signal:</b> Evaluated sector momentum score of <b>{company_row['market_opportunity_score']}/100</b>.</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Tab 6: Summary
        with tab_summary:
            st.markdown(f"""
                <div class="saas-card" style="border-top:none; border-radius:0 0 12px 12px; min-height: 200px;">
                    <div style="font-size:1.02rem; line-height:1.6; color:#D1D5DB;">{company_row["account_summary"]}</div>
                </div>
            """, unsafe_allow_html=True)
