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
        values = worksheet.get_all_values()
        df = pd.DataFrame(values[1:], columns=values[0])
        
        # --- THE FIX ---
        # 1. Clean: Remove rows with no Date
        df = df[df.iloc[:, 0] != ""]
        # 2. Convert Steps to numeric so we can filter
        df.iloc[:, 12] = pd.to_numeric(df.iloc[:, 12], errors='coerce').fillna(0)
        # 3. Drop rows where Steps are 0 (This removes the "incomplete morning" rows)
        df = df[df.iloc[:, 12] > 0]
        
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- Calculations ---
df = load_data()
if not df.empty:
    df['Date'] = pd.to_datetime(df.iloc[:, 0], format='%d/%m/%Y')
    # Numeric conversion
    cols_to_num = {1: 'Cal', 3: 'Weight', 12: 'Steps', 16: 'Prot', 17: 'Carb', 18: 'Fat', 19: 'Alc'}
    for idx, name in cols_to_num.items():
        df[name] = pd.to_numeric(df.iloc[:, idx].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
    
    df = df.sort_values('Date')
    
    # Now that we filtered out the morning rows, the "last" row is always a full day
    total_days = len(df)
    last_7 = df.tail(7)
    
    # --- UI ---
    st.title("🛡️ Hardy House Command")
    
    # Metrics now use the filtered 'df'
    c1, c2, c3 = st.columns(3)
    c1.metric("7-Day Avg Steps", f"{int(last_7['Steps'].mean()):,}")
    c2.metric("Days on Diet", total_days)
    c3.metric("Last Logged Date", df.iloc[-1]['Date'].strftime('%d/%m/%Y'))

    # Display clean dataframe for verification
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info("Waiting for data... (Ensure you have logged a full day with steps!)")
