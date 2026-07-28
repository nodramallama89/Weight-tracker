import streamlit as st
import pandas as pd
import numpy as np
import gspread
import plotly.graph_objects as go
import plotly.express as px
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import time
import re

# ─────────────────────────────────────────────
#  PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Hardy House Health — VisionOS Showcase",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Boot Sequence Notification ──
if 'booted' not in st.session_state:
    st.toast('VisionOS Health Telemetry Active.', icon='⚡')
    time.sleep(0.4)
    st.toast('Concentric Rings & Metabolic Engine Online.', icon='💚')
    st.session_state.booted = True

# ─────────────────────────────────────────────
#  VISIONOS DARK GLASSMORPHISM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --bg-app:          #0B0C12;
  --bg-card:         rgba(20, 23, 36, 0.76);
  --bg-card-hover:   rgba(28, 32, 50, 0.90);
  --glass-border:    rgba(255, 255, 255, 0.12);
  --glass-blur:      blur(40px) saturate(220%);
  --glass-blur-sm:   blur(20px) saturate(180%);

  --shadow-card:       0 8px 32px rgba(0, 0, 0, 0.35), 0 2px 8px rgba(0, 0, 0, 0.20);
  --shadow-card-hover: 0 16px 48px rgba(10, 132, 255, 0.22), 0 4px 16px rgba(0, 0, 0, 0.40);

  --text-primary:   #FFFFFF;
  --text-secondary: rgba(235, 235, 245, 0.75);
  --text-tertiary:  rgba(235, 235, 245, 0.45);

  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  --font-body:    'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;

  /* Neon Accents */
  --red:    #FF2D55;
  --amber:  #FF9F0A;
  --green:  #30D158;
  --teal:   #64D2FF;
  --blue:   #0A84FF;
  --purple: #BF5AF2;

  --radius-xl: 24px;
  --radius-lg: 18px;
  --radius-md: 12px;
}

*, *::before, *::after { box-sizing: border-box; }

.stApp {
  background-color: var(--bg-app);
  background-image:
    radial-gradient(at 15% 15%, rgba(10, 132, 255, 0.18) 0px, transparent 55%),
    radial-gradient(at 85% 20%, rgba(255, 45, 85, 0.15) 0px, transparent 55%),
    radial-gradient(at 50% 80%, rgba(48, 209, 88, 0.12) 0px, transparent 55%),
    linear-gradient(180deg, #0B0C12 0%, #12141F 100%);
  background-size: cover;
  background-attachment: fixed;
  font-family: var(--font-body);
  color: var(--text-primary);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.2rem 2rem 3rem; max-width: 1720px; }

/* ── Typography ── */
.page-eyebrow {
  font-size: 0.78rem; font-weight: 800; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--blue); text-align: center;
  display: block; margin-bottom: 0.2rem; animation: fadeUp 0.5s ease both;
}
.page-eyebrow .status-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background-color: var(--green); margin-right: 7px;
  box-shadow: 0 0 12px rgba(48,209,88,0.8);
}

.page-title {
  font-family: var(--font-display) !important; font-size: 3.1rem !important;
  font-weight: 900 !important; letter-spacing: -0.035em !important;
  color: #FFFFFF !important; text-align: center !important;
  margin: 0 0 0.15rem !important; animation: fadeUp 0.6s ease 0.05s both;
  text-shadow: 0 0 30px rgba(255,255,255,0.25);
}

.page-subtitle {
  font-size: 0.98rem; color: var(--text-secondary); text-align: center;
  margin-bottom: 1.8rem; font-weight: 500; animation: fadeUp 0.7s ease 0.1s both;
}

/* ── VisionOS Glass Cards ── */
.card {
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl); padding: 22px 20px 20px;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.15);
  border: 1px solid var(--glass-border); text-align: center; margin-bottom: 14px;
  position: relative; overflow: hidden;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  animation: springUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.card:hover {
  transform: translateY(-6px) scale(1.008);
  box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,0.25);
  border-color: rgba(255,255,255,0.28); background: var(--bg-card-hover);
}

