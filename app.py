import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# App config
st.set_page_config(page_title="Hardy House Fitness Dashboard", layout="wide")

# --- Google Sheets Authentication ---
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
        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

# --- Dashboard UI ---
st.title("📈 Hardy House Fitness Dashboard")
st.caption("Auto-refreshing view from Google Sheets")

df = load_data()

if not df.empty:
    # 1. Convert Date
    df['Date'] = pd.to_datetime(df.iloc[:, 0], format='%d/%m/%Y', errors='coerce')
    
    # 2. Convert numeric columns carefully
    # We create a copy to avoid the TypeError
    for col_idx in [1, 3, 12, 16, 17, 18]: # Calories(B), Weight(D), Steps(M), Protein(Q), Carbs(R), Fat(S)
        col_name = df.columns[col_idx]
        df[col_name] = pd.to_numeric(df[col_name].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
    
    df = df.dropna(subset=['Date']).sort_values(by="Date")
    latest = df.iloc[-1]

    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Weight", f"{int(latest.iloc[3])} lbs")
    c2.metric("Calories", f"{int(latest.iloc[1])} kcal")
    c3.metric("Steps", f"{int(latest.iloc[12]):,}")
    c4.metric("Protein %", f"{int(latest.iloc[16])}%")

    st.markdown("---")
    
    # Graphs
    tab1, tab2 = st.tabs(["Weight & Progress", "Activity & Macros"])
    
    with tab1:
        st.subheader("Weight Trend")
        st.line_chart(data=df.set_index('Date').iloc[:, 3])
        st.subheader("Total Loss (lbs)")
        st.bar_chart(data=df.set_index('Date').iloc[:, 6])
        
    with tab2:
        st.subheader("Step Count")
        st.area_chart(data=df.set_index('Date').iloc[:, 12])
        st.subheader("Macro Split (P/C/F %)")
        st.line_chart(data=df.set_index('Date').iloc[:, 16:19])

    st.markdown("---")
    st.subheader("Detailed Logs")
    # Show clean dataframe
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

else:
    st.warning("No data found. Check your sheet connection.")
