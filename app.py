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
        # Define headers based on your list
        headers = ["Date", "Cal", "Net_Cal", "Weight", "Weight_ST", "Gain_Loss", "Total_Loss", "Total_Loss_ST", 
                   "To_Target", "To_Target_ST", "BMI", "To_Target_BMI", "Steps", "Miles", "Active_Cal", 
                   "Prot", "Carb", "Fat", "Alc", "Notes", "BP_Sys", "BP_Dia"]
        df = pd.DataFrame(data[1:], columns=headers)
        
        # Clean columns to numeric
        for col in ['Cal', 'Steps', 'Prot', 'Carb', 'Fat', 'Alc']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Filter for completed rows: Steps (Column M) must have data
    completed_rows = df[df['Steps'].notna()]
    
    if not completed_rows.empty:
        yesterday = completed_rows.iloc[-1]
        
        st.title("🛡️ Yesterday's Review")
        st.subheader(f"Date: {yesterday['Date']}")
        
        # 1. Calories (Column B)
        cal_diff = yesterday['Cal'] - 1633
        st.metric("Calories Consumed", f"{yesterday['Cal']:.0f}", f"{cal_diff:+.0f} vs 1633")
        
        # 2. Steps (Column M)
        step_diff = yesterday['Steps'] - 10000
        st.metric("Steps", f"{yesterday['Steps']:,.0f}", f"{step_diff:+.0f} vs 10k")
        
        # 3. Macros (Columns Q, R, S, T)
        cols = st.columns(4)
        cols[0].metric("Prot", f"{yesterday['Prot']:.0f}%")
        cols[1].metric("Carbs", f"{yesterday['Carb']:.0f}%")
        cols[2].metric("Fat", f"{yesterday['Fat']:.0f}%")
        cols[3].metric("Alc", f"{yesterday['Alc']:.0f} kcal")
    else:
        st.error("No completed rows found.")
else:
    st.error("Could not load data.")
