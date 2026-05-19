import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="centered")

# --- CSS: iOS Glassmorphism ---
st.markdown("""
    <style>
    .stApp { background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/254d2662ac5ab10a7396cb5471a719e3d3f25095/cool-background-ppt.jpg'); background-size: cover; background-attachment: fixed; }
    .card { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); border-radius: 20px; padding: 20px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); border: 1px solid rgba(255, 255, 255, 0.2); text-align: center; color: white; margin-bottom: 10px; }
    .val { font-size: 1.8rem; font-weight: 800; margin: 5px 0; }
    .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
    h1, h2, h3 { color: white !important; text-align: center; }
    div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { color: white !important; font-weight: bold; }
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
    tab1, tab2, tab3 = st.tabs(["🛡️ Yesterday's Review", "📊 Lifetime Stats", "⚖️ Weight"])
    
    # Helper to clean/convert
    def to_n(val):
        try: return float(str(val).replace('%','').replace(',',''))
        except: return 0.0

    # --- Tab 1: Yesterday's Review (Column M/Index 12) ---
    with tab1:
        completed = df[df.iloc[:, 12] != ""]
        if not completed.empty:
            y = completed.iloc[-1]
            st.title("Yesterday's Review")
            cals, steps = to_n(y.iloc[1]), to_n(y.iloc[12])
            
            # Cal + Step Cards
            st.markdown(f"<div class='card'><div class='label'>Calories</div><div class='val'>{cals:.0f}</div><div style='color:{'#ff6b6b' if cals>1633 else '#51cf66'}'>{cals-1633:+.0f} vs 1633</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Steps</div><div class='val'>{steps:,.0f}</div><div style='color:{'#51cf66' if steps>=10000 else '#ff6b6b'}'>{steps-10000:+.0f} vs 10k</div></div>", unsafe_allow_html=True)
            
            # Macro Row
            m = st.columns(4)
            labels = ["Prot", "Carb", "Fat", "Alc"]
            for i, idx in enumerate([16, 17, 18, 19]):
                m[i].markdown(f"<div class='card'><div class='label'>{labels[i]}</div><div style='font-size:1.1rem; font-weight:bold;'>{y.iloc[idx]}%</div></div>", unsafe_allow_html=True)

    # --- Tab 2: Lifetime Stats (Latest Row) ---
    with tab2:
        l = df.iloc[-1]
        st.title("Lifetime Stats")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='card'><div class='label'>Total Loss (lbs)</div><div class='val'>{l.iloc[6]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target (lbs)</div><div class='val'>{l.iloc[8]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>BMI</div><div class='val'>{l.iloc[10]}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><div class='label'>Total Loss (St)</div><div class='val'>{l.iloc[7]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target (St)</div><div class='val'>{l.iloc[9]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Target BMI</div><div class='val'>{l.iloc[11]}</div></div>", unsafe_allow_html=True)

    # --- Tab 3: Weight Graph ---
    with tab3:
        st.title("Weight Progress")
        # Indices: 0=Date, 3=Weight
        dates = df.iloc[:, 0]
        weights = pd.to_numeric(df.iloc[:, 3], errors='coerce')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=weights, mode='lines+markers', line=dict(color='#ffffff', width=3)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                          xaxis=dict(gridcolor='rgba(255,255,255,0.2)'), yaxis=dict(gridcolor='rgba(255,255,255,0.2)'))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Could not load data.")
