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

# ── Boot Sequence Notification ──
if 'booted' not in st.session_state:
    st.toast('Apple Health Sync Active — Core Telemetry Updated.', icon='✅')
    time.sleep(0.4)
    st.toast('Analytics & Debuff Engine Initialized.', icon='⚡')
    st.session_state.booted = True

# ─────────────────────────────────────────────
#  PREMIUM GLASSMORPHISM CSS (iOS / macOS Light Theme)
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

/* ── iOS Segmented Control Tabs ── */
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
#  PLOTLY THEME SYSTEM
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
#  DATA LOADING & PIPELINE
# ─────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    """
    Load telemetry from Google Sheets.
    
    Standard Column Schema Mapping:
    0: Date                 10: BMI             20: Fiber (g)
    1: Calories In          11: To Target BMI   21: BP Systolic
    2: Net Calories         12: Steps           22: BP Diastolic
    3: Weight (lbs)         13: Active Cals     23: Heart Rate (bpm)
    4: Target Weight        14: Resting Cals    24: Water / Hydration (ml)
    5: Trend Variance       15: Total Cals Out  25: Sodium (mg)
    6: Total Loss (lbs)     16: Protein %       26: Potassium (mg)
    7: Total Loss %         17: Carbs %         27: Magnesium (mg)
    8: To Target (lbs)      18: Fat %           28: Caffeine (mg)
    9: To Target %          19: Alcohol (kcal)  29: Added Sugars (g)
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
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ── Filter for Fully Logged / Completed Days ──
if not df.empty:
    # Filter rows where steps (column 12) or calories (column 1) are populated
    df_valid = df[df.iloc[:, 12].astype(str).str.strip() != ""].reset_index(drop=True)
    if df_valid.empty:
        df_valid = df
else:
    df_valid = df


# ─────────────────────────────────────────────
#  ROBUST NUMERICAL HELPERS
# ─────────────────────────────────────────────
def get_num(idx, source=None):
    """Safely extract a numeric series from any DataFrame column index."""
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
    except:
        return 0.0

