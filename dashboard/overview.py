"""
Overview Dashboard for Enterprise GTM Account Intelligence Platform.
Renders advanced SaaS-style KPI metrics cards and interactive Plotly distributions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.constants import PLOTLY_LAYOUT_DEFAULTS, PLOTLY_DARK_LAYOUT_DEFAULTS

def render_overview(df: pd.DataFrame) -> None:
    """Renders the executive analytics dashboard."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0;">GTM Analytics Overview</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:1.1rem; margin-top:2px;">Performance metrics, alignment distribution, and target leadership dashboards.</p>', unsafe_allow_html=True)
    
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

    # ------------------ RENDER EXECUTIVE KPI CARDS ------------------
    # Render KPI Cards in two rows of 4
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Accounts</div>
                <div class="metric-value">{total_accounts}</div>
                <div class="metric-delta">Target Database</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tier 1 Target</div>
                <div class="metric-value">{tier_1_count}</div>
                <div class="metric-delta">{int(tier_1_count/total_accounts*100) if total_accounts > 0 else 0}% of Database</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg ICP Score</div>
                <div class="metric-value">{avg_icp:.1f}</div>
                <div class="metric-delta">Ideal Target Fit</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Buying Score</div>
                <div class="metric-value">{avg_buying:.1f}</div>
                <div class="metric-delta">Intent Velocity</div>
            </div>
        """, unsafe_allow_html=True)
        
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Opportunity</div>
                <div class="metric-value" style="color: #6366f1;">{avg_gtm:.1f}</div>
                <div class="metric-delta">Integrated Index</div>
            </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">High Priority</div>
                <div class="metric-value" style="color: #ef4444;">{high_priority}</div>
                <div class="metric-delta down">Ready for Outreach</div>
            </div>
        """, unsafe_allow_html=True)
    with col7:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Top Segment</div>
                <div class="metric-value" style="font-size:1.4rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{top_industry}</div>
                <div class="metric-delta">{top_industry_count} Accounts</div>
            </div>
        """, unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Top Opportunity</div>
                <div class="metric-value" style="font-size:1.4rem; color: #10b981; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{highest_opp_name}</div>
                <div class="metric-delta">Score: {highest_opp_score}/100</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")

    # ------------------ PLOTLY VISUALIZATIONS ------------------
    # Curated color scheme definitions
    color_discrete_sequence = ["#6366f1", "#14b8a6", "#f59e0b", "#ef4444", "#3b82f6", "#10b981"]
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Chart 1: ICP Score Distribution (Histogram)
        st.markdown('<h4 style="color:#1e293b; font-weight:600; margin-bottom:5px;">ICP Score Distribution</h4>', unsafe_allow_html=True)
        fig_icp = px.histogram(
            df, 
            x="icp_score", 
            nbins=15, 
            color_discrete_sequence=["#6366f1"],
            labels={"icp_score": "ICP Score", "count": "Number of Accounts"}
        )
        fig_icp.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            xaxis_title="ICP Score Range",
            yaxis_title="Count",
            bargap=0.08
        )
        st.plotly_chart(fig_icp, use_container_width=True)
        
        # Chart 2: ABM Tier Distribution (Pie Chart)
        st.markdown('<h4 style="color:#1e293b; font-weight:600; margin-bottom:5px;">ABM Tier Ratio</h4>', unsafe_allow_html=True)
        tier_counts = df["abm_tier"].value_counts().reset_index()
        tier_counts.columns = ["ABM Tier", "Count"]
        # Map specific colors to tiers
        tier_colors = {"Tier 1": "#10b981", "Tier 2": "#f59e0b", "Tier 3": "#64748b"}
        fig_tier = px.pie(
            tier_counts, 
            values="Count", 
            names="ABM Tier",
            color="ABM Tier",
            color_discrete_map=tier_colors,
            hole=0.4
        )
        fig_tier.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        fig_tier.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_tier, use_container_width=True)

    with chart_col2:
        # Chart 3: Industry Breakdown (Donut Chart)
        st.markdown('<h4 style="color:#1e293b; font-weight:600; margin-bottom:5px;">Industry Segment Breakdown</h4>', unsafe_allow_html=True)
        ind_counts = df["Industry"].value_counts().reset_index()
        ind_counts.columns = ["Industry", "Count"]
        fig_ind = px.pie(
            ind_counts,
            values="Count",
            names="Industry",
            color_discrete_sequence=color_discrete_sequence,
            hole=0.4
        )
        fig_ind.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        fig_ind.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_ind, use_container_width=True)
        
        # Chart 4: Buying Signal Analysis (Bar Chart)
        st.markdown('<h4 style="color:#1e293b; font-weight:600; margin-bottom:5px;">Buying Signal Levels</h4>', unsafe_allow_html=True)
        signal_counts = df["buying_signal_level"].value_counts().reset_index()
        signal_counts.columns = ["Buying Signal", "Count"]
        # Force order: High, Medium, Low
        signal_order = ["High", "Medium", "Low"]
        signal_counts["Buying Signal"] = pd.Categorical(signal_counts["Buying Signal"], categories=signal_order, ordered=True)
        signal_counts = signal_counts.sort_values("Buying Signal")
        
        signal_colors = {"High": "#ef4444", "Medium": "#ff9f43", "Low": "#8395a7"}
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
            xaxis_title="Buying Signal Level",
            yaxis_title="Count"
        )
        st.plotly_chart(fig_signal, use_container_width=True)
        
    st.markdown("---")
    
    # Chart 5: Leaderboard - Top 10 Accounts (Horizontal Bar Chart)
    st.markdown('<h3 class="section-title">🏆 Top 10 Accounts Leaderboard (GTM Opportunity Score)</h3>', unsafe_allow_html=True)
    leaderboard_df = df.sort_values(by="gtm_opportunity_score", ascending=True).tail(10)
    
    fig_lead = go.Figure()
    # Add horizontal bars for ICP and GTM Opportunity score
    fig_lead.add_trace(go.Bar(
        y=leaderboard_df["Company Name"],
        x=leaderboard_df["icp_score"],
        name="ICP Fit Score",
        orientation="h",
        marker=dict(color="#818cf8")
    ))
    fig_lead.add_trace(go.Bar(
        y=leaderboard_df["Company Name"],
        x=leaderboard_df["gtm_opportunity_score"],
        name="GTM Opportunity Score",
        orientation="h",
        marker=dict(color="#10b981")
    ))
    
    fig_lead.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        barmode="group",
        height=450,
        xaxis_title="Score",
        yaxis=dict(title="Company", tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_lead, use_container_width=True)
