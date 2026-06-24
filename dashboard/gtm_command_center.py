"""
GTM Command Center Page for Enterprise GTM Account Intelligence Platform.
Acts as the central executive hub showing top opportunities, immediate outreach alerts,
and segment breakdowns in an Apollo/HubSpot style layout.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from utils.helpers import get_tier_badge, get_priority_badge, get_opportunity_badge

def render_command_center(df: pd.DataFrame) -> None:
    """Renders the executive command center dashboard."""
    if df.empty:
        st.info("No account data loaded. Please upload a CSV file or load sample data from the sidebar.")
        return
        
    st.markdown('<h1 style="margin-bottom:0;">GTM Command Center</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-size:1.1rem; margin-top:2px;">Central nervous system for RevOps, founders, and sales development teams.</p>', unsafe_allow_html=True)
    
    # ------------------ TOP SUMMARY STATS ------------------
    # Pre-calculating variables for the command center
    total_accounts = len(df)
    tier_1 = len(df[df["abm_tier"] == "Tier 1"])
    avg_gtm_opp = int(round(df["gtm_opportunity_score"].mean()))
    high_priority = len(df[df["priority_level"] == "High"])
    
    # Render mini stats strip
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Accounts</div>
                <div class="metric-value">{total_accounts}</div>
                <div class="metric-delta">Active Batch</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tier 1 Elite</div>
                <div class="metric-value">{tier_1}</div>
                <div class="metric-delta">{int(tier_1/total_accounts*100) if total_accounts > 0 else 0}% of ICP Target</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Opportunity</div>
                <div class="metric-value">{avg_gtm_opp}/100</div>
                <div class="metric-delta">GTM Score</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Immediate Focus</div>
                <div class="metric-value" style="color: #ef4444;">{high_priority}</div>
                <div class="metric-delta down">High Priority Target</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ------------------ LAYOUT GRID ------------------
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        # Section 1: Immediate Outreach Targets
        st.markdown('<h3 class="section-title">🚨 Accounts Requiring Immediate Outreach</h3>', unsafe_allow_html=True)
        # Filter for High priority and High/Medium buying signal
        immediate_df = df[
            (df["priority_level"] == "High") & 
            (df["buying_signal_level"].isin(["High", "Medium"]))
        ].sort_values(by="gtm_opportunity_score", ascending=False).head(5)
        
        if not immediate_df.empty:
            for _, row in immediate_df.iterrows():
                # Display individual quick-info row
                opp_badge = get_opportunity_badge(row["gtm_opportunity_level"])
                priority_badge = get_priority_badge(row["priority_level"])
                tier_badge = get_tier_badge(row["abm_tier"])
                
                with st.container():
                    st.markdown(f"""
                        <div style="padding:15px; border:1px solid #e2e8f0; border-radius:10px; margin-bottom:10px; background-color: #ffffff;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="font-size:1.1rem; color:#4f46e5;">{row['Company Name']}</strong>
                                <div>{tier_badge} {opp_badge}</div>
                            </div>
                            <div style="font-size:0.85rem; color:#64748b; margin-top:5px;">
                                <b>Industry:</b> {row['Industry']} | <b>Location:</b> {row['Location']} | <b>Hiring:</b> {row['Hiring Activity']}
                            </div>
                            <div style="font-size:0.9rem; margin-top:8px; padding:8px; background-color:#faf5ff; border-radius:6px; color:#4a5568; border-left:3px solid #818cf8;">
                                <b>Next Play:</b> Direct CEO email to <b>{row['primary_contact']}</b> focusing on {row['Industry']} efficiency.
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No high priority immediate outreach targets found in this batch.")
            
        # Section 2: Segment Opportunities
        st.markdown('<h3 class="section-title" style="margin-top:25px;">💼 Fastest Growing / High Opportunity Industries</h3>', unsafe_allow_html=True)
        # Compute industry performance average
        ind_group = df.groupby("Industry").agg(
            avg_opp=("gtm_opportunity_score", "mean"),
            avg_icp=("icp_score", "mean"),
            count=("id", "count")
        ).reset_index().sort_values(by="avg_opp", ascending=False)
        
        for _, row in ind_group.iterrows():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid #f1f5f9;">
                    <div>
                        <strong style="color:#1e293b;">{row['Industry']}</strong>
                        <span style="font-size:0.8rem; color:#64748b; margin-left:8px;">({row['count']} companies)</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:15px;">
                        <span style="font-size:0.85rem; color:#64748b;">Avg Fit: <b>{int(round(row['avg_icp']))}</b></span>
                        <span style="background-color:#e0e7ff; color:#3730a3; padding:4px 8px; border-radius:6px; font-weight:700; font-size:0.85rem;">
                            {int(round(row['avg_opp']))} Opp Score
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    with right_col:
        # Section 3: Exceptional & Top Opportunities Leaderboard
        st.markdown('<h3 class="section-title">🏆 Top Opportunities</h3>', unsafe_allow_html=True)
        top_df = df.sort_values(by="gtm_opportunity_score", ascending=False).head(5)
        
        for idx, row in top_df.iterrows():
            score_color = "#10b981" if row["gtm_opportunity_score"] >= 90 else "#0d9488"
            st.markdown(f"""
                <div style="display:flex; align-items:center; margin-bottom:15px; padding:10px; border-radius:8px; border:1px solid #f1f5f9; background-color:#ffffff;">
                    <div style="background-color:{score_color}; color:#ffffff; font-weight:800; border-radius:50%; width:36px; height:36px; display:flex; align-items:center; justify-content:center; margin-right:12px; font-size:0.9rem;">
                        {row['gtm_opportunity_score']}
                    </div>
                    <div style="flex-grow:1;">
                        <div style="font-weight:600; color:#1e293b;">{row['Company Name']}</div>
                        <div style="font-size:0.75rem; color:#64748b;">{row['Industry']} • {row['Funding Stage']}</div>
                    </div>
                    <div>
                        <span style="background-color:#f1f5f9; color:#475569; font-size:0.75rem; font-weight:600; padding:2px 6px; border-radius:4px;">
                            {row['abm_tier']}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        # Section 4: GTM Action Checklist / Recommended Plays
        st.markdown('<h3 class="section-title" style="margin-top:25px;">⚡ Recommended Playbook Strategy</h3>', unsafe_allow_html=True)
        # Select one top company to display as active play spotlight
        spotlight = df.sort_values(by="gtm_opportunity_score", ascending=False).iloc[0] if not df.empty else None
        
        if spotlight is not None:
            # Parse playbook
            playbook_steps = spotlight["playbook"]
            
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding:18px; border-radius:12px; border:1px solid #e2e8f0;">
                    <span style="font-size:0.7rem; background-color:#818cf8; color:#ffffff; font-weight:700; padding:2px 6px; border-radius:4px; text-transform:uppercase;">Playbook Spotlight</span>
                    <h4 style="margin:5px 0; color:#0f172a;">{spotlight['Company Name']}</h4>
                    <p style="font-size:0.8rem; color:#64748b; margin-bottom:12px;">Strategy for mapping <b>{spotlight['primary_contact']}</b></p>
            """, unsafe_allow_html=True)
            
            for step in playbook_steps[:3]:  # Top 3 actions
                st.markdown(f"""
                    <div style="font-size:0.85rem; color:#334155; margin-bottom:8px; display:flex; gap:8px;">
                        <span style="color:#4f46e5; font-weight:bold;">✔</span>
                        <span>{step}</span>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
