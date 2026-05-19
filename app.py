import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- Polished "App-Like" Styling ---
st.markdown("""
    <style>
    /* Force consistent height for cards */
    [data-testid="column"] { display: flex; }
    .card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #eef0f2;
        width: 100%;
        display: flex;
        flex-direction: column;
    }
    .stat-title { font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .stat-val { font-size: 2.2rem; font-weight: 700; color: #2c3e50; }
    .stat-footer { font-size: 0.85rem; color: #95a5a6; margin-top: auto; }
    .stApp { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

def render_card(title, value, footer):
    st.markdown(f"""
        <div class='card'>
            <div class='stat-title'>{title}</div>
            <div class='stat-val'>{value}</div>
            <div class='stat-footer'>{footer}</div>
        </div>
    """, unsafe_allow_html=True)

# --- Logic & Data Loading ---
# [Include your validated load_data() function here]
# ...

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    loss_per_week = ((df.iloc[0]['Weight'] - df.iloc[-1]['Weight']) / ((df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7))
    days_to_target = (df.iloc[-1]['Weight'] - 175) / (loss_per_week / 7) if loss_per_week > 0 else 0
    target_date = datetime.now() + timedelta(days=days_to_target)

    # --- Energy Row ---
    st.subheader("⚡ Energy Status")
    c1, c2, c3 = st.columns(3)
    with c1: render_card("Average Calories", f"{avg_cal:.0f}", "Lifetime Average")
    with c2: render_card("vs Target (1633)", f"{avg_cal-1633:.0f}", "Goal: 1,633 kcal")
    with c3: render_card("vs Maint (2500)", f"{avg_cal-2500:.0f}", "Maintenance: 2,500 kcal")
    
    # --- Momentum Row ---
    st.subheader("🚀 Momentum (Steps vs 10k Target)")
    r1, r2, r3 = st.columns(3)
    with r1: render_card("7D Avg", f"{s7:,.0f}", "Target: 10,000 steps")
    with r2: render_card("14D Avg", f"{s14:,.0f}", "Target: 10,000 steps")
    with r3: render_card("30D Avg", f"{s30:,.0f}", "Target: 10,000 steps")
    
    # --- Milestones Row ---
    st.subheader("🎯 Mission Milestones")
    m1, m2, m3 = st.columns(3)
    with m1: render_card("Days on Diet", f"{len(df)}", "Since day 1")
    with m2: render_card("Avg Loss/Week", f"{loss_per_week:.2f} lbs", "Overall pace")
    with m3: render_card("Est. Target Date", target_date.strftime('%b %d, %Y'), "Based on lifetime pace")

    with st.expander("📂 View Raw Telemetry Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
