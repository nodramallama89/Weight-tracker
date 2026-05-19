import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="centered")

# --- CSS: iOS Glassmorphism + Tab Fixes ---
st.markdown("""
    <style>
    .stApp { background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/254d2662ac5ab10a7396cb5471a719e3d3f25095/cool-background-ppt.jpg'); background-size: cover; background-attachment: fixed; }
    .card { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); border-radius: 20px; padding: 25px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); border: 1px solid rgba(255, 255, 255, 0.2); text-align: center; color: white; margin-bottom: 20px; }
    .val { font-size: 2.2rem; font-weight: 800; }
    .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
    h1, h2, h3 { color: white !important; text-align: center; }
    /* Force tab text to be white */
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
        # Create DF from all data, index 0 is header
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    tab1, tab2, tab3 = st.tabs(["🛡️ Yesterday's Review", "📊 Lifetime Stats", "⚖️ Weight"])
    
    # --- Tab 1: Yesterday's Review ---
    with tab1:
        completed = df[df.iloc[:, 12] != ""] # Column M (Steps)
        if not completed.empty:
            y = completed.iloc[-1]
            st.title("Yesterday's Review")
            cals, steps = float(str(y[1]).replace(',','')), float(str(y[12]).replace(',',''))
            
            st.markdown(f"<div class='card'><div class='label'>Calories</div><div class='val'>{cals:.0f}</div><div style='color:{'#ff6b6b' if cals>1633 else '#51cf66'}'>{cals-1633:+.0f} vs 1633</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Steps</div><div class='val'>{steps:,.0f}</div><div style='color:{'#51cf66' if steps>=10000 else '#ff6b6b'}'>{steps-10000:+.0f} vs 10k</div></div>", unsafe_allow_html=True)
        
    # --- Tab 2: Lifetime Stats ---
    with tab2:
        l = df.iloc[-1]
        st.title("Lifetime Stats")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='card'><div class='label'>Total Loss (lbs)</div><div class='val'>{l[6]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target (lbs)</div><div class='val'>{l[8]}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><div class='label'>Total Loss (St)</div><div class='val'>{l[7]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>To Target (St)</div><div class='val'>{l[9]}</div></div>", unsafe_allow_html=True)

    # --- Tab 3: Weight Graph ---
    with tab3:
        st.title("Weight Progress")
        # Prepare Data
        chart_df = df[[df.columns[0], df.columns[3]]].copy() # Date(0) and Weight(3)
        chart_df.columns = ['Date', 'Weight']
        chart_df['Weight'] = pd.to_numeric(chart_df['Weight'], errors='coerce')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=chart_df['Date'], y=chart_df['Weight'], mode='lines+markers', line=dict(color='#ffffff', width=3)))
        
        # Make transparent
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Could not load data.")
