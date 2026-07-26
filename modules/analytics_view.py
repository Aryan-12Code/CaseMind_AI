"""
analytics_view.py — Analytics & Suspicion Dashboard for CaseMind AI.

Interactive Plotly charts and the rule-based suspicion score leaderboard.
"""

import streamlit as st
from modules.database import init_db
import modules.chart_generator as cg
from modules.suspicion_score import generate_suspicion_scores


def render() -> None:
    """Render the Analytics page."""
    init_db()

    st.title("📊 Analytics & Insights")
    st.write("Deep dive into evidence distribution, keyword frequencies, and entity analytics.")
    st.markdown("---")

    # ── Suspicion Leaderboard ────────────────────────────────────────────────
    st.subheader("🚨 High-Risk Individuals (Suspicion Scores)")
    st.write("Rule-based scoring detecting potentially suspicious behavior (money, destruction, secrets).")
    
    with st.spinner("Calculating risk scores..."):
        suspects = generate_suspicion_scores()
        
    if not suspects:
        st.info("No persons detected to score.")
    else:
        # Show top 5 in detailed cards
        for s in suspects[:5]:
            st.markdown(f"""
            <div style="background-color:#1E1E1E; padding:15px; border-radius:8px; margin-bottom:10px; border:1px solid #333;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                    <h4 style="margin:0; color:#FFF;">{s['name']}</h4>
                    <span style="background-color:{s['risk_color']}; color:white; padding:3px 10px; border-radius:12px; font-size:0.85em; font-weight:bold;">
                        {s['risk_level']} ({s['percentage']}%)
                    </span>
                </div>
                <!-- Progress Bar -->
                <div style="width:100%; background-color:#333; border-radius:4px; height:8px; margin-bottom:10px;">
                    <div style="width:{s['percentage']}%; background-color:{s['risk_color']}; height:100%; border-radius:4px;"></div>
                </div>
                <div style="color:#aaa; font-size:0.9em;">
                    <strong>Reasons:</strong> {', '.join(s['reasons'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.expander("View all scored individuals"):
            st.dataframe([
                {"Name": s["name"], "Score": f"{s['percentage']}%", "Risk": s["risk_level"], "Top Reason": s["reasons"][0] if s["reasons"] else "None"}
                for s in suspects
            ], use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Interactive Charts ───────────────────────────────────────────────────
    st.subheader("📈 Evidence Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(cg.get_evidence_type_pie_chart(), use_container_width=True)
        st.plotly_chart(cg.get_entity_distribution_pie(), use_container_width=True)
        
    with col2:
        st.plotly_chart(cg.get_most_mentioned_people_bar(), use_container_width=True)
        st.plotly_chart(cg.get_keyword_frequency_bar(), use_container_width=True)
        
    st.markdown("---")
    st.plotly_chart(cg.get_upload_timeline_line(), use_container_width=True)
