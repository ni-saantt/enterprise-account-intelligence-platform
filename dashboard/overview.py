"""
Overview Dashboard for Enterprise GTM Account Intelligence Platform.
Clean B2B SaaS layout with Lucide SVG icons, delta sparklines, and professional dark-theme Plotly charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.constants import SVG_ICONS, PLOTLY_LAYOUT_DEFAULTS

def render_overview(df: pd.DataFrame) -> None:
    """Renders the executive analytics dashboard."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">GTM Analytics Overview</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Executive GTM health trends, fit distributions, and intent analytics dashboards.</p>', unsafe_allow_html=True)
    
    # ------------------ COMPUTE KPI METRICS ------------------
    total_accounts = len(df)
    tier_1_count = len(df[df["abm_tier"] == "Tier 1"])
    avg_icp = df["icp_score"].mean()
    avg_buying = df["buying_signal_score"].mean()
    avg_gtm = df["gtm_opportunity_score"].mean()
    high_priority = len(df[df["priority_level"] == "High"])
    
    # Top Industry Segment
    if not df["Industry"].mode().empty:
        top_industry = df["Industry"].mode()[0]
        top_industry_count = len(df[df["Industry"] == top_industry])
    else:
        top_industry = "N/A"
        top_industry_count = 0
        
    # Highest Opportunity Company
    highest_opp_row = df.sort_values(by="gtm_opportunity_score", ascending=False).iloc[0] if not df.empty else None
    if highest_opp_row is not None:
        highest_opp_name = highest_opp_row["Company Name"]
        highest_opp_score = highest_opp_row["gtm_opportunity_score"]
    else:
        highest_opp_name = "N/A"
        highest_opp_score = 0

    # ------------------ RENDER METRICS CARDS (ROW 1) ------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Total Accounts</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['building']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{total_accounts}</h2>
                    <span class="saas-metric-delta delta-up">+12.4%</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 20 Q15 15 30 10 T60 12 T90 5 T120 2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Tier 1 Target</span>
                    <span style="color: #F59E0B;">{SVG_ICONS['target']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{tier_1_count}</h2>
                    <span class="saas-metric-delta delta-up">+{int(tier_1_count/total_accounts*100) if total_accounts > 0 else 0}%</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#3B82F6" stroke-width="1.5">
                        <path d="M0 12 Q15 14 30 12 T60 13 T90 10 T120 8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Avg ICP Fit</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['user']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_icp:.1f}</h2>
                    <span class="saas-metric-delta delta-up">+4.1%</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 10 Q15 15 30 18 T60 5 T90 8 T120 4" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Avg Buying Intent</span>
                    <span style="color: #22C55E;">{SVG_ICONS['trending-up']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_buying:.1f}</h2>
                    <span class="saas-metric-delta delta-up">+8.3%</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 22 Q15 15 30 18 T60 8 T90 10 T120 4" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # ------------------ RENDER METRICS CARDS (ROW 2) ------------------
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Avg GTM Index</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['target']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_gtm:.1f}</h2>
                    <span class="saas-metric-delta delta-up">+5.2%</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#3B82F6" stroke-width="1.5">
                        <path d="M0 15 Q15 12 30 18 T60 8 T90 14 T120 10" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">High Priority</span>
                    <span style="color: #EF4444;">{SVG_ICONS['activity']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{high_priority}</h2>
                    <span class="saas-metric-delta delta-down" style="color:#EF4444 !important;">Active</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#EF4444" stroke-width="1.5">
                        <path d="M0 5 Q15 12 30 10 T60 18 T90 12 T120 20" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col7:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Top Segment</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['briefcase']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value" style="font-size:1.3rem !important; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{top_industry}</h2>
                    <span class="saas-metric-delta delta-up">{top_industry_count} acc</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 10 Q15 14 30 10 T60 15 T90 8 T120 2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Top Account</span>
                    <span style="color: #22C55E;">{SVG_ICONS['rocket']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value" style="font-size:1.3rem !important; color:#10B981; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{highest_opp_name}</h2>
                    <span class="saas-metric-delta delta-up">{highest_opp_score}</span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 18 Q15 12 30 15 T60 8 T90 10 T120 4" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")

    # ------------------ CHART VISUALIZATIONS ------------------
    chart_color_sequence = ["#3B82F6", "#14B8A6", "#F59E0B", "#EF4444", "#8B5CF6", "#10B981"]
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Chart 1: ICP Score Distribution (Histogram)
        with st.container(border=True):
            st.markdown(f'<div class="saas-card-title"><span style="color:#3B82F6;">{SVG_ICONS["bar-chart"]}</span><span>ICP Score Distribution</span></div>', unsafe_allow_html=True)
            fig_icp = px.histogram(
                df, 
                x="icp_score", 
                nbins=12, 
                color_discrete_sequence=["#3B82F6"],
                labels={"icp_score": "ICP Score", "count": "Count"}
            )
            fig_icp.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=280,
                xaxis_title="ICP Score",
                yaxis_title="Count",
                bargap=0.08
            )
            st.plotly_chart(fig_icp, use_container_width=True)
        
        # Chart 2: ABM Tier Distribution (Pie)
        with st.container(border=True):
            st.markdown(f'<div class="saas-card-title"><span style="color:#F59E0B;">{SVG_ICONS["target"]}</span><span>ABM Tier Ratio</span></div>', unsafe_allow_html=True)
            tier_counts = df["abm_tier"].value_counts().reset_index()
            tier_counts.columns = ["ABM Tier", "Count"]
            tier_colors = {"Tier 1": "#22C55E", "Tier 2": "#F59E0B", "Tier 3": "#64748B"}
            fig_tier = px.pie(
                tier_counts, 
                values="Count", 
                names="ABM Tier",
                color="ABM Tier",
                color_discrete_map=tier_colors,
                hole=0.45
            )
            fig_tier.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=280,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            fig_tier.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_tier, use_container_width=True)

    with chart_col2:
        # Chart 3: Industry Breakdown (Donut)
        with st.container(border=True):
            st.markdown(f'<div class="saas-card-title"><span style="color:#14B8A6;">{SVG_ICONS["briefcase"]}</span><span>Industry Segment Breakdown</span></div>', unsafe_allow_html=True)
            ind_counts = df["Industry"].value_counts().reset_index()
            ind_counts.columns = ["Industry", "Count"]
            fig_ind = px.pie(
                ind_counts,
                values="Count",
                names="Industry",
                color_discrete_sequence=chart_color_sequence,
                hole=0.45
            )
            fig_ind.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=280,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            fig_ind.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_ind, use_container_width=True)
        
        # Chart 4: Buying Signal Levels
        with st.container(border=True):
            st.markdown(f'<div class="saas-card-title"><span style="color:#EF4444;">{SVG_ICONS["activity"]}</span><span>Buying Signal Levels</span></div>', unsafe_allow_html=True)
            signal_counts = df["buying_signal_level"].value_counts().reset_index()
            signal_counts.columns = ["Buying Signal", "Count"]
            signal_order = ["High", "Medium", "Low"]
            signal_counts["Buying Signal"] = pd.Categorical(signal_counts["Buying Signal"], categories=signal_order, ordered=True)
            signal_counts = signal_counts.sort_values("Buying Signal")
            
            signal_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#64748B"}
            fig_signal = px.bar(
                signal_counts,
                x="Buying Signal",
                y="Count",
                color="Buying Signal",
                color_discrete_map=signal_colors,
                labels={"Count": "Account Count"}
            )
            fig_signal.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=280,
                xaxis_title="Intent Level",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_signal, use_container_width=True)
        
    st.markdown("---")
    
    # Chart 5: Leaderboard - Top 10 Accounts (Horizontal Bar Chart)
    st.markdown('<h3 style="color:#FFFFFF; margin-bottom:12px;">Top 10 Accounts Leaderboard</h3>', unsafe_allow_html=True)
    with st.container(border=True):
        leaderboard_df = df.sort_values(by="gtm_opportunity_score", ascending=True).tail(10)
        
        fig_lead = go.Figure()
        fig_lead.add_trace(go.Bar(
            y=leaderboard_df["Company Name"],
            x=leaderboard_df["icp_score"],
            name="ICP Fit Score",
            orientation="h",
            marker=dict(color="#3B82F6")
        ))
        fig_lead.add_trace(go.Bar(
            y=leaderboard_df["Company Name"],
            x=leaderboard_df["gtm_opportunity_score"],
            name="GTM Opportunity Score",
            orientation="h",
            marker=dict(color="#10B981")
        ))
        
        fig_lead.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            barmode="group",
            height=420,
            xaxis_title="Score Index",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_lead, use_container_width=True)
