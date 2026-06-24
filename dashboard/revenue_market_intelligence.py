"""
Revenue and Market Intelligence Page for Enterprise GTM Account Intelligence Platform.
Performs GTM Quadrant Analysis and simulates GTM revenue potential based on firmographic segment ACVs.
Clean B2B SaaS layout with Lucide SVG icons and no emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.constants import SVG_ICONS, PLOTLY_LAYOUT_DEFAULTS

def render_revenue_market_intelligence(df: pd.DataFrame) -> None:
    """Renders Founder's Office market opportunity analytics."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">Revenue & Market Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">Macro market evaluations, segment revenue forecasts, and GTM fit quadrant simulations.</p>', unsafe_allow_html=True)
    
    # ------------------ REVENUE POTENTIAL BY SEGMENT ------------------
    st.markdown('<h3 style="color:#FFFFFF; margin-bottom:12px;">Segment Addressable Revenue Simulation</h3>', unsafe_allow_html=True)
    
    # Target ACVs per segment
    ACV_MAPPINGS = {
        "Enterprise": 50000,
        "Mid-Market": 20000,
        "SMB": 500,
        "Startup": 150
    }
    
    # Let users customize target ACVs dynamically in the page
    with st.container(border=True):
        acv_col1, acv_col2, acv_col3, acv_col4 = st.columns(4)
        with acv_col1:
            acv_ent = st.number_input("Enterprise ACV ($)", value=50000, step=5000)
        with acv_col2:
            acv_mid = st.number_input("Mid-Market ACV ($)", value=20000, step=2000)
        with acv_col3:
            acv_smb = st.number_input("SMB ACV ($)", value=5000, step=500)
        with acv_col4:
            acv_stu = st.number_input("Startup ACV ($)", value=1500, step=100)
            
    custom_acvs = {
        "Enterprise": acv_ent,
        "Mid-Market": acv_mid,
        "SMB": acv_smb,
        "Startup": acv_stu
    }
    
    # Compute counts and revenue
    seg_group = df["firmographic_segment"].value_counts().reset_index()
    seg_group.columns = ["Segment", "Count"]
    
    seg_group["ACV"] = seg_group["Segment"].map(custom_acvs)
    seg_group["Pipeline Value"] = seg_group["Count"] * seg_group["ACV"]
    
    total_pipeline = seg_group["Pipeline Value"].sum()
    
    # Display Pipeline Summary Cards
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Simulated Market Pipe</span>
                    <span style="color:#10B981;">{SVG_ICONS['dollar-sign']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value" style="color:#22C55E !important;">${total_pipeline:,.0f}</h2>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="20" viewBox="0 0 120 20" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 18 Q15 12 30 15 T60 8 T90 10 T120 2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        avg_deal_size = total_pipeline / len(df) if len(df) > 0 else 0
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Average ACV</span>
                    <span style="color:#3B82F6;">{SVG_ICONS['activity']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">${avg_deal_size:,.0f}</h2>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="20" viewBox="0 0 120 20" fill="none" stroke="#3B82F6" stroke-width="1.5">
                        <path d="M0 10 Q15 14 30 10 T60 15 T90 8 T120 2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        pipe_summary_str = " | ".join([f"<b>{row['Segment']}:</b> ${row['Pipeline Value']:,.0f}" for _, row in seg_group.iterrows()])
        st.markdown(f"""
            <div class="saas-card" style="padding:20px; height:122px; display:flex; flex-direction:column; justify-content:center;">
                <div class="saas-metric-label" style="margin-bottom:8px;">Pipeline Contribution</div>
                <div style="font-size:0.85rem; color:#9CA3AF;">{pipe_summary_str}</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Render Revenue Potential Bar Chart
    with st.container(border=True):
        fig_rev = px.bar(
            seg_group,
            x="Segment",
            y="Pipeline Value",
            color="Segment",
            text="Pipeline Value",
            color_discrete_sequence=["#3B82F6", "#14B8A6", "#8B5CF6", "#F59E0B"],
            labels={"Pipeline Value": "Pipeline Value ($)"}
        )
        fig_rev.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            height=300,
            xaxis_title="Firmographic Segment",
            yaxis_title="Pipeline Potential ($)"
        )
        fig_rev.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_rev, use_container_width=True)
    
    st.markdown("---")

    # ------------------ GTM QUADRANT FIT ANALYSIS ------------------
    st.markdown('<h3 style="color:#FFFFFF; margin-bottom:4px;">GTM Fit & Intent Quadrant Analysis</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748B; font-size:0.88rem; margin-top:0; margin-bottom:16px;">Maps Account ICP Alignment (Fit) against Buying Signals (Intent) to isolate priority segments.</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        fig_quad = px.scatter(
            df,
            x="icp_score",
            y="buying_signal_score",
            color="gtm_opportunity_score",
            size="Employee Count",
            hover_name="Company Name",
            hover_data=["Industry", "Funding Stage", "Location", "priority_level", "abm_tier"],
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={
                "icp_score": "ICP Score (Fit)",
                "buying_signal_score": "Buying Signal Score (Intent)",
                "gtm_opportunity_score": "GTM Opportunity Score"
            }
        )
        
        # Draw quadrant dividers
        fig_quad.add_shape(
            type="line", x0=60, y0=0, x1=60, y1=100,
            line=dict(color="#253047", width=1.5, dash="dash")
        )
        fig_quad.add_shape(
            type="line", x0=0, y0=40, x1=100, y1=40,
            line=dict(color="#253047", width=1.5, dash="dash")
        )
        
        # Add labels in the four quadrants
        fig_quad.add_annotation(
            x=80, y=85, text="Sweet Spot (High Fit + High Intent)",
            showarrow=False, font=dict(color="#22C55E", size=10, family="Plus Jakarta Sans")
        )
        fig_quad.add_annotation(
            x=25, y=85, text="Intent Waves (Low Fit + High Intent)",
            showarrow=False, font=dict(color="#3B82F6", size=10, family="Plus Jakarta Sans")
        )
        fig_quad.add_annotation(
            x=80, y=15, text="Long-term Fit (High Fit + Low Intent)",
            showarrow=False, font=dict(color="#F59E0B", size=10, family="Plus Jakarta Sans")
        )
        fig_quad.add_annotation(
            x=25, y=15, text="Cold Targets (Low Fit + Low Intent)",
            showarrow=False, font=dict(color="#64748B", size=10, family="Plus Jakarta Sans")
        )
        
        fig_quad.update_layout(
            **PLOTLY_LAYOUT_DEFAULTS,
            xaxis=dict(range=[0, 105], title="ICP Score (Fit)"),
            yaxis=dict(range=[0, 105], title="Buying Signal Score (Intent)"),
            height=480
        )
        
        st.plotly_chart(fig_quad, use_container_width=True)
    
    st.markdown("---")

    # ------------------ INDUSTRY MACRO SUMMARY ------------------
    st.markdown('<h3 style="color:#FFFFFF; margin-bottom:12px;">Industry Segment Deep-Dive Matrix</h3>', unsafe_allow_html=True)
    
    ind_macro = df.groupby("Industry").agg(
        avg_icp=("icp_score", "mean"),
        avg_buying=("buying_signal_score", "mean"),
        avg_opp=("gtm_opportunity_score", "mean"),
        total_accounts=("id", "count")
    ).reset_index()
    
    # Calculate simulated industry pipeline
    df_with_acv = df.copy()
    df_with_acv["ACV"] = df_with_acv["firmographic_segment"].map(custom_acvs)
    ind_pipeline = df_with_acv.groupby("Industry")["ACV"].sum().reset_index()
    ind_pipeline.columns = ["Industry", "Simulated Pipeline ($)"]
    
    ind_macro = ind_macro.merge(ind_pipeline, on="Industry")
    ind_macro = ind_macro.sort_values(by="avg_opp", ascending=False)
    
    html_rows = []
    for _, row in ind_macro.iterrows():
        html_rows.append(f"""
            <tr style="border-bottom:1px solid #253047;">
                <td style="padding:12px; font-weight:600; color:#FFFFFF;">{row['Industry']}</td>
                <td style="padding:12px; text-align:center; font-weight:600; color:#3B82F6;">{row['avg_icp']:.1f}</td>
                <td style="padding:12px; text-align:center; font-weight:600; color:#F59E0B;">{row['avg_buying']:.1f}</td>
                <td style="padding:12px; text-align:center; font-weight:700; color:#22C55E;">{row['avg_opp']:.1f}</td>
                <td style="padding:12px; text-align:center; color:#9CA3AF;">{row['total_accounts']}</td>
                <td style="padding:12px; text-align:right; font-weight:700; color:#FFFFFF;">${row['Simulated Pipeline ($)']:,.0f}</td>
            </tr>
        """)
        
    st.markdown(f"""
        <div class="saas-card">
            <table style="width:100%; border-collapse:collapse; font-size:0.88rem; text-align:left;">
                <thead>
                    <tr style="background-color:#111827; border-bottom:2px solid #253047; color:#9CA3AF;">
                        <th style="padding:12px;">Industry Sector</th>
                        <th style="padding:12px; text-align:center;">Average ICP Score</th>
                        <th style="padding:12px; text-align:center;">Average Buying Signal</th>
                        <th style="padding:12px; text-align:center;">Average GTM Index</th>
                        <th style="padding:12px; text-align:center;">Total Accounts</th>
                        <th style="padding:12px; text-align:right;">Simulated Pipeline</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(html_rows)}
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)
