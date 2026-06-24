"""
Analytics Page for Enterprise GTM Account Intelligence Platform.
Implements drill-down focused collapsible analysis sections.
Clean B2B SaaS layout with Lucide SVG icons, dark themes, and dynamic Plotly charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.constants import SVG_ICONS, PLOTLY_LAYOUT_DEFAULTS
from utils.helpers import clean_html

def render_analytics(df: pd.DataFrame) -> None:
    """Renders the collapsible drill-down analytics dashboard."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data in the Data Integration tab.")
        return
        
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">GTM Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Deep dataset drill-downs, segment breakdown matrices, and fit histograms.</p>', unsafe_allow_html=True)
    
    chart_color_sequence = ["#3B82F6", "#14B8A6", "#F59E0B", "#EF4444", "#8B5CF6", "#10B981"]
    
    # ------------------ 1. INDUSTRY ANALYSIS ------------------
    with st.expander("💼 Industry Analysis", expanded=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#14B8A6;">{SVG_ICONS["briefcase"]}</span><span>Industry Distribution</span></div>'), unsafe_allow_html=True)
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
                height=260,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            fig_ind.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_ind, use_container_width=True)
            
        with col2:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#3B82F6;">{SVG_ICONS["users"]}</span><span>Accounts count by Industry Sector</span></div>'), unsafe_allow_html=True)
            st.dataframe(
                ind_counts,
                column_config={
                    "Industry": st.column_config.TextColumn("Industry Sector"),
                    "Count": st.column_config.NumberColumn("Total Accounts", format="%d")
                },
                use_container_width=True,
                hide_index=True
            )

    # ------------------ 2. FUNDING ANALYSIS ------------------
    with st.expander("💵 Funding Analysis", expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#F59E0B;">{SVG_ICONS["dollar-sign"]}</span><span>Funding Stage Distribution</span></div>'), unsafe_allow_html=True)
            fund_counts = df["Funding Stage"].value_counts().reset_index()
            fund_counts.columns = ["Funding Stage", "Count"]
            fig_fund = px.bar(
                fund_counts,
                x="Funding Stage",
                y="Count",
                color="Funding Stage",
                color_discrete_sequence=chart_color_sequence
            )
            fig_fund.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=260,
                xaxis_title="Funding Stage",
                yaxis_title="Accounts"
            )
            st.plotly_chart(fig_fund, use_container_width=True)
            
        with col2:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#22C55E;">{SVG_ICONS["trending-up"]}</span><span>Recent Funding Velocity</span></div>'), unsafe_allow_html=True)
            rf_counts = df["Recent Funding"].value_counts().reset_index()
            rf_counts.columns = ["Recent Funding", "Count"]
            fig_rf = px.pie(
                rf_counts,
                values="Count",
                names="Recent Funding",
                color="Recent Funding",
                color_discrete_map={"Yes": "#10B981", "No": "#64748B"},
                hole=0.45
            )
            fig_rf.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=260
            )
            st.plotly_chart(fig_rf, use_container_width=True)

    # ------------------ 3. LOCATION ANALYSIS ------------------
    with st.expander("🌐 Location Analysis", expanded=False):
        st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#3B82F6;">{SVG_ICONS["globe"]}</span><span>Geographic Accounts Distribution</span></div>'), unsafe_allow_html=True)
        loc_counts = df["Location"].value_counts().reset_index()
        loc_counts.columns = ["Location", "Count"]
        
        fig_loc = px.bar(
            loc_counts,
            x="Location",
            y="Count",
            color="Location",
            color_discrete_sequence=chart_color_sequence
        )
        fig_loc.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            height=300,
            xaxis_title="HQ Location / Region",
            yaxis_title="Account Count"
        )
        st.plotly_chart(fig_loc, use_container_width=True)

    # ------------------ 4. GROWTH ANALYSIS ------------------
    with st.expander("📈 Growth Analysis", expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#EF4444;">{SVG_ICONS["activity"]}</span><span>Hiring Activity Intensity</span></div>'), unsafe_allow_html=True)
            hir_counts = df["Hiring Activity"].value_counts().reset_index()
            hir_counts.columns = ["Hiring Speed", "Count"]
            fig_hir = px.bar(
                hir_counts, x="Hiring Speed", y="Count", color="Hiring Speed",
                color_discrete_map={"High": "#22C55E", "Medium": "#3B82F6", "Low": "#F59E0B", "None": "#64748B"}
            )
            fig_hir.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS, height=240, showlegend=False,
                xaxis_title="Hiring Activity", yaxis_title="Accounts"
            )
            st.plotly_chart(fig_hir, use_container_width=True)
            
        with col2:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#10B981;">{SVG_ICONS["check-circle"]}</span><span>Expansion Footprint Velocity</span></div>'), unsafe_allow_html=True)
            exp_counts = df["Expansion Status"].value_counts().reset_index()
            exp_counts.columns = ["Expansion Status", "Count"]
            fig_exp = px.bar(
                exp_counts, x="Expansion Status", y="Count", color="Expansion Status",
                color_discrete_map={"Expanding": "#10B981", "Stable": "#3B82F6", "Contracting": "#EF4444"}
            )
            fig_exp.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS, height=240, showlegend=False,
                xaxis_title="Expansion Status", yaxis_title="Accounts"
            )
            st.plotly_chart(fig_exp, use_container_width=True)

    # ------------------ 5. SCORE ANALYSIS & CORRELATIONS ------------------
    with st.expander("📊 Score Analysis & Correlations", expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#3B82F6;">{SVG_ICONS["bar-chart"]}</span><span>ICP Score Distribution</span></div>'), unsafe_allow_html=True)
            fig_icp = px.histogram(
                df, x="icp_score", nbins=12, color_discrete_sequence=["#3B82F6"]
            )
            fig_icp.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS, height=240,
                xaxis_title="ICP Score", yaxis_title="Count", bargap=0.08
            )
            st.plotly_chart(fig_icp, use_container_width=True)
            
        with col2:
            st.markdown(clean_html(f'<div class="saas-card-title"><span style="color:#10B981;">{SVG_ICONS["target"]}</span><span>GTM Opportunity Score Distribution</span></div>'), unsafe_allow_html=True)
            fig_opp = px.histogram(
                df, x="gtm_opportunity_score", nbins=12, color_discrete_sequence=["#10B981"]
            )
            fig_opp.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS, height=240,
                xaxis_title="Opportunity Score", yaxis_title="Count", bargap=0.08
            )
            st.plotly_chart(fig_opp, use_container_width=True)
            
        st.markdown("#### Opportunity Score Correlations")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(clean_html(f'<div class="saas-card-title">Industry vs Opportunity Score</div>'), unsafe_allow_html=True)
            fig_box_ind = px.box(df, x="Industry", y="gtm_opportunity_score", color_discrete_sequence=["#3B82F6"])
            fig_box_ind.update_layout(**PLOTLY_LAYOUT_DEFAULTS, height=250, xaxis_title=None, yaxis_title="Score")
            st.plotly_chart(fig_box_ind, use_container_width=True)
        with col_c2:
            st.markdown(clean_html(f'<div class="saas-card-title">Funding Stage vs Opportunity Score</div>'), unsafe_allow_html=True)
            fig_box_fund = px.box(df, x="Funding Stage", y="gtm_opportunity_score", color_discrete_sequence=["#F59E0B"])
            fig_box_fund.update_layout(**PLOTLY_LAYOUT_DEFAULTS, height=250, xaxis_title=None, yaxis_title="Score")
            st.plotly_chart(fig_box_fund, use_container_width=True)
        with col_c3:
            st.markdown(clean_html(f'<div class="saas-card-title">Location vs Opportunity Score</div>'), unsafe_allow_html=True)
            fig_box_loc = px.box(df, x="Location", y="gtm_opportunity_score", color_discrete_sequence=["#14B8A6"])
            fig_box_loc.update_layout(**PLOTLY_LAYOUT_DEFAULTS, height=250, xaxis_title=None, yaxis_title="Score")
            st.plotly_chart(fig_box_loc, use_container_width=True)
