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
        
        # 1. Ensure Date is clean
        df = df[df.iloc[:, 0] != ""]
        
        # 2. Convert Steps (Col M, index 12) to numeric safely
        df.iloc[:, 12] = pd.to_numeric(df.iloc[:, 12], errors='coerce').fillna(0)
        
        # 3. Filter: Only keep rows where Steps > 0
        df = df[df.iloc[:, 12] > 0]
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# --- Load & Prep ---
df = load_data()

if not df.empty:
    # Convert all relevant columns to numeric
    # B:1, D:3, M:12, P:15, Q:16, R:17, S:18, T:19, V:21, W:22
    numeric_indices = [1, 3, 12, 15, 16, 17, 18, 19, 21, 22]
    for idx in numeric_indices:
        df.iloc[:, idx] = pd.to_numeric(df.iloc[:, idx].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
    
    df['Date'] = pd.to_datetime(df.iloc[:, 0], format='%d/%m/%Y')
    df = df.sort_values('Date')
    
    # --- Metrics ---
    total_days = len(df)
    last_7 = df.tail(7)
    
    st.title("🛡️ Hardy House Command")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("7-Day Avg Steps", f"{int(last_7.iloc[:, 12].mean()):,}")
    c2.metric("Days on Diet", total_days)
    c3.metric("Last Logged Date", df.iloc[-1, 0])

    st.subheader("Data Preview")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info("Waiting for data... Please ensure your 'Main sheet' is populated and the Steps column has values for completed days.")
