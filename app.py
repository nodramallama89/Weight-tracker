import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# Custom CSS for a sleek, non-clinical look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    [data-testid="stMetric"] { 
        background-color: #1c2526; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #334444;
        color: #e0e0e0;
    }
    h2 { color: #00ffcc !important; }
    </style>
""", unsafe_allow_html=True)

# ... (Include your existing get_gsheets_client and load_data functions here) ...
# [Keep the exact load_data logic you verified works!]

df = load_data()

if not df.empty:
    st.title("🛡️ HARDY HOUSE COMMAND")
    
    # --- Calculations ---
    avg_cal = df['Cal'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    loss_per_week = ((df.iloc[0]['Weight'] - df.iloc[-1]['Weight']) / ((df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7))
    target_date = datetime.now() + timedelta(days=(df.iloc[-1]['Weight'] - 175) / (loss_per_week / 7))

    # --- UI Layout ---
    # Section: Energy & Macros
    st.subheader("⚡ Energy Status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Calories", f"{avg_cal:.0f}", f"{avg_cal - 1633:.0f} vs Target", delta_color="inverse")
    c2.metric("vs Maintenance", f"{2500 - avg_cal:.0f} kcal", "Remaining to 2500")
    c3.metric("Step Count (Avg)", f"{df['Steps'].mean():,.0f}")
    
    # Section: Momentum
    st.subheader("🚀 Momentum (Steps)")
    r1, r2, r3 = st.columns(3)
    r1.metric("7D Avg", f"{s7:,.0f}")
    # Higher average = Good trend (Green arrow)
    r2.metric("14D Avg", f"{s14:,.0f}", f"{s7-s14:,.0f} vs 14D", delta_color="normal")
    r3.metric("30D Avg", f"{s30:,.0f}", f"{s7-s30:,.0f} vs 30D", delta_color="normal")
    
    # Section: Milestones
    st.subheader("🎯 Mission Milestones")
    d1, d2, d3 = st.columns(3)
    d1.metric("Days on Diet", len(df))
    d2.metric("Avg Loss/Week", f"{loss_per_week:.2f} lbs")
    d3.metric("Est. Target Date", target_date.strftime('%b %d, %Y'))
