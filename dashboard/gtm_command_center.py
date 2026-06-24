"""
GTM Command Center Page for Enterprise GTM Account Intelligence Platform.
Clean B2B SaaS layout with Lucide SVG icons, delta sparklines, and a structured dark theme grid.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List
from utils.constants import SVG_ICONS, PLOTLY_LAYOUT_DEFAULTS
from utils.helpers import get_tier_badge, get_priority_badge, get_opportunity_badge

def render_command_center(df: pd.DataFrame) -> None:
    """Renders the executive command center dashboard."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0; color:#FFFFFF;">GTM Command Center</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748B; font-size:1rem; margin-top:2px; margin-bottom:24px;">'
        'Central nervous system for RevOps, founders, and sales development teams.'
        '</p>', 
        unsafe_allow_html=True
    )
    
    # ------------------ TOP EXECUTIVE METRICS STRIP ------------------
    total_accounts = len(df)
    tier_1 = len(df[df["abm_tier"] == "Tier 1"])
    avg_gtm_opp = df["gtm_opportunity_score"].mean()
    high_priority = len(df[df["priority_level"] == "High"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Card 1: Total Accounts
    with col1:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Total Accounts</span>
                    <span style="color: #3B82F6;">{SVG_ICONS['building']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{total_accounts}</h2>
                    <span class="saas-metric-delta delta-up">
                        +12.4%
                    </span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 20 Q15 15 30 10 T60 12 T90 5 T120 2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Card 2: Tier 1 Elite
    with col2:
        tier1_pct = int(tier_1 / total_accounts * 100) if total_accounts > 0 else 0
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Tier 1 Elite Target</span>
                    <span style="color: #F59E0B;">{SVG_ICONS['target']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{tier_1}</h2>
                    <span class="saas-metric-delta delta-up">
                        {tier1_pct}% of ICP
                    </span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#3B82F6" stroke-width="1.5">
                        <path d="M0 12 Q15 14 30 12 T60 13 T90 10 T120 8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Card 3: Avg Opportunity Score
    with col3:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Avg Opportunity</span>
                    <span style="color: #22C55E;">{SVG_ICONS['trending-up']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{avg_gtm_opp:.1f}</h2>
                    <span class="saas-metric-delta delta-up">
                        +5.2%
                    </span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#22C55E" stroke-width="1.5">
                        <path d="M0 22 Q15 15 30 18 T60 8 T90 10 T120 4" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Card 4: Immediate Focus
    with col4:
        st.markdown(f"""
            <div class="saas-metric-card">
                <div class="saas-metric-header">
                    <span class="saas-metric-label">Immediate Focus</span>
                    <span style="color: #EF4444;">{SVG_ICONS['activity']}</span>
                </div>
                <div class="saas-metric-value-row">
                    <h2 class="saas-metric-value">{high_priority}</h2>
                    <span class="saas-metric-delta delta-down" style="color:#EF4444 !important;">
                        🚨 Active
                    </span>
                </div>
                <div class="sparkline-container">
                    <svg width="120" height="24" viewBox="0 0 120 24" fill="none" stroke="#EF4444" stroke-width="1.5">
                        <path d="M0 5 Q15 12 30 10 T60 18 T90 12 T120 20" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ------------------ SECOND ROW: PIPELINE & DISTRIBUTIONS ------------------
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    
    with row2_col1:
        # Pipeline Health
        ACV_MAPPINGS = {"Enterprise": 50000, "Mid-Market": 20000, "SMB": 5000, "Startup": 1500}
        df_acv = df.copy()
        df_acv["acv_val"] = df_acv["firmographic_segment"].map(ACV_MAPPINGS)
        total_pipe = df_acv["acv_val"].sum()
        
        st.markdown(f"""
            <div class="saas-card" style="height: 380px;">
                <div class="saas-card-title">
                    <span style="color: #3B82F6;">{SVG_ICONS['dollar-sign']}</span>
                    <span>Pipeline Health</span>
                </div>
                <div style="margin-top: 15px;">
                    <div style="font-size: 0.85rem; color: #9CA3AF;">Simulated Addressable Pipeline</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #FFFFFF; margin-top: 4px;">${total_pipe:,.0f}</div>
                </div>
                <div style="margin-top: 30px;">
                    <div style="display:flex; justify-content:space-between; font-size: 0.82rem; color: #9CA3AF; margin-bottom: 5px;">
                        <span>Enterprise Segment Reach</span>
                        <span style="color:#FFFFFF; font-weight:600;">{len(df[df['firmographic_segment']=='Enterprise'])} Accounts</span>
                    </div>
                    <div class="saas-progress-bar">
                        <div class="saas-progress-value" style="width: {int(len(df[df['firmographic_segment']=='Enterprise'])/total_accounts*100) if total_accounts > 0 else 0}%; background-color:#3B82F6;"></div>
                    </div>
                    
                    <div style="display:flex; justify-content:space-between; font-size: 0.82rem; color: #9CA3AF; margin-bottom: 5px; margin-top: 15px;">
                        <span>Mid-Market Segment Reach</span>
                        <span style="color:#FFFFFF; font-weight:600;">{len(df[df['firmographic_segment']=='Mid-Market'])} Accounts</span>
                    </div>
                    <div class="saas-progress-bar">
                        <div class="saas-progress-value" style="width: {int(len(df[df['firmographic_segment']=='Mid-Market'])/total_accounts*100) if total_accounts > 0 else 0}%; background-color:#14B8A6;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with row2_col2:
        # Tier Distribution Donut
        with st.container(border=True, key="height380"):
            st.markdown(f'<div class="saas-card-title"><span style="color:#F59E0B;">{SVG_ICONS["target"]}</span><span>ABM Tier Distribution</span></div>', unsafe_allow_html=True)
            
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
            
    with row2_col3:
        # Buying Signal Distribution
        with st.container(border=True, key="height380"):
            st.markdown(f'<div class="saas-card-title"><span style="color:#EF4444;">{SVG_ICONS["activity"]}</span><span>Intent Signals</span></div>', unsafe_allow_html=True)
            
            signal_counts = df["buying_signal_level"].value_counts().reset_index()
            signal_counts.columns = ["Buying Signal", "Count"]
            signal_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#64748B"}
            
            fig_signal = px.pie(
                signal_counts,
                values="Count",
                names="Buying Signal",
                color="Buying Signal",
                color_discrete_map=signal_colors,
                hole=0.55
            )
            fig_signal.update_layout(
                **PLOTLY_LAYOUT_DEFAULTS,
                height=260,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            fig_signal.update_traces(textposition='inside', textinfo='percent')
            st.plotly_chart(fig_signal, use_container_width=True)

    # ------------------ THIRD ROW: TOP OPPORTUNITIES ------------------
    st.markdown('<h3 style="color:#FFFFFF; margin-top:20px; margin-bottom:12px;">Top Opportunities</h3>', unsafe_allow_html=True)
    top_df = df.sort_values(by="gtm_opportunity_score", ascending=False).head(4)
    
    opp_cols = st.columns(4)
    for idx, (_, row) in enumerate(top_df.iterrows()):
        with opp_cols[idx]:
            opp_badge = get_opportunity_badge(row["gtm_opportunity_level"])
            priority_badge = get_priority_badge(row["priority_level"])
            tier_badge = get_tier_badge(row["abm_tier"])
            
            st.markdown(f"""
                <div class="saas-card" style="height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-size:0.75rem; color:#64748B; font-weight:600;">{row['Industry']}</span>
                            <span style="background-color:#1E293B; color:#FFFFFF; border:1px solid #253047; padding:2px 6px; border-radius:4px; font-size:0.8rem; font-weight:700;">
                                {row['gtm_opportunity_score']}
                            </span>
                        </div>
                        <h4 style="margin:0; color:#FFFFFF; font-size:1.1rem; font-weight:700;">{row['Company Name']}</h4>
                        <div style="font-size:0.8rem; color:#9CA3AF; margin-top:4px;">{row['Location']} • {row['Funding Stage']}</div>
                    </div>
                    <div>
                        <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:10px;">
                            {tier_badge} {priority_badge}
                        </div>
                        <div style="font-size:0.8rem; color:#64748B; border-top:1px solid #253047; padding-top:8px;">
                            <b>Primary Contact:</b> {row['primary_contact']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # ------------------ FOURTH ROW: RECOMMENDED ACTIONS & PLAYBOOKS ------------------
    st.markdown('<h3 style="color:#FFFFFF; margin-top:20px; margin-bottom:12px;">Recommended Actions</h3>', unsafe_allow_html=True)
    action_col_left, action_col_right = st.columns([3, 2])
    
    with action_col_left:
        # Accounts needing outreach list
        with st.container(border=True, key="minheight360"):
            st.markdown(f"""
                <div class="saas-card-title">
                    <span style="color:#EF4444;">{SVG_ICONS['activity']}</span>
                    <span>Immediate Outreach Target List</span>
                </div>
            """, unsafe_allow_html=True)
            
            immediate_targets = df[
                (df["priority_level"] == "High") & 
                (df["buying_signal_level"].isin(["High", "Medium"]))
            ].sort_values(by="gtm_opportunity_score", ascending=False).head(3)
            
            if not immediate_targets.empty:
                for _, row in immediate_targets.iterrows():
                    opp_badge = get_opportunity_badge(row["gtm_opportunity_level"])
                    priority_badge = get_priority_badge(row["priority_level"])
                    tier_badge = get_tier_badge(row["abm_tier"])
                    st.markdown(f"""
                        <div style="padding:16px; border:1px solid #253047; border-radius:8px; margin-bottom:12px; background-color:#111827;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="font-size:0.95rem; color:#FFFFFF;">{row['Company Name']}</strong>
                                <div>{tier_badge} {opp_badge}</div>
                            </div>
                            <div style="font-size:0.8rem; color:#9CA3AF; margin-top:4px;">
                                Sector: {row['Industry']} | Emp: {row['Employee Count']} | Primary Contact: {row['primary_contact']}
                            </div>
                            <div style="font-size:0.82rem; margin-top:8px; padding:8px; background-color:#1A2235; border-radius:6px; color:#D1D5DB; border-left:3px solid #3B82F6;">
                                <b>Recommended Play:</b> Directly email the <b>{row['primary_contact']}</b> with value-proposition referencing scaling {row['Industry']}.
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No high priority immediate outreach targets found in this batch.")

    with action_col_right:
        # Spotlight Playbook
        spotlight = df.sort_values(by="gtm_opportunity_score", ascending=False).iloc[0] if not df.empty else None
        if spotlight is not None:
            with st.container(border=True, key="minheight360"):
                st.markdown(f"""
                    <div class="saas-card-title">
                        <span style="color:#3B82F6;">{SVG_ICONS['rocket']}</span>
                        <span>Playbook Spotlight: {spotlight['Company Name']}</span>
                    </div>
                    <div style="font-size:0.82rem; color:#9CA3AF; margin-bottom:12px;">
                        Target Contact: <b>{spotlight['primary_contact']}</b> (Primary)
                    </div>
                    <div class="timeline-container">
                """, unsafe_allow_html=True)
                
                playbook_steps = spotlight["playbook"]
                day_labels = ["Day 1", "Day 3", "Day 7", "Day 14", "Day 21"]
                
                for idx, step in enumerate(playbook_steps[:4]):
                    clean_text = step.split(".", 1)[1].strip() if "." in step else step
                    st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-badge">{idx + 1}</div>
                            <div class="timeline-title">{day_labels[idx]} - {clean_text.split(':')[0]}</div>
                            <div class="timeline-desc">{clean_text.split(':')[-1] if ':' in clean_text else clean_text}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("</div>", unsafe_allow_html=True)
            
    # ------------------ FIFTH ROW: MARKET INTELLIGENCE METRIC ------------------
    st.markdown('<h3 style="color:#FFFFFF; margin-top:20px; margin-bottom:12px;">Market Intelligence Summary</h3>', unsafe_allow_html=True)
    
    ind_data = df.groupby("Industry").agg(
        avg_fit=("icp_score", "mean"),
        avg_intent=("buying_signal_score", "mean"),
        avg_opp=("gtm_opportunity_score", "mean"),
        cnt=("id", "count")
    ).reset_index().sort_values(by="avg_opp", ascending=False)
    
    html_rows = []
    for _, row in ind_data.iterrows():
        html_rows.append(f"""
            <tr style="border-bottom:1px solid #253047;">
                <td style="padding:12px; font-weight:600; color:#FFFFFF;">{row['Industry']}</td>
                <td style="padding:12px; text-align:center; color:#E5E7EB;">{row['cnt']} Accounts</td>
                <td style="padding:12px; text-align:center; font-weight:600; color:#3B82F6;">{row['avg_fit']:.1f}</td>
                <td style="padding:12px; text-align:center; font-weight:600; color:#EF4444;">{row['avg_intent']:.1f}</td>
                <td style="padding:12px; text-align:center; font-weight:700; color:#22C55E;">{row['avg_opp']:.1f}</td>
            </tr>
        """)
        
    st.markdown(f"""
        <div class="saas-card">
            <table style="width:100%; border-collapse:collapse; font-size:0.88rem; text-align:left;">
                <thead>
                    <tr style="background-color:#111827; border-bottom:2px solid #253047; color:#9CA3AF;">
                        <th style="padding:12px;">Industry Vertical</th>
                        <th style="padding:12px; text-align:center;">Segment Count</th>
                        <th style="padding:12px; text-align:center;">Average ICP Fit</th>
                        <th style="padding:12px; text-align:center;">Average Intent Velocity</th>
                        <th style="padding:12px; text-align:center;">Average GTM Index</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(html_rows)}
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)
