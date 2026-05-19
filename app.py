import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="wide")

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
        worksheet = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        raw_data = worksheet.get_all_values()
        header = raw_data[0]
        rows = raw_data[1:]
        
        # Build a list of clean dictionaries
        clean_rows = []
        for r in rows:
            if not r[0]: continue # Skip if no date
            
            # Helper to convert messy strings to numbers
            def to_num(val):
                try: 
                    return float(str(val).replace('%','').replace(',',''))
                except: return 0.0

            row_data = {
                "Date": pd.to_datetime(r[0], format='%d/%m/%Y'),
                "Cal": to_num(r[1]),
                "Weight": to_num(r[3]),
                "Steps": to_num(r[12]),
                "Prot": to_num(r[16]),
                "Carb": to_num(r[17]),
                "Fat": to_num(r[18]),
                "Alc": to_num(r[19])
            }
            # Only keep completed days
            if row_data["Steps"] > 0:
                clean_rows.append(row_data)
        
        return pd.DataFrame(clean_rows)
    except Exception as e:
        st.error(f"Error loading: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🛡️ Hardy House Command")
    
    # Simple Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Calories", f"{df['Cal'].mean():.0f}", f"{df['Cal'].mean() - 1633:.0f}")
    c2.metric("Avg Steps", f"{df['Steps'].mean():,.0f}", f"{df['Steps'].mean() - 10000:.0f}")
    c3.metric("Days on Diet", len(df))
    
    # Rolling Avgs
    r1, r2, r3 = st.columns(3)
    r1.metric("Steps (7d)", f"{df.tail(7)['Steps'].mean():,.0f}")
    r2.metric("Steps (14d)", f"{df.tail(14)['Steps'].mean():,.0f}")
    r3.metric("Steps (30d)", f"{df.tail(30)['Steps'].mean():,.0f}")
    
    st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("Still working out the kinks! Data is loading...")
