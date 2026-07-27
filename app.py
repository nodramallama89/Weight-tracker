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
    page_title="Hardy House Health — World-Class Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Boot Sequence ──
if 'booted' not in st.session_state:
    st.toast('Masterclass Health Engine Active.', icon='✅')
    time.sleep(0.4)
    st.toast('TDEE Engine & Biometric Matrix Online.', icon='💚')
    st.session_state.booted = True

# ─────────────────────────────────────────────
#  PREMIUM GLASSMORPHISM CSS (Apple / Samsung Health Aesthetics)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
  --bg-app:          #F2F2F7;
  --bg-card:         rgba(255, 255, 255, 0.78);
  --bg-card-hover:   rgba(255, 255, 255, 0.92);
  --glass-border:    rgba(255, 255, 255, 0.75);
  --glass-blur:      blur(30px) saturate(200%);
  --glass-blur-sm:   blur(18px) saturate(170%);

  --shadow-card:       0 2px 10px rgba(15,23,42,0.04), 0 18px 40px rgba(15,23,42,0.09);
  --shadow-card-hover: 0 8px 24px rgba(15,23,42,0.08), 0 30px 64px rgba(15,23,42,0.15);

  --text-primary:   #1D1D1F;
  --text-secondary: rgba(60,60,67,0.72);
  --text-tertiary:  rgba(60,60,67,0.45);

  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  --font-body:    'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;

  /* RAG & Accents */
  --red:    #FF375F;
  --amber:  #FF9F0A;
  --green:  #30D158;
  --teal:   #64D2FF;
  --blue:   #0A84FF;
  --purple: #BF5AF2;

  --radius-xl: 22px;
  --radius-lg: 16px;
  --radius-md: 12px;
}

*, *::before, *::after { box-sizing: border-box; }

.stApp {
  background-image:
    linear-gradient(180deg, rgba(242,242,247,0.50) 0%, rgba(242,242,247,0.82) 50%, rgba(242,242,247,0.95) 100%),
    url('https://github.com/nodramallama89/Weight-tracker/blob/33fc966fe489b029049541e417658a7441afa776/Gemini_Generated_Image_1zukku1zukku1zuk.png?raw=true');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: var(--font-body);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1680px; }

/* ── Typography ── */
.page-eyebrow {
  font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--text-tertiary); text-align: center;
  display: block; margin-bottom: 0.3rem; animation: fadeUp 0.5s ease both;
}
.page-eyebrow .status-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background-color: var(--green); margin-right: 7px;
  box-shadow: 0 0 0 4px rgba(48,209,88,0.25);
}

.page-title {
  font-family: var(--font-display) !important; font-size: 2.8rem !important;
  font-weight: 900 !important; letter-spacing: -0.03em !important;
  color: var(--text-primary) !important; text-align: center !important;
  margin: 0 0 0.2rem !important; animation: fadeUp 0.6s ease 0.05s both;
  text-shadow: 0 2px 14px rgba(255,255,255,0.8);
}

.page-subtitle {
  font-size: 0.95rem; color: var(--text-secondary); text-align: center;
  margin-bottom: 1.8rem; font-weight: 600; animation: fadeUp 0.7s ease 0.1s both;
}

/* ── Cards ── */
.card {
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl); padding: 22px 20px 20px;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.8);
  border: 1px solid var(--glass-border); text-align: center; margin-bottom: 14px;
  position: relative; overflow: hidden;
  transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1);
  animation: springUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.card:hover {
  transform: translateY(-4px); box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,0.9);
  border-color: rgba(255,255,255,0.95); background: var(--bg-card-hover);
}

.val { font-family: var(--font-display); font-size: 2.25rem; font-weight: 800; margin: 4px 0; line-height: 1; color: var(--text-primary); letter-spacing: -0.02em; }
.val-sm { font-family: var(--font-display); font-size: 1.55rem; font-weight: 800; margin: 4px 0; line-height: 1; color: var(--text-primary); letter-spacing: -0.01em; }
.label { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em; color: var(--text-tertiary); }

