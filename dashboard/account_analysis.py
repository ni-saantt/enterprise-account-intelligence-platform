"""
Account Analysis Page for Enterprise GTM Account Intelligence Platform.
Implements the interactive prioritization table and the account deep-dive profile inspector.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from utils.helpers import (
    get_tier_badge, 
    get_priority_badge, 
    get_opportunity_badge, 
    get_buying_signal_badge,
    to_excel_bytes,
    to_csv_bytes
)

def render_account_analysis(df: pd.DataFrame) -> None:
    """Renders the account prioritization grid and detail viewer."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0;">Account Intelligence Prioritization</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:1.1rem; margin-top:2px;">Filter, segment, export, and inspect detailed account execution playbooks.</p>', unsafe_allow_html=True)
    
    # ------------------ SIDEBAR OR IN-PAGE CONTROLS / FILTERS ------------------
    st.markdown('<div style="background-color:#f8fafc; padding:20px; border-radius:10px; border:1px solid #e2e8f0; margin-bottom:25px;">', unsafe_allow_html=True)
    
    # Grid of filter controls
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        search_query = st.text_input("🔍 Search Company Name", value="", placeholder="e.g. Zoho")
    with f_col2:
        selected_tiers = st.multiselect("ABM Tier", options=["Tier 1", "Tier 2", "Tier 3"])
    with f_col3:
        selected_industries = st.multiselect("Industry Vertical", options=sorted(df["Industry"].unique()))
    with f_col4:
        selected_priorities = st.multiselect("Outreach Priority", options=["High", "Medium", "Low"])
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply filters to dataset
    filtered_df = df.copy()
    
    if search_query:
        filtered_df = filtered_df[filtered_df["Company Name"].str.contains(search_query, case=False, na=False)]
        
    if selected_tiers:
        filtered_df = filtered_df[filtered_df["abm_tier"].isin(selected_tiers)]
        
    if selected_industries:
        filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industries)]
        
    if selected_priorities:
        filtered_df = filtered_df[filtered_df["priority_level"].isin(selected_priorities)]
        
    # ------------------ EXPORT CONTROLS ------------------
    export_df = filtered_df[[
        "Company Name", "Industry", "Funding Stage", "Employee Count", "Location", 
        "Hiring Activity", "Recent Funding", "Expansion Status", "icp_score", 
        "abm_tier", "buying_signal_score", "buying_signal_level", "market_opportunity_score",
        "gtm_opportunity_score", "gtm_opportunity_level", "priority_level", 
        "primary_contact", "secondary_contact", "firmographic_segment"
    ]].copy()
    
    exp_col1, exp_col2, exp_col3 = st.columns([6, 1, 1])
    with exp_col1:
        st.markdown(f'<span style="font-size: 0.9rem; color: #64748b;">Showing <b>{len(filtered_df)}</b> of <b>{len(df)}</b> accounts.</span>', unsafe_allow_html=True)
    with exp_col2:
        st.download_button(
            label="📥 Export Excel",
            data=to_excel_bytes(export_df),
            file_name="gtm_account_prioritization.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with exp_col3:
        st.download_button(
            label="📥 Export CSV",
            data=to_csv_bytes(export_df),
            file_name="gtm_account_prioritization.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    # ------------------ ACCOUNT PRIORITIZATION TABLE ------------------
    # Render table columns with custom styling
    table_df = filtered_df[[
        "Company Name", "Industry", "icp_score", "buying_signal_level", 
        "gtm_opportunity_score", "abm_tier", "priority_level", "primary_contact", "secondary_contact"
    ]].copy()
    
    # Rename columns for presentation
    table_df.columns = [
        "Company", "Industry", "ICP Score", "Buying Signal", 
        "Opportunity Score", "Tier", "Priority", "Primary Contact", "Secondary Contact"
    ]
    
    # Sort option
    sort_by = st.selectbox("Sort Table By", ["Opportunity Score", "ICP Score", "Company"], index=0)
    if sort_by == "Opportunity Score":
        table_df = table_df.sort_values(by="Opportunity Score", ascending=False)
    elif sort_by == "ICP Score":
        table_df = table_df.sort_values(by="ICP Score", ascending=False)
    else:
        table_df = table_df.sort_values(by="Company", ascending=True)
        
    # Format table output using HTML tags for visual aesthetics
    html_rows = []
    for _, row in table_df.iterrows():
        tier_badge = get_tier_badge(row["Tier"])
        priority_badge = get_priority_badge(row["Priority"])
        signal_badge = get_buying_signal_badge(row["Buying Signal"])
        
        # Color coding for opportunity scores
        score = row["Opportunity Score"]
        score_style = "color:#10b981; font-weight:700;" if score >= 90 else "color:#14b8a6;" if score >= 75 else "color:#f59e0b;" if score >= 60 else "color:#64748b;"
        
        html_rows.append(f"""
            <tr>
                <td style="padding: 12px; font-weight: 600; color: #1e293b;">{row['Company']}</td>
                <td style="padding: 12px; color: #475569;">{row['Industry']}</td>
                <td style="padding: 12px; text-align: center; font-weight: 600;">{row['ICP Score']}</td>
                <td style="padding: 12px; text-align: center;">{signal_badge}</td>
                <td style="padding: 12px; text-align: center; font-weight: 700; {score_style}">{score}</td>
                <td style="padding: 12px; text-align: center;">{tier_badge}</td>
                <td style="padding: 12px; text-align: center;">{priority_badge}</td>
                <td style="padding: 12px; color: #475569;">{row['Primary Contact']}</td>
                <td style="padding: 12px; color: #64748b;">{row['Secondary Contact']}</td>
            </tr>
        """)
        
    html_table = f"""
    <div style="overflow-x: auto; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; background-color: #ffffff;">
            <thead>
                <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: 600;">
                    <th style="padding: 12px;">Company</th>
                    <th style="padding: 12px;">Industry</th>
                    <th style="padding: 12px; text-align: center;">ICP Score</th>
                    <th style="padding: 12px; text-align: center;">Buying Signal</th>
                    <th style="padding: 12px; text-align: center;">Opportunity Score</th>
                    <th style="padding: 12px; text-align: center;">ABM Tier</th>
                    <th style="padding: 12px; text-align: center;">Outreach Priority</th>
                    <th style="padding: 12px;">Primary Persona</th>
                    <th style="padding: 12px;">Secondary Persona</th>
                </tr>
            </thead>
            <tbody>
                {"".join(html_rows) if html_rows else '<tr><td colspan="9" style="padding: 20px; text-align: center; color: #64748b;">No accounts match the active filter criteria.</td></tr>'}
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)
    
    st.markdown("---")

    # ------------------ ACCOUNT DEEP-DIVE INSPECTOR ------------------
    st.markdown('<h2 class="section-title">🔍 Account Deep-Dive Inspector</h2>', unsafe_allow_html=True)
    
    company_options = sorted(df["Company Name"].unique())
    selected_company_name = st.selectbox("Select Account to Audit", options=company_options)
    
    if selected_company_name:
        company_row = df[df["Company Name"] == selected_company_name].iloc[0]
        
        # Grid layout for detail view
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            # Profile & Firmographics Card
            st.markdown(f"""
                <div class="profile-section">
                    <h3 style="margin-top:0; color:#4f46e5; border-bottom: 2px solid #f1f5f9; padding-bottom:10px;">{company_row['Company Name']} Profile</h3>
                    <table style="width:100%; font-size:0.9rem; border-collapse:collapse; margin-top:10px;">
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b; width:45%;">Industry</td><td style="padding:8px 0; color:#1e293b;">{company_row['Industry']}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Funding Stage</td><td style="padding:8px 0; color:#1e293b;">{company_row['Funding Stage']}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Employee Count</td><td style="padding:8px 0; color:#1e293b;">{company_row['Employee Count']} ({company_row['firmographic_segment']})</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Location</td><td style="padding:8px 0; color:#1e293b;">{company_row['Location']}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Hiring Activity</td><td style="padding:8px 0; color:#1e293b;">{company_row['Hiring Activity']}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Recent Funding</td><td style="padding:8px 0; color:#1e293b;">{company_row['Recent Funding']}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Expansion Status</td><td style="padding:8px 0; color:#1e293b;">{company_row['Expansion Status']}</td></tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
            # GTM Scoring breakdown
            tier_badge = get_tier_badge(company_row["abm_tier"])
            priority_badge = get_priority_badge(company_row["priority_level"])
            opp_badge = get_opportunity_badge(company_row["gtm_opportunity_level"])
            signal_badge = get_buying_signal_badge(company_row["buying_signal_level"])
            
            st.markdown(f"""
                <div class="profile-section">
                    <h3 style="margin-top:0; color:#1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom:10px;">GTM Index Summary</h3>
                    <table style="width:100%; font-size:0.9rem; border-collapse:collapse; margin-top:10px;">
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b; width:45%;">ABM Tier</td><td style="padding:8px 0;">{tier_badge}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Outreach Priority</td><td style="padding:8px 0;">{priority_badge}</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">GTM Opportunity</td><td style="padding:8px 0;">{opp_badge} (Score: <b>{company_row['gtm_opportunity_score']}</b>)</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">ICP Fit Score</td><td style="padding:8px 0; color:#1e293b; font-weight:700;">{company_row['icp_score']}/100</td></tr>
                        <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 0; font-weight:600; color:#64748b;">Buying Signal Score</td><td style="padding:8px 0; color:#1e293b; font-weight:700;">{company_row['buying_signal_score']}/100 ({signal_badge})</td></tr>
                        <tr><td style="padding:8px 0; font-weight:600; color:#64748b;">Market Opp Score</td><td style="padding:8px 0; color:#1e293b; font-weight:700;">{company_row['market_opportunity_score']}/100</td></tr>
                    </table>
                </div>
            """, unsafe_allow_html=True)
            
        with col_right:
            # AI Account Summary
            st.markdown('<div class="profile-section">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top:0; color:#0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom:10px;">✨ AI Account summary</h3>', unsafe_allow_html=True)
            st.write(company_row["account_summary"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Decision Maker Map
            st.markdown(f"""
                <div class="profile-section">
                    <h3 style="margin-top:0; color:#0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom:10px;">👤 Decision Maker Persona Mapping</h3>
                    <div style="margin-top:10px;">
                        <div style="margin-bottom:10px;">
                            <span style="font-size:0.75rem; background-color:#e0e7ff; color:#3730a3; padding:2px 6px; border-radius:4px; font-weight:600;">Primary Target Contact</span>
                            <div style="font-size:1.1rem; font-weight:700; color:#1e293b; margin-top:3px;">{company_row['primary_contact']}</div>
                        </div>
                        <div style="margin-bottom:12px;">
                            <span style="font-size:0.75rem; background-color:#f1f5f9; color:#475569; padding:2px 6px; border-radius:4px; font-weight:600;">Secondary Target Contact</span>
                            <div style="font-size:1.1rem; font-weight:700; color:#1e293b; margin-top:3px;">{company_row['secondary_contact']}</div>
                        </div>
                        <div style="font-size:0.85rem; color:#64748b; padding:10px; background-color:#f8fafc; border-radius:6px; border-left:3px solid #cbd5e1; line-height:1.4;">
                            <b>Target Mapping Rationale:</b> {company_row['contact_reasoning']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # GTM Playbook Checklist
            st.markdown('<div class="profile-section">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top:0; color:#0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom:10px;">🚀 Recommended GTM Playbook Sequence</h3>', unsafe_allow_html=True)
            for step in company_row["playbook"]:
                # Print each step nicely
                num_part, text_part = step.split(".", 1) if "." in step else ("•", step)
                st.markdown(f"""
                    <div class="playbook-step">
                        <div class="playbook-num">{num_part.strip()}</div>
                        <div class="playbook-text">{text_part.strip()}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
