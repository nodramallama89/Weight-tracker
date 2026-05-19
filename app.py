import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_config(layout="wide") # Note: corrected from st.set_page_config

# --- High Contrast Cockpit CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    h2 { color: #00ffcc !important; border-bottom: 1px solid #334444; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ... (Include your existing load_data function here) ...
# [Keep the exact robust load_data logic you verified works!]

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # --- Calculations ---
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # --- Energy Section ---
    st.subheader("⚡ Energy Status")
    c1, c2, c3 = st.columns(3)
    # Goal: Under 1633 is Green, Over is Red
    c1.metric("Avg Calories", f"{avg_cal:.0f}")
    c2.metric("vs Target (1633)", f"{avg_cal - 1633:.0f}", delta_color="inverse")
    c3.metric("vs Maint (2500)", f"{avg_cal - 2500:.0f}", delta_color="inverse")
    
    # --- Momentum Section ---
    st.subheader("🚀 Momentum (Steps vs 10k Target)")
    r1, r2, r3 = st.columns(3)
    # Goal: Over 10k is Green, Under is Red
    r1.metric("7D Avg (vs 10k)", f"{s7:,.0f}", f"{s7 - 10000:,.0f}")
    r2.metric("14D Avg (vs 10k)", f"{s14:,.0f}", f"{s14 - 10000:,.0f}")
    r3.metric("30D Avg (vs 10k)", f"{s30:,.0f}", f"{s30 - 10000:,.0f}")
    
    # --- Milestones Section ---
    st.subheader("🎯 Mission Milestones")
    d1, d2, d3 = st.columns(3)
    d1.metric("Days on Diet", len(df))
    # Dynamic Loss Rate
    loss_per_week = ((df.iloc[0]['Weight'] - df.iloc[-1]['Weight']) / ((df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7))
    d2.metric("Avg Loss/Week", f"{loss_per_week:.2f} lbs")
    # Est target date
    days_to_target = (df.iloc[-1]['Weight'] - 175) / (loss_per_week / 7) if loss_per_week > 0 else 0
    target_date = datetime.now() + timedelta(days=days_to_target)
    d3.metric("Est. Target Date", target_date.strftime('%b %d, %Y') if loss_per_week > 0 else "N/A")