.delta { font-size: 0.78rem; font-weight: 700; margin-top: 10px; padding: 5px 13px; border-radius: 50px; display: inline-block; box-shadow: 0 2px 8px rgba(15,23,42,0.06); }
.delta-pos { background: rgba(48, 209, 88, 0.16); color: #1E9145; border: 1px solid rgba(48, 209, 88, 0.3); }
.delta-neg { background: rgba(255, 55, 95, 0.14); color: #E0264F; border: 1px solid rgba(255, 55, 95, 0.28); }

/* ── RAG Macro Badges ── */
.rag-badge {
  display: inline-block; font-size: 0.72rem; font-weight: 800; text-transform: uppercase;
  padding: 4px 10px; border-radius: 20px; margin-top: 6px; letter-spacing: 0.06em;
}
.rag-green { background: rgba(48, 209, 88, 0.18); color: #198038; border: 1px solid rgba(48, 209, 88, 0.35); }
.rag-amber { background: rgba(255, 159, 10, 0.18); color: #C67200; border: 1px solid rgba(255, 159, 10, 0.35); }
.rag-red   { background: rgba(255, 55, 95, 0.16); color: #D01144; border: 1px solid rgba(255, 55, 95, 0.35); }

/* ── Top Insights Box ── */
.insights-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl); padding: 22px 28px;
  border: 1px solid var(--glass-border); box-shadow: var(--shadow-card);
  margin-bottom: 20px; text-align: left;
}
.insights-title {
  font-family: var(--font-display); font-size: 0.82rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--blue); margin-bottom: 12px;
}
.insight-item {
  font-size: 0.95rem; color: var(--text-primary); font-weight: 500;
  margin-bottom: 8px; line-height: 1.5; display: flex; align-items: flex-start; gap: 8px;
}

/* ── Status Modifiers ── */
.debuff-container { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 8px; }
.debuff-badge {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
  border-radius: 20px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em;
  backdrop-filter: var(--glass-blur-sm); box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.debuff-warning { background: rgba(255, 55, 95, 0.14); color: #D01144; border: 1px solid rgba(255, 55, 95, 0.3); }
.debuff-caution { background: rgba(255, 159, 10, 0.16); color: #C67200; border: 1px solid rgba(255, 159, 10, 0.3); }
.debuff-optimal { background: rgba(48, 209, 88, 0.16); color: #198038; border: 1px solid rgba(48, 209, 88, 0.3); }

.section-header { font-family: var(--font-display); font-size: 1.65rem; font-weight: 800; color: var(--text-primary); margin: 0 0 0.3rem; text-align: center; letter-spacing: -0.01em; text-shadow: 0 1px 12px rgba(255,255,255,0.6); }
.section-sub { font-size: 0.8rem; color: var(--text-tertiary); text-align: center; margin-top: 0; margin-bottom: 1.6rem; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 700; }

/* ── Tab Bar ── */
div[data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.55) !important; backdrop-filter: var(--glass-blur-sm) !important;
  -webkit-backdrop-filter: var(--glass-blur-sm) !important; border-radius: 16px !important;
  padding: 5px !important; border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card) !important; margin-bottom: 1.8rem !important; flex-wrap: wrap !important; gap: 2px;
}
div[data-baseweb="tab"] { border-radius: 11px !important; transition: all 0.25s ease !important; }
div[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.35) !important; }
div[data-baseweb="tab"][aria-selected="true"] { background: rgba(255,255,255,0.95) !important; box-shadow: 0 2px 8px rgba(15,23,42,0.12) !important; }
div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { color: var(--text-secondary) !important; font-size: 0.88rem !important; font-weight: 600 !important; }
div[data-baseweb="tab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; font-weight: 800 !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }

/* ── Plotly Containers ── */
.stPlotlyChart {
  background: var(--bg-card) !important; backdrop-filter: var(--glass-blur) !important;
  -webkit-backdrop-filter: var(--glass-blur) !important; border-radius: var(--radius-xl) !important;
  padding: 16px !important; border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.8) !important;
  transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stPlotlyChart:hover { box-shadow: var(--shadow-card-hover) !important; }

@keyframes springUpFade { 0% { opacity: 0; transform: translateY(18px); } 100% { opacity: 1; transform: translateY(0); } }
@keyframes fadeUp { 0% { opacity: 0; transform: translateY(10px); } 100% { opacity: 1; transform: translateY(0); } }

[data-testid="stDataFrame"] {
  background: var(--bg-card); backdrop-filter: var(--glass-blur-sm);
  border-radius: var(--radius-lg); border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card); padding: 8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME & GAUGE GENERATORS
# ─────────────────────────────────────────────
def apply_theme(fig, title="", subtitle=""):
    full_title = f"<b>{title}</b>" + (f"<br><span style='font-size:12px;color:rgba(60,60,67,0.55);font-family:Inter'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(family="Inter, sans-serif", color='#1D1D1F', size=19), x=0.03, xanchor='left', y=0.96),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color='rgba(60,60,67,0.75)', size=12),
        legend=dict(font=dict(color='#1D1D1F', size=11), bgcolor='rgba(255,255,255,0.85)', bordercolor='rgba(60,60,67,0.12)', borderwidth=1, x=0.01, y=0.99, orientation='h'),
        xaxis=dict(
            color='rgba(60,60,67,0.55)', gridcolor='rgba(60,60,67,0.07)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.5)",
            showgrid=True, zeroline=False
        ),
        yaxis=dict(
            color='rgba(60,60,67,0.55)', gridcolor='rgba(60,60,67,0.07)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.5)",
            zeroline=False
        ),
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(255,255,255,0.98)', bordercolor='#0A84FF', font=dict(color='#1D1D1F', size=13, family='Inter, sans-serif')),
    )
    return fig

def make_semi_gauge(val, title, min_v, max_v, green_range, amber_range, red_range, unit=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={'suffix': f" {unit}", 'font': {'size': 26, 'color': '#1D1D1F', 'family': 'Inter'}},
        title={'text': title, 'font': {'size': 14, 'color': 'rgba(60,60,67,0.7)', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': "rgba(60,60,67,0.3)"},
            'bar': {'color': "#1D1D1F", 'thickness': 0.25},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': green_range, 'color': 'rgba(48,209,88,0.75)'},
                {'range': amber_range, 'color': 'rgba(255,159,10,0.75)'},
                {'range': red_range, 'color': 'rgba(255,55,95,0.75)'}
            ]
        }
    ))
    fig.update_layout(height=210, margin=dict(l=15, r=15, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig


# ─────────────────────────────────────────────
#  DATA PIPELINE
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    """
    Column Schema (0 to 24):
    0: Date                 10: BMI             20: Notes
    1: Calories consumed    11: To target BMI   21: Systolic BP
    2: Net calories         12: Steps           22: Diastolic BP
    3: Weight (lbs)         13: Approx miles    23: Heart Rate (HR)
    4: Weight (St)          14: Activity time   24: Water (ml)
    5: Gain/Loss            15: Activity cals
    6: Total loss (lbs)     16: Protein (% Tgt)
    7: Total loss (St)      17: Net Carbs (% Tgt)
    8: To tgt (lbs)         18: Fat (% Tgt)
    9: To tgt (St)          19: Alcohol (kcal)
    """
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

# Filter completed rows (Steps Col 12 non-blank)
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
    """
    RAG Rules for Macro % of Target:
    - Protein: <60% RED, 60-85% AMBER, 85%+ GREEN
    - Net Carbs: <90% GREEN, 90-110% AMBER, >110% RED
    - Fat: <90% GREEN, 90-110% AMBER, >110% RED
    """
    v = safe(val_pct)
    if macro_type == 'protein':
        if v < 60.0:
            return "RED", "#FF375F", "rag-red", "Under Target (<60%)"
        elif v <= 85.0:
            return "AMBER", "#FF9F0A", "rag-amber", "Moderate (60–85%)"
        else:
            return "GREEN", "#30D158", "rag-green", "Optimal (85%+)"
    else: # carbs or fat
        if v < 90.0:
            return "GREEN", "#30D158", "rag-green", "Optimal (<90%)"
        elif v <= 110.0:
            return "AMBER", "#FF9F0A", "rag-amber", "Moderate (90–110%)"
        else:
            return "RED", "#FF375F", "rag-red", "Excess (>110%)"

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
    
    # Alcohol (Col 19 kcal)
    alc_kcal = clean_float(row_data.iloc[19]) if len(row_data) > 19 else 0.0
    if alc_kcal > 0:
        badges.append(f"<div class='debuff-badge debuff-warning'>🍷 Alcohol Active (+{alc_kcal:,.0f} kcal) — Sleep & Recovery Suppressed</div>")
    
    # Calories (Col 1)
    cals = clean_float(row_data.iloc[1]) if len(row_data) > 1 else 0.0
    if cals > 1633:
        badges.append(f"<div class='debuff-badge debuff-caution'>🔥 Caloric Surplus (+{cals - 1633:,.0f} kcal over target)</div>")
    elif 0 < cals <= 1633:
        badges.append("<div class='debuff-badge debuff-optimal'>🔥 Caloric Target Hit (≤ 1,633 kcal)</div>")

    # Steps (Col 12)
    steps = clean_float(row_data.iloc[12]) if len(row_data) > 12 else 0.0
    if steps >= 10000:
        badges.append(f"<div class='debuff-badge debuff-optimal'>👟 Kinetic Goal Hit ({steps:,.0f} Steps)</div>")
    elif steps < 8000:
        badges.append(f"<div class='debuff-badge debuff-caution'>👟 Low Activity ({steps:,.0f} Steps)</div>")

    # Water (Col 24)
    water_ml = clean_float(row_data.iloc[24]) if len(row_data) > 24 else 0.0
    if water_ml >= 3000:
        badges.append(f"<div class='debuff-badge debuff-optimal'>💧 Hydration Optimal ({water_ml:,.0f} ml)</div>")
    elif 0 < water_ml < 3000:
        badges.append(f"<div class='debuff-badge debuff-caution'>💧 Hydration Under Target ({water_ml:,.0f} / 3,000 ml)</div>")

    # Macro RAG
    p_pct = clean_float(row_data.iloc[16]) if len(row_data) > 16 else 0.0
    c_pct = clean_float(row_data.iloc[17]) if len(row_data) > 17 else 0.0
    f_pct = clean_float(row_data.iloc[18]) if len(row_data) > 18 else 0.0
    
    p_rag, _, _, _ = eval_macro_rag(p_pct, 'protein')
    c_rag, _, _, _ = eval_macro_rag(c_pct, 'carbs')
    f_rag, _, _, _ = eval_macro_rag(f_pct, 'fat')

    if p_rag == "RED":
        badges.append("<div class='debuff-badge debuff-warning'>🥩 Protein Deficit (<60% Target)</div>")
    if c_rag == "RED":
        badges.append("<div class='debuff-badge debuff-warning'>🍞 Excess Net Carbs (>110% Target)</div>")
    if f_rag == "RED":
        badges.append("<div class='debuff-badge debuff-warning'>🥑 Excess Dietary Fat (>110% Target)</div>")

    if not badges:
        badges.append("<div class='debuff-badge debuff-optimal'>🛡️ All Telemetry Nominal</div>")

    return f"<div class='debuff-container'>{''.join(badges)}</div>"


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
if not df.empty:

    # ── Top Header ──
    st.markdown("""
    <span class='page-eyebrow'><span class='status-dot'></span>MASTERCLASS HEALTH TELEMETRY ENGINE</span>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='page-title'>Hardy House Health</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>World-Class Biometric Intelligence & Multi-Factor Performance Matrix</div>", unsafe_allow_html=True)

    # ── 19 Expanded Tabs ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17, tab18, tab19 = st.tabs([
        "🛡️ Command", "🧬 Metabolic", "🫀 Cardio", "📊 Lifetime", "🔥 Calories",
        "💧 Hydration", "⚖️ Weight", "📉 Variance", "👟 Steps", "🥗 Macro RAG",
        "📅 Patterns", "📈 Averages", "🎯 Milestone", "🏆 Trophies", "🧠 Analytics",
        "📋 Sit Rep", "🔮 Forecast", "⚡ Momentum", "🗄️ Data Log"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Command Center
    # ══════════════════════════════════════════
    with tab1:
        completed = df_valid
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "LATEST_DATA"
            cals  = clean_float(y.iloc[1])
            steps = clean_float(y.iloc[12])

            # ── TOP INSIGHTS ENGINE ──
            last_14 = completed.tail(14)
            cals_14 = pd.to_numeric(last_14.iloc[:, 1], errors='coerce')
            p_14    = pd.to_numeric(last_14.iloc[:, 16], errors='coerce')
            w_14    = pd.to_numeric(last_14.iloc[:, 24], errors='coerce')

            p_green_cnt = (p_14 >= 85).sum()
            cal_hit_cnt = (cals_14 <= 1633).sum()
            water_hit_cnt = (w_14 >= 3000).sum()

            st.markdown(f"""
            <div class='insights-card'>
                <div class='insights-title'>⚡ AUTOMATED BIOMETRIC INSIGHTS ({date_str})</div>
                <div class='insight-item'>• <b>Caloric Adherence:</b> Reached calorie goal (≤1,633 kcal) on <b>{cal_hit_cnt} of the last 14 days</b> ({(cal_hit_cnt/14*100):.0f}% compliance).</div>
                <div class='insight-item'>• <b>Protein RAG Status:</b> Achieved <b>GREEN Protein status (≥85% Target)</b> on <b>{p_green_cnt} of the last 14 days</b>.</div>
                <div class='insight-item'>• <b>Hydration Performance:</b> Hit target 3,000 ml water volume on <b>{water_hit_cnt} of the last 14 days</b>.</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='section-header'>Yesterday's Debrief</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>{date_str}</div>", unsafe_allow_html=True)

            # Primary KPI Cards
            c1, c2 = st.columns(2)
            cal_delta  = cals  - 1633
            step_delta = steps - 10000
            with c1:
                cal_arrow    = "▲" if cal_delta > 0 else "▼"
                cal_pill_cls = "delta-neg" if cal_delta > 0 else "delta-pos"
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Calories Consumed</div>
                    <div class='val count-up' data-target='{cals}' data-decimals='0' data-suffix=' kcal'>{fmt_num(cals, 0, ' kcal')}</div>
                    <div class='delta {cal_pill_cls}'>{cal_arrow} {abs(cal_delta):,.0f} vs Target</div>
                  </div>""", unsafe_allow_html=True)
            with c2:
                step_arrow    = "▲" if step_delta >= 0 else "▼"
                step_pill_cls = "delta-pos" if step_delta >= 0 else "delta-neg"
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Steps Taken</div>
                    <div class='val count-up' data-target='{steps}' data-decimals='0' data-suffix=''>{fmt_num(steps, 0, '')}</div>
                    <div class='delta {step_pill_cls}'>{step_arrow} {abs(step_delta):,.0f} vs Target</div>
                  </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

            # RAG Macro Grid (% Target) + Alcohol (kcal)
            m1, m2, m3, m4 = st.columns(4)
            
            # Protein (% Target)
            prot_pct = clean_float(y.iloc[16]) if len(y) > 16 else 0.0
            p_rag, p_color, p_badge_cls, p_desc = eval_macro_rag(prot_pct, 'protein')
            m1.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {p_color};'>
                <div class='label'>Protein (% Target)</div>
                <div class='val-sm count-up' data-target='{prot_pct}' data-decimals='1' data-suffix='%'>{fmt_num(prot_pct, 1, '%')}</div>
                <div class='rag-badge {p_badge_cls}'>{p_rag}: {p_desc}</div>
              </div>""", unsafe_allow_html=True)

            # Net Carbs (% Target)
            carbs_pct = clean_float(y.iloc[17]) if len(y) > 17 else 0.0
            c_rag, c_color, c_badge_cls, c_desc = eval_macro_rag(carbs_pct, 'carbs')
            m2.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {c_color};'>
                <div class='label'>Net Carbs (% Target)</div>
                <div class='val-sm count-up' data-target='{carbs_pct}' data-decimals='1' data-suffix='%'>{fmt_num(carbs_pct, 1, '%')}</div>
                <div class='rag-badge {c_badge_cls}'>{c_rag}: {c_desc}</div>
              </div>""", unsafe_allow_html=True)

            # Fat (% Target)
            fat_pct = clean_float(y.iloc[18]) if len(y) > 18 else 0.0
            f_rag, f_color, f_badge_cls, f_desc = eval_macro_rag(fat_pct, 'fat')
            m3.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {f_color};'>
                <div class='label'>Fat (% Target)</div>
                <div class='val-sm count-up' data-target='{fat_pct}' data-decimals='1' data-suffix='%'>{fmt_num(fat_pct, 1, '%')}</div>
                <div class='rag-badge {f_badge_cls}'>{f_rag}: {f_desc}</div>
              </div>""", unsafe_allow_html=True)

            # Alcohol (kcal)
            alc_kcal = clean_float(y.iloc[19]) if len(y) > 19 else 0.0
            alc_border = "#30D158" if alc_kcal == 0 else "#BF5AF2"
            m4.markdown(f"""
              <div class='card' style='border-bottom: 4px solid {alc_border};'>
                <div class='label'>Alcohol Intake</div>
                <div class='val-sm count-up' data-target='{alc_kcal}' data-decimals='0' data-suffix=' kcal'>{fmt_num(alc_kcal, 0, ' kcal')}</div>
                <div class='rag-badge {"rag-green" if alc_kcal==0 else "rag-red"}'>{"ZERO" if alc_kcal==0 else "ACTIVE"}</div>
              </div>""", unsafe_allow_html=True)

            # Radial Gauge Cluster
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-sub'>Vitals & Pulse Dial Gauge Cluster</div>", unsafe_allow_html=True)
            
            sys_val = clean_float(y.iloc[21]) if len(y) > 21 and clean_float(y.iloc[21]) > 0 else 118.0
            dia_val = clean_float(y.iloc[22]) if len(y) > 22 and clean_float(y.iloc[22]) > 0 else 78.0
            hr_val  = clean_float(y.iloc[23]) if len(y) > 23 and clean_float(y.iloc[23]) > 0 else 72.0

            g1, g2, g3 = st.columns(3)
            with g1:
                st.plotly_chart(make_semi_gauge(sys_val, "Systolic BP", 80, 180, [80, 120], [120, 140], [140, 180], "mmHg"), use_container_width=True)
            with g2:
                st.plotly_chart(make_semi_gauge(dia_val, "Diastolic BP", 50, 120, [50, 80], [80, 90], [90, 120], "mmHg"), use_container_width=True)
            with g3:
                st.plotly_chart(make_semi_gauge(hr_val, "Resting HR", 40, 130, [40, 75], [75, 90], [90, 130], "BPM"), use_container_width=True)

            st.markdown(evaluate_debuffs(y), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — 🧬 Metabolic Intelligence & Dynamic TDEE
    # ══════════════════════════════════════════
    with tab2:
        st.markdown("<div class='section-header'>Metabolic Intelligence Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Dynamic TDEE Re-estimation & True Fat Mass Loss Vector</div>", unsafe_allow_html=True)

        w_series = get_num(3, df_valid).dropna()
        cals_series = get_num(1, df_valid).dropna()

        if len(w_series) >= 14:
            # 14-day & 30-day TDEE Re-estimation
            w_14_start = w_series.iloc[-14]
            w_14_end   = w_series.iloc[-1]
            w_14_drop  = w_14_start - w_14_end # lbs lost in 14 days
            avg_cals_14 = cals_series.tail(14).mean()

            # 3500 kcal per lb of weight
            est_tdee_14 = avg_cals_14 + (w_14_drop * 3500.0 / 14.0)

            w_30_start = w_series.iloc[-30] if len(w_series) >= 30 else w_series.iloc[0]
            w_30_days  = 30 if len(w_series) >= 30 else len(w_series)
            w_30_drop  = w_30_start - w_14_end
            avg_cals_30 = cals_series.tail(w_30_days).mean()
            est_tdee_30 = avg_cals_30 + (w_30_drop * 3500.0 / float(w_30_days))

            # Cumulative Caloric Deficit
            cum_deficit = (est_tdee_30 - cals_series.tail(w_30_days)).sum()
            calc_fat_lost_lbs = cum_deficit / 3500.0

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.markdown(card("14-Day Dynamic TDEE", num_target=est_tdee_14, decimals=0, suffix=" kcal/day"), unsafe_allow_html=True)
            with mc2:
                st.markdown(card("30-Day Dynamic TDEE", num_target=est_tdee_30, decimals=0, suffix=" kcal/day"), unsafe_allow_html=True)
            with mc3:
                st.markdown(card("Estimated True Fat Loss (30d)", num_target=calc_fat_lost_lbs, decimals=1, suffix=" lbs"), unsafe_allow_html=True)

            # TDEE vs Intake Chart
            dates_tdee = df_valid.iloc[-w_30_days:, 0]
            fig_t = go.Figure()
            fig_t.add_trace(go.Bar(x=dates_tdee, y=cals_series.tail(w_30_days), name="Actual Calories In", marker_color='rgba(10,132,255,0.7)'))
            fig_t.add_hline(y=est_tdee_30, line_dash="dash", line_color="#FF375F", annotation_text=f"Estimated TDEE ({est_tdee_30:.0f} kcal)", annotation_font_color="#FF375F")
            st.plotly_chart(apply_theme(fig_t, "Daily Intake vs Re-calculated TDEE Baseline", "DYNAMIC METABOLIC BURNS"), use_container_width=True)
        else:
            st.info("Requires at least 14 days of logged weight & calories to calculate dynamic TDEE.")

    # ══════════════════════════════════════════
    #  TAB 3 — 🫀 Biological Cardio Age & Vitals
    # ══════════════════════════════════════════
    with tab3:
        st.markdown("<div class='section-header'>Cardiovascular Matrix</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Hemodynamic Health, Pulse Pressure & Mean Arterial Pressure (MAP)</div>", unsafe_allow_html=True)

        sys_data = get_num(21)
        dia_data = get_num(22)
        hr_data  = get_num(23)

        last_sys = sys_data.dropna().iloc[-1] if sys_data.dropna().shape[0] > 0 else 120.0
        last_dia = dia_data.dropna().iloc[-1] if dia_data.dropna().shape[0] > 0 else 80.0
        pulse_pressure = last_sys - last_dia
        map_val = last_dia + (pulse_pressure / 3.0)

        vc1, vc2, vc3 = st.columns(3)
        with vc1:
            st.markdown(card("Pulse Pressure (Sys - Dia)", num_target=pulse_pressure, decimals=0, suffix=" mmHg"), unsafe_allow_html=True)
        with vc2:
            st.markdown(card("Mean Arterial Pressure (MAP)", num_target=map_val, decimals=1, suffix=" mmHg"), unsafe_allow_html=True)
        with vc3:
            st.markdown(card("Avg Resting Heart Rate", num_target=hr_data.dropna().mean() if hr_data.dropna().shape[0]>0 else 72, decimals=0, suffix=" BPM"), unsafe_allow_html=True)

        fig_cardio = go.Figure()
        fig_cardio.add_trace(go.Scatter(x=df.iloc[:, 0], y=sys_data, name="Systolic BP", mode='lines+markers', line=dict(color='#FF375F', width=2.5)))
        fig_cardio.add_trace(go.Scatter(x=df.iloc[:, 0], y=dia_data, name="Diastolic BP", mode='lines+markers', line=dict(color='#0A84FF', width=2.5)))
        if hr_data.notna().any():
            fig_cardio.add_trace(go.Scatter(x=df.iloc[:, 0], y=hr_data, name="Resting HR (BPM)", mode='lines', line=dict(color='#BF5AF2', width=2, dash='dot')))
        st.plotly_chart(apply_theme(fig_cardio, "Blood Pressure & Heart Rate Trends", "HEMODYNAMIC PROFILING"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 4 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab4:
        l = df.iloc[-1]
        st.markdown("<div class='section-header'>Lifetime Stats</div>", unsafe_allow_html=True)

        st.markdown(f"""
          <div class='card' style='background:linear-gradient(135deg,#0A84FF 0%,#30D158 130%);
               border: none; margin-bottom:1.5rem; box-shadow: 0 10px 30px rgba(10,132,255,0.28);'>
            <div class='label' style='color:rgba(255,255,255,0.85); font-size:0.78rem; letter-spacing:0.1em;'>ACTIVE STREAK</div>
            <div class='count-up' data-target='{len(df)}' data-decimals='0' style='font-family:Inter,sans-serif; font-size:4.2rem; font-weight:800;
                        color:#ffffff; margin:8px 0; line-height:1; letter-spacing:-0.02em;'>{fmt_num(len(df), 0, '')}</div>
            <div style='font-family:Inter,sans-serif; font-size:0.85rem; color:rgba(255,255,255,0.9); font-weight:600;'>CONSECUTIVE DAYS LOGGED</div>
          </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Total Loss (lbs)", num_target=clean_float(l.iloc[6]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Total Loss (Stone)", display_val=f"{l.iloc[7]}"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("To Target (lbs)", num_target=clean_float(l.iloc[8]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("To Target (Stone)", display_val=f"{l.iloc[9]}"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Current BMI", num_target=clean_float(l.iloc[10]), decimals=1), unsafe_allow_html=True)
            st.markdown(card("To Target BMI", num_target=clean_float(l.iloc[11]), decimals=1), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 5 — Calories
    # ══════════════════════════════════════════
    with tab5:
        cal_series = get_num(1)
        cal_min = float(cal_series.min()) if cal_series.notna().any() else 0
        cal_max = float(cal_series.max()) if cal_series.notna().any() else 2000
        cal_range = cal_max - cal_min if cal_max != cal_min else 1

        def norm(v): return max(0.0, min(1.0, (v - cal_min) / cal_range))
        colorscale = [[0.0, '#2FA84F'], [norm(1633), '#30D158'], [norm(1634), '#FF9F0A'], [norm(1700), '#FF7A1A'], [norm(1701), '#FF375F'], [1.0, '#D01144']]
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
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(2), name="Net Calories", mode='lines', line=dict(color='#1D1D1F', width=2.5, dash='dot')))
        fig.add_hline(y=1633, line_dash="dash", line_color="#30D158", annotation_text="Target 1,633", annotation_font_color="#1E9145")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
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
        hyd_series = get_num(24)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=hyd_series, name="Hydration (ml)",
            marker=dict(color=hyd_series, colorscale=[[0, '#0A84FF'], [1, '#64D2FF']], line=dict(width=1, color='rgba(255,255,255,0.6)')),
        ))
        fig.add_hline(y=3000, line_dash="dash", line_color="#0A84FF", annotation_text="3,000 ml TARGET", annotation_font_color="#0A84FF")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Hydration Volume", "TARGET: 3,000 ML"), use_container_width=True)

        st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
        hyd_logged = hyd_series.dropna()
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown(card("7-Day Avg Water", num_target=hyd_logged.tail(7).mean(), decimals=0, suffix=" ml"), unsafe_allow_html=True)
        with hc2:
            st.markdown(card("30-Day Avg Water", num_target=hyd_logged.tail(30).mean(), decimals=0, suffix=" ml"), unsafe_allow_html=True)
        with hc3:
            st.markdown(card("90-Day Avg Water", num_target=hyd_logged.tail(90).mean(), decimals=0, suffix=" ml"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 7 — Weight Trajectory (Smoothing Engine)
    # ══════════════════════════════════════════
    with tab7:
        w_series = get_num(3).dropna()
        dates_w  = df.iloc[:len(w_series), 0]
        w_ema    = w_series.ewm(span=7, adjust=False).mean()
        w_max    = float(w_series.max()) + 2 if not w_series.empty else 210

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates_w, y=w_series, name="Raw Daily Scale Weight", mode='markers+lines',
            line=dict(color='rgba(191,90,242,0.4)', width=1.5, dash='dot'),
            marker=dict(color='#BF5AF2', size=6, opacity=0.8), zorder=2
        ))
        fig.add_trace(go.Scatter(
            x=dates_w, y=w_ema, name="7-Day Trend EMA (Happy Scale)", mode='lines',
            line=dict(color='#0A84FF', width=3.5), zorder=3
        ))
        fig.add_hline(y=170, line_dash="dash", line_color="#30D158", annotation_text="🎯 GOAL: 170 lbs (12 st 2 lbs)", annotation_font_color="#1E9145", annotation_position="top left")

        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory & Trend Smoothing", "RAW SCALE ACTUALS VS 7-DAY EXPONENTIAL MOVING AVERAGE"), use_container_width=True)

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
    #  TAB 8 — Scale Variance
    # ══════════════════════════════════════════
    with tab8:
        trend = get_num(5) # Col 5
        colors_trend = ['#30D158' if v <= 0 else '#FF375F' for v in trend.fillna(0)]

        fig = go.Figure()
        fig.add_hrect(y0=-5, y1=0, fillcolor='rgba(48,209,88,0.06)', layer="below", line_width=0)
        fig.add_hrect(y0=0,  y1=5, fillcolor='rgba(255,55,95,0.06)', layer="below", line_width=0)
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=trend, mode='lines+markers',
            line=dict(color='#FF9F0A', width=2),
            marker=dict(color=colors_trend, size=7, symbol='circle', line=dict(color='#ffffff', width=1.5)),
            name="Net Trend", fill='tozeroy', fillcolor='rgba(255,159,10,0.10)',
        ))
        fig.add_hline(y=0, line_dash="solid", line_color="#1D1D1F", line_width=1.5)
        fig.update_layout(yaxis=dict(range=[-5, 5]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Scale Variance", "RANGE ±5 LBS DELTA"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 9 — Steps
    # ══════════════════════════════════════════
    with tab9:
        steps_data  = get_num(12)
        def step_color(s):
            if s >= 10000: return '#30D158'
            elif s >= 8001: return '#FF9F0A'
            else: return '#FF375F'
        step_colors = [step_color(s) for s in steps_data.fillna(0)]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=steps_data, name="Steps",
            marker=dict(color=step_colors, line=dict(width=1, color='rgba(255,255,255,0.6)')),
        ))
        fig.add_hline(y=10000, line_dash="dash", line_color="#30D158", annotation_text="10K TARGET", annotation_font_color="#1E9145")
        fig.add_hline(y=8000, line_dash="dot", line_color="#FF375F", annotation_text="8K FLOOR", annotation_font_color="#E0264F")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Step Volume", "STATUS: TRACKING"), use_container_width=True)

        st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
        steps_logged = steps_data.dropna()
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(card("7-Day Avg", num_target=steps_logged.tail(7).mean(), decimals=0), unsafe_allow_html=True)
        with sc2:
            st.markdown(card("30-Day Avg", num_target=steps_logged.tail(30).mean(), decimals=0), unsafe_allow_html=True)
        with sc3:
            st.markdown(card("90-Day Avg", num_target=steps_logged.tail(90).mean(), decimals=0), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 10 — RAG Macro Matrix
    # ══════════════════════════════════════════
    with tab10:
        st.markdown("<div class='section-header'>RAG Macro Performance Matrix</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Proportional Target Adherence (% Target) over Time</div>", unsafe_allow_html=True)

        p_pcts = get_num(16)
        c_pcts = get_num(17)
        f_pcts = get_num(18)

        fig_m = go.Figure()
        fig_m.add_trace(go.Scatter(x=df.iloc[:, 0], y=p_pcts, name="Protein (% Target)", mode='lines', line=dict(color='#FF375F', width=2.5)))
        fig_m.add_trace(go.Scatter(x=df.iloc[:, 0], y=c_pcts, name="Net Carbs (% Target)", mode='lines', line=dict(color='#0A84FF', width=2.5)))
        fig_m.add_trace(go.Scatter(x=df.iloc[:, 0], y=f_pcts, name="Fat (% Target)", mode='lines', line=dict(color='#FFD60A', width=2.5)))

        fig_m.add_hline(y=85.0, line_dash="dash", line_color="#30D158", annotation_text="Protein Green Floor (85%)")
        fig_m.add_hline(y=110.0, line_dash="dash", line_color="#FF375F", annotation_text="Carb/Fat Red Ceiling (110%)")

        fig_m.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig_m, "Macro Target Compliance (% Target)", "RAG COMPLIANCE ENGINE"), use_container_width=True)

        p_green_cnt = (p_pcts >= 85).sum()
        p_amber_cnt = ((p_pcts >= 60) & (p_pcts < 85)).sum()
        p_red_cnt   = (p_pcts < 60).sum()

        fig_pie = go.Figure(data=[go.Pie(
            labels=['Green (Optimal)', 'Amber (Moderate)', 'Red (Under Target)'],
            values=[p_green_cnt, p_amber_cnt, p_red_cnt],
            hole=.6,
            marker_colors=['#30D158', '#FF9F0A', '#FF375F']
        )])
        fig_pie.update_layout(title="Protein RAG Adherence Distribution", paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter"))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 11 — 📅 Day of Week Pattern Profiler
    # ══════════════════════════════════════════
    with tab11:
        st.markdown("<div class='section-header'>Weekly Pattern Profiler</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Behavioral Variance by Day of the Week</div>", unsafe_allow_html=True)

        dow_df = df_valid.copy()
        dow_df['Day'] = dow_df.iloc[:, 0].dt.day_name()
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        dow_df['Calories'] = pd.to_numeric(dow_df.iloc[:, 1], errors='coerce')
        dow_df['Steps']    = pd.to_numeric(dow_df.iloc[:, 12], errors='coerce')
        dow_df['Water']    = pd.to_numeric(dow_df.iloc[:, 24], errors='coerce')

        dow_summary = dow_df.groupby('Day')[['Calories', 'Steps', 'Water']].mean().reindex(days_order)

        fig_dow = go.Figure()
        fig_dow.add_trace(go.Bar(x=dow_summary.index, y=dow_summary['Calories'], name='Avg Calories', marker_color='#0A84FF'))
        fig_dow.add_hline(y=1633, line_dash="dash", line_color="#30D158", annotation_text="1,633 Target")
        st.plotly_chart(apply_theme(fig_dow, "Average Caloric Intake by Day of Week", "BEHAVIORAL RISK ANALYSIS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 12 — Averages
    # ══════════════════════════════════════════
    with tab12:
        w_series = get_num(3).dropna()
        avg_loss = (w_series.iloc[0] - w_series.iloc[-1]) / (len(df) / 7) if len(w_series) > 1 else 0.0

        st.markdown("<div class='section-header'>Historical Averages</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Avg Cals / Day", num_target=get_num(1).mean(), decimals=0, suffix=" kcal"), unsafe_allow_html=True)
            st.markdown(card("Avg Protein % Target", num_target=get_num(16).mean(), decimals=1, suffix="%"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("Avg Steps / Day", num_target=get_num(12).mean(), decimals=0), unsafe_allow_html=True)
            st.markdown(card("Avg Net Carbs % Target", num_target=get_num(17).mean(), decimals=1, suffix="%"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Avg Loss / Week", num_target=avg_loss, decimals=2, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Avg Fat % Target", num_target=get_num(18).mean(), decimals=1, suffix="%"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 13 — 🎯 Stone Gateway & Milestones
    # ══════════════════════════════════════════
    with tab13:
        st.markdown("<div class='section-header'>Stone Gateway & Milestone Tracker</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Breakdown to Major Stone Boundaries</div>", unsafe_allow_html=True)

        latest_w = get_num(3).dropna().iloc[-1] if not get_num(3).dropna().empty else 200.0

        st_15 = 210.0 # 15 stone
        st_14 = 196.0 # 14 stone
        st_13 = 182.0 # 13 stone
        st_12_2 = 170.0 # 12 stone 2 lbs (Final Goal)

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(card("15 Stone Threshold", display_val="PASSED" if latest_w < st_15 else f"{latest_w - st_15:.1f} lbs to go"), unsafe_allow_html=True)
        with sc2:
            st.markdown(card("14 Stone Threshold (196 lbs)", display_val="PASSED" if latest_w < st_14 else f"{latest_w - st_14:.1f} lbs to go"), unsafe_allow_html=True)
        with sc3:
            st.markdown(card("13 Stone Threshold (182 lbs)", display_val="PASSED" if latest_w < st_13 else f"{latest_w - st_13:.1f} lbs to go"), unsafe_allow_html=True)
        with sc4:
            st.markdown(card("12 st 2 lbs Final Goal", display_val="ACHIEVED" if latest_w <= st_12_2 else f"{latest_w - st_12_2:.1f} lbs to go"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 14 — Trophy Room
    # ══════════════════════════════════════════
    with tab14:
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
        perfect_hyd_days   = (hyd_arr >= 3000).sum()
        ideal_bp_days      = ((sys_arr > 0) & (sys_arr <= 120) & (dia_arr > 0) & (dia_arr <= 80)).sum()

        def get_pct(days, total): return (days / total * 100) if total > 0 else 0

        badges = [
            {"title": "Iron Will", "desc": f"{perfect_cals_days} Days ({get_pct(perfect_cals_days, total_days):.1f}%) ≤ 1,633 kcal", "unlocked": perfect_cals_days > 0, "icon": "🔥"},
            {"title": "Marathoner", "desc": f"{perfect_steps_days} Days ({get_pct(perfect_steps_days, total_days):.1f}%) ≥ 10k Steps", "unlocked": perfect_steps_days > 0, "icon": "👟"},
            {"title": "Aqua Master", "desc": f"{perfect_hyd_days} Days ({get_pct(perfect_hyd_days, total_days):.1f}%) ≥ 3L Water", "unlocked": perfect_hyd_days > 0, "icon": "💧"},
            {"title": "Zen Heart", "desc": f"{ideal_bp_days} Days ({get_pct(ideal_bp_days, total_days):.1f}%) Ideal BP", "unlocked": ideal_bp_days > 0, "icon": "❤️"},
            {"title": "First Blood", "desc": "Drop 5 lbs total", "unlocked": total_loss_lbs >= 5, "icon": "📉"},
            {"title": "Double Digits", "desc": "Drop 10 lbs total", "unlocked": total_loss_lbs >= 10, "icon": "📉"},
            {"title": "The 15 Club", "desc": "Drop 15 lbs total", "unlocked": total_loss_lbs >= 15, "icon": "📉"},
            {"title": "Twenty Down", "desc": "Drop 20 lbs total", "unlocked": total_loss_lbs >= 20, "icon": "📉"},
            {"title": "Quarter Century", "desc": "Drop 25 lbs total", "unlocked": total_loss_lbs >= 25, "icon": "📉"},
            {"title": "Sub-200 Club", "desc": "Drop below 200 lbs (14 st 4)", "unlocked": min_weight < 200, "icon": "🎯"},
            {"title": "195 lb Milestone", "desc": "Drop below 195 lbs", "unlocked": min_weight < 195, "icon": "🎯"},
            {"title": "190 lb Milestone", "desc": "Drop below 190 lbs", "unlocked": min_weight < 190, "icon": "🎯"},
            {"title": "185 lb Milestone", "desc": "Drop below 185 lbs", "unlocked": min_weight < 185, "icon": "🎯"},
            {"title": "180 lb Milestone", "desc": "Drop below 180 lbs", "unlocked": min_weight < 180, "icon": "🎯"},
            {"title": "175 lb Milestone", "desc": "Drop below 175 lbs", "unlocked": min_weight < 175, "icon": "🎯"},
            {"title": "Goal Achieved", "desc": "Hit 170 lbs target", "unlocked": min_weight <= 170, "icon": "🏆"}
        ]

        def render_badge(b):
            if b["unlocked"]:
                extra = "border-color: rgba(48,209,88,0.35); box-shadow: 0 4px 16px rgba(48,209,88,0.14);"
                val_color = "#1E9145"; status = "UNLOCKED"
            else:
                extra = "opacity: 0.55; background: var(--bg-card);"
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
    #  TAB 15 — Analytics Engine & Heatmap
    # ══════════════════════════════════════════
    with tab15:
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

        weight_delta = w_series - w_series.shift(1)
        valid_mask   = weight_delta.notna()

        good_cal_mask = (cals_series <= 1633) & valid_mask
        bad_cal_mask  = (cals_series > 1633) & valid_mask
        avg_good_cal  = weight_delta[good_cal_mask].mean() if good_cal_mask.sum() > 0 else 0.0
        avg_bad_cal   = weight_delta[bad_cal_mask].mean() if bad_cal_mask.sum() > 0 else 0.0

        prot_green_mask = (prot_series >= 85) & valid_mask
        avg_prot_green  = weight_delta[prot_green_mask].mean() if prot_green_mask.sum() > 0 else 0.0

        carb_green_mask = (carb_series < 90) & valid_mask
        avg_carb_green  = weight_delta[carb_green_mask].mean() if carb_green_mask.sum() > 0 else 0.0

        alc_mask = (alc_series > 0) & valid_mask
        avg_alc  = weight_delta[alc_mask].mean() if alc_mask.sum() > 0 else 0.0

        corr_df = pd.DataFrame({
            'Scale Shift (lbs)': weight_delta,
            'Calories': cals_series,
            'Steps': steps_series,
            'Water (ml)': hyd_series,
            'Protein %': prot_series,
            'Carbs %': carb_series,
            'Fat %': fat_series,
            'Alcohol (kcal)': alc_series
        }).dropna()

        if len(corr_df) > 5:
            corr_matrix = corr_df.corr()
            fig_corr = px.imshow(
                corr_matrix, text_auto=".2f", aspect="auto",
                color_continuous_scale="RdBu_r",
                title="Telemetry Correlation Heatmap (Pearson r)"
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
                <span style='color: #1E9145; font-weight: 800;'>{avg_good_cal:+.2f} lbs</span>. 
                Exceeding 1,633 kcal shifts the scale by <span style='color: #E0264F; font-weight: 800;'>{avg_bad_cal:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>🥩</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>Protein RAG Compliance Effect</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Hitting <b>GREEN Protein (≥85% Target)</b> produces an average scale shift of 
                <span style='color: #1E9145; font-weight: 800;'>{avg_prot_green:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 16 — Weekly Sit Rep
    # ══════════════════════════════════════════
    with tab16:
        st.markdown("<div class='section-header'>Weekly Sit Rep</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Last 7 Days vs Previous 7 Days</div>", unsafe_allow_html=True)

        if len(df_valid) >= 14:
            last_7 = df_valid.iloc[-7:]
            prev_7 = df_valid.iloc[-14:-7]

            l7_cals = pd.to_numeric(last_7.iloc[:, 1], errors='coerce').mean()
            p7_cals = pd.to_numeric(prev_7.iloc[:, 1], errors='coerce').mean()

            l7_steps = pd.to_numeric(last_7.iloc[:, 12], errors='coerce').mean()
            p7_steps = pd.to_numeric(prev_7.iloc[:, 12], errors='coerce').mean()

            l7_w_start = pd.to_numeric(last_7.iloc[0, 3], errors='coerce')
            l7_w_end   = pd.to_numeric(last_7.iloc[-1, 3], errors='coerce')
            l7_change  = l7_w_end - l7_w_start

            p7_w_start = pd.to_numeric(prev_7.iloc[0, 3], errors='coerce')
            p7_w_end   = pd.to_numeric(prev_7.iloc[-1, 3], errors='coerce')
            p7_change  = p7_w_end - p7_w_start

            cal_diff    = l7_cals - p7_cals
            step_diff   = l7_steps - p7_steps
            change_diff = l7_change - p7_change

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(card("Avg Cals (7 Days)", num_target=l7_cals, decimals=0, suffix=" kcal", delta_val=cal_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)
            with col2:
                st.markdown(card("Avg Steps (7 Days)", num_target=l7_steps, decimals=0, delta_val=step_diff, delta_label="vs Prev", invert=False), unsafe_allow_html=True)
            with col3:
                st.markdown(card("Weight Change (7 Days)", display_val=f"{safe(l7_change):+.1f} lbs", delta_val=change_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)
        else:
            st.info("System requires at least 14 days of telemetry to generate a comparative Sit Rep.")

    # ══════════════════════════════════════════
    #  TAB 17 — Forecast Projection Engine
    # ══════════════════════════════════════════
    with tab17:
        st.markdown("<div class='section-header'>Forecasting Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Estimated Arrival Date (ETA) to 170 lbs (12 st 2 lbs)</div>", unsafe_allow_html=True)

        w_series = get_num(3).dropna()
        if len(w_series) >= 14:
            window = min(21, len(w_series))
            recent = w_series.tail(window).reset_index(drop=True)
            x = np.arange(len(recent))
            slope, _ = np.polyfit(x, recent.values, 1) # lbs / day
            loss_rate_per_day = -slope
            current_w = w_series.iloc[-1]

            if loss_rate_per_day > 0.01 and current_w > 170:
                days_to_goal = int((current_w - 170) / loss_rate_per_day)
                eta_date = pd.Timestamp.now() + pd.Timedelta(days=days_to_goal)

                st.markdown(f"""
                <div class='card' style='padding: 36px 20px;'>
                    <div style='font-size: 2.6rem; margin-bottom: 8px;'>🔮</div>
                    <div class='val' style='font-size: 2.3rem; color: #0A84FF;'>{eta_date.strftime('%B %d, %Y')}</div>
                    <div class='label' style='margin-top: 14px; font-size: 0.85rem;'>Projected Goal Achievement Date</div>
                    <div style='font-family: var(--font-body); font-size: 0.95rem; color: var(--text-secondary); margin-top: 14px;'>
                        Based on your {window}-day trend of dropping <b>{loss_rate_per_day*7:.1f} lbs per week</b>.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif current_w <= 170:
                st.markdown("<div class='card'><div class='val' style='color:#1E9145;'>TARGET ACHIEVED</div></div>", unsafe_allow_html=True)
            else:
                st.info(f"Your {window}-day trend is currently flat or increasing ({loss_rate_per_day*7:+.1f} lbs/week). Maintain a deficit to generate an ETA.")
        else:
            st.info("Requires at least 14 days of logged weight telemetry to calculate projection.")

    # ══════════════════════════════════════════
    #  TAB 18 — Momentum Score
    # ══════════════════════════════════════════
    with tab18:
        st.markdown("<div class='section-header'>Momentum Score</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Daily Composite Score — Calories + Steps + Water + Macro RAG</div>", unsafe_allow_html=True)

        momentum_days = df_valid
        if len(momentum_days) >= 1:
            cal_m   = get_num(1, momentum_days).replace(0, np.nan)
            steps_m = get_num(12, momentum_days)
            hyd_m   = get_num(24, momentum_days)
            prot_m  = get_num(16, momentum_days)

            cal_score   = (1633 / cal_m).clip(upper=1).fillna(0) * 25
            step_score  = (steps_m / 10000).clip(upper=1).fillna(0) * 25
            hyd_score   = (hyd_m / 3000).clip(upper=1).fillna(0) * 25
            prot_score  = (prot_m / 85.0).clip(upper=1).fillna(0) * 25

            daily_score = (cal_score + step_score + hyd_score + prot_score).round(0).clip(upper=100)

            def score_band(s):
                if s >= 75: return ("Optimal", "#30D158", "rgba(48,209,88,0.14)")
                elif s >= 50: return ("Moderate", "#FF9F0A", "rgba(255,159,10,0.14)")
                else: return ("Needs Focus", "#FF375F", "rgba(255,55,95,0.12)")

            latest_score = safe(daily_score.iloc[-1])
            latest_label, latest_color, latest_fill = score_band(latest_score)

            good_day = daily_score >= 75
            current_streak = 0
            for v in good_day.tolist()[::-1]:
                if v: current_streak += 1
                else: break

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Latest Momentum Score</div>
                    <div class='val' style='color:{latest_color};'>{latest_score:.0f}<span style='font-size:0.5em; opacity:0.6;'>/100</span></div>
                    <div class='delta' style='background:{latest_fill}; color:{latest_color}; border:1px solid {latest_color}55;'>{latest_label}</div>
                  </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(card("Current Streak (≥75)", display_val=f"{current_streak} {'day' if current_streak == 1 else 'days'}"), unsafe_allow_html=True)
            with c3:
                st.markdown(card("Avg Score (90 Days)", num_target=daily_score.tail(90).mean(), decimals=0), unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_hrect(y0=75, y1=100, fillcolor='rgba(48,209,88,0.06)', layer="below", line_width=0)
            fig.add_trace(go.Scatter(
                x=momentum_days.iloc[:, 0], y=daily_score, mode='lines+markers', name='Health Score',
                line=dict(color='#0A84FF', width=2.5),
                marker=dict(color='#0A84FF', size=6),
                fill='tozeroy', fillcolor='rgba(10,132,255,0.08)'
            ))
            fig.add_hline(y=75, line_dash="dash", line_color="#30D158", annotation_text="TARGET (75+)")
            fig.update_layout(yaxis=dict(range=[0, 100]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
            st.plotly_chart(apply_theme(fig, "Momentum Score Trend", "COMPOSITE HEALTH MATRIX"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 19 — Raw Telemetry Log
    # ══════════════════════════════════════════
    with tab19:
        st.markdown("<div class='section-header'>Raw Telemetry Log</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Latest 30 Records</div>", unsafe_allow_html=True)

        display_df = df.copy()
        display_df[0] = display_df[0].dt.strftime('%Y-%m-%d')
        display_df = display_df.iloc[::-1].head(30)
        display_df.columns = [str(i) for i in range(len(display_df.columns))]

        cols_to_show = {
            '0': 'Date', '1': 'Calories', '3': 'Weight (lbs)', '4': 'Weight (St)',
            '12': 'Steps', '16': 'Protein % Tgt', '17': 'Carbs % Tgt', '18': 'Fat % Tgt',
            '19': 'Alcohol (kcal)', '21': 'Systolic BP', '22': 'Diastolic BP', '23': 'HR', '24': 'Water (ml)'
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
