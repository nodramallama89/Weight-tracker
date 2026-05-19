import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- CSS: iOS Glassmorphism ---
st.markdown("""
    <style>
    .stApp { background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/254d2662ac5ab10a7396cb5471a719e3d3f25095/cool-background-ppt.jpg'); background-size: cover; background-attachment: fixed; }
    .card { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(15px); border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); border: 1px solid rgba(255, 255, 255, 0.2); text-align: center; color: white; margin-bottom: 10px; }
    .val { font-size: 2rem; font-weight: 800; margin: 5px 0; }
    .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
    h1 { font-size: 3rem !important; color: white !important; text-align: center; margin-bottom: 20px !important; }
    div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { color: white !important; font-size: 1.1rem; font-weight: bold; }
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
    tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Yesterday's Review", "📊 Lifetime Stats", "⚖️ Weight", "📉 Gain/Loss"])
    
    # --- Tab 1: Yesterday's Review ---
    with tab1:
        completed = df[df.iloc[:, 12] != ""] 
        if not completed.empty:
            y = completed.iloc[-1]
            st.title("Yesterday's Review")
            cals, steps = float(str(y.iloc[1]).replace(',','')), float(str(y.iloc[12]).replace(',',''))
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='card'><div class='label'>Calories</div><div class='val'>{cals:.0f}</div><div style='color:{'#ff6b6b' if cals>1633 else '#51cf66'}'>{cals-1633:+.0f} vs 1633</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='card'><div class='label'>Steps</div><div class='val'>{steps:,.0f}</div><div style='color:{'#51cf66' if steps>=10000 else '#ff6b6b'}'>{steps-10000:+.0f} vs 10k</div></div>", unsafe_allow_html=True)
            
            m = st.columns(4)
            labels = ["Prot", "Carb", "Fat", "Alc"]
            for i, idx in enumerate([16, 17, 18, 19]):
                m[i].markdown(f"<div class='card'><div class='label'>{labels[i]}</div><div class='val' style='font-size:1.5rem;'>{str(y.iloc[idx]).replace('%','')}%</div></div>", unsafe_allow_html=True)

    # --- Tab 2: Lifetime Stats ---
    with tab2:
        l = df.iloc[-1]
        st.title("Lifetime Stats")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='card'><div class='label'>Total Loss (lbs)</div><div class='val'>{l.iloc[6]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Total Loss (St)</div><div class='val'>{l.iloc[7]}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><div class='label'>To Target (lbs)</div><div class='val'>{l.iloc[8]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target (St)</div><div class='val'>{l.iloc[9]}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='card'><div class='label'>BMI</div><div class='val'>{l.iloc[10]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Target BMI</div><div class='val'>{l.iloc[11]}</div></div>", unsafe_allow_html=True)

    # --- Tab 3: Weight Graph ---
    with tab3:
        st.title("Weight Progress")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=pd.to_numeric(df.iloc[:, 3], errors='coerce'), mode='lines+markers', line=dict(color='#ffffff', width=4)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                          xaxis=dict(gridcolor='rgba(255,255,255,0.2)', tickfont=dict(size=14)), 
                          yaxis=dict(gridcolor='rgba(255,255,255,0.2)', tickfont=dict(size=14)),
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # --- Tab 4: Gain/Loss Graph ---
    with tab4:
        st.title("Gain/Loss Trend")
        # Column F is index 5
        dates = df.iloc[:, 0]
        gain_loss = pd.to_numeric(df.iloc[:, 5], errors='coerce')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=gain_loss, mode='lines+markers', line=dict(color='#ff9f43', width=4)))
        fig.add_hline(y=0, line_dash="dash", line_color="white") # Zero reference line
        
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                          xaxis=dict(gridcolor='rgba(255,255,255,0.2)', tickfont=dict(size=14)), 
                          yaxis=dict(gridcolor='rgba(255,255,255,0.2)', tickfont=dict(size=14)),
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Could not load data.")
