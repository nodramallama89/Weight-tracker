import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

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
        
        # Get data as a list of lists (the most raw format possible)
        all_data = worksheet.get_all_values()
        
        # Convert to DataFrame, skip first row for headers
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        
        # BRUTE FORCE CLEAN: 
        # Remove empty rows
        df = df[df.iloc[:, 0] != ""]
        
        # Force the 'Steps' column (index 12) to be strictly numeric
        # We use 'coerce' so any garbage data becomes a 0
        df.iloc[:, 12] = pd.to_numeric(df.iloc[:, 12].astype(str).str.replace(',', '').str.replace('.0', ''), errors='coerce').fillna(0)
        
        # Filter for completed days only
        df = df[df.iloc[:, 12] > 0]
        
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- Main App ---
df = load_data()

if not df.empty:
    st.title("🛡️ Hardy House Command")
    
    # Simple Numeric Prep
    df['Steps'] = df.iloc[:, 12].astype(int)
    last_7 = df.tail(7)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("7-Day Avg Steps", f"{int(last_7['Steps'].mean()):,}")
    c2.metric("Days on Diet", len(df))
    c3.metric("Last Logged Date", df.iloc[-1, 0])

    st.dataframe(df.sort_values(by=df.columns[0], ascending=False), use_container_width=True)
else:
    st.info("Waiting for data... Ensure Column M (Steps) is clean numbers.")
