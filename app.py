import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# App config
st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- Authentication ---
def get_gsheets_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_data():
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        values = worksheet.get_all_values()
        df = pd.DataFrame(values[1:], columns=values[0])
        # Clean: Drop rows where Date is empty
        df = df[df.iloc[:, 0] != ""]
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- Load & Clean Data ---
df = load_data()
if not df.empty:
    df['Date'] = pd.to_datetime(df.iloc[:, 0], format='%d/%m/%Y')
    # Numeric conversion
    cols_to_num = {1: 'Cal', 3: 'Weight', 12: 'Steps', 16: 'Prot', 17: 'Carb', 18: 'Fat', 19: 'Alc'}
    for idx, name in cols_to_num.items():
        df[name] = pd.to_numeric(df.iloc[:, idx].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
    
    df = df.sort_values('Date')
    
    # --- Calculations ---
    # Global Metrics
    total_days = len(df)
    avg_cal = df['Cal'].mean()
    avg_steps = df['Steps'].mean()
    
    # Rolling averages
    last_7 = df.tail(7)
    last_14 = df.tail(14)
    last_30 = df.tail(30)
    
    # Alcohol Logic
    alc_days = (df['Alc'] > 0).sum()
    alc_freq = total_days / alc_days if alc_days > 0 else 0
    
    # Weight Loss Rate (per week)
    if total_days >= 7:
        start_w = df.iloc[0]['Weight']
        latest_w = df.iloc[-1]['Weight']
        weeks = (df.iloc[-1]['Date'] - df.iloc[0]['Date']).days / 7
        avg_loss_per_week = (start_w - latest_w) / weeks if weeks > 0 else 0
    else:
        avg_loss_per_week = 0

    # --- UI Layout ---
    st.title("🛡️ Hardy House Command")
    
    tab1, tab2 = st.tabs(["📊 Averages & Metrics", "📈 Detailed Trends"])
    
    with tab1:
        st.subheader("Calorie & Step Targets")
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Calories", f"{int(avg_cal)}", f"{int(avg_cal - 1633)} vs Target")
        c2.metric("Avg Steps", f"{int(avg_steps):,}", f"{int(avg_steps - 10000)} vs Target")
        c3.metric("Variance to Maint", f"{int(2500 - avg_cal)} under")
        
        st.subheader("Macro & Lifestyle")
        c4, c5, c6 = st.columns(3)
        c4.metric("Avg Protein %", f"{df['Prot'].mean():.1f}%")
        c5.metric("Avg Carbs %", f"{df['Carb'].mean():.1f}%")
        c6.metric("Alcohol Freq", f"1 in {alc_freq:.1f} days")
        
        st.subheader("Trends & Projections")
        c7, c8, c9 = st.columns(3)
        c7.metric("Days on Diet", total_days)
        c8.metric("Avg Loss/Week", f"{avg_loss_per_week:.2f} lbs")
        c9.metric("7-Day Step Avg", f"{int(last_7['Steps'].mean()):,}")
        
    with tab2:
        st.line_chart(df.set_index('Date')[['Weight']])
        st.line_chart(df.set_index('Date')[['Cal', 'Steps']])

else:
    st.info("Waiting for data...")
