import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="wide")

# --- CSS: Scaled Up Glassmorphism ---
st.markdown("""
    <style>
    .stApp { background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/main/BG.jpg'); background-size: cover; background-attachment: fixed; }
    .card { background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(15px); border-radius: 20px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; color: white; margin-bottom: 10px; }
    .val { font-size: 2rem; font-weight: 800; margin: 5px 0; color: white; }
    .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; color: #cccccc; }
    h1 { font-size: 3rem !important; color: white !important; text-align: center; margin-bottom: 20px !important; }
    .stPlotlyChart { background: rgba(0, 0, 0, 0.4) !important; backdrop-filter: blur(15px) !important; border-radius: 20px !important; padding: 15px !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important; }
    div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { color: white !important; font-size: 1.1rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Helper to force White Theme on all Plotly Charts ---
def apply_theme(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color='white')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(font=dict(color='white')),
        xaxis=dict(color='white', gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
        yaxis=dict(color='white', gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
        yaxis2=dict(color='white', gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white'))
    )
    return fig

@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:])
        df[0] = pd.to_datetime(df[0], dayfirst=True, errors='coerce')
        return df
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    def get_num(idx): return pd.to_numeric(df.iloc[:, idx].astype(str).str.replace('%','').str.replace(',',''), errors='coerce')

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "🛡️ Review", "📊 Life", "🔥 Calories", "⚖️ Weight", "📉 Gain/Loss", 
        "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ BP", "📅 Weekend Warrior", "🎯 Deficit ROI", "📅 Calendar"
    ])
    
    with tab1: # Review
        completed = df[df.iloc[:, 12] != ""] 
        if not completed.empty:
            y = completed.iloc[-1]
            st.title("Yesterday's Review")
            cals, steps = float(str(y.iloc[1]).replace(',','')), float(str(y.iloc[12]).replace(',',''))
            c1, c2 = st.columns(2)
            with c1: st.markdown(f"<div class='card'><div class='label'>Calories</div><div class='val'>{cals:.0f}</div><div style='color:{'#ff6b6b' if cals>1633 else '#51cf66'}'>{cals-1633:+.0f} vs 1633</div></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='card'><div class='label'>Steps</div><div class='val'>{steps:,.0f}</div><div style='color:{'#51cf66' if steps>=10000 else '#ff6b6b'}'>{steps-10000:+.0f} vs 10k</div></div>", unsafe_allow_html=True)
            m = st.columns(4)
            labels = ["Protein", "Carbs", "Fat", "Alcohol"]
            for i, idx in enumerate([16, 17, 18, 19]):
                m[i].markdown(f"<div class='card'><div class='label'>{labels[i]}</div><div class='val' style='font-size:1.5rem;'>{str(y.iloc[idx]).replace('%','')}%</div></div>", unsafe_allow_html=True)

    with tab2: # Life
        l = df.iloc[-1]
        st.title("Lifetime Stats")
        st.markdown(f"<div class='card'><div class='label'>Days on Diet</div><div class='val'>{len(df)}</div></div>", unsafe_allow_html=True)
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

    with tab5: # Gain/Loss & Velocity
        st.title("Gain/Loss & Velocity")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df[0], y=get_num(5), name="Total Trend", line=dict(color='#ff9f43', width=4)), secondary_y=False)
        velocity = get_num(3).diff() * -1
        fig.add_trace(go.Bar(x=df[0], y=velocity, name="Velocity (lbs/day)", marker_color=['#51cf66' if x > 0 else '#ff6b6b' for x in velocity]), secondary_y=True)
        st.plotly_chart(apply_theme(fig, "Progress Trend & Daily Velocity"), use_container_width=True)

    with tab12: # Calendar Heatmap
        st.title("Performance Calendar")
        # FORCE NUMERIC
        df['Heat'] = get_num(5)
        df['Week'] = df[0].dt.isocalendar().week
        df['Day'] = df[0].dt.dayofweek
        heat = df.pivot_table(index='Day', columns='Week', values='Heat', aggfunc='mean')
        fig = go.Figure(data=go.Heatmap(z=heat.values, x=heat.columns, y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], colorscale='RdYlGn', zmid=0))
        st.plotly_chart(apply_theme(fig, "Daily Gain (Red) vs Loss (Green)"), use_container_width=True)

    with tab10: # Weekend
        st.title("Weekday vs. Weekend")
        plot_df = df.copy()
        plot_df['Type'] = plot_df[0].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
        plot_df[1] = pd.to_numeric(plot_df[1].astype(str).str.replace(',', ''), errors='coerce')
        plot_df[12] = pd.to_numeric(plot_df[12].astype(str).str.replace(',', ''), errors='coerce')
        summary = plot_df.groupby('Type')[[1, 12]].mean()
        c1, c2 = st.columns(2)
        for i, col in enumerate([1, 12]):
            fig = go.Figure([go.Bar(x=summary.index, y=summary[col], marker_color=['#ff6b6b', '#1dd1a1'])])
            (c1 if i==0 else c2).plotly_chart(apply_theme(fig, "Avg Calories" if i==0 else "Avg Steps"), use_container_width=True)

    with tab11: # ROI
        st.title("Deficit ROI")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=get_num(2), y=get_num(5), mode='markers', marker=dict(color='#feca57', size=12)))
        fig.add_hline(y=0, line_dash="dash", line_color="white")
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(apply_theme(fig, "Net Calories vs. Weight Change"), use_container_width=True)

    with tab3: # Calories
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.iloc[:, 0], y=get_num(1), name="Calories", text=get_num(1), texttemplate='%{text:.0f}', textposition='auto', marker_color='#ff9f43'))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(2), name="Net Cal", mode='lines+markers', line=dict(color='#ffffff', width=3)))
        st.plotly_chart(apply_theme(fig, "Calories Consumption"), use_container_width=True)

    with tab4: # Weight
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(3), mode='lines+markers', text=get_num(3), texttemplate='%{text:.1f}', textposition='top center', line=dict(color='#ffffff', width=4)))
        st.plotly_chart(apply_theme(fig, "Weight Progress"), use_container_width=True)

    with tab6: # Steps
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=df.iloc[:, 0], y=get_num(12), name="Steps", marker_color='#1dd1a1'), secondary_y=False)
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(15), name="Active Cals", mode='lines+markers', line=dict(color='#feca57', width=3)), secondary_y=True)
        st.plotly_chart(apply_theme(fig, "Steps & Active Burn"), use_container_width=True)

    with tab7: # Macros
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(16), name="Protein", mode='lines+markers', line=dict(color='#ff6b6b', width=3)))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(17), name="Carbs", mode='lines+markers', line=dict(color='#48dbfb', width=3)))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(18), name="Fat", mode='lines+markers', line=dict(color='#feca57', width=3)))
        st.plotly_chart(apply_theme(fig, "Macros Trend"), use_container_width=True)

    with tab8: # Averages
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

    with tab9: # BP
        fig = go.Figure()
        fig.add_hrect(y0=0, y1=80, fillcolor="green", opacity=0.15, line_width=0, layer="below")
        fig.add_hrect(y0=80, y1=120, fillcolor="lightgreen", opacity=0.15, line_width=0, layer="below")
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(21), name="Systolic", mode='lines+markers', connectgaps=True, line=dict(color='#ff7675', width=3)))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(22), name="Diastolic", mode='lines+markers', connectgaps=True, line=dict(color='#74b9ff', width=3)))
        st.plotly_chart(apply_theme(fig, "Blood Pressure"), use_container_width=True)
else:
    st.error("Could not load data.")
