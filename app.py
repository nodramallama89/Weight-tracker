import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Yesterday's Review", layout="centered")

# --- CSS: iOS Glassmorphism + Background ---
st.markdown("""
    <style>
    .stApp {
        background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/254d2662ac5ab10a7396cb5471a719e3d3f25095/cool-background-ppt.jpg');
        background-size: cover;
        background-attachment: fixed;
    }
    .card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        margin-bottom: 20px;
        color: white;
    }
    .val { font-size: 3rem; font-weight: 800; }
    .label { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
    .delta { font-size: 1.1rem; font-weight: 600; margin-top: 5px; }
    h1, h2 { color: white !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        return pd.DataFrame(data[1:])
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    # Column Index Mapping: 12 is Steps (M), 1 is Calories (B)
    completed_rows = df[df[12] != ""]
    
    if not completed_rows.empty:
        yesterday = completed_rows.iloc[-1]
        
        def to_n(val):
            try: return float(str(val).replace('%','').replace(',',''))
            except: return 0.0

        cals = to_n(yesterday[1])
        steps = to_n(yesterday[12])
        
        st.title("🛡️ Yesterday's Review")
        
        # 1. Calories
        cal_diff = cals - 1633
        st.markdown(f"""
            <div class='card'>
                <div class='label'>Calories Consumed</div>
                <div class='val'>{cals:.0f}</div>
                <div class='delta' style='color: {'#ff6b6b' if cal_diff > 0 else '#51cf66'}'>
                    {'+' if cal_diff > 0 else ''}{cal_diff:.0f} vs 1633
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. Steps
        step_diff = steps - 10000
        st.markdown(f"""
            <div class='card'>
                <div class='label'>Steps</div>
                <div class='val'>{steps:,.0f}</div>
                <div class='delta' style='color: {'#51cf66' if step_diff >= 0 else '#ff6b6b'}'>
                    {'+' if step_diff >= 0 else ''}{step_diff:,.0f} vs 10k
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 3. Macros
        cols = st.columns(4)
        macro_labels = ["Prot", "Carb", "Fat", "Alc"]
        macro_indices = [16, 17, 18, 19]
        
        for i, col in enumerate(cols):
            val = to_n(yesterday[macro_indices[i]])
            col.markdown(f"""
                <div class='card'>
                    <div class='label'>{macro_labels[i]}</div>
                    <div class='val' style='font-size: 1.5rem'>{val:.0f}{'%' if i<3 else ''}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("No completed rows found.")
else:
    st.error("Could not load data.")
