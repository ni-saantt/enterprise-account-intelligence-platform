"""
Market Intelligence Page for Enterprise GTM Account Intelligence Platform.
Derives GTM Opportunity indexes, momentum segments, and vertical rankings dynamically.
Clean B2B SaaS layout with Lucide SVG icons, charts, and no fake simulated revenue metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.constants import SVG_ICONS, PLOTLY_LAYOUT_DEFAULTS
from utils.helpers import clean_html

def render_market_intelligence(df: pd.DataFrame) -> None:
    """Renders data-driven GTM Opportunity Index and Industry momentum dashboards."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data in the Data Integration tab.")
        return
        
    st.title("Market Intelligence")
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Opportunity index analysis, industry momentum rankings, and geographical market expansion signals.</p>', unsafe_allow_html=True)
    
    # ------------------ OPPORTUNITY INDEX KPIs ------------------
    avg_opp_idx = df["market_opportunity_score"].mean()
    high_opp_count = len(df[df["market_opportunity_score"] >= 75])
    total_accounts = len(df)
    high_opp_pct = int(high_opp_count / total_accounts * 100) if total_accounts > 0 else 0
    
    # Calculate Momentum sectors
    # 1. Fastest Growing (highest Expanding status)
    expanding_df = df[df["Expansion Status"] == "Expanding"]
    if not expanding_df.empty:
        fastest_growing = expanding_df["Industry"].mode()[0]
        fg_count = len(expanding_df[expanding_df["Industry"] == fastest_growing])
    else:
        fastest_growing = "N/A"
        fg_count = 0
        
    # 2. Top Hiring (highest High Hiring activity)
    hiring_df = df[df["Hiring Activity"] == "High"]
    if not hiring_df.empty:
        top_hiring = hiring_df["Industry"].mode()[0]
        th_count = len(hiring_df[hiring_df["Industry"] == top_hiring])
    else:
        top_hiring = "N/A"
        th_count = 0
        
    # 3. Funding Momentum (highest Recent Funding)
    funded_df = df[df["Recent Funding"] == "Yes"]
    if not funded_df.empty:
        funding_momentum = funded_df["Industry"].mode()[0]
        fm_count = len(funded_df[funded_df["Industry"] == funding_momentum])
    else:
        funding_momentum = "N/A"
        fm_count = 0
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Average Opportunity Index</span>
                    <span style="color:#3B82F6;">{SVG_ICONS['activity']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_opp_idx:.1f}</h2>
                </div>
                <div style="font-size:0.8rem; color:#9CA3AF; margin-top:8px;">
                    Scale 0-100 GTM fit score
                </div>
            </div>
        """), unsafe_allow_html=True)
    with col2:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">High Opportunity Accounts</span>
                    <span style="color:#10B981;">{SVG_ICONS['target']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{high_opp_count}</h2>
                </div>
                <div style="font-size:0.8rem; color:#10B981; margin-top:8px; font-weight:600;">
                    {high_opp_pct}% index >= 75
                </div>
            </div>
        """), unsafe_allow_html=True)
    with col3:
        st.markdown(clean_html(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Market Expansion Segments</span>
                    <span style="color:#F59E0B;">{SVG_ICONS['globe']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value" style="font-size:1.45rem !important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{df['Location'].mode()[0] if not df['Location'].mode().empty else 'N/A'}</h2>
                </div>
                <div style="font-size:0.8rem; color:#9CA3AF; margin-top:8px;">
                    Top regional HQ density
                </div>
            </div>
        """), unsafe_allow_html=True)
        
    st.markdown("---")
    
    # ------------------ SECTOR MOMENTUM ------------------
    st.markdown("### GTM Momentum Segments")
    c_mom1, c_mom2, c_mom3 = st.columns(3)
    with c_mom1:
        with st.container(border=True):
            st.markdown(clean_html(f"""
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#22C55E;">{SVG_ICONS['trending-up']}</span>
                    <span style="font-weight:700; color:#FFFFFF; font-size:0.95rem;">Fastest Growing Industry</span>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; margin-top:8px;">{fastest_growing}</div>
                <div style="font-size:0.85rem; color:#9CA3AF; margin-top:4px;">
                    Based on <b>{fg_count}</b> accounts in "Expanding" stage.
                </div>
            """), unsafe_allow_html=True)
    with c_mom2:
        with st.container(border=True):
            st.markdown(clean_html(f"""
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#3B82F6;">{SVG_ICONS['users']}</span>
                    <span style="font-weight:700; color:#FFFFFF; font-size:0.95rem;">Top Hiring Industry</span>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; margin-top:8px;">{top_hiring}</div>
                <div style="font-size:0.85rem; color:#9CA3AF; margin-top:4px;">
                    Based on <b>{th_count}</b> accounts with "High" hiring density.
                </div>
            """), unsafe_allow_html=True)
    with c_mom3:
        with st.container(border=True):
            st.markdown(clean_html(f"""
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:#F59E0B;">{SVG_ICONS['dollar-sign']}</span>
                    <span style="font-weight:700; color:#FFFFFF; font-size:0.95rem;">Funding Momentum</span>
                </div>
                <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; margin-top:8px;">{funding_momentum}</div>
                <div style="font-size:0.85rem; color:#9CA3AF; margin-top:4px;">
                    Based on <b>{fm_count}</b> accounts with recent funding updates.
                </div>
            """), unsafe_allow_html=True)

    st.markdown("---")
    
    # ------------------ OPPORTUNITY CHARTS ------------------
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### Opportunity Index vs Industry Vertical")
        ind_avg_opp = df.groupby("Industry")["market_opportunity_score"].mean().reset_index()
        ind_avg_opp = ind_avg_opp.sort_values(by="market_opportunity_score", ascending=False)
        fig_ind_opp = px.bar(
            ind_avg_opp,
            x="Industry",
            y="market_opportunity_score",
            color_discrete_sequence=["#3B82F6"]
        )
        fig_ind_opp.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            height=280,
            xaxis_title=None,
            yaxis_title="Avg Index (0-100)"
        )
        st.plotly_chart(fig_ind_opp, use_container_width=True)
        
    with col_g2:
        st.markdown("#### Opportunity Index vs Geography Region")
        loc_avg_opp = df.groupby("Location")["market_opportunity_score"].mean().reset_index()
        loc_avg_opp = loc_avg_opp.sort_values(by="market_opportunity_score", ascending=False)
        fig_loc_opp = px.bar(
            loc_avg_opp,
            x="Location",
            y="market_opportunity_score",
            color_discrete_sequence=["#14B8A6"]
        )
        fig_loc_opp.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            height=280,
            xaxis_title=None,
            yaxis_title="Avg Index (0-100)"
        )
        st.plotly_chart(fig_loc_opp, use_container_width=True)
        
    # ------------------ INDUSTRY RANKING TABLE ------------------
    st.markdown("---")
    st.markdown("### GTM Industry Vertical Rank Matrix")
    
    ind_macro = df.groupby("Industry").agg(
        avg_icp=("icp_score", "mean"),
        avg_buying=("buying_signal_score", "mean"),
        avg_opp=("market_opportunity_score", "mean"),
        total_accounts=("Company Name", "count")
    ).reset_index().sort_values(by="avg_opp", ascending=False)
    
    ind_macro.columns = ["Industry Sector", "Average ICP Score", "Average Buying Signal", "Market Opportunity Index", "Total Accounts"]
    
    st.dataframe(
        ind_macro,
        column_config={
            "Industry Sector": st.column_config.TextColumn("Industry Sector", width="medium"),
            "Average ICP Score": st.column_config.ProgressColumn("Average ICP Score", min_value=0, max_value=100, format="%.1f"),
            "Average Buying Signal": st.column_config.ProgressColumn("Average Buying Signal", min_value=0, max_value=100, format="%.1f"),
            "Market Opportunity Index": st.column_config.ProgressColumn("Market Opportunity Index", min_value=0, max_value=100, format="%.1f"),
            "Total Accounts": st.column_config.NumberColumn("Total Accounts", format="%d")
        },
        use_container_width=True,
        hide_index=True
    )
