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
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        
        # Get everything as raw data (list of lists)
        raw_data = worksheet.get_all_values()
        
        # Create a clean DataFrame
        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        
        # Manually extract the Step column (index 12)
        # This bypasses all the type errors by grabbing the raw strings
        steps_raw = df.iloc[:, 12].tolist()
        
        # Convert to a clean list of floats, ignoring empty strings or errors
        clean_steps = []
        for x in steps_raw:
            try:
                # Remove commas, strip spaces, convert
                val = float(str(x).replace(',', '').strip())
                clean_steps.append(val)
            except:
                clean_steps.append(0.0)
        
        # Add back as a proper numeric column
        df['Steps_Clean'] = clean_steps
        
        # Filter for rows where steps > 0 (The "Completed Day" filter)
        df = df[df['Steps_Clean'] > 0]
        
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

# --- Main Logic ---
df = load_data()

if not df.empty:
    st.title("🛡️ Hardy House Command")
    
    # 7-Day Average Calculation
    # We take the tail(7) of the filtered, cleaned dataframe
    last_7_avg = df['Steps_Clean'].tail(7).mean()
    
    c1, c2 = st.columns(2)
    c1.metric("7-Day Avg Steps (True)", f"{int(last_7_avg):,}")
    c2.metric("Total Completed Days", len(df))
    
    st.dataframe(df.sort_values(by=df.columns[0], ascending=False), use_container_width=True)
else:
    st.warning("No data found or all steps are 0.")
