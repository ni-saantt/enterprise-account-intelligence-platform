"""
GTM Command Center Page for Enterprise GTM Account Intelligence Platform.
Executive Summary Dashboard derived entirely from the active dataset.
Clean B2B SaaS layout with Lucide SVG icons and no emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List
from utils.constants import SVG_ICONS, PLOTLY_LAYOUT_DEFAULTS
from utils.helpers import clean_html
from database.database import list_batches

def render_command_center(df: pd.DataFrame) -> None:
    """Renders the executive summary command center."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data in the Data Integration tab.")
        return
        
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">GTM Command Center</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">'
        'Executive Summary Dashboard.'
        '</p>', 
        unsafe_allow_html=True
    )
    
    # ------------------ COMPUTE EXECUTIVE METRICS ------------------
    total_accounts = len(df)
    tier_1_count = len(df[df["abm_tier"] == "Tier 1"])
    avg_icp = df["icp_score"].mean()
    avg_opp = df["gtm_opportunity_score"].mean()
    
    # Fetch Data Quality Score from database metadata
    active_batch_id = st.session_state.get("active_batch_id", "None")
    quality_score = 100
    try:
        batches = list_batches(only_active=False)
        active_meta = next((b for b in batches if b["batch_id"] == active_batch_id), None)
        if active_meta:
            quality_score = active_meta.get("quality_score", 100)
    except Exception:
        pass

    # Dynamic metrics comparison tags
    tier1_pct = int(tier_1_count / total_accounts * 100) if total_accounts > 0 else 0
    avg_icp_pct = int(len(df[df["icp_score"] >= 60]) / total_accounts * 100) if total_accounts > 0 else 0
    avg_opp_pct = int(len(df[df["gtm_opportunity_score"] >= 75]) / total_accounts * 100) if total_accounts > 0 else 0
    
    # ------------------ RENDER TOP KPIs (ROW 1) ------------------
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Total Accounts</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['building']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{total_accounts}</h2>
                </div>
                <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 8px;">
                    Active GTM records
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    with col2:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Avg ICP Fit</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['user']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_icp:.1f}</h2>
                </div>
                <div style="font-size: 0.8rem; color: #10B981; margin-top: 8px; font-weight: 600;">
                    {avg_icp_pct}% Tier 1/2 Fit
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    with col3:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Avg Opportunity</span>
                    <span style="color: #22C55E;">{SVG_ICONS['trending-up']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_opp:.1f}</h2>
                </div>
                <div style="font-size: 0.8rem; color: #10B981; margin-top: 8px; font-weight: 600;">
                    {avg_opp_pct}% High Opp
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    with col4:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Tier 1 Target</span>
                    <span style="color: #F59E0B;">{SVG_ICONS['target']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{tier_1_count}</h2>
                </div>
                <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 8px;">
                    {tier1_pct}% of total dataset
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    with col5:
        score_color = "#22C55E" if quality_score >= 80 else "#F59E0B" if quality_score >= 60 else "#EF4444"
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Data Quality</span>
                    <span style="color: {score_color};">{SVG_ICONS['check-circle']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value" style="color: {score_color} !important;">{quality_score}%</h2>
                </div>
                <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 8px;">
                    Validation health score
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    st.markdown("---")
    
    # ------------------ TOP CHARTS (ROW 2) ------------------
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        # ABM Tier Distribution (Pie)
        with st.container(border=True, key="height380"):
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#F59E0B;">{SVG_ICONS["target"]}</span><span>Tier Distribution</span></div>'), unsafe_allow_html=True)
            
            tier_counts = df["abm_tier"].value_counts().reset_index()
            tier_counts.columns = ["ABM Tier", "Count"]
            tier_colors = {"Tier 1": "#22C55E", "Tier 2": "#F59E0B", "Tier 3": "#64748B"}
            
            fig_tier = px.pie(
                tier_counts, 
                values="Count", 
                names="ABM Tier",
                color="ABM Tier",
                color_discrete_map=tier_colors,
                hole=0.55
            )
            fig_tier.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=260,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            fig_tier.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig_tier, use_container_width=True)
            
    with col_c2:
        # Industry Distribution (Bar)
        with st.container(border=True, key="height380"):
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#3B82F6;">{SVG_ICONS["briefcase"]}</span><span>Industry Distribution</span></div>'), unsafe_allow_html=True)
            
            ind_counts = df["Industry"].value_counts().reset_index()
            ind_counts.columns = ["Industry", "Count"]
            
            fig_ind = px.bar(
                ind_counts.head(6),
                x="Industry",
                y="Count",
                color_discrete_sequence=["#3B82F6"]
            )
            fig_ind.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=260,
                xaxis_title=None,
                yaxis_title="Count"
            )
            st.plotly_chart(fig_ind, use_container_width=True)
            
    with col_c3:
        # Geographic Distribution (Bar)
        with st.container(border=True, key="height380"):
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#14B8A6;">{SVG_ICONS["globe"]}</span><span>Geography Distribution</span></div>'), unsafe_allow_html=True)
            
            loc_counts = df["Location"].value_counts().reset_index()
            loc_counts.columns = ["Location", "Count"]
            
            fig_loc = px.bar(
                loc_counts.head(6),
                x="Location",
                y="Count",
                color_discrete_sequence=["#14B8A6"]
            )
            fig_loc.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=260,
                xaxis_title=None,
                yaxis_title="Count"
            )
            st.plotly_chart(fig_loc, use_container_width=True)
