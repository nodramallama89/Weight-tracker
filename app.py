import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Yesterday's Review", layout="centered")

# --- Glassmorphism Style ---
st.markdown("""
    <style>
    .card { background: white; border-radius: 20px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; }
    .val { font-size: 2.5rem; font-weight: 800; color: #1c1c1e; }
    .label { font-size: 0.9rem; color: #8e8e93; text-transform: uppercase; font-weight: 600; }
    .delta { font-size: 1rem; font-weight: 700; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        # Force numeric, convert errors to NaN, then drop incomplete rows
        for col in ['Cal', 'Steps', 'Prot', 'Carb', 'Fat', 'Alc']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')
        # Only keep full rows where steps are recorded
        return df.dropna(subset=['Steps', 'Cal'])
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    # Get the very last row
    yesterday = df.iloc[-1]
    
    st.title("🛡️ Yesterday's Review")
    
    # 1. Calories
    cal_diff = yesterday['Cal'] - 1633
    cal_color = "green" if cal_diff <= 0 else "red"
    cal_arrow = "↓" if cal_diff <= 0 else "↑"
    
    st.markdown(f"""
        <div class='card'>
            <div class='label'>Calories Consumed</div>
            <div class='val'>{yesterday['Cal']:.0f}</div>
            <div class='delta' style='color:{cal_color}'>{cal_arrow} {abs(cal_diff):.0f} vs 1633</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # 2. Steps
    step_diff = yesterday['Steps'] - 10000
    step_color = "green" if step_diff >= 0 else "red"
    step_arrow = "↑" if step_diff >= 0 else "↓"
    
    st.markdown(f"""
        <div class='card'>
            <div class='label'>Steps</div>
            <div class='val'>{yesterday['Steps']:,.0f}</div>
            <div class='delta' style='color:{step_color}'>{step_arrow} {abs(step_diff):,.0f} vs 10,000</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # 3. Macros
    cols = st.columns(4)
    cols[0].metric("Protein", f"{yesterday['Prot']:.0f}%")
    cols[1].metric("Carbs", f"{yesterday['Carb']:.0f}%")
    cols[2].metric("Fat", f"{yesterday['Fat']:.0f}%")
    cols[3].metric("Alcohol", f"{yesterday['Alc']:.0f}%")
    
else:
    st.error("No full data rows found.")
