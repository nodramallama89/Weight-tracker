import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="centered")

# --- CSS: iOS Glassmorphism ---
st.markdown("""
    <style>
    .stApp { background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/254d2662ac5ab10a7396cb5471a719e3d3f25095/cool-background-ppt.jpg'); background-size: cover; background-attachment: fixed; }
    .card { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); border: 1px solid rgba(255, 255, 255, 0.2); text-align: center; color: white; margin-bottom: 20px; }
    .val { font-size: 2.2rem; font-weight: 800; }
    .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
    h1, h2, h3 { color: white !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:])
        return df
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    tab1, tab2 = st.tabs(["🛡️ Yesterday's Review", "📊 Lifetime Stats"])
    
    # --- Tab 1: Yesterday's Review (Last row with steps) ---
    with tab1:
        completed = df[df[12] != ""] # Column M (12)
        if not completed.empty:
            y = completed.iloc[-1]
            st.title("Yesterday's Review")
            st.markdown(f"### {y[0]}") # Date
            
            cals, steps = float(str(y[1]).replace(',','')), float(str(y[12]).replace(',',''))
            
            # Cards
            st.markdown(f"<div class='card'><div class='label'>Calories</div><div class='val'>{cals:.0f}</div><div style='color:{'#ff6b6b' if cals>1633 else '#51cf66'}'>{cals-1633:+.0f} vs 1633</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Steps</div><div class='val'>{steps:,.0f}</div><div style='color:{'#51cf66' if steps>=10000 else '#ff6b6b'}'>{steps-10000:+.0f} vs 10k</div></div>", unsafe_allow_html=True)
            
            # Macros
            m = st.columns(4)
            labels = ["Prot", "Carb", "Fat", "Alc"]
            for i, idx in enumerate([16, 17, 18, 19]):
                m[i].markdown(f"<div class='card'><div class='label'>{labels[i]}</div><div style='font-size:1.2rem'>{y[idx]}%</div></div>", unsafe_allow_html=True)
        else:
            st.error("No completed days yet.")

    # --- Tab 2: Lifetime Stats (Latest row) ---
    with tab2:
        l = df.iloc[-1] # The absolute latest entry (Morning weight)
        st.title("Lifetime Stats")
        
        # Grid layout for lifetime stats
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='card'><div class='label'>Total Loss</div><div class='val'>{l[6]} lbs</div><div>{l[7]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target</div><div class='val'>{l[8]} lbs</div><div>{l[9]}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><div class='label'>BMI</div><div class='val'>{l[10]}</div><div>Current</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target BMI</div><div class='val'>{l[11]}</div><div>Remaining</div></div>", unsafe_allow_html=True)
else:
    st.error("Could not load data.")