.val { font-family: var(--font-display); font-size: 2.4rem; font-weight: 800; margin: 4px 0; line-height: 1; color: #FFFFFF; letter-spacing: -0.025em; text-shadow: 0 2px 12px rgba(0,0,0,0.5); }
.val-sm { font-family: var(--font-display); font-size: 1.65rem; font-weight: 800; margin: 4px 0; line-height: 1; color: #FFFFFF; letter-spacing: -0.015em; }
.label { font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.11em; color: var(--text-tertiary); }

.delta { font-size: 0.78rem; font-weight: 700; margin-top: 10px; padding: 5px 13px; border-radius: 50px; display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.delta-pos { background: rgba(48, 209, 88, 0.22); color: #30D158; border: 1px solid rgba(48, 209, 88, 0.4); }
.delta-neg { background: rgba(255, 45, 85, 0.20); color: #FF2D55; border: 1px solid rgba(255, 45, 85, 0.38); }

/* ── Context Explainer Cards ── */
.context-card {
  background: rgba(22, 26, 42, 0.80);
  backdrop-filter: var(--glass-blur-sm); -webkit-backdrop-filter: var(--glass-blur-sm);
  border-radius: var(--radius-lg); padding: 22px 26px;
  border: 1px solid var(--glass-border); box-shadow: var(--shadow-card);
  margin-bottom: 20px; text-align: left;
}
.context-title {
  font-family: var(--font-display); font-size: 0.85rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--teal); margin-bottom: 8px;
}
.context-text {
  font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6; font-weight: 400;
}

/* ── Top Insights Box ── */
.insights-card {
  background: rgba(22, 26, 42, 0.85);
  backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl); padding: 22px 28px;
  border: 1px solid var(--glass-border); box-shadow: var(--shadow-card);
  margin-bottom: 20px; text-align: left;
}
.insights-title {
  font-family: var(--font-display); font-size: 0.82rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.12em; color: var(--blue); margin-bottom: 12px;
}
.insight-item {
  font-size: 0.95rem; color: var(--text-primary); font-weight: 400;
  margin-bottom: 8px; line-height: 1.5; display: flex; align-items: flex-start; gap: 8px;
}

/* ── RAG Badges ── */
.rag-badge {
  display: inline-block; font-size: 0.72rem; font-weight: 800; text-transform: uppercase;
  padding: 4px 10px; border-radius: 20px; margin-top: 6px; letter-spacing: 0.06em;
}
.rag-green { background: rgba(48, 209, 88, 0.22); color: #30D158; border: 1px solid rgba(48, 209, 88, 0.4); }
.rag-amber { background: rgba(255, 159, 10, 0.22); color: #FF9F0A; border: 1px solid rgba(255, 159, 10, 0.4); }
.rag-red   { background: rgba(255, 45, 85, 0.20); color: #FF2D55; border: 1px solid rgba(255, 45, 85, 0.4); }

/* ── Status Modifiers ── */
.debuff-container { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 8px; }
.debuff-badge {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
  border-radius: 20px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em;
  backdrop-filter: var(--glass-blur-sm); box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.debuff-warning { background: rgba(255, 45, 85, 0.22); color: #FF2D55; border: 1px solid rgba(255, 45, 85, 0.4); }
.debuff-caution { background: rgba(255, 159, 10, 0.22); color: #FF9F0A; border: 1px solid rgba(255, 159, 10, 0.4); }
.debuff-optimal { background: rgba(48, 209, 88, 0.22); color: #30D158; border: 1px solid rgba(48, 209, 88, 0.4); }

.section-header { font-family: var(--font-display); font-size: 1.7rem; font-weight: 800; color: #FFFFFF; margin: 0 0 0.3rem; text-align: center; letter-spacing: -0.01em; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
.section-sub { font-size: 0.8rem; color: var(--text-tertiary); text-align: center; margin-top: 0; margin-bottom: 1.6rem; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 700; }

/* ── VisionOS Segmented Control Tabs ── */
div[data-baseweb="tab-list"] {
  background: rgba(20, 24, 38, 0.75) !important; backdrop-filter: var(--glass-blur-sm) !important;
  -webkit-backdrop-filter: var(--glass-blur-sm) !important; border-radius: 20px !important;
  padding: 6px !important; border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card) !important; margin-bottom: 1.8rem !important; flex-wrap: wrap !important; gap: 2px;
}
div[data-baseweb="tab"] { border-radius: 14px !important; transition: all 0.25s ease !important; }
div[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.08) !important; }
div[data-baseweb="tab"][aria-selected="true"] { background: rgba(255,255,255,0.18) !important; box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important; border: 1px solid rgba(255,255,255,0.15) !important; }
div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { color: var(--text-secondary) !important; font-size: 0.88rem !important; font-weight: 600 !important; }
div[data-baseweb="tab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; font-weight: 800 !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }

/* ── Plotly Containers ── */
.stPlotlyChart {
  background: var(--bg-card) !important; backdrop-filter: var(--glass-blur) !important;
  -webkit-backdrop-filter: var(--glass-blur) !important; border-radius: var(--radius-xl) !important;
  padding: 16px !important; border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.12) !important;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stPlotlyChart:hover { box-shadow: var(--shadow-card-hover) !important; }

@keyframes springUpFade { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
@keyframes fadeUp { 0% { opacity: 0; transform: translateY(10px); } 100% { opacity: 1; transform: translateY(0); } }

[data-testid="stDataFrame"] {
  background: var(--bg-card); backdrop-filter: var(--glass-blur-sm);
  border-radius: var(--radius-lg); border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card); padding: 8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME & DIAL GAUGES
# ─────────────────────────────────────────────
def apply_theme(fig, title="", subtitle=""):
    full_title = f"<b>{title}</b>" + (f"<br><span style='font-size:12px;color:rgba(235,235,245,0.55);font-family:Inter'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(family="Inter, sans-serif", color='#FFFFFF', size=19), x=0.03, xanchor='left', y=0.96),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='rgba(235,235,245,0.75)', size=12),
        legend=dict(font=dict(color='#FFFFFF', size=11), bgcolor='rgba(20,24,38,0.85)', bordercolor='rgba(255,255,255,0.12)', borderwidth=1, x=0.01, y=0.99, orientation='h'),
        xaxis=dict(
            color='rgba(235,235,245,0.55)', gridcolor='rgba(255,255,255,0.06)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.6)",
            showgrid=True, zeroline=False
        ),
        yaxis=dict(
            color='rgba(235,235,245,0.55)', gridcolor='rgba(255,255,255,0.06)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.6)",
            zeroline=False
        ),
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(20,24,38,0.95)', bordercolor='#0A84FF', font=dict(color='#FFFFFF', size=13, family='Inter, sans-serif')),
    )
    return fig

def make_semi_gauge(val, title, min_v, max_v, green_range, amber_range, red_range, unit=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={'suffix': f" {unit}", 'font': {'size': 26, 'color': '#FFFFFF', 'family': 'Inter'}},
        title={'text': title, 'font': {'size': 14, 'color': 'rgba(235,235,245,0.7)', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
            'bar': {'color': "#FFFFFF", 'thickness': 0.25},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': green_range, 'color': 'rgba(48,209,88,0.85)'},
                {'range': amber_range, 'color': 'rgba(255,159,10,0.85)'},
                {'range': red_range, 'color': 'rgba(255,45,85,0.85)'}
            ]
        }
    ))
    fig.update_layout(height=210, margin=dict(l=15, r=15, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ─────────────────────────────────────────────
#  100% FUNCTIONAL PLOTLY ACTIVITY RING ENGINE
# ─────────────────────────────────────────────
def build_plotly_activity_rings(cal_pct, step_pct, water_pct, prot_pct):
    """
    Renders an interactive Concentric Ring Chart (Apple Watch style) using Plotly Barpolar.
    Guaranteed to fill and animate on all screens.
    """
    c_pct = max(0.0, min(100.0, float(cal_pct)))
    s_pct = max(0.0, min(100.0, float(step_pct)))
    w_pct = max(0.0, min(100.0, float(water_pct)))
    p_pct = max(0.0, min(100.0, float(prot_pct)))

    vals   = [c_pct, s_pct, w_pct, p_pct]
    labels = ["Calories", "Steps", "Water", "Protein"]
    colors = ["#FF2D55", "#30D158", "#0A84FF", "#BF5AF2"]

    fig = go.Figure()

    # Outer -> Inner Radii
    radii = [100, 78, 56, 34]

    for val, label, color, r in zip(vals, labels, colors, radii):
        # 1. Background Ring Track (100%)
        fig.add_trace(go.Barpolar(
            r=[20], theta=[180], width=[360],
            base=[r - 10],
            marker_color=color, marker_opacity=0.18,
            showlegend=False, hoverinfo='none'
        ))
        # 2. Active Filled Arc
        angle = (val / 100.0) * 360.0
        if angle > 0:
            fig.add_trace(go.Barpolar(
                r=[20], theta=[angle / 2.0], width=[angle],
                base=[r - 10],
                marker_color=color, marker_opacity=0.95,
                name=f"{label}: {val:.0f}%",
                hoverinfo='name'
            ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 110]),
            angularaxis=dict(visible=False, direction='clockwise', rotation=90)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=230,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(
            orientation='h', x=0.02, y=-0.08,
            font=dict(color='#FFFFFF', size=11, family='Inter')
        )
    )
    return fig


# ─────────────────────────────────────────────
#  INLINE MICRO SPARKLINE GENERATOR
# ─────────────────────────────────────────────
def make_sparkline_card(label, current_val, decimals, suffix, data_series, color):
    """Generates an glass card with an embedded 7-day sparkline chart."""
    recent_7 = data_series.tail(7).dropna()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=recent_7.values, mode='lines',
        line=dict(color=color, width=2.5, shape='spline'),
        fill='tozeroy', fillcolor=f"{color}22", hoverinfo='none'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=38,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    
    val_formatted = f"{current_val:,.{decimals}f}" if pd.notna(current_val) else "N/A"
    
    st.markdown(f"""
    <div class='card' style='padding: 16px 14px; text-align: left;'>
        <div class='label'>{label}</div>
        <div class='val-sm' style='margin: 2px 0 6px;'>{val_formatted}<span style='font-size:0.6em; opacity:0.6; margin-left:4px;'>{suffix}</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# ─────────────────────────────────────────────
#  DATA PIPELINE
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        df = pd.DataFrame(data[1:])
        df[0] = pd.to_datetime(df[0], dayfirst=True, errors='coerce')
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    df_valid = df[df.iloc[:, 12].astype(str).str.strip() != ""].reset_index(drop=True)
    if df_valid.empty:
        df_valid = df
else:
    df_valid = df


# ─────────────────────────────────────────────
#  HELPERS & RAG RULES
# ─────────────────────────────────────────────
def get_num(idx, source=None):
    src = df if source is None else source
    if src.empty or idx >= src.shape[1]:
        return pd.Series([0.0] * len(src))
    return pd.to_numeric(
        src.iloc[:, idx].astype(str).str.replace('%', '').str.replace(',', ''),
        errors='coerce'
    )

def clean_float(val):
    try:
        cleaned = re.sub(r'[^\d\.-]', '', str(val))
        if cleaned in ['', '-', '.']: return 0.0
        return float(cleaned)
    except Exception:
        return 0.0

def safe(x):
    try:
        return float(x) if pd.notna(x) else 0.0
    except (TypeError, ValueError):
        return 0.0

def lbs_to_stone(lbs):
    v = safe(lbs)
    st_val = int(v // 14)
    rem_lbs = v % 14
    return f"{st_val} st {rem_lbs:.1f} lbs"

def fmt_num(value, decimals=0, suffix=''):
    v = safe(value)
    formatted = f"{v:,.{decimals}f}"
    if suffix:
        formatted += f"<span style='font-size:0.65em; opacity:0.55; margin-left:4px;'>" + suffix + "</span>"
    return formatted

def eval_macro_rag(val_pct, macro_type):
    v = safe(val_pct)
    if macro_type == 'protein':
        if v < 60.0:
            return "RED", "#FF2D55", "rag-red", "Under Target (<60%)"
        elif v <= 85.0:
            return "AMBER", "#FF9F0A", "rag-amber", "Moderate (60–85%)"
        else:
            return "GREEN", "#30D158", "rag-green", "Optimal (85%+)"
    else:
        if v < 90.0:
            return "GREEN", "#30D158", "rag-green", "Optimal (<90%)"
        elif v <= 110.0:
            return "AMBER", "#FF9F0A", "rag-amber", "Moderate (90–110%)"
        else:
            return "RED", "#FF2D55", "rag-red", "Excess (>110%)"

def card(label, display_val="", num_target=None, decimals=0, suffix="", delta_val=None, delta_label="", size="normal", invert=False):
    val_class = "val" if size == "normal" else "val-sm"

    if num_target is not None:
        val_class += " count-up"
        val_html = f"<div class='{val_class}' data-target='{safe(num_target)}' data-decimals='{decimals}' data-suffix='{suffix}'>{fmt_num(num_target, decimals, suffix)}</div>"
    else:
        val_html = f"<div class='{val_class}'>{display_val}</div>"

    delta_html = ""
    if delta_val is not None:
        delta_val = safe(delta_val)
        if invert:
            cls   = "delta-neg" if delta_val >= 0 else "delta-pos"
        else:
            cls   = "delta-pos" if delta_val >= 0 else "delta-neg"

        arrow = "▲" if delta_val >= 0 else "▼"
        delta_html = f"<div class='delta {cls}'>{arrow} {abs(delta_val):,.1f} {delta_label}</div>"

    return f"""
    <div class='card'>
      <div class='label'>{label}</div>
      {val_html}
      {delta_html}
    </div>"""


# ─────────────────────────────────────────────
#  STATUS MODIFIERS ENGINE
# ─────────────────────────────────────────────
def evaluate_debuffs(row_data):
    badges = []
    
    alc_kcal = clean_float(row_data.iloc[19]) if len(row_data) > 19 else 0.0
    if alc_kcal > 0:
        badges.append(f"<div class='debuff-badge debuff-warning'>🍷 Alcohol Active (+{alc_kcal:,.0f} kcal) — Sleep & Recovery Suppressed</div>")
    
    cals = clean_float(row_data.iloc[1]) if len(row_data) > 1 else 0.0
    if cals > 1633:
        badges.append(f"<div class='debuff-badge debuff-caution'>🔥 Caloric Surplus (+{cals - 1633:,.0f} kcal over target)</div>")
    elif 0 < cals <= 1633:
        badges.append("<div class='debuff-badge debuff-optimal'>🔥 Caloric Target Hit (≤ 1,633 kcal)</div>")

    steps = clean_float(row_data.iloc[12]) if len(row_data) > 12 else 0.0
    if steps >= 10000:
        badges.append(f"<div class='debuff-badge debuff-optimal'>👟 Kinetic Goal Hit ({steps:,.0f} Steps)</div>")
    elif steps < 8000:
        badges.append(f"<div class='debuff-badge debuff-caution'>👟 Low Activity ({steps:,.0f} Steps)</div>")

    water_ml = clean_float(row_data.iloc[24]) if len(row_data) > 24 else 0.0
    if water_ml >= 5000:
        badges.append(f"<div class='debuff-badge debuff-optimal'>💧 Hydration Target Hit ({water_ml:,.0f} ml)</div>")
    elif 0 < water_ml < 5000:
        badges.append(f"<div class='debuff-badge debuff-caution'>💧 Hydration Under Target ({water_ml:,.0f} / 5,000 ml)</div>")

    rhr = clean_float(row_data.iloc[27]) if len(row_data) > 27 else 0.0
    if rhr > 0 and rhr <= 65:
        badges.append(f"<div class='debuff-badge debuff-optimal'>❤️ Excellent Resting HR ({rhr:,.0f} BPM)</div>")
    elif rhr > 75:
        badges.append(f"<div class='debuff-badge debuff-caution'>❤️ Elevated Resting HR ({rhr:,.0f} BPM)</div>")

    if not badges:
        badges.append("<div class='debuff-badge debuff-optimal'>🛡️ All Telemetry Nominal</div>")

    return f"<div class='debuff-container'>{''.join(badges)}</div>"


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
if not df.empty:

    st.markdown("""
    <span class='page-eyebrow'><span class='status-dot'></span>VISIONOS BIOMETRIC SHOWCASE ENGINE</span>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='page-title'>Hardy House Health</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>World-Class Apple Fitness Biometric Intelligence & Showcase Suite</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17 = st.tabs([
        "🛡️ Command", "🧬 Metabolic", "🫀 Cardio", "📊 Lifetime", "🔥 Calories",
        "💧 Hydration", "⚖️ Weight", "👟 Steps & Elevation", "🥗 Macro RAG", "📅 Patterns",
        "📈 Averages", "🎯 Milestones", "🏆 Trophies", "🧠 Analytics", "🔮 Forecast",
        "⚡ Momentum (30d)", "🗄️ Data Log"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Command Center (With Functional Plotly Rings & Sparklines)
    # ══════════════════════════════════════════
    with tab1:
        completed = df_valid
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "LATEST_DATA"
            cals  = clean_float(y.iloc[1])
            steps = clean_float(y.iloc[12])
            water = clean_float(y.iloc[24])
            prot  = clean_float(y.iloc[16])

            last_14 = completed.tail(14)
            cals_14 = pd.to_numeric(last_14.iloc[:, 1], errors='coerce')
            p_14    = pd.to_numeric(last_14.iloc[:, 16], errors='coerce')
            w_14    = pd.to_numeric(last_14.iloc[:, 24], errors='coerce')

            p_green_cnt = (p_14 >= 85).sum()
            cal_hit_cnt = (cals_14 <= 1633).sum()
            water_hit_cnt = (w_14 >= 5000).sum()

            cal_pct_14   = (cal_hit_cnt / 14.0) * 100.0
            p_pct_14     = (p_green_cnt / 14.0) * 100.0
            water_pct_14 = (water_hit_cnt / 14.0) * 100.0
            step_pct_y   = (steps / 10000.0) * 100.0
            cal_pct_y    = ((1633.0 / cals) * 100.0) if cals > 0 else 0.0
            water_pct_y  = (water / 5000.0) * 100.0

            # Row 1: Interactive Apple Activity Ring & Diagnostic Insights
            col_ring, col_insights = st.columns([1, 2])
            with col_ring:
                st.plotly_chart(build_plotly_activity_rings(cal_pct_y, step_pct_y, water_pct_y, prot), use_container_width=True)

            with col_insights:
                st.markdown(f"""
                <div class='insights-card'>
                    <div class='insights-title'>⚡ AUTOMATED BIOMETRIC INSIGHTS ({date_str})</div>
                    <div class='insight-item'>• <b>Caloric Adherence:</b> Reached calorie goal (≤ 1,633 kcal) on <b>{cal_hit_cnt} of the last 14 days</b> (<b>{cal_pct_14:.0f}% compliance</b>).</div>
                    <div class='insight-item'>• <b>Protein RAG Status:</b> Reached <b>GREEN Protein status (≥ 85% Target)</b> on <b>{p_green_cnt} of the last 14 days</b> (<b>{p_pct_14:.0f}% compliance</b>).</div>
                    <div class='insight-item'>• <b>Hydration Performance (5,000 ml Target):</b> Reached target water volume on <b>{water_hit_cnt} of the last 14 days</b> (<b>{water_pct_14:.0f}% compliance</b>).</div>
                </div>
                """, unsafe_allow_html=True)

            # Row 2: Micro-Trend Sparkline Cards
            st.markdown("<div class='section-sub'>7-Day Biometric Micro-Trends</div>", unsafe_allow_html=True)
            sp1, sp2, sp3, sp4 = st.columns(4)
            with sp1:
                make_sparkline_card("Weight Trend", clean_float(y.iloc[3]), 1, "lbs", get_num(3, completed), "#BF5AF2")
            with sp2:
                make_sparkline_card("Calorie Trend", cals, 0, "kcal", get_num(1, completed), "#FF2D55")
            with sp3:
                make_sparkline_card("Step Volume", steps, 0, "steps", get_num(12, completed), "#30D158")
            with sp4:
                make_sparkline_card("Hydration Volume", water, 0, "ml", get_num(24, completed), "#0A84FF")

            st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

            # RAG Macro Grid (% Target)
            m1, m2, m3, m4 = st.columns(4)
            p_rag, p_color, p_badge_cls, p_desc = eval_macro_rag(prot, 'protein')
            m1.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {p_color};'>
                <div class='label'>Protein (% Target)</div>
                <div class='val-sm count-up' data-target='{prot}' data-decimals='1' data-suffix='%'>{fmt_num(prot, 1, '%')}</div>
                <div class='rag-badge {p_badge_cls}'>{p_rag}: {p_desc}</div>
              </div>""", unsafe_allow_html=True)

            carbs_pct = clean_float(y.iloc[17]) if len(y) > 17 else 0.0
            c_rag, c_color, c_badge_cls, c_desc = eval_macro_rag(carbs_pct, 'carbs')
            m2.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {c_color};'>
                <div class='label'>Net Carbs (% Target)</div>
                <div class='val-sm count-up' data-target='{carbs_pct}' data-decimals='1' data-suffix='%'>{fmt_num(carbs_pct, 1, '%')}</div>
                <div class='rag-badge {c_badge_cls}'>{c_rag}: {c_desc}</div>
              </div>""", unsafe_allow_html=True)

            fat_pct = clean_float(y.iloc[18]) if len(y) > 18 else 0.0
            f_rag, f_color, f_badge_cls, f_desc = eval_macro_rag(fat_pct, 'fat')
            m3.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {f_color};'>
                <div class='label'>Fat (% Target)</div>
                <div class='val-sm count-up' data-target='{fat_pct}' data-decimals='1' data-suffix='%'>{fmt_num(fat_pct, 1, '%')}</div>
                <div class='rag-badge {f_badge_cls}'>{f_rag}: {f_desc}</div>
              </div>""", unsafe_allow_html=True)

            alc_kcal = clean_float(y.iloc[19]) if len(y) > 19 else 0.0
            alc_border = "#30D158" if alc_kcal == 0 else "#BF5AF2"
            m4.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {alc_border};'>
                <div class='label'>Alcohol Intake</div>
                <div class='val-sm count-up' data-target='{alc_kcal}' data-decimals='0' data-suffix=' kcal'>{fmt_num(alc_kcal, 0, ' kcal')}</div>
                <div class='rag-badge {"rag-green" if alc_kcal==0 else "rag-red"}'>{"ZERO" if alc_kcal==0 else "ACTIVE"}</div>
              </div>""", unsafe_allow_html=True)

            # Vitals Gauges
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            sys_val = clean_float(y.iloc[21]) if len(y) > 21 and clean_float(y.iloc[21]) > 0 else 118.0
            dia_val = clean_float(y.iloc[22]) if len(y) > 22 and clean_float(y.iloc[22]) > 0 else 78.0
            rhr_val = clean_float(y.iloc[27]) if len(y) > 27 and clean_float(y.iloc[27]) > 0 else clean_float(y.iloc[23])
            if rhr_val == 0: rhr_val = 72.0

            g1, g2, g3 = st.columns(3)
            with g1:
                st.plotly_chart(make_semi_gauge(sys_val, "Systolic BP", 80, 180, [80, 120], [120, 140], [140, 180], "mmHg"), use_container_width=True)
            with g2:
                st.plotly_chart(make_semi_gauge(dia_val, "Diastolic BP", 50, 120, [50, 80], [80, 90], [90, 120], "mmHg"), use_container_width=True)
            with g3:
                st.plotly_chart(make_semi_gauge(rhr_val, "Resting HR", 40, 130, [40, 65], [65, 80], [80, 130], "BPM"), use_container_width=True)

            st.markdown(evaluate_debuffs(y), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — 🧬 Metabolic Intelligence
    # ══════════════════════════════════════════
    with tab2:
        st.markdown("<div class='section-header'>Metabolic Intelligence Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Dynamic TDEE Re-estimation & Caloric Deficit RAG Bars</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='context-card'>
            <div class='context-title'>💡 UNDERSTANDING YOUR METABOLIC BURN & RAG BARS</div>
            <div class='context-text'>
                <b>Total Daily Energy Expenditure (TDEE)</b> is re-calculated directly from your actual scale drops.<br>
                <b>Bar Color Coding:</b><br>
                • <b style='color:#30D158;'>GREEN Bar:</b> Intake ≤ 1,633 kcal (Target Achieved — Maximum Deficit)<br>
                • <b style='color:#FF9F0A;'>AMBER Bar:</b> Intake 1,634–1,750 kcal (Moderate Deficit)<br>
                • <b style='color:#FF2D55;'>RED Bar:</b> Intake > 1,750 kcal (Surplus / Reduced Deficit)
            </div>
        </div>
        """, unsafe_allow_html=True)

        w_series = get_num(3, df_valid).dropna()
        cals_series = get_num(1, df_valid).dropna()

        if len(w_series) >= 14:
            w_14_start = w_series.iloc[-14]
            w_14_end   = w_series.iloc[-1]
            w_14_drop  = w_14_start - w_14_end
            avg_cals_14 = cals_series.tail(14).mean()

            est_tdee_14 = avg_cals_14 + (w_14_drop * 3500.0 / 14.0)

            w_30_days  = 30 if len(w_series) >= 30 else len(w_series)
            w_30_start = w_series.iloc[-w_30_days]
            w_30_drop  = w_30_start - w_14_end
            avg_cals_30 = cals_series.tail(w_30_days).mean()
            est_tdee_30 = avg_cals_30 + (w_30_drop * 3500.0 / float(w_30_days))

            daily_deficit = est_tdee_30 - 1633.0
            weekly_fat_loss_proj = (daily_deficit * 7.0) / 3500.0

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(card("Real TDEE (14d Rolling)", num_target=est_tdee_14, decimals=0, suffix=" kcal/day"), unsafe_allow_html=True)
            with mc2:
                st.markdown(card("Real TDEE (30d Rolling)", num_target=est_tdee_30, decimals=0, suffix=" kcal/day"), unsafe_allow_html=True)
            with mc3:
                st.markdown(card("Projected Fat Loss @ 1633 Target", num_target=weekly_fat_loss_proj, decimals=2, suffix=" lbs/wk"), unsafe_allow_html=True)

            def get_bar_color(c):
                if c <= 1633: return '#30D158'
                elif c <= 1750: return '#FF9F0A'
                else: return '#FF2D55'

            recent_cals = cals_series.tail(w_30_days)
            bar_colors = [get_bar_color(c) for c in recent_cals]
            dates_tdee = df_valid.iloc[-w_30_days:, 0]

            fig_t = go.Figure()
            fig_t.add_trace(go.Bar(x=dates_tdee, y=recent_cals, name="Daily Calorie Intake", marker_color=bar_colors))
            fig_t.add_hline(y=est_tdee_30, line_dash="dash", line_color="#0A84FF", annotation_text=f"Dynamic TDEE ({est_tdee_30:.0f} kcal)")
            fig_t.add_hline(y=1633, line_dash="dot", line_color="#30D158", annotation_text="1,633 Target")
            st.plotly_chart(apply_theme(fig_t, "Daily Intake RAG Performance vs TDEE Baseline", "COLOR-CODED CALORIC BARS"), use_container_width=True)
        else:
            st.info("Requires at least 14 days of logged weight & calories to calculate dynamic TDEE.")

    # ══════════════════════════════════════════
    #  TAB 3 — 🫀 Cardio Vitals & Workload (RPP)
    # ══════════════════════════════════════════
    with tab3:
        st.markdown("<div class='section-header'>Cardiovascular Matrix & Rate Pressure Product</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Resting HR Dynamics, Myocardial Workload & Alcohol Elevation</div>", unsafe_allow_html=True)

        sys_data = get_num(21)
        dia_data = get_num(22)
        rhr_data = get_num(27)
        if not rhr_data.notna().any(): rhr_data = get_num(23)

        alc_series = get_num(19)

        valid_rhr_mask  = rhr_data.notna() & (rhr_data > 0)
        alc_days_mask   = (alc_series > 0) & valid_rhr_mask
        sober_days_mask = (alc_series == 0) & valid_rhr_mask

        avg_rhr_alc   = rhr_data[alc_days_mask].mean() if alc_days_mask.sum() > 0 else 0.0
        avg_rhr_sober = rhr_data[sober_days_mask].mean() if sober_days_mask.sum() > 0 else 0.0
        rhr_diff      = avg_rhr_alc - avg_rhr_sober

        # Rate Pressure Product (RPP) = Systolic BP * Resting HR
        last_sys = sys_data.dropna().iloc[-1] if sys_data.dropna().shape[0] > 0 else 120.0
        last_dia = dia_data.dropna().iloc[-1] if dia_data.dropna().shape[0] > 0 else 80.0
        last_rhr = rhr_data.dropna().iloc[-1] if rhr_data.dropna().shape[0] > 0 else 72.0
        
        rpp_index = last_sys * last_rhr
        pulse_pressure = last_sys - last_dia
        map_val = last_dia + (pulse_pressure / 3.0)

        alc_color   = "#FF2D55" if avg_rhr_alc > avg_rhr_sober else "#30D158"
        sober_color = "#30D158" if avg_rhr_sober <= avg_rhr_alc else "#FF2D55"

        st.markdown(f"""
        <div class='context-card'>
            <div class='context-title'>❤️ CARDIO WORKLOAD (RPP) & RECOVERY PHYSIOLOGY</div>
            <div class='context-text'>
                • <b>Rate Pressure Product (RPP):</b> <b style='color:#64D2FF;'>{rpp_index:,.0f}</b> (Systolic BP × Resting HR). Measures myocardial oxygen consumption. Normal resting RPP is <b>6,000–10,000</b>.<br>
                • <b>Alcohol Cardio Strain:</b> On days following alcohol consumption, Resting HR averaged <b style='color:{alc_color};'>{avg_rhr_alc:.1f} BPM</b> vs. <b style='color:{sober_color};'>{avg_rhr_sober:.1f} BPM</b> on sober days.
            </div>
        </div>
        """, unsafe_allow_html=True)

        vc1, vc2, vc3 = st.columns(3)
        with vc1:
            st.markdown(card("Pulse Pressure (Sys - Dia)", num_target=pulse_pressure, decimals=0, suffix=" mmHg"), unsafe_allow_html=True)
        with vc2:
            st.markdown(card("Mean Arterial Pressure (MAP)", num_target=map_val, decimals=1, suffix=" mmHg"), unsafe_allow_html=True)
        with vc3:
            st.markdown(card("Rate Pressure Product (RPP)", num_target=rpp_index, decimals=0, suffix=" index"), unsafe_allow_html=True)

        fig_cardio = go.Figure()
        fig_cardio.add_trace(go.Scatter(x=df.iloc[:, 0], y=sys_data, name="Systolic BP", mode='lines+markers', connectgaps=True, line=dict(color='#FF2D55', width=2.5)))
        fig_cardio.add_trace(go.Scatter(x=df.iloc[:, 0], y=dia_data, name="Diastolic BP", mode='lines+markers', connectgaps=True, line=dict(color='#0A84FF', width=2.5)))
        if rhr_data.notna().any():
            fig_cardio.add_trace(go.Scatter(x=df.iloc[:, 0], y=rhr_data, name="Resting HR (BPM)", mode='lines+markers', connectgaps=True, line=dict(color='#30D158', width=2.5)))
        st.plotly_chart(apply_theme(fig_cardio, "Blood Pressure & Resting HR Trends", "HEMODYNAMIC & CARDIAC MONITORING"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 4 — Lifetime Cumulative Analytics
    # ══════════════════════════════════════════
    with tab4:
        l = df.iloc[-1]
        st.markdown("<div class='section-header'>Lifetime Cumulative Telemetry</div>", unsafe_allow_html=True)

        st.markdown(f"""
          <div class='card' style='background:linear-gradient(135deg,#0A84FF 0%,#30D158 130%);
               border: none; margin-bottom:1.5rem; box-shadow: 0 10px 30px rgba(10,132,255,0.28);'>
            <div class='label' style='color:rgba(255,255,255,0.85); font-size:0.78rem; letter-spacing:0.1em;'>ACTIVE STREAK</div>
            <div class='count-up' data-target='{len(df)}' data-decimals='0' style='font-family:Inter,sans-serif; font-size:4.2rem; font-weight:800;
                        color:#ffffff; margin:8px 0; line-height:1; letter-spacing:-0.02em;'>{fmt_num(len(df), 0, '')}</div>
            <div style='font-family:Inter,sans-serif; font-size:0.85rem; color:rgba(255,255,255,0.9); font-weight:600;'>CONSECUTIVE DAYS LOGGED</div>
          </div>""", unsafe_allow_html=True)

        total_steps_lt   = get_num(12).sum()
        total_miles_lt   = get_num(13).sum()
        total_flights_lt = get_num(26).sum()
        total_elevation_ft = total_flights_lt * 10.0
        total_act_cals   = get_num(15).sum()
        total_water_l    = get_num(24).sum() / 1000.0
        total_marathons  = total_miles_lt / 26.2 if total_miles_lt > 0 else 0.0

        rhr_series_lt = get_num(27)
        if not rhr_series_lt.notna().any(): rhr_series_lt = get_num(23)
        avg_rhr_lt    = rhr_series_lt.replace(0, np.nan).dropna().mean()

        total_stand_hrs = get_num(28).sum()
        total_ex_mins   = get_num(29).sum()

        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        with r1_c1:
            st.markdown(card("Total Weight Loss (lbs)", num_target=clean_float(l.iloc[6]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
        with r1_c2:
            st.markdown(card("Total Weight Loss (Stone)", display_val=f"{l.iloc[7]}"), unsafe_allow_html=True)
        with r1_c3:
            st.markdown(card("To Target (lbs)", num_target=clean_float(l.iloc[8]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
        with r1_c4:
            st.markdown(card("To Target (Stone)", display_val=f"{l.iloc[9]}"), unsafe_allow_html=True)

        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1:
            st.markdown(card("Total Miles Walked", num_target=total_miles_lt, decimals=1, suffix=" miles"), unsafe_allow_html=True)
        with r2_c2:
            st.markdown(card("Equivalent Marathons", num_target=total_marathons, decimals=1, suffix=" races"), unsafe_allow_html=True)
        with r2_c3:
            st.markdown(card("Total Flights Climbed", num_target=total_flights_lt, decimals=0, suffix=" flights"), unsafe_allow_html=True)
        with r2_c4:
            st.markdown(card("Vertical Elevation Gained", num_target=total_elevation_ft, decimals=0, suffix=" ft"), unsafe_allow_html=True)

        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        with r3_c1:
            st.markdown(card("Average Resting HR", num_target=avg_rhr_lt if pd.notna(avg_rhr_lt) else 0, decimals=0, suffix=" BPM"), unsafe_allow_html=True)
        with r3_c2:
            st.markdown(card("Total Exercise Minutes", num_target=total_ex_mins, decimals=0, suffix=" mins"), unsafe_allow_html=True)
        with r3_c3:
            st.markdown(card("Total Stand Hours Logged", num_target=total_stand_hrs, decimals=0, suffix=" hrs"), unsafe_allow_html=True)
        with r3_c4:
            st.markdown(card("Total Water Consumed", num_target=total_water_l, decimals=0, suffix=" Liters"), unsafe_allow_html=True)

        r4_c1, r4_c2, r4_c3, r4_c4 = st.columns(4)
        with r4_c1:
            st.markdown(card("Current BMI", num_target=clean_float(l.iloc[10]), decimals=1), unsafe_allow_html=True)
        with r4_c2:
            st.markdown(card("To Target BMI", num_target=clean_float(l.iloc[11]), decimals=1), unsafe_allow_html=True)
        with r4_c3:
            st.markdown(card("Total Steps Logged", num_target=total_steps_lt, decimals=0, suffix=" steps"), unsafe_allow_html=True)
        with r4_c4:
            st.markdown(card("Total Activity Cals Burned", num_target=total_act_cals, decimals=0, suffix=" kcal"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 5 — Calories
    # ══════════════════════════════════════════
    with tab5:
        cal_series = get_num(1)
        cal_min = float(cal_series.min()) if cal_series.notna().any() else 0
        cal_max = float(cal_series.max()) if cal_series.notna().any() else 2000
        cal_range = cal_max - cal_min if cal_max != cal_min else 1

        def norm(v): return max(0.0, min(1.0, (v - cal_min) / cal_range))
        colorscale = [[0.0, '#2FA84F'], [norm(1633), '#30D158'], [norm(1634), '#FF9F0A'], [norm(1700), '#FF7A1A'], [norm(1701), '#FF2D55'], [1.0, '#D01144']]
        clean_cs = []
        seen = set()
        for pos, col in colorscale:
            if pos not in seen:
                seen.add(pos)
                clean_cs.append([pos, col])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=cal_series, name="Calories In",
            marker=dict(color=cal_series, colorscale=clean_cs, cmin=cal_min, cmax=cal_max, line=dict(width=0)), opacity=0.92,
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(2), name="Net Calories", mode='lines', line=dict(color='#FFFFFF', width=2.5, dash='dot')))
        fig.add_hline(y=1633, line_dash="dash", line_color="#30D158", annotation_text="Target 1,633", annotation_font_color="#30D158")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Caloric Intake vs Net Calories", "TARGET: ≤ 1,633 KCAL"), use_container_width=True)

        st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
        cal_logged = cal_series.dropna()
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown(card("7-Day Avg", num_target=cal_logged.tail(7).mean(), decimals=0, suffix=" kcal"), unsafe_allow_html=True)
        with cc2:
            st.markdown(card("30-Day Avg", num_target=cal_logged.tail(30).mean(), decimals=0, suffix=" kcal"), unsafe_allow_html=True)
        with cc3:
            st.markdown(card("90-Day Avg", num_target=cal_logged.tail(90).mean(), decimals=0, suffix=" kcal"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Hydration
    # ══════════════════════════════════════════
    with tab6:
        st.markdown("<div class='section-header'>Hydration & Fluid Intelligence</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>5,000 ML (5 LITERS) TARGET BASELINE</div>", unsafe_allow_html=True)

        hyd_series = get_num(24)
        hyd_logged = hyd_series.dropna()

        w_series = get_num(3, df_valid)
        w_delta  = w_series - w_series.shift(1)
        valid_mask = w_delta.notna()

        high_water_mask = (hyd_series >= 5000) & valid_mask
        low_water_mask  = (hyd_series < 5000) & (hyd_series > 0) & valid_mask

        avg_drop_high_w = w_delta[high_water_mask].mean() if high_water_mask.sum() > 0 else 0.0
        avg_drop_low_w  = w_delta[low_water_mask].mean() if low_water_mask.sum() > 0 else 0.0

        drop_high_desc = f"{abs(avg_drop_high_w):.2f} lbs drop" if avg_drop_high_w <= 0 else f"{abs(avg_drop_high_w):.2f} lbs gain"
        drop_low_desc  = f"{abs(avg_drop_low_w):.2f} lbs drop" if avg_drop_low_w <= 0 else f"{abs(avg_drop_low_w):.2f} lbs gain"

        high_color = "#30D158" if avg_drop_high_w <= avg_drop_low_w else "#0A84FF"
        low_color  = "#30D158" if avg_drop_low_w < avg_drop_high_w else "#0A84FF"

        st.markdown(f"""
        <div class='context-card'>
            <div class='context-title'>💧 HYDRATION IMPACT ON SCALE MOVEMENT</div>
            <div class='context-text'>
                Note: A negative number (e.g. -0.30 lbs) indicates a <b>weight drop on the scale</b>.<br>
                • On days drinking <b>≥ 5,000 ml</b>, your average scale shift was <b style='color:{high_color};'>{avg_drop_high_w:+.2f} lbs</b> ({drop_high_desc}).<br>
                • On days under <b>5,000 ml</b>, your average scale shift was <b style='color:{low_color};'>{avg_drop_low_w:+.2f} lbs</b> ({drop_low_desc}).
            </div>
        </div>
        """, unsafe_allow_html=True)

        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown(card("7-Day Avg Water", num_target=hyd_logged.tail(7).mean(), decimals=0, suffix=" ml"), unsafe_allow_html=True)
        with hc2:
            st.markdown(card("30-Day Avg Water", num_target=hyd_logged.tail(30).mean(), decimals=0, suffix=" ml"), unsafe_allow_html=True)
        with hc3:
            st.markdown(card("90-Day Avg Water", num_target=hyd_logged.tail(90).mean(), decimals=0, suffix=" ml"), unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=hyd_series, name="Hydration (ml)",
            marker=dict(color=hyd_series, colorscale=[[0, '#0A84FF'], [1, '#64D2FF']]),
        ))
        fig.add_hline(y=5000, line_dash="dash", line_color="#0A84FF", annotation_text="5,000 ML TARGET", annotation_font_color="#0A84FF")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Hydration Volume (ml)", "TARGET: 5,000 ML (5 LITERS)"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 7 — Weight Trajectory
    # ══════════════════════════════════════════
    with tab7:
        w_series = get_num(3).dropna()
        dates_w  = df.iloc[:len(w_series), 0]
        w_ema    = w_series.ewm(span=7, adjust=False).mean()
        w_max    = float(w_series.max()) + 2 if not w_series.empty else 210

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates_w, y=w_series, name="Raw Scale Weight", mode='markers',
            marker=dict(color='#BF5AF2', size=7, opacity=0.8, line=dict(color='#ffffff', width=1)), zorder=2
        ))
        fig.add_trace(go.Scatter(
            x=dates_w, y=w_ema, name="7-Day Trend EMA (Happy Scale)", mode='lines',
            line=dict(color='#0A84FF', width=3.5, shape='spline'), zorder=3,
            fill='tozeroy', fillcolor='rgba(10, 132, 255, 0.08)'
        ))
        fig.add_hline(y=170, line_dash="dash", line_color="#30D158", annotation_text="🎯 GOAL: 170 lbs (12 st 2 lbs)", annotation_font_color="#30D158", annotation_position="top left")

        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory & Trend Smoothing", "NEON SMOOTHING ENGINE VS DAILY ACTUALS"), use_container_width=True)

        latest_lbs = w_series.iloc[-1] if not w_series.empty else 0.0
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            st.markdown(card("Current Weight (lbs)", num_target=latest_lbs, decimals=1, suffix=" lbs"), unsafe_allow_html=True)
        with wc2:
            st.markdown(card("Current Weight (Stone)", display_val=lbs_to_stone(latest_lbs)), unsafe_allow_html=True)
        with wc3:
            st.markdown(card("7-Day Trend Weight", num_target=w_ema.iloc[-1] if not w_ema.empty else 0, decimals=1, suffix=" lbs"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 8 — Steps, Elevation & Landmark Challenge
    # ══════════════════════════════════════════
    with tab8:
        st.markdown("<div class='section-header'>Kinetic Movement & Landmark Elevation</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Steps, Flights, Exercise Mins & Vertical Landmark Challenges</div>", unsafe_allow_html=True)

        steps_data   = get_num(12)
        flights_data = get_num(26)
        ex_mins_data = get_num(29)

        total_elev_ft = flights_data.sum() * 10.0
        everest_pct   = (total_elev_ft / 29032.0) * 100.0
        burj_pct      = (total_elev_ft / 2717.0) * 100.0

        st.markdown(f"""
        <div class='context-card'>
            <div class='context-title'>🏔️ VERTICAL ELEVATION LANDMARK CHALLENGE</div>
            <div class='context-text'>
                • <b>Total Vertical Elevation Gained:</b> <b style='color:#30D158;'>{total_elev_ft:,.0f} feet</b>.<br>
                • <b>Burj Khalifa Progress:</b> Equivalent to climbing the Burj Khalifa <b style='color:#0A84FF;'>{burj_pct/100:.1f} times</b> (2,717 ft).<br>
                • <b>Mount Everest Challenge:</b> Completed <b style='color:#64D2FF;'>{everest_pct:.1f}%</b> of Mount Everest's peak height (29,032 ft)!
            </div>
        </div>
        """, unsafe_allow_html=True)

        def step_color(s):
            if s >= 10000: return '#30D158'
            elif s >= 8000: return '#FF9F0A'
            else: return '#FF2D55'

        def flight_color(f):
            if f >= 10: return '#30D158'
            elif f >= 5: return '#FF9F0A'
            else: return '#FF2D55'

        def ex_color(m):
            if m >= 50: return '#30D158'
            elif m >= 30: return '#FF9F0A'
            else: return '#FF2D55'

        fig_s = go.Figure()
        fig_s.add_trace(go.Bar(x=df.iloc[:, 0], y=steps_data, name="Steps", marker_color=[step_color(s) for s in steps_data.fillna(0)]))
        fig_s.add_hline(y=10000, line_dash="dash", line_color="#30D158", annotation_text="10,000 Target")
        st.plotly_chart(apply_theme(fig_s, "1. Daily Step Volume", "GREEN ≥ 10k // AMBER 8k-9.9k // RED < 8k"), use_container_width=True)

        fig_f = go.Figure()
        fig_f.add_trace(go.Bar(x=df.iloc[:, 0], y=flights_data, name="Flights", marker_color=[flight_color(f) for f in flights_data.fillna(0)]))
        fig_f.add_hline(y=10, line_dash="dash", line_color="#30D158", annotation_text="10 Flights Target")
        st.plotly_chart(apply_theme(fig_f, "2. Daily Flights Climbed", "GREEN ≥ 10 // AMBER 5-9 // RED < 5"), use_container_width=True)

        fig_e = go.Figure()
        fig_e.add_trace(go.Bar(x=df.iloc[:, 0], y=ex_mins_data, name="Exercise Mins", marker_color=[ex_color(m) for m in ex_mins_data.fillna(0)]))
        fig_e.add_hline(y=50, line_dash="dash", line_color="#30D158", annotation_text="50 Mins Goal")
        fig_e.add_hline(y=30, line_dash="dot", line_color="#FF9F0A", annotation_text="30 Mins Floor")
        st.plotly_chart(apply_theme(fig_e, "3. Daily Exercise Minutes (Brisk Intensity)", "GREEN ≥ 50m // AMBER 30-49m // RED < 30m"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 9 — Macro RAG Matrix
    # ══════════════════════════════════════════
    with tab9:
        st.markdown("<div class='section-header'>RAG Macro Performance Matrix</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Proportional Target Adherence (% Target) over Time</div>", unsafe_allow_html=True)

        p_pcts = get_num(16)
        c_pcts = get_num(17)
        f_pcts = get_num(18)

        p_green_pct_30 = (p_pcts.tail(30) >= 85).sum() / 30.0 * 100.0
        c_green_pct_30 = (c_pcts.tail(30) < 90).sum() / 30.0 * 100.0
        f_green_pct_30 = (f_pcts.tail(30) < 90).sum() / 30.0 * 100.0

        st.markdown(f"""
        <div class='context-card'>
            <div class='context-title'>🥗 MACRONUTRIENT RAG COMPLIANCE & FAT LOSS PHYSIOLOGY</div>
            <div class='context-text'>
                • <b>Protein (≥ 85% Target):</b> Reached Green status on <b>{p_green_pct_30:.0f}% of last 30 days</b>. High protein preserves lean muscle mass during deficits and elevates Thermic Effect of Food (TEF).<br>
                • <b>Net Carbs (< 90% Target):</b> Reached Green status on <b>{c_green_pct_30:.0f}% of last 30 days</b>. Keeping net carbs strictly controlled minimizes glycogen-bound water retention.<br>
                • <b>Dietary Fat (< 90% Target):</b> Reached Green status on <b>{f_green_pct_30:.0f}% of last 30 days</b>. Controlling fats ensures total daily intake remains within the 1,633 kcal deficit window.
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig_m = go.Figure()
        fig_m.add_trace(go.Scatter(x=df.iloc[:, 0], y=p_pcts, name="Protein (% Target)", mode='lines', line=dict(color='#FF2D55', width=2.5)))
        fig_m.add_trace(go.Scatter(x=df.iloc[:, 0], y=c_pcts, name="Net Carbs (% Target)", mode='lines', line=dict(color='#0A84FF', width=2.5)))
        fig_m.add_trace(go.Scatter(x=df.iloc[:, 0], y=f_pcts, name="Fat (% Target)", mode='lines', line=dict(color='#FFD60A', width=2.5)))

        fig_m.add_hline(y=85.0, line_dash="dash", line_color="#30D158", annotation_text="Protein Green Floor (85%)")
        fig_m.add_hline(y=110.0, line_dash="dash", line_color="#FF2D55", annotation_text="Carb/Fat Red Ceiling (110%)")

        fig_m.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig_m, "Macro Target Compliance (% Target)", "RAG COMPLIANCE ENGINE"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 10 — 📅 Patterns
    # ══════════════════════════════════════════
    with tab10:
        st.markdown("<div class='section-header'>Weekly Pattern Profiler</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Behavioral Variance & Scale Shifts by Day of the Week</div>", unsafe_allow_html=True)

        tf_choice = st.radio("Select Time Horizon:", ["Last 14 Days", "Last 30 Days", "Lifetime"], horizontal=True)

        if tf_choice == "Last 14 Days":
            dow_source = df_valid.tail(14).copy()
        elif tf_choice == "Last 30 Days":
            dow_source = df_valid.tail(30).copy()
        else:
            dow_source = df_valid.copy()

        dow_source['Day'] = dow_source.iloc[:, 0].dt.day_name()
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        dow_source['Calories'] = pd.to_numeric(dow_source.iloc[:, 1], errors='coerce')
        dow_source['Steps']    = pd.to_numeric(dow_source.iloc[:, 12], errors='coerce')
        dow_source['Water']    = pd.to_numeric(dow_source.iloc[:, 24], errors='coerce')
        
        w_s = pd.to_numeric(dow_source.iloc[:, 3], errors='coerce')
        dow_source['Scale_Shift'] = w_s - w_s.shift(1)

        dow_summary = dow_source.groupby('Day')[['Calories', 'Steps', 'Water', 'Scale_Shift']].mean().reindex(days_order)

        best_cal_day  = dow_summary['Calories'].idxmin()
        worst_cal_day = dow_summary['Calories'].idxmax()
        best_drop_day = dow_summary['Scale_Shift'].idxmin()
        worst_gain_day = dow_summary['Scale_Shift'].idxmax()

        st.markdown(f"""
        <div class='insights-card'>
            <div class='insights-title'>📅 DIAGNOSTIC PATTERN INSIGHTS ({tf_choice.upper()})</div>
            <div class='insight-item'>• <b>Best Day for Caloric Control:</b> <b style='color:#30D158;'>{best_cal_day}s</b> (Avg intake: <b>{dow_summary.loc[best_cal_day, 'Calories']:.0f} kcal</b>).</div>
            <div class='insight-item'>• <b>Highest Caloric Surplus Risk:</b> <b style='color:#FF2D55;'>{worst_cal_day}s</b> (Avg intake: <b>{dow_summary.loc[worst_cal_day, 'Calories']:.0f} kcal</b>).</div>
            <div class='insight-item'>• <b>Peak Scale Drop Day:</b> <b style='color:#30D158;'>{best_drop_day}s</b> (Avg next-morning scale shift: <b>{dow_summary.loc[best_drop_day, 'Scale_Shift']:+.2f} lbs</b>).</div>
            <div class='insight-item'>• <b>Most Resistant / Gain Day:</b> <b style='color:#FF2D55;'>{worst_gain_day}s</b> (Avg next-morning scale shift: <b>{dow_summary.loc[worst_gain_day, 'Scale_Shift']:+.2f} lbs</b>).</div>
        </div>
        """, unsafe_allow_html=True)

        fig_dow = go.Figure()
        fig_dow.add_trace(go.Bar(x=dow_summary.index, y=dow_summary['Calories'], name='Avg Calories', marker_color='#0A84FF'))
        fig_dow.add_hline(y=1633, line_dash="dash", line_color="#30D158", annotation_text="1,633 Target Ceiling")
        st.plotly_chart(apply_theme(fig_dow, f"Average Caloric Intake by Day of Week ({tf_choice})", "BEHAVIORAL PATTERN ANALYSIS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 11 — Historical Telemetry Averages
    # ══════════════════════════════════════════
    with tab11:
        w_series = get_num(3).dropna()
        avg_loss = (w_series.iloc[0] - w_series.iloc[-1]) / (len(df) / 7) if len(w_series) > 1 else 0.0

        rhr_series_avg = get_num(27)
        if not rhr_series_avg.notna().any(): rhr_series_avg = get_num(23)
        avg_rhr_val = rhr_series_avg.replace(0, np.nan).dropna().mean()

        st.markdown("<div class='section-header'>Historical Telemetry Averages</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Avg Cals / Day", num_target=get_num(1).mean(), decimals=0, suffix=" kcal"), unsafe_allow_html=True)
            st.markdown(card("Avg Protein % Target", num_target=get_num(16).mean(), decimals=1, suffix="%"), unsafe_allow_html=True)
            st.markdown(card("Avg Resting HR", num_target=avg_rhr_val if pd.notna(avg_rhr_val) else 0, decimals=0, suffix=" BPM"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("Avg Steps / Day", num_target=get_num(12).mean(), decimals=0), unsafe_allow_html=True)
            st.markdown(card("Avg Net Carbs % Target", num_target=get_num(17).mean(), decimals=1, suffix="%"), unsafe_allow_html=True)
            st.markdown(card("Avg Flights Climbed", num_target=get_num(26).mean(), decimals=1, suffix=" flights"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Avg Loss / Week", num_target=avg_loss, decimals=2, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Avg Fat % Target", num_target=get_num(18).mean(), decimals=1, suffix="%"), unsafe_allow_html=True)
            st.markdown(card("Avg Exercise Minutes", num_target=get_num(29).replace(0, np.nan).dropna().mean() if get_num(29).dropna().shape[0]>0 else 0, decimals=0, suffix=" mins"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 12 — 🎯 Milestones
    # ══════════════════════════════════════════
    with tab12:
        st.markdown("<div class='section-header'>Milestones & Gateway Tracker</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Breakthrough Gateways to 170 lbs (12 st 2 lbs)</div>", unsafe_allow_html=True)

        w_series = get_num(3).dropna()
        latest_w = w_series.iloc[-1] if not w_series.empty else 200.0
        start_w  = w_series.iloc[0] if not w_series.empty else 220.0
        goal_w   = 170.0

        total_dist = start_w - goal_w
        dist_covered = start_w - latest_w
        pct_achieved = max(0.0, min(100.0, (dist_covered / total_dist) * 100.0)) if total_dist > 0 else 0.0

        st.markdown(f"""
        <div class='card' style='padding:24px; margin-bottom:20px;'>
            <div class='label' style='font-size:0.85rem;'>OVERALL GOAL PROGRESS</div>
            <div class='val' style='color:#0A84FF; font-size:3.2rem;'>{pct_achieved:.1f}%</div>
            <div style='background:rgba(255,255,255,0.08); border-radius:10px; height:14px; margin-top:12px; overflow:hidden;'>
                <div style='background:linear-gradient(90deg, #0A84FF, #30D158); width:{pct_achieved}%; height:100%;'></div>
            </div>
            <div style='font-size:0.85rem; color:var(--text-secondary); margin-top:10px;'><b>{latest_w - goal_w:.1f} lbs</b> remaining until 170 lbs target</div>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(card("15 Stone Gateway (210 lbs)", display_val="PASSED" if latest_w < 210 else f"{latest_w - 210:.1f} lbs left"), unsafe_allow_html=True)
        with sc2:
            st.markdown(card("14 Stone Gateway (196 lbs)", display_val="PASSED" if latest_w < 196 else f"{latest_w - 196:.1f} lbs left"), unsafe_allow_html=True)
        with sc3:
            st.markdown(card("13 Stone Gateway (182 lbs)", display_val="PASSED" if latest_w < 182 else f"{latest_w - 182:.1f} lbs left"), unsafe_allow_html=True)
        with sc4:
            st.markdown(card("12 st 2 lbs Goal (170 lbs)", display_val="ACHIEVED" if latest_w <= 170 else f"{latest_w - 170:.1f} lbs left"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 13 — Trophy Room
    # ══════════════════════════════════════════
    with tab13:
        st.markdown("<div class='section-header'>The Trophy Room</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Milestone Unlocks</div>", unsafe_allow_html=True)

        total_days = len(df)
        cals_in   = get_num(1)
        steps_arr = get_num(12)
        sys_arr   = get_num(21)
        dia_arr   = get_num(22)
        hyd_arr   = get_num(24)

        total_loss_lbs = clean_float(df.iloc[-1].iloc[6]) if not df.empty else 0
        min_weight     = get_num(3).min()

        perfect_cals_days  = ((cals_in > 0) & (cals_in <= 1633)).sum()
        perfect_steps_days = (steps_arr >= 10000).sum()
        perfect_hyd_days   = (hyd_arr >= 5000).sum()
        ideal_bp_days      = ((sys_arr > 0) & (sys_arr <= 120) & (dia_arr > 0) & (dia_arr <= 80)).sum()

        def get_pct(days, total): return (days / total * 100) if total > 0 else 0

        badges = [
            {"title": "Iron Will", "desc": f"{perfect_cals_days} Days ({get_pct(perfect_cals_days, total_days):.1f}%) ≤ 1,633 kcal", "unlocked": perfect_cals_days > 0, "icon": "🔥"},
            {"title": "Marathoner", "desc": f"{perfect_steps_days} Days ({get_pct(perfect_steps_days, total_days):.1f}%) ≥ 10k Steps", "unlocked": perfect_steps_days > 0, "icon": "👟"},
            {"title": "Aqua Master", "desc": f"{perfect_hyd_days} Days ({get_pct(perfect_hyd_days, total_days):.1f}%) ≥ 5L Water", "unlocked": perfect_hyd_days > 0, "icon": "💧"},
            {"title": "Zen Heart", "desc": f"{ideal_bp_days} Days ({get_pct(ideal_bp_days, total_days):.1f}%) Ideal BP", "unlocked": ideal_bp_days > 0, "icon": "❤️"},
            {"title": "First Blood", "desc": "Drop 5 lbs total", "unlocked": total_loss_lbs >= 5, "icon": "📉"},
            {"title": "Double Digits", "desc": "Drop 10 lbs total", "unlocked": total_loss_lbs >= 10, "icon": "📉"},
            {"title": "The 15 Club", "desc": "Drop 15 lbs total", "unlocked": total_loss_lbs >= 15, "icon": "📉"},
            {"title": "Twenty Down", "desc": "Drop 20 lbs total", "unlocked": total_loss_lbs >= 20, "icon": "📉"},
            {"title": "Quarter Century", "desc": "Drop 25 lbs total", "unlocked": total_loss_lbs >= 25, "icon": "📉"},
            {"title": "Sub-200 Club", "desc": "Drop below 200 lbs", "unlocked": min_weight < 200, "icon": "🎯"},
            {"title": "195 lb Milestone", "desc": "Drop below 195 lbs", "unlocked": min_weight < 195, "icon": "🎯"},
            {"title": "190 lb Milestone", "desc": "Drop below 190 lbs", "unlocked": min_weight < 190, "icon": "🎯"},
            {"title": "185 lb Milestone", "desc": "Drop below 185 lbs", "unlocked": min_weight < 185, "icon": "🎯"},
            {"title": "180 lb Milestone", "desc": "Drop below 180 lbs", "unlocked": min_weight < 180, "icon": "🎯"},
            {"title": "175 lb Milestone", "desc": "Drop below 175 lbs", "unlocked": min_weight < 175, "icon": "🎯"},
            {"title": "Goal Achieved", "desc": "Hit 170 lbs target", "unlocked": min_weight <= 170, "icon": "🏆"}
        ]

        def render_badge(b):
            if b["unlocked"]:
                extra = "border-color: rgba(48,209,88,0.4); box-shadow: 0 4px 20px rgba(48,209,88,0.22);"
                val_color = "#30D158"; status = "UNLOCKED"
            else:
                extra = "opacity: 0.45; background: var(--bg-card);"
                val_color = "var(--text-tertiary)"; status = "LOCKED"

            return f"""
            <div class='card' style='{extra} transition: all 0.3s ease; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size:2.3rem; margin-bottom:8px;'>{b['icon']}</div>
                <div class='label' style='color:{val_color}; margin-bottom:4px; letter-spacing:0.08em;'>{status}</div>
                <div class='val-sm' style='font-size:1.05rem; margin-bottom:2px;'>{b['title']}</div>
                <div style='font-family:Inter,sans-serif; font-size:0.7rem; color:var(--text-tertiary); font-weight:500;'>{b['desc']}</div>
            </div>"""

        for i in range(0, len(badges), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(badges):
                    with cols[j]:
                        st.markdown(render_badge(badges[i + j]), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 14 — Analytics Engine
    # ══════════════════════════════════════════
    with tab14:
        st.markdown("<div class='section-header'>Masterclass Analytics Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Multi-Factor Correlation Matrix & Cause-and-Effect Analysis</div>", unsafe_allow_html=True)

        analytics_window = df_valid.tail(90).reset_index(drop=True)

        w_series     = get_num(3, analytics_window)
        cals_series  = get_num(1, analytics_window)
        steps_series = get_num(12, analytics_window)
        hyd_series   = get_num(24, analytics_window)
        prot_series  = get_num(16, analytics_window)
        carb_series  = get_num(17, analytics_window)
        fat_series   = get_num(18, analytics_window)
        alc_series   = get_num(19, analytics_window)
        rhr_series   = get_num(27, analytics_window)
        if not rhr_series.notna().any(): rhr_series = get_num(23, analytics_window)
        flights_series = get_num(26, analytics_window)

        weight_delta = w_series - w_series.shift(1)
        valid_mask   = weight_delta.notna()

        good_cal_mask = (cals_series <= 1633) & valid_mask
        bad_cal_mask  = (cals_series > 1633) & valid_mask
        avg_good_cal  = weight_delta[good_cal_mask].mean() if good_cal_mask.sum() > 0 else 0.0
        avg_bad_cal   = weight_delta[bad_cal_mask].mean() if bad_cal_mask.sum() > 0 else 0.0

        prot_green_mask = (prot_series >= 85) & valid_mask
        avg_prot_green  = weight_delta[prot_green_mask].mean() if prot_green_mask.sum() > 0 else 0.0

        corr_df = pd.DataFrame({
            'Scale Shift (lbs)': weight_delta,
            'Calories': cals_series,
            'Steps': steps_series,
            'Water (ml)': hyd_series,
            'Protein %': prot_series,
            'Carbs %': carb_series,
            'Fat %': fat_series,
            'Alcohol (kcal)': alc_series,
            'Resting HR': rhr_series,
            'Flights Climbed': flights_series
        }).dropna()

        if len(corr_df) > 5:
            corr_matrix = corr_df.corr()
            fig_corr = px.imshow(
                corr_matrix, text_auto=".2f", aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Expanded Telemetry Correlation Heatmap (Pearson r)"
            )
            fig_corr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
            st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>🔥</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>Caloric Efficiency Shift</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Days staying <b style='color:var(--text-primary);'>≤ 1,633 kcal</b> average a next-morning scale shift of 
                <span style='color: #30D158; font-weight: 800;'>{avg_good_cal:+.2f} lbs</span>. 
                Exceeding 1,633 kcal shifts the scale by <span style='color: #FF2D55; font-weight: 800;'>{avg_bad_cal:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>🥩</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>Protein RAG Compliance Effect</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Hitting <b>GREEN Protein (≥ 85% Target)</b> produces an average scale shift of 
                <span style='color: #30D158; font-weight: 800;'>{avg_prot_green:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 15 — Masterpiece Forecasting Engine
    # ══════════════════════════════════════════
    with tab15:
        st.markdown("<div class='section-header'>Masterpiece Forecast & Velocity Matrix</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Multi-Scenario Velocity Models & Stepping Stone ETAs to 170 lbs</div>", unsafe_allow_html=True)

        w_series = get_num(3).dropna()
        if len(w_series) >= 14:
            window = min(21, len(w_series))
            recent = w_series.tail(window).reset_index(drop=True)
            x = np.arange(len(recent))
            slope, _ = np.polyfit(x, recent.values, 1)
            current_rate_per_day = -slope
            current_rate_per_wk  = current_rate_per_day * 7.0
            current_w = w_series.iloc[-1]

            goal_w = 170.0
            lbs_left = current_w - goal_w

            days_current = int(lbs_left / current_rate_per_day) if current_rate_per_day > 0 else 999
            days_aggr    = int(lbs_left / (2.0 / 7.0))
            days_cons    = int(lbs_left / (1.0 / 7.0))

            eta_current = pd.Timestamp.now() + pd.Timedelta(days=days_current)
            eta_aggr    = pd.Timestamp.now() + pd.Timedelta(days=days_aggr)
            eta_cons    = pd.Timestamp.now() + pd.Timedelta(days=days_cons)

            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.markdown(f"""
                <div class='card' style='border-top: 4px solid #FF9F0A;'>
                    <div class='label'>Conservative Rate (1.0 lb/wk)</div>
                    <div class='val-sm' style='color:#FF9F0A;'>{eta_cons.strftime('%b %d, %Y')}</div>
                    <div style='font-size:0.8rem; color:var(--text-secondary); margin-top:6px;'>In {days_cons} days</div>
                </div>""", unsafe_allow_html=True)

            with fc2:
                st.markdown(f"""
                <div class='card' style='border-top: 4px solid #0A84FF; box-shadow: 0 12px 32px rgba(10,132,255,0.30);'>
                    <div class='label'>Current Velocity ({current_rate_per_wk:.1f} lbs/wk)</div>
                    <div class='val' style='color:#0A84FF;'>{eta_current.strftime('%b %d, %Y') if days_current < 999 else 'N/A'}</div>
                    <div style='font-size:0.85rem; color:#FFFFFF; font-weight:700; margin-top:6px;'>In {days_current if days_current < 999 else 'N/A'} days</div>
                </div>""", unsafe_allow_html=True)

            with fc3:
                st.markdown(f"""
                <div class='card' style='border-top: 4px solid #30D158;'>
                    <div class='label'>Aggressive Rate (2.0 lbs/wk)</div>
                    <div class='val-sm' style='color:#30D158;'>{eta_aggr.strftime('%b %d, %Y')}</div>
                    <div style='font-size:0.8rem; color:var(--text-secondary); margin-top:6px;'>In {days_aggr} days</div>
                </div>""", unsafe_allow_html=True)

            milestones = [190.0, 185.0, 180.0, 175.0, 170.0]
            m_rows = []
            for m in milestones:
                if current_w > m:
                    m_lbs = current_w - m
                    m_days = int(m_lbs / current_rate_per_day) if current_rate_per_day > 0 else 999
                    m_date = (pd.Timestamp.now() + pd.Timedelta(days=m_days)).strftime('%B %d, %Y') if m_days < 999 else 'N/A'
                    m_rows.append({'Milestone': f"{m:.0f} lbs ({lbs_to_stone(m)})", 'Distance': f"{m_lbs:.1f} lbs", 'Days Away': m_days, 'Projected Date': m_date})
                else:
                    m_rows.append({'Milestone': f"{m:.0f} lbs ({lbs_to_stone(m)})", 'Distance': "0.0 lbs", 'Days Away': 0, 'Projected Date': "ACHIEVED"})

            st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-sub'>Gateway Milestone Arrival Table</div>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(m_rows), use_container_width=True, hide_index=True)

            future_days = np.arange(0, days_current + 10)
            proj_weights = current_w - (future_days * current_rate_per_day)

            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=df.iloc[:, 0], y=w_series, name="Historical Weight", mode='lines', line=dict(color='#BF5AF2', width=2.5)))
            
            future_dates = [pd.Timestamp.now() + pd.Timedelta(days=int(d)) for d in future_days]
            fig_proj.add_trace(go.Scatter(x=future_dates, y=proj_weights, name="Projected Trajectory Path", mode='lines', line=dict(color='#0A84FF', width=3, dash='dash')))
            fig_proj.add_hline(y=170, line_dash="solid", line_color="#30D158", annotation_text="170 lbs Goal Line")
            st.plotly_chart(apply_theme(fig_proj, "Future Trajectory Path to 170 lbs Goal", "PROJECTED WEIGHT DECAY CURVE"), use_container_width=True)
        else:
            st.info("Requires at least 14 days of logged weight telemetry to calculate forecasting model.")

    # ══════════════════════════════════════════
    #  TAB 16 — Rolling 30-Day Momentum Score
    # ══════════════════════════════════════════
    with tab16:
        st.markdown("<div class='section-header'>Rolling 30-Day Momentum Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>30-Day Health Score — Calories + Steps + Water + Macro RAG</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='context-card'>
            <div class='context-title'>⚡ HOW YOUR MOMENTUM SCORE IS CALCULATED (0–100)</div>
            <div class='context-text'>
                Your daily score combines <b>4 equal biometrics (25 points each)</b>:<br>
                1. <b>Caloric Target (25 pts):</b> Full 25 pts for staying ≤ 1,633 kcal.<br>
                2. <b>Kinetic Activity (25 pts):</b> Full 25 pts for reaching ≥ 10,000 steps.<br>
                3. <b>Hydration Goal (25 pts):</b> Full 25 pts for drinking ≥ 5,000 ml water.<br>
                4. <b>Protein RAG Status (25 pts):</b> Full 25 pts for achieving ≥ 85% Protein target.<br><br>
                <b>WHAT GOOD LOOKS LIKE:</b><br>
                • <b style='color:#30D158;'>75 – 100 (Optimal Zone):</b> Continuous high-velocity fat loss.<br>
                • <b style='color:#FF9F0A;'>50 – 74 (Moderate Zone):</b> Steady maintenance or slow loss.<br>
                • <b style='color:#FF2D55;'>0 – 49 (Needs Focus):</b> At risk of plateau or weight bounce.
            </div>
        </div>
        """, unsafe_allow_html=True)

        momentum_30 = df_valid.tail(30).reset_index(drop=True)
        if len(momentum_30) >= 1:
            cal_m   = get_num(1, momentum_30).replace(0, np.nan)
            steps_m = get_num(12, momentum_30)
            hyd_m   = get_num(24, momentum_30)
            prot_m  = get_num(16, momentum_30)

            cal_score   = (1633 / cal_m).clip(upper=1).fillna(0) * 25.0
            step_score  = (steps_m / 10000).clip(upper=1).fillna(0) * 25.0
            hyd_score   = (hyd_m / 5000.0).clip(upper=1).fillna(0) * 25.0
            prot_score  = (prot_m / 85.0).clip(upper=1).fillna(0) * 25.0

            daily_score_30 = (cal_score + step_score + hyd_score + prot_score).round(0).clip(upper=100)

            def score_band(s):
                if s >= 75: return ("Optimal", "#30D158", "rgba(48,209,88,0.22)")
                elif s >= 50: return ("Moderate", "#FF9F0A", "rgba(255,159,10,0.22)")
                else: return ("Needs Focus", "#FF2D55", "rgba(255,45,85,0.20)")

            latest_score = safe(daily_score_30.iloc[-1])
            latest_label, latest_color, latest_fill = score_band(latest_score)

            good_days = daily_score_30 >= 75
            current_streak_30 = 0
            for v in good_days.tolist()[::-1]:
                if v: current_streak_30 += 1
                else: break

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Latest Score</div>
                    <div class='val' style='color:{latest_color};'>{latest_score:.0f}<span style='font-size:0.5em; opacity:0.6;'>/100</span></div>
                    <div class='delta' style='background:{latest_fill}; color:{latest_color}; border:1px solid {latest_color}55;'>{latest_label}</div>
                  </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(card("Current 30d Optimal Streak", display_val=f"{current_streak_30} {'day' if current_streak_30 == 1 else 'days'}"), unsafe_allow_html=True)
            with c3:
                st.markdown(card("30-Day Rolling Avg Score", num_target=daily_score_30.mean(), decimals=0), unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_hrect(y0=75, y1=100, fillcolor='rgba(48,209,88,0.08)', layer="below", line_width=0)
            fig.add_trace(go.Scatter(
                x=momentum_30.iloc[:, 0], y=daily_score_30, mode='lines+markers', name='Health Score',
                line=dict(color='#0A84FF', width=3),
                marker=dict(color='#0A84FF', size=7),
                fill='tozeroy', fillcolor='rgba(10,132,255,0.12)'
            ))
            fig.add_hline(y=75, line_dash="dash", line_color="#30D158", annotation_text="TARGET (75+)")
            fig.update_layout(yaxis=dict(range=[0, 100]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(255,255,255,0.03)'), type="date"))
            st.plotly_chart(apply_theme(fig, "Rolling 30-Day Momentum Trend", "COMPOSITE HEALTH MATRIX"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 17 — Raw Telemetry Log
    # ══════════════════════════════════════════
    with tab17:
        st.markdown("<div class='section-header'>Raw Telemetry Log</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Latest 30 Records</div>", unsafe_allow_html=True)

        display_df = df.copy()
        display_df[0] = display_df[0].dt.strftime('%Y-%m-%d')
        display_df = display_df.iloc[::-1].head(30)
        display_df.columns = [str(i) for i in range(len(display_df.columns))]

        cols_to_show = {
            '0': 'Date', '1': 'Calories', '3': 'Weight (lbs)', '4': 'Weight (St)',
            '12': 'Steps', '13': 'Miles', '16': 'Protein % Tgt', '17': 'Carbs % Tgt', '18': 'Fat % Tgt',
            '19': 'Alcohol (kcal)', '21': 'Systolic BP', '22': 'Diastolic BP', '26': 'Flights Climbed',
            '27': 'Resting HR', '28': 'Stand Hrs', '29': 'Exercise Mins', '24': 'Water (ml)'
        }

        existing_cols = [c for c in cols_to_show.keys() if c in display_df.columns]
        clean_df = display_df[existing_cols].rename(columns=cols_to_show)

        st.dataframe(clean_df, use_container_width=True, hide_index=True, height=450)

    # ─────────────────────────────────────────────
    #  JAVASCRIPT ODOMETER INJECTOR
    # ─────────────────────────────────────────────
    js_code = r"""
    <script>
    const docs = window.parent.document;

    function runOdometer() {
        const targets = Array.from(docs.querySelectorAll('.count-up')).filter(el => el.offsetParent !== null);

        targets.forEach(el => {
            if (el.animFrame) cancelAnimationFrame(el.animFrame);

            const target = parseFloat(el.getAttribute('data-target')) || 0;
            const decimals = parseInt(el.getAttribute('data-decimals')) || 0;
            const suffix = el.getAttribute('data-suffix') || '';
            const duration = 1200;
            const start = performance.now();

            function update(now) {
                const elapsed = now - start;
                const progress = Math.min(elapsed / duration, 1);
                const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
                const current = target * ease;

                let formatted = current.toFixed(decimals);
                let parts = formatted.split(".");
                parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                formatted = parts.join(".");

                let suffixHtml = suffix ? "<span style='font-size:0.65em; opacity:0.55; margin-left:4px;'>" + suffix + "</span>" : "";
                el.innerHTML = formatted + suffixHtml;

                if (progress < 1) {
                    el.animFrame = requestAnimationFrame(update);
                } else {
                    let finalFormatted = target.toFixed(decimals);
                    let p = finalFormatted.split(".");
                    p[0] = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                    el.innerHTML = p.join(".") + suffixHtml;
                }
            }
            el.animFrame = requestAnimationFrame(update);
        });
    }

    runOdometer();

    docs.body.addEventListener('click', function(e) {
        let target = e.target;
        while (target && target !== docs.body) {
            if (target.getAttribute('role') === 'tab' || target.getAttribute('data-baseweb') === 'tab') {
                setTimeout(runOdometer, 60);
                break;
            }
            target = target.parentNode;
        }
    });
    </script>
    """
    components.html(js_code, height=0, width=0)

else:
    st.error("Data link severed. Please verify Google Sheet credentials and URL.")