def safe(x):
    """Coerce NaN/None to float safely."""
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
    """
    Evaluates telemetry metrics for a row and generates iOS-style Status Warning Badges.
    Integrates Alcohol, Caffeine, Added Sugars, Sodium, and Fiber.
    """
    badges = []
    
    # 1. Alcohol Debuff (Index 19)
    alc_kcal = clean_float(row_data.iloc[19]) if len(row_data) > 19 else 0.0
    if alc_kcal > 0:
        badges.append(f"<div class='debuff-badge debuff-warning'>🍷 Alcohol Active (+{alc_kcal:,.0f} kcal) — REM & Oxidation Suppressed</div>")
    
    # 2. Caffeine High Intake (Index 28)
    caffeine_mg = clean_float(row_data.iloc[28]) if len(row_data) > 28 else 0.0
    if caffeine_mg >= 300:
        badges.append(f"<div class='debuff-badge debuff-caution'>⚡ High Caffeine ({caffeine_mg:,.0f} mg) — Sleep Spike Risk</div>")
    
    # 3. Added Sugars (Index 29)
    sugars_g = clean_float(row_data.iloc[29]) if len(row_data) > 29 else 0.0
    if sugars_g > 36:
        badges.append(f"<div class='debuff-badge debuff-warning'>🍬 Excess Sugars ({sugars_g:,.0f} g) — Insulin & Retention Risk</div>")
        
    # 4. Sodium Spike (Index 25)
    sodium_mg = clean_float(row_data.iloc[25]) if len(row_data) > 25 else 0.0
    if sodium_mg > 2300:
        badges.append(f"<div class='debuff-badge debuff-caution'>🧂 High Sodium ({sodium_mg:,.0f} mg) — Temporary Fluid Retention</div>")

    # 5. Fiber Deficit (Index 20)
    fiber_g = clean_float(row_data.iloc[20]) if len(row_data) > 20 else 0.0
    if 0 < fiber_g < 25:
        badges.append(f"<div class='debuff-badge debuff-caution'>🌾 Fiber Deficit ({fiber_g:,.0f} g / 30g Target)</div>")
    elif fiber_g >= 30:
        badges.append(f"<div class='debuff-badge debuff-optimal'>🌾 Fiber Optimal ({fiber_g:,.0f} g)</div>")

    if not badges:
        badges.append("<div class='debuff-badge debuff-optimal'>🛡️ All Telemetry Nominal — Zero Active Debuffs</div>")

    return f"<div class='debuff-container'>{''.join(badges)}</div>"


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
if not df.empty:

    # ── Header ──
    st.markdown("""
    <span class='page-eyebrow'><span class='status-dot'></span>LIVE GOOGLE SHEETS TELEMETRY</span>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='page-title'>Hardy House Health</h1></div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Biometric tracking, recovery intelligence & trend analytics</div>", unsafe_allow_html=True)

    # ── 17 Segmented Tabs ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17 = st.tabs([
        "🛡️ Review", "📊 Lifetime", "🔥 Calories", "💧 Recovery", "⚖️ Weight",
        "📉 Trend", "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ Vitals", "🎯 Target", "🏆 Trophies", "🧠 Analytics", "📋 Sit Rep", "🔮 Forecast", "⚡ Momentum", "🗄️ Data Log"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Yesterday's Debrief (Review)
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

            # Primary Cards Grid
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

            # Macro & Fiber Grid (ALCOHOL SEPARATED OUT OF PERCENTAGE LOOP)
            macro_labels  = ["Protein", "Carbs", "Fat"]
            macro_colors  = ["#FF375F", "#0A84FF", "#FFD60A"]
            macro_indices = [16, 17, 18]
            
            m1, m2, m3, m4, m5 = st.columns(5)
            
            # 1-3. True Macros (%)
            m_cols = [m1, m2, m3]
            for i, (lbl, color, idx) in enumerate(zip(macro_labels, macro_colors, macro_indices)):
                val_raw = clean_float(y.iloc[idx])
                m_cols[i].markdown(f"""
                  <div class='card' style='border-bottom: 3px solid {color};'>
                    <div class='label'>{lbl} Split</div>
                    <div class='val-sm count-up' data-target='{val_raw}' data-decimals='1' data-suffix='%'>{fmt_num(val_raw, 1, '%')}</div>
                  </div>""", unsafe_allow_html=True)

            # 4. Alcohol Metric (FIX: Displayed as Caloric Contribution)
            alc_kcal = clean_float(y.iloc[19]) if len(y) > 19 else 0.0
            m4.markdown(f"""
              <div class='card' style='border-bottom: 3px solid #BF5AF2;'>
                <div class='label'>Alcohol Intake</div>
                <div class='val-sm count-up' data-target='{alc_kcal}' data-decimals='0' data-suffix=' kcal'>{fmt_num(alc_kcal, 0, ' kcal')}</div>
              </div>""", unsafe_allow_html=True)

            # 5. Fiber Intake (Index 20)
            fiber_g = clean_float(y.iloc[20]) if len(y) > 20 else 0.0
            m5.markdown(f"""
              <div class='card' style='border-bottom: 3px solid #30D158;'>
                <div class='label'>Dietary Fiber</div>
                <div class='val-sm count-up' data-target='{fiber_g}' data-decimals='1' data-suffix=' g'>{fmt_num(fiber_g, 1, ' g')}</div>
              </div>""", unsafe_allow_html=True)

            # Status Modifiers / Debuff Engine Section
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='section-sub' style='margin-bottom:0.6rem;'>Active Status Modifiers & Recovery Impact</div>", unsafe_allow_html=True)
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
        # Ensure scale metrics strictly adhere to whole lbs for current actual readings
        with c1:
            st.markdown(card("Total Loss", num_target=clean_float(l.iloc[6]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Total Loss %", display_val=f"{l.iloc[7]}"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("To Target", num_target=clean_float(l.iloc[8]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("To Target %", display_val=f"{l.iloc[9]}"), unsafe_allow_html=True)
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
    #  TAB 4 — Hydration & Electrolyte Recovery
    # ══════════════════════════════════════════
    with tab4:
        hyd_series = get_num(24)
        sod_series = get_num(25)
        pot_series = get_num(26)
        mag_series = get_num(27)

        st.markdown("<div class='section-header'>Hydration & Electrolytes</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Fluid Volume & Mineral Recovery Balance</div>", unsafe_allow_html=True)

        # Chart: Hydration Volume
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=hyd_series, name="Hydration (ml)",
            marker=dict(color=hyd_series, colorscale=[[0, '#0A84FF'], [1, '#64D2FF']], line=dict(width=1, color='rgba(255,255,255,0.6)')),
        ))
        fig.add_hline(y=3000, line_dash="dash", line_color="#0A84FF", annotation_text="3,000 ml TARGET", annotation_font_color="#0A84FF")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Hydration", "MEASURED IN MILLILITERS"), use_container_width=True)

        # Electrolyte Suite Summary Cards
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        ec1, ec2, ec3, ec4 = st.columns(4)
        
        last_sod = sod_series.iloc[-1] if not sod_series.empty else 0
        last_pot = pot_series.iloc[-1] if not pot_series.empty else 0
        last_mag = mag_series.iloc[-1] if not mag_series.empty else 0
        k_na_ratio = (last_pot / last_sod) if last_sod > 0 else 0.0

        with ec1:
            st.markdown(card("Sodium Intake", num_target=last_sod, decimals=0, suffix=" mg"), unsafe_allow_html=True)
        with ec2:
            st.markdown(card("Potassium Intake", num_target=last_pot, decimals=0, suffix=" mg"), unsafe_allow_html=True)
        with ec3:
            st.markdown(card("Magnesium Intake", num_target=last_mag, decimals=0, suffix=" mg"), unsafe_allow_html=True)
        with ec4:
            st.markdown(card("K : Na Balance Ratio", num_target=k_na_ratio, decimals=2, suffix=""), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 5 — Weight Trajectory
    # ══════════════════════════════════════════
    with tab5:
        w_series = get_num(3).dropna()
        # Ensure scale readings treat numbers as whole lbs
        w_series_whole = w_series.round(0)
        w_max = float(w_series_whole.max()) + 2 if not w_series_whole.empty else 210

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series_whole), 0], y=w_series_whole,
            name="Weight (lbs)", mode='lines+markers',
            line=dict(color='#1D1D1F', width=2),
            marker=dict(color='#BF5AF2', size=8, symbol='circle', line=dict(color='#ffffff', width=1.5)),
            zorder=3
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series_whole), 0], y=w_series_whole, mode='lines', line=dict(color='rgba(191,90,242,0.35)', width=10), hoverinfo='skip', showlegend=False, zorder=2))
        fig.add_hline(y=170, line_dash="dash", line_color="#0A84FF", annotation_text="🎯 GOAL: 170 lbs", annotation_font_color="#0A84FF", annotation_position="top left")

        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory", "DAILY MORNING SCALE READINGS (WHOLE LBS)"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Daily Gain / Loss Variance Trend
    # ══════════════════════════════════════════
    with tab6:
        # TEMPORAL OFFSET ALIGNMENT: Telemetry on Row X drives scale shift from Row X-1 to Row X.
        w_series = get_num(3)
        weight_delta = w_series - w_series.shift(1)
        colors_trend = ['#30D158' if v <= 0 else '#FF375F' for v in weight_delta.fillna(0)]

        fig = go.Figure()
        fig.add_hrect(y0=-5, y1=0, fillcolor='rgba(48,209,88,0.06)', layer="below", line_width=0)
        fig.add_hrect(y0=0,  y1=5, fillcolor='rgba(255,55,95,0.06)', layer="below", line_width=0)
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=weight_delta, mode='lines+markers',
            line=dict(color='#FF9F0A', width=2),
            marker=dict(color=colors_trend, size=7, symbol='circle', line=dict(color='#ffffff', width=1.5)),
            name="Daily Shift (lbs)", fill='tozeroy', fillcolor='rgba(255,159,10,0.10)',
        ))
        fig.add_hline(y=0, line_dash="solid", line_color="#1D1D1F", line_width=1.5)
        fig.update_layout(yaxis=dict(range=[-5, 5]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Scale Shift", "NET DAY-OVER-DAY WEIGHT DELTA (LBS)"), use_container_width=True)

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
        st.plotly_chart(apply_theme(fig, "Daily Kinetic Steps", "TARGET: 10,000 STEPS"), use_container_width=True)

        st.markdown("<div style='margin-top:22px'></div>", unsafe_allow_html=True)
        steps_logged = steps_data.dropna()
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(card("7-Day Avg Steps", num_target=steps_logged.tail(7).mean(), decimals=0), unsafe_allow_html=True)
        with sc2:
            st.markdown(card("30-Day Avg Steps", num_target=steps_logged.tail(30).mean(), decimals=0), unsafe_allow_html=True)
        with sc3:
            st.markdown(card("90-Day Avg Steps", num_target=steps_logged.tail(90).mean(), decimals=0), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 8 — Macros & Fiber Tracking
    # ══════════════════════════════════════════
    with tab8:
        st.markdown("<div class='section-header'>Macronutrient & Fiber Profiling</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Proportional Distribution & Daily Roughage</div>", unsafe_allow_html=True)

        # Macro Line Splines
        fig_m = go.Figure()
        macro_cfg = [(16, "Protein", "#FF375F", "rgba(255,55,95,0.10)"), (17, "Carbs", "#0A84FF", "rgba(10,132,255,0.10)"),
