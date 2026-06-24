"""
Revenue and Market Intelligence Page for Enterprise GTM Account Intelligence Platform.
Performs GTM Quadrant Analysis and simulates GTM revenue potential based on firmographic segment ACVs.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.constants import PLOTLY_LAYOUT_DEFAULTS

def render_revenue_market_intelligence(df: pd.DataFrame) -> None:
    """Renders Founder's Office market opportunity analytics."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0;">Revenue & Market Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:1.1rem; margin-top:2px;">Macro market evaluations, segment revenue forecasts, and GTM fit quadrant simulations.</p>', unsafe_allow_html=True)
    
    # ------------------ REVENUE POTENTIAL BY SEGMENT ------------------
    st.markdown('<h3 class="section-title">💰 Segment Addressable Revenue Simulation</h3>', unsafe_allow_html=True)
    
    # Target ACVs per segment
    ACV_MAPPINGS = {
        "Enterprise": 50000,
        "Mid-Market": 20000,
        "SMB": 5000,
        "Startup": 1500
    }
    
    # Let users customize target ACVs dynamically in the page! (Super premium feature)
    with st.expander("⚙ Custom ACV Settings"):
        acv_col1, acv_col2, acv_col3, acv_col4 = st.columns(4)
        with acv_col1:
            acv_ent = st.number_input("Enterprise ACV ($)", value=ACV_MAPPINGS["Enterprise"], step=5000)
        with acv_col2:
            acv_mid = st.number_input("Mid-Market ACV ($)", value=ACV_MAPPINGS["Mid-Market"], step=2000)
        with acv_col3:
            acv_smb = st.number_input("SMB ACV ($)", value=ACV_MAPPINGS["SMB"], step=500)
        with acv_col4:
            acv_stu = st.number_input("Startup ACV ($)", value=ACV_MAPPINGS["Startup"], step=100)
            
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
            <div class="metric-card">
                <div class="metric-label">Simulated Market Pipe</div>
                <div class="metric-value" style="color:#10b981;">${total_pipeline:,.0f}</div>
                <div class="metric-delta">Target Pipeline Value</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        # Pipeline average deal size
        avg_deal_size = total_pipeline / len(df) if len(df) > 0 else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average ACV</div>
                <div class="metric-value">${avg_deal_size:,.0f}</div>
                <div class="metric-delta">Across all profiles</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        # Segment contribution details
        pipe_summary_str = " | ".join([f"<b>{row['Segment']}:</b> ${row['Pipeline Value']:,.0f}" for _, row in seg_group.iterrows()])
        st.markdown(f"""
            <div class="metric-card" style="height:104px; display:flex; flex-direction:column; justify-content:center;">
                <div class="metric-label">Pipeline Contribution</div>
                <div style="font-size:0.88rem; color:#475569; margin-top:2px;">{pipe_summary_str}</div>
            </div>
        """, unsafe_allow_html=True)
        
    # Render Revenue Potential Bar Chart
    fig_rev = px.bar(
        seg_group,
        x="Segment",
        y="Pipeline Value",
        color="Segment",
        text="Pipeline Value",
        color_discrete_sequence=["#6366f1", "#14b8a6", "#3b82f6", "#f59e0b"],
        labels={"Pipeline Value": "Pipeline Value ($)"}
    )
    fig_rev.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis_title="Firmographic Segment",
        yaxis_title="Pipeline Potential ($)"
    )
    fig_rev.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig_rev, use_container_width=True)
    
    st.markdown("---")

    # ------------------ GTM QUADRANT FIT ANALYSIS ------------------
    st.markdown('<h3 class="section-title">🎯 GTM FIT & INTENT QUADRANT ANALYSIS</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:0.9rem; margin-top:-10px; margin-bottom:15px;">Maps Account ICP Alignment (Fit) against Buying Signals (Intent) to isolate priority segments.</p>', unsafe_allow_html=True)
    
    # Create the scatter plot
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
    
    # Draw quadrant dividers at ICP=60, Buying=40 (or ICP=70, Buying=50)
    fig_quad.add_shape(
        type="line", x0=60, y0=0, x1=60, y1=100,
        line=dict(color="#cbd5e1", width=1.5, dash="dash")
    )
    fig_quad.add_shape(
        type="line", x0=0, y0=40, x1=100, y1=40,
        line=dict(color="#cbd5e1", width=1.5, dash="dash")
    )
    
    # Add labels in the four quadrants
    fig_quad.add_annotation(
        x=80, y=80, text="🔥 Sweet Spot (High Fit + High Intent)",
        showarrow=False, font=dict(color="#10b981", size=11, family="Plus Jakarta Sans")
    )
    fig_quad.add_annotation(
        x=25, y=80, text="⚡ Intent Waves (Low Fit + High Intent)",
        showarrow=False, font=dict(color="#3b82f6", size=11, family="Plus Jakarta Sans")
    )
    fig_quad.add_annotation(
        x=80, y=20, text="📈 Long-term Fit (High Fit + Low Intent)",
        showarrow=False, font=dict(color="#f59e0b", size=11, family="Plus Jakarta Sans")
    )
    fig_quad.add_annotation(
        x=25, y=20, text="💤 Cold Targets (Low Fit + Low Intent)",
        showarrow=False, font=dict(color="#64748b", size=11, family="Plus Jakarta Sans")
    )
    
    fig_quad.update_layout(
        **PLOTLY_LAYOUT_DEFAULTS,
        xaxis=dict(range=[0, 105]),
        yaxis=dict(range=[0, 105]),
        height=550
    )
    
    st.plotly_chart(fig_quad, use_container_width=True)
    
    st.markdown("---")

    # ------------------ INDUSTRY MACRO SUMMARY ------------------
    st.markdown('<h3 class="section-title">📊 Industry Segment Deep-Dive Matrix</h3>', unsafe_allow_html=True)
    
    ind_macro = df.groupby("Industry").agg(
        avg_icp=("icp_score", "mean"),
        avg_buying=("buying_signal_score", "mean"),
        avg_opp=("gtm_opportunity_score", "mean"),
        total_accounts=("id", "count")
    ).reset_index()
    
    # Calculate simulated industry pipeline
    # Match segments for each industry and multiply by ACV
    df_with_acv = df.copy()
    df_with_acv["ACV"] = df_with_acv["firmographic_segment"].map(custom_acvs)
    ind_pipeline = df_with_acv.groupby("Industry")["ACV"].sum().reset_index()
    ind_pipeline.columns = ["Industry", "Simulated Pipeline ($)"]
    
    # Merge and present
    ind_macro = ind_macro.merge(ind_pipeline, on="Industry")
    
    # Sort
    ind_macro = ind_macro.sort_values(by="avg_opp", ascending=False)
    
    # Display Industry Macro Table
    html_rows = []
    for _, row in ind_macro.iterrows():
        html_rows.append(f"""
            <tr style="border-bottom:1px solid #f1f5f9;">
                <td style="padding: 12px; font-weight: 600; color: #1e293b;">{row['Industry']}</td>
                <td style="padding: 12px; text-align: center; font-weight: 600; color: #6366f1;">{row['avg_icp']:.1f}</td>
                <td style="padding: 12px; text-align: center; font-weight: 600; color: #ff9f43;">{row['avg_buying']:.1f}</td>
                <td style="padding: 12px; text-align: center; font-weight: 700; color: #10b981;">{row['avg_opp']:.1f}</td>
                <td style="padding: 12px; text-align: center; color: #475569;">{row['total_accounts']}</td>
                <td style="padding: 12px; text-align: right; font-weight: 700; color: #1e293b;">${row['Simulated Pipeline ($)']:,.0f}</td>
            </tr>
        """)
        
    html_table = f"""
    <div style="overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 10px;">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; background-color: #ffffff;">
            <thead>
                <tr style="background-color: #f8fafc; border-bottom: 2px solid #e2e8f0; color: #475569; font-weight: 600;">
                    <th style="padding: 12px;">Industry Sector</th>
                    <th style="padding: 12px; text-align: center;">Average ICP Score</th>
                    <th style="padding: 12px; text-align: center;">Average Buying Signal</th>
                    <th style="padding: 12px; text-align: center;">Average Opportunity Score</th>
                    <th style="padding: 12px; text-align: center;">Total Accounts</th>
                    <th style="padding: 12px; text-align: right;">Simulated Pipe Value</th>
                </tr>
            </thead>
            <tbody>
                {"".join(html_rows)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)
