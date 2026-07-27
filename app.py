import streamlit as st
import pandas as pd
import numpy as np
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import time
import re

# ─────────────────────────────────────────────
#  PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Hardy House Health Telemetry",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Boot Notification ──
if 'booted' not in st.session_state:
    st.toast('Sync Complete — Telemetry Active.', icon='✅')
    time.sleep(0.4)
    st.toast('Analytics & Debuff Engine Online.', icon='💚')
    st.session_state.booted = True

# ─────────────────────────────────────────────
#  PREMIUM GLASSMORPHISM CSS (Apple Health Theme)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
  --bg-app:          #F2F2F7;
  --bg-card:         rgba(255, 255, 255, 0.72);
  --bg-card-hover:   rgba(255, 255, 255, 0.88);
  --glass-border:    rgba(255, 255, 255, 0.65);
  --glass-blur:      blur(28px) saturate(190%);
  --glass-blur-sm:   blur(16px) saturate(160%);

  --shadow-card:       0 2px 8px rgba(15,23,42,0.04), 0 16px 36px rgba(15,23,42,0.08);
  --shadow-card-hover: 0 8px 20px rgba(15,23,42,0.08), 0 28px 60px rgba(15,23,42,0.14);

  --text-primary:   #1D1D1F;
  --text-secondary: rgba(60,60,67,0.72);
  --text-tertiary:  rgba(60,60,67,0.45);

  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  --font-body:    'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;

  /* Accents */
  --red:    #FF375F;
  --orange: #FF9F0A;
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
    linear-gradient(180deg, rgba(242,242,247,0.55) 0%, rgba(242,242,247,0.85) 50%, rgba(242,242,247,0.96) 100%),
    url('https://github.com/nodramallama89/Weight-tracker/blob/33fc966fe489b029049541e417658a7441afa776/Gemini_Generated_Image_1zukku1zukku1zuk.png?raw=true');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: var(--font-body);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.8rem 2.2rem 3rem; max-width: 1650px; }

/* ── Typography ── */
.page-eyebrow {
  font-size: 0.78rem; font-weight: 700; letter-spacing: 0.09em;
  text-transform: uppercase; color: var(--text-tertiary); text-align: center;
  display: block; margin-bottom: 0.3rem; animation: fadeUp 0.5s ease both;
}
.page-eyebrow .status-dot {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background-color: var(--green); margin-right: 7px;
  box-shadow: 0 0 0 4px rgba(48,209,88,0.2);
}

.page-title {
  font-family: var(--font-display) !important; font-size: 2.7rem !important;
  font-weight: 900 !important; letter-spacing: -0.03em !important;
  color: var(--text-primary) !important; text-align: center !important;
  margin: 0 0 0.2rem !important; animation: fadeUp 0.6s ease 0.05s both;
  text-shadow: 0 2px 14px rgba(255,255,255,0.7);
}

.page-subtitle {
  font-size: 0.95rem; color: var(--text-secondary); text-align: center;
  margin-bottom: 2rem; font-weight: 500; animation: fadeUp 0.7s ease 0.1s both;
}

/* ── Frosted Glass Cards ── */
.card {
  background: var(--bg-card);
  backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl); padding: 22px 20px 20px;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.7);
  border: 1px solid var(--glass-border); text-align: center; margin-bottom: 14px;
  position: relative; overflow: hidden;
  transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1);
  animation: springUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.card:hover {
  transform: translateY(-4px); box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,0.85);
  border-color: rgba(255,255,255,0.9); background: var(--bg-card-hover);
}

.val { font-family: var(--font-display); font-size: 2.25rem; font-weight: 800; margin: 4px 0; line-height: 1; color: var(--text-primary); letter-spacing: -0.02em; }
.val-sm { font-family: var(--font-display); font-size: 1.55rem; font-weight: 800; margin: 4px 0; line-height: 1; color: var(--text-primary); letter-spacing: -0.01em; }
.label { font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.09em; color: var(--text-tertiary); }

