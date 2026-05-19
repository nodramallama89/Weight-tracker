import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="centered")

@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        # Create dataframe, skip first row (headers)
        df = pd.DataFrame(data[1:])
        return df
    except Exception as e:
        st.error(f"Error loading: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Column Index Mapping (0-based)
    # A=0, B=1, ..., M=12, Q=16, R=17, S=18, T=19
    # We filter by Steps (Column 12) being NOT empty
    completed_rows = df[df[12] != ""]
    
    if not completed_rows.empty:
        yesterday = completed_rows.iloc[-1]
        
        # Helper to convert to float safely
        def to_n(val):
            try: return float(str(val).replace('%','').replace(',',''))
            except: return 0.0

        cals = to_n(yesterday[1]) # Column B
        steps = to_n(yesterday[12]) # Column M
        prot = to_n(yesterday[16]) # Column Q
        carbs = to_n(yesterday[17]) # Column R
        fat = to_n(yesterday[18]) # Column S
        alc = to_n(yesterday[19]) # Column T
        
        st.title("🛡️ Yesterday's Review")
        st.subheader(f"Date: {yesterday[0]}") # Column A
        
        # 1. Calories (Target 1633)
        cal_diff = cals - 1633
        st.metric("Calories Consumed", f"{cals:.0f}", f"{cal_diff:+.0f} vs 1633", delta_color="inverse")
        
        # 2. Steps (Target 10,000)
        step_diff = steps - 10000
        st.metric("Steps", f"{steps:,.0f}", f"{step_diff:+.0f} vs 10k")
        
        # 3. Macros
        cols = st.columns(4)
        cols[0].metric("Prot", f"{prot:.0f}%")
        cols[1].metric("Carbs", f"{carbs:.0f}%")
        cols[2].metric("Fat", f"{fat:.0f}%")
        cols[3].metric("Alc", f"{alc:.0f}")
    else:
        st.error("No completed rows (with steps) found.")
else:
    st.error("Could not load data.")
