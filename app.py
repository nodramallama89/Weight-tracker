import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- CSS: Scaled Up Glassmorphism ---
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
    def get_num(idx):
        return pd.to_numeric(df.iloc[:, idx].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🛡️ Review", "📊 Life", "🔥 Calories", "⚖️ Weight", "📉 Gain/Loss", "👟 Steps", "🥗 Macros", "📈 Averages"])
    
    # --- Tab 1: Review ---
    with tab1:
        completed = df[df.iloc[:, 12] != ""] 
        if not completed.empty:
            y = completed.iloc[-1]
            st.title("Yesterday's Review")
            cals, steps = float(str(y.iloc[1]).replace(',','')), float(str(y.iloc[12]).replace(',',''))
            c1, c2 = st.columns(2)
            with c1: st.markdown(f"<div class='card'><div class='label'>Calories</div><div class='val'>{cals:.0f}</div><div style='color:{'#ff6b6b' if cals>1633 else '#51cf66'}'>{cals-1633:+.0f} vs 1633</div></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><div class='label'>Steps</div><div class='val'>{steps:,.0f}</div><div style='color:{'#51cf66' if steps>=10000 else '#ff6b6b'}'>{steps-10000:+.0f} vs 10k</div></div>", unsafe_allow_html=True)

    # --- Tab 2: Life (Restructured Grid) ---
    with tab2:
        l = df.iloc[-1]
        st.title("Lifetime Stats")
        # Days on Diet Top Card
        st.markdown(f"<div class='card'><div class='label'>Days on Diet</div><div class='val'>{len(df)}</div></div>", unsafe_allow_html=True)
        # 3x2 Grid
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

    # --- Tab 8: Averages (New 3x2 Grid) ---
    with tab8:
        st.title("Historical Averages")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='card'><div class='label'>Avg Cals/Day</div><div class='val'>{get_num(1).mean():.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Avg Protein</div><div class='val'>{get_num(16).mean():.0f}%</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><div class='label'>Avg Steps/Day</div><div class='val'>{get_num(12).mean():,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Avg Carbs</div><div class='val'>{get_num(17).mean():.0f}%</div></div>", unsafe_allow_html=True)
        with c3:
            avg_loss = (get_num(3).iloc[0] - get_num(3).iloc[-1]) / (len(df)/7)
            st.markdown(f"<div class='card'><div class='label'>Avg Loss/Week</div><div class='val'>{avg_loss:.2f} lbs</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><div class='label'>Avg Fat</div><div class='val'>{get_num(18).mean():.0f}%</div></div>", unsafe_allow_html=True)

    # --- Tabs 3-7: Graphs (Kept as is) ---
    with tab3:
        st.title("Calories Consumption")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.iloc[:, 0], y=get_num(1), name="Calories", text=get_num(1), texttemplate='%{text:.0f}', textposition='auto', marker_color='#ff9f43'))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(2), name="Net Cal", mode='lines+markers', line=dict(color='#ffffff', width=3)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", legend=dict(font=dict(color='white')), xaxis=dict(gridcolor='rgba(255,255,255,0.2)'), yaxis=dict(gridcolor='rgba(255,255,255,0.2)'))
        st.plotly_chart(fig, use_container_width=True)
    with tab4:
        st.title("Weight Progress")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(3), mode='lines+markers', text=get_num(3), texttemplate='%{text:.1f}', textposition='top center', line=dict(color='#ffffff', width=4)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis=dict(gridcolor='rgba(255,255,255,0.2)'), yaxis=dict(gridcolor='rgba(255,255,255,0.2)'))
        st.plotly_chart(fig, use_container_width=True)
    with tab5:
        st.title("Gain/Loss Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(5), mode='lines+markers', text=get_num(5), texttemplate='%{text:.1f}', textposition='top center', line=dict(color='#ff9f43', width=4)))
        fig.add_hline(y=0, line_dash="dash", line_color="white")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis=dict(gridcolor='rgba(255,255,255,0.2)'), yaxis=dict(gridcolor='rgba(255,255,255,0.2)'))
        st.plotly_chart(fig, use_container_width=True)
    with tab6:
        st.title("Steps Trend")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.iloc[:, 0], y=get_num(12), text=get_num(12), texttemplate='%{text:.0f}', textposition='auto', marker_color='#1dd1a1'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis=dict(gridcolor='rgba(255,255,255,0.2)'), yaxis=dict(gridcolor='rgba(255,255,255,0.2)'))
        st.plotly_chart(fig, use_container_width=True)
    with tab7:
        st.title("Macros Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(16), name="Protein", mode='lines+markers', text=get_num(16), texttemplate='%{text:.0f}', textposition='top center', line=dict(color='#ff6b6b', width=3)))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(17), name="Carbs", mode='lines+markers', text=get_num(17), texttemplate='%{text:.0f}', textposition='top center', line=dict(color='#48dbfb', width=3)))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(18), name="Fat", mode='lines+markers', text=get_num(18), texttemplate='%{text:.0f}', textposition='top center', line=dict(color='#feca57', width=3)))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", legend=dict(font=dict(color='white')), xaxis=dict(gridcolor='rgba(255,255,255,0.2)'), yaxis=dict(gridcolor='rgba(255,255,255,0.2)'))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Could not load data.")