.delta { font-size: 0.78rem; font-weight: 700; margin-top: 10px; padding: 5px 13px; border-radius: 50px; display: inline-block; box-shadow: 0 2px 8px rgba(15,23,42,0.06); }
.delta-pos { background: rgba(48, 209, 88, 0.16); color: #1E9145; border: 1px solid rgba(48, 209, 88, 0.3); }
.delta-neg { background: rgba(255, 55, 95, 0.14); color: #E0264F; border: 1px solid rgba(255, 55, 95, 0.28); }

/* ── Debuff & Status Modifiers ── */
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

/* ── Tab Styling ── */
div[data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.5) !important; backdrop-filter: var(--glass-blur-sm) !important;
  -webkit-backdrop-filter: var(--glass-blur-sm) !important; border-radius: 16px !important;
  padding: 5px !important; border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card) !important; margin-bottom: 2rem !important; flex-wrap: wrap !important; gap: 2px;
}
div[data-baseweb="tab"] { border-radius: 11px !important; transition: all 0.25s ease !important; }
div[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.35) !important; }
div[data-baseweb="tab"][aria-selected="true"] { background: rgba(255,255,255,0.92) !important; box-shadow: 0 2px 8px rgba(15,23,42,0.12) !important; }
div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { color: var(--text-secondary) !important; font-size: 0.88rem !important; font-weight: 600 !important; }
div[data-baseweb="tab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; font-weight: 800 !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }

/* ── Plotly Containers ── */
.stPlotlyChart {
  background: var(--bg-card) !important; backdrop-filter: var(--glass-blur) !important;
  -webkit-backdrop-filter: var(--glass-blur) !important; border-radius: var(--radius-xl) !important;
  padding: 16px !important; border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.7) !important;
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
#  PLOTLY THEME
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


# ─────────────────────────────────────────────
#  DATA LOADING
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

# Filter for rows where steps (column 12) or calories (column 1) are completed
if not df.empty:
    df_valid = df[df.iloc[:, 12].astype(str).str.strip() != ""].reset_index(drop=True)
    if df_valid.empty:
        df_valid = df
else:
    df_valid = df


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_num(idx, source=None):
    """Safely extract a numeric series from any column index."""
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

def fmt_num(value, decimals=0, suffix=''):
    v = safe(value)
    formatted = f"{v:,.{decimals}f}"
    if suffix:
        formatted += f"<span style='font-size:0.65em; opacity:0.55; margin-left:4px;'>{suffix}</span>"
    return formatted

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
#  STATUS MODIFIERS ("DEBUFF") ENGINE
# ─────────────────────────────────────────────
def evaluate_debuffs(row_data):
    """Evaluates telemetry metrics for a row and generates status warning pills."""
    badges = []
    
    # 1. Alcohol Active (Col 19 kcal)
    alc_kcal = clean_float(row_data.iloc[19]) if len(row_data) > 19 else 0.0
    if alc_kcal > 0:
        badges.append(f"<div class='debuff-badge debuff-warning'>🍷 Alcohol Active (+{alc_kcal:,.0f} kcal) — Sleep & Recovery Suppressed</div>")
    
    # 2. Caloric Intake Check (Col 1)
    cals = clean_float(row_data.iloc[1]) if len(row_data) > 1 else 0.0
    if cals > 1633:
        badges.append(f"<div class='debuff-badge debuff-caution'>🔥 Caloric Surplus (+{cals - 1633:,.0f} kcal over target)</div>")
    elif 0 < cals <= 1633:
        badges.append("<div class='debuff-badge debuff-optimal'>🔥 Caloric Target Hit (≤ 1,633 kcal)</div>")

    # 3. Steps Target Check (Col 12)
    steps = clean_float(row_data.iloc[12]) if len(row_data) > 12 else 0.0
    if steps >= 10000:
        badges.append(f"<div class='debuff-badge debuff-optimal'>👟 Kinetic Goal Hit ({steps:,.0f} Steps)</div>")
    elif steps < 8000:
        badges.append(f"<div class='debuff-badge debuff-caution'>👟 Low Activity ({steps:,.0f} Steps)</div>")

    # 4. Water Target Check (Col 24)
    water_ml = clean_float(row_data.iloc[24]) if len(row_data) > 24 else 0.0
    if water_ml >= 3000:
        badges.append(f"<div class='debuff-badge debuff-optimal'>💧 Hydration Optimal ({water_ml:,.0f} ml)</div>")
    elif 0 < water_ml < 3000:
        badges.append(f"<div class='debuff-badge debuff-caution'>💧 Hydration Under Target ({water_ml:,.0f} / 3,000 ml)</div>")

    if not badges:
        badges.append("<div class='debuff-badge debuff-optimal'>🛡️ All Telemetry Nominal</div>")

    return f"<div class='debuff-container'>{''.join(badges)}</div>"


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
if not df.empty:

    # ── Header ──
    st.markdown("""
    <span class='page-eyebrow'><span class='status-dot'></span>LIVE TELEMETRY STREAM</span>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='page-title'>Hardy House Health</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Daily wellness, recovery intelligence & trend analytics</div>", unsafe_allow_html=True)

    # ── 17 Tabs ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17 = st.tabs([
        "🛡️ Review", "📊 Lifetime", "🔥 Calories", "💧 Hydration", "⚖️ Weight",
        "📉 Trend", "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ Vitals", "🎯 Target", "🏆 Trophies", "🧠 Analytics", "📋 Sit Rep", "🔮 Forecast", "⚡ Momentum", "🗄️ Data Log"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Review (Yesterday's Debrief)
    # ══════════════════════════════════════════
    with tab1:
        completed = df_valid
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "LATEST_DATA"
            cals  = clean_float(y.iloc[1])
            steps = clean_float(y.iloc[12])

            st.markdown("<div class='section-header'>Yesterday's Debrief</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>{date_str}</div>", unsafe_allow_html=True)

            # Primary Metrics Grid
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

            # Macros & Alcohol Grid
            m1, m2, m3, m4 = st.columns(4)
            
            # Col 16: Protein (Target 141.2g)
            prot_g = clean_float(y.iloc[16]) if len(y) > 16 else 0.0
            m1.markdown(f"""
              <div class='card' style='border-bottom: 3px solid #FF375F;'>
                <div class='label'>Protein (Tgt 141.2g)</div>
                <div class='val-sm count-up' data-target='{prot_g}' data-decimals='1' data-suffix='g'>{fmt_num(prot_g, 1, 'g')}</div>
              </div>""", unsafe_allow_html=True)

            # Col 17: Net Carbs (Target 220g)
            carbs_g = clean_float(y.iloc[17]) if len(y) > 17 else 0.0
            m2.markdown(f"""
              <div class='card' style='border-bottom: 3px solid #0A84FF;'>
                <div class='label'>Net Carbs (Tgt 220g)</div>
                <div class='val-sm count-up' data-target='{carbs_g}' data-decimals='1' data-suffix='g'>{fmt_num(carbs_g, 1, 'g')}</div>
              </div>""", unsafe_allow_html=True)

            # Col 18: Fat (Target 65.2g)
            fat_g = clean_float(y.iloc[18]) if len(y) > 18 else 0.0
            m3.markdown(f"""
              <div class='card' style='border-bottom: 3px solid #FFD60A;'>
                <div class='label'>Fat (Tgt 65.2g)</div>
                <div class='val-sm count-up' data-target='{fat_g}' data-decimals='1' data-suffix='g'>{fmt_num(fat_g, 1, 'g')}</div>
              </div>""", unsafe_allow_html=True)

            # Col 19: Alcohol (kcal) - EXPLICITLY IN KCAL
            alc_kcal = clean_float(y.iloc[19]) if len(y) > 19 else 0.0
            m4.markdown(f"""
              <div class='card' style='border-bottom: 3px solid #BF5AF2;'>
                <div class='label'>Alcohol Intake</div>
                <div class='val-sm count-up' data-target='{alc_kcal}' data-decimals='0' data-suffix=' kcal'>{fmt_num(alc_kcal, 0, ' kcal')}</div>
              </div>""", unsafe_allow_html=True)

            # Debuff Status Engine
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-sub' style='margin-bottom:0.6rem;'>Active Status Modifiers</div>", unsafe_allow_html=True)
            st.markdown(evaluate_debuffs(y), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab2:
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
            st.markdown(card("Total Loss", num_target=clean_float(l.iloc[6]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Total Loss (Stone)", display_val=f"{l.iloc[7]}"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("To Target", num_target=clean_float(l.iloc[8]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("To Target (Stone)", display_val=f"{l.iloc[9]}"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Current BMI", num_target=clean_float(l.iloc[10]), decimals=1), unsafe_allow_html=True)
            st.markdown(card("To Target BMI", num_target=clean_float(l.iloc[11]), decimals=1), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 3 — Calories
    # ══════════════════════════════════════════
    with tab3:
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
        st.plotly_chart(apply_theme(fig, "Caloric Intake", "≤1,633 GREEN // >1,700 RED"), use_container_width=True)

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
    #  TAB 4 — Hydration
    # ══════════════════════════════════════════
    with tab4:
        hyd_series = get_num(24)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=hyd_series, name="Hydration (ml)",
            marker=dict(color=hyd_series, colorscale=[[0, '#0A84FF'], [1, '#64D2FF']], line=dict(width=1, color='rgba(255,255,255,0.6)')),
        ))
        fig.add_hline(y=3000, line_dash="dash", line_color="#0A84FF", annotation_text="3,000 ml TARGET", annotation_font_color="#0A84FF")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Hydration", "MEASURED IN MILLILITERS"), use_container_width=True)

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
    #  TAB 5 — Weight
    # ══════════════════════════════════════════
    with tab5:
        w_series = get_num(3).dropna()
        w_max = float(w_series.max()) + 2 if not w_series.empty else 210

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            name="Weight (lbs)", mode='lines+markers',
            line=dict(color='#1D1D1F', width=2),
            marker=dict(color='#BF5AF2', size=8, symbol='circle', line=dict(color='#ffffff', width=1.5)),
            zorder=3
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series), 0], y=w_series, mode='lines', line=dict(color='rgba(191,90,242,0.35)', width=10), hoverinfo='skip', showlegend=False, zorder=2))
        fig.add_hline(y=170, line_dash="dash", line_color="#0A84FF", annotation_text="🎯 GOAL: 170 lbs", annotation_font_color="#0A84FF", annotation_position="top left")

        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory", "DAILY ACTUALS (LBS)"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Gain / Loss Trend
    # ══════════════════════════════════════════
    with tab6:
        # Col 5 is Gain/Loss directly logged
        trend = get_num(5)
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
        st.plotly_chart(apply_theme(fig, "Weight Variance", "RANGE ±5 LBS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 7 — Steps
    # ══════════════════════════════════════════
    with tab7:
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
        st.plotly_chart(apply_theme(fig, "Daily Steps", "STATUS: TRACKING"), use_container_width=True)

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
    #  TAB 8 — Macros
    # ══════════════════════════════════════════
    with tab8:
        fig = go.Figure()
        macro_cfg = [
            (16, "Protein (g)", "#FF375F", "rgba(255,55,95,0.10)"),
            (17, "Net Carbs (g)", "#0A84FF", "rgba(10,132,255,0.10)"),
            (18, "Fat (g)", "#FFD60A", "rgba(255,214,10,0.12)")
        ]
        
        for idx, name, color, fill in macro_cfg:
            series = get_num(idx)
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0], y=series, name=name, mode='lines',
                line=dict(color=color, width=3, shape='spline'),
                fill='tozeroy', fillcolor=fill,
            ))
            
        fig.add_hline(y=141.2, line_dash="dot", line_color="#FF375F", annotation_text="Protein Target (141.2g)")
        fig.add_hline(y=220.0, line_dash="dot", line_color="#0A84FF", annotation_text="Carbs Target (220g)")
        fig.add_hline(y=65.2, line_dash="dot", line_color="#FFD60A", annotation_text="Fat Target (65.2g)")

        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Macronutrient Breakdown (Grams)", "PROTEIN // CARBS // FAT"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 9 — Averages
    # ══════════════════════════════════════════
    with tab9:
        w_series = get_num(3).dropna()
        avg_loss = (w_series.iloc[0] - w_series.iloc[-1]) / (len(df) / 7) if len(w_series) > 1 else 0.0

        st.markdown("<div class='section-header'>Historical Data</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Avg Cals / Day", num_target=get_num(1).mean(), decimals=0), unsafe_allow_html=True)
            st.markdown(card("Avg Protein", num_target=get_num(16).mean(), decimals=1, suffix="g"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("Avg Steps / Day", num_target=get_num(12).mean(), decimals=0), unsafe_allow_html=True)
            st.markdown(card("Avg Net Carbs", num_target=get_num(17).mean(), decimals=1, suffix="g"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Avg Loss / Week", num_target=avg_loss, decimals=2, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Avg Fat", num_target=get_num(18).mean(), decimals=1, suffix="g"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 10 — Blood Pressure & Vitals
    # ══════════════════════════════════════════
    with tab10:
        sys_data = get_num(21)
        dia_data = get_num(22)
        hr_data  = get_num(23)

        fig = go.Figure()
        fig.add_hrect(y0=60, y1=80, fillcolor='rgba(48,209,88,0.06)', layer="below", line_width=0)
        fig.add_hrect(y0=80, y1=90, fillcolor='rgba(255,214,10,0.07)', layer="below", line_width=0)
        fig.add_hrect(y0=90, y1=180, fillcolor='rgba(255,55,95,0.06)', layer="below", line_width=0)

        fig.add_hline(y=120, line_dash="dash", line_color="#30D158", annotation_text="SYS IDEAL", annotation_font_color="#1E9145")
        fig.add_hline(y=80, line_dash="dash", line_color="#0A84FF", annotation_text="DIA IDEAL", annotation_font_color="#0A84FF")

        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=sys_data, name="Systolic", mode='lines+markers', connectgaps=True, line=dict(color='#FF375F', width=3), marker=dict(size=8, color='#FF375F', line=dict(color='#ffffff', width=1.5))))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=dia_data, name="Diastolic", mode='lines+markers', connectgaps=True, line=dict(color='#0A84FF', width=3), marker=dict(size=8, color='#0A84FF', line=dict(color='#ffffff', width=1.5))))
        
        # Plot HR if present
        if hr_data.notna().any():
            fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=hr_data, name="Heart Rate (BPM)", mode='lines+markers', connectgaps=True, line=dict(color='#BF5AF2', width=2, dash='dot'), marker=dict(size=6, color='#BF5AF2')))

        fig.update_layout(yaxis=dict(range=[50, 180]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Vitals Monitor", "BLOOD PRESSURE & HEART RATE"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 11 — Target Gauge
    # ══════════════════════════════════════════
    with tab11:
        st.markdown("<div class='section-header'>Mission Progress</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Distance to 170 lbs</div>", unsafe_allow_html=True)

        w_series = get_num(3).dropna()
        if len(w_series) > 1:
            current_w = w_series.iloc[-1]
            start_w   = w_series.iloc[0]
            goal_w    = 170

            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = current_w,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Current Weight (lbs)", 'font': {'color': 'rgba(60,60,67,0.7)', 'size': 18, 'family': 'Inter'}},
                delta = {'reference': start_w, 'increasing': {'color': '#FF375F'}, 'decreasing': {'color': '#30D158'}},
                gauge = {
                    'axis': {'range': [goal_w - 5, start_w + 5], 'tickcolor': "rgba(60,60,67,0.4)", 'tickfont': {'color': 'rgba(60,60,67,0.6)'}},
                    'bar': {'color': "#0A84FF"},
                    'bgcolor': "rgba(0,0,0,0.03)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(60,60,67,0.12)",
                    'steps': [
                        {'range': [goal_w, goal_w + 10], 'color': "rgba(48,209,88,0.14)"},
                        {'range': [goal_w + 10, start_w], 'color': "rgba(255,159,10,0.10)"}
                    ],
                    'threshold': {'line': {'color': "#BF5AF2", 'width': 4}, 'thickness': 0.85, 'value': goal_w}
                }
            ))

            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#1D1D1F', family='Inter'), height=450, margin=dict(t=60, b=40))
            st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 12 — Trophy Room
    # ══════════════════════════════════════════
    with tab12:
        st.markdown("<div class='section-header'>The Trophy Room</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Unlock milestones through consistency</div>", unsafe_allow_html=True)

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
    #  TAB 13 — Analytics Engine
    # ══════════════════════════════════════════
    with tab13:
        st.markdown("<div class='section-header'>Data Insights</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Cause and Effect Analysis — Last 90 Logged Days</div>", unsafe_allow_html=True)

        analytics_window = df_valid.tail(90).reset_index(drop=True)

        w_series     = get_num(3, analytics_window)
        cals_series  = get_num(1, analytics_window)
        steps_series = get_num(12, analytics_window)
        hyd_series   = get_num(24, analytics_window)
        prot_series  = get_num(16, analytics_window)
        alc_series   = get_num(19, analytics_window)

        # TEMPORAL ALIGNMENT: Telemetry on Row X drives scale shift observed on Row X (Weight_X - Weight_X-1)
        weight_delta = w_series - w_series.shift(1)
        valid_mask   = weight_delta.notna()

        # 1. Caloric Efficiency
        good_cal_mask = (cals_series <= 1633) & valid_mask
        bad_cal_mask  = (cals_series > 1633) & valid_mask

        avg_change_good_cals = weight_delta[good_cal_mask].mean() if good_cal_mask.sum() > 0 else 0.0
        avg_change_bad_cals  = weight_delta[bad_cal_mask].mean() if bad_cal_mask.sum() > 0 else 0.0

        # 2. Step Impact
        good_step_mask = (steps_series >= 10000) & valid_mask
        success_rate   = (weight_delta[good_step_mask] <= 0).sum() / good_step_mask.sum() * 100 if good_step_mask.sum() > 0 else 0.0

        # 3. Hydration Impact
        good_hyd_mask    = (hyd_series >= 3000) & valid_mask
        bad_hyd_mask     = (hyd_series < 3000) & (hyd_series > 0) & valid_mask
        hyd_success_good = (weight_delta[good_hyd_mask] <= 0).sum() / good_hyd_mask.sum() * 100 if good_hyd_mask.sum() > 0 else 0.0
        hyd_success_bad  = (weight_delta[bad_hyd_mask] <= 0).sum() / bad_hyd_mask.sum() * 100 if bad_hyd_mask.sum() > 0 else 0.0

        # 4. Protein Power Impact
        high_prot_mask = (prot_series >= 141.2) & valid_mask
        avg_change_high_prot = weight_delta[high_prot_mask].mean() if high_prot_mask.sum() > 0 else 0.0

        # 5. Alcohol Impact
        alc_mask = (alc_series > 0) & valid_mask
        avg_change_alc = weight_delta[alc_mask].mean() if alc_mask.sum() > 0 else 0.0

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>🔥</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>Caloric Threshold Engine</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Staying <b style='color:var(--text-primary);'>≤ 1,633 kcal</b> produces an average daily scale shift of 
                <span style='color: #1E9145; font-weight: 800;'>{avg_change_good_cals:+.2f} lbs</span>. 
                Exceeding 1,633 kcal shifts the scale by <span style='color: #E0264F; font-weight: 800;'>{avg_change_bad_cals:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>👟</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>Kinetic Success Rate</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Hitting your 10,000 step goal yields a <span style='color: #1E9145; font-weight: 800;'>{success_rate:.0f}% success rate</span> 
                for maintaining or dropping weight on the scale the following morning.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>💧</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>The Hydration Catalyst</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Drinking 3,000 ml or more of water gives you a <span style='color: #1E9145; font-weight: 800;'>{hyd_success_good:.0f}%</span> chance of dropping weight the next morning. On days under target, that drops to <span style='color: #FF9F0A; font-weight: 800;'>{hyd_success_bad:.0f}%</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
            <div style='font-size: 1.8rem; margin-bottom: 6px;'>🥩</div>
            <div class='val-sm' style='margin-bottom: 8px; color: #0A84FF;'>Protein Correlation</div>
            <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                Hitting protein target (<b>≥ 141.2g</b>) correlates with an average scale shift of 
                <span style='color: #1E9145; font-weight: 800;'>{avg_change_high_prot:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if alc_mask.sum() > 0:
            st.markdown(f"""
            <div class='card' style='text-align: left; padding: 26px; margin-bottom: 14px;'>
                <div style='font-size: 1.8rem; margin-bottom: 6px;'>🍷</div>
                <div class='val-sm' style='margin-bottom: 8px; color: #BF5AF2;'>Alcohol Impact</div>
                <div style='font-family: var(--font-body); font-size: 1.02rem; color: var(--text-secondary); line-height: 1.6;'>
                    Days with logged alcohol intake resulted in an average next-morning scale movement of 
                    <span style='color: #E0264F; font-weight: 800;'>{avg_change_alc:+.2f} lbs</span>.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 14 — Weekly Sit Rep
    # ══════════════════════════════════════════
    with tab14:
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
    #  TAB 15 — Forecast Projection Engine
    # ══════════════════════════════════════════
    with tab15:
        st.markdown("<div class='section-header'>Forecasting Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Estimated Arrival Date (ETA) to 170 lbs</div>", unsafe_allow_html=True)

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
            st.info("Requires at least 14 days of logged weight telemetry to calculate a projection.")

    # ══════════════════════════════════════════
    #  TAB 16 — Momentum Score
    # ══════════════════════════════════════════
    with tab16:
        st.markdown("<div class='section-header'>Momentum Score</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Daily Score — Calories + Steps + Water + Protein</div>", unsafe_allow_html=True)

        momentum_days = df_valid
        if len(momentum_days) >= 1:
            cal_m   = get_num(1, momentum_days).replace(0, np.nan)
            steps_m = get_num(12, momentum_days)
            hyd_m   = get_num(24, momentum_days)
            prot_m  = get_num(16, momentum_days)

            cal_score   = (1633 / cal_m).clip(upper=1).fillna(0) * 25
            step_score  = (steps_m / 10000).clip(upper=1).fillna(0) * 25
            hyd_score   = (hyd_m / 3000).clip(upper=1).fillna(0) * 25
            prot_score  = (prot_m / 141.2).clip(upper=1).fillna(0) * 25

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
                    <div class='label'>Latest Score</div>
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
            st.plotly_chart(apply_theme(fig, "Momentum Score Trend", "COMPOSITE HEALTH SCORE"), use_container_width=True)

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
            '12': 'Steps', '16': 'Protein (g)', '17': 'Net Carbs (g)', '18': 'Fat (g)',
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
