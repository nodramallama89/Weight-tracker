import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Yesterday's Review", layout="centered")

@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean numeric columns
        cols = ['Cal', 'Steps', 'Prot', 'Carb', 'Fat', 'Alc']
        for col in cols:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # THIS is the logic fix: Filter for completed rows where Steps > 0
    completed_rows = df[df['Steps'].notna() & (df['Steps'] > 0)]
    
    if not completed_rows.empty:
        yesterday = completed_rows.iloc[-1]
        
        st.title("🛡️ Yesterday's Review")
        st.subheader(f"Date: {yesterday['Date']}")
        
        # Calories
        cal_diff = yesterday['Cal'] - 1633
        st.metric("Calories Consumed", f"{yesterday['Cal']:.0f}", f"{cal_diff:+.0f} vs 1633")
        
        # Steps
        step_diff = yesterday['Steps'] - 10000
        st.metric("Steps", f"{yesterday['Steps']:,.0f}", f"{step_diff:+.0f} vs 10k")
        
        # Macros
        cols = st.columns(4)
        cols[0].metric("Prot", f"{yesterday['Prot']:.0f}%")
        cols[1].metric("Carbs", f"{yesterday['Carb']:.0f}%")
        cols[2].metric("Fat", f"{yesterday['Fat']:.0f}%")
        cols[3].metric("Alc", f"{yesterday['Alc']:.0f}%")
    else:
        st.error("No completed rows (with steps) found.")
else:
    st.error("Could not load data.")
