import streamlit as st
import pandas as pd
import numpy as np
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import time
import re

st.set_page_config(page_title="Hardy House Health", layout="wide", initial_sidebar_state="collapsed")

# ── Boot Sequence Notification ──
if 'booted' not in st.session_state:
    st.toast('Welcome back — data synced.', icon='✅')
    time.sleep(0.5)
    st.toast('All metrics up to date.', icon='💚')
    st.session_state.booted = True

# ─────────────────────────────────────────────
#  PREMIUM CSS — Apple Health / Fitness Light Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Root tokens ── */
:root {
  --bg-app:          #F2F2F7;
  --bg-card:         #FFFFFF;
  --bg-card-soft:    #F7F7FA;
  --bg-card-muted:   #EFEFF3;

  --glass-bg:        rgba(255,255,255,0.68);
  --glass-bg-hover:  rgba(255,255,255,0.80);
  --glass-border:    rgba(255,255,255,0.55);
  --glass-blur:      blur(28px) saturate(180%);
  --glass-blur-sm:   blur(16px) saturate(160%);

  --border-subtle:   rgba(60,60,67,0.08);
  --border-strong:   rgba(60,60,67,0.16);

  --shadow-card:       0 1px 2px rgba(15,23,42,0.05), 0 14px 34px rgba(15,23,42,0.10);
  --shadow-card-hover: 0 6px 14px rgba(15,23,42,0.08), 0 26px 54px rgba(15,23,42,0.16);

  --text-primary:   #1D1D1F;
  --text-secondary: rgba(60,60,67,0.72);
  --text-tertiary:  rgba(60,60,67,0.45);

  --font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  --font-body:    'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
  --font-caption: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  /* Apple Health / Fitness system accents */
  --red:    #FF375F;
  --orange: #FF9F0A;
  --yellow: #FFD60A;
  --green:  #30D158;
  --teal:   #64D2FF;
  --blue:   #0A84FF;
  --purple: #BF5AF2;
  --pink:   #FF2D55;

  --radius-xl: 22px;
  --radius-lg: 16px;
  --radius-md: 12px;
}

/* ── Base reset ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Background ── */
.stApp {
  background-image:
    linear-gradient(180deg, rgba(242,242,247,0.50) 0%, rgba(242,242,247,0.82) 55%, rgba(242,242,247,0.94) 100%),
    url('https://github.com/nodramallama89/Weight-tracker/blob/33fc966fe489b029049541e417658a7441afa776/Gemini_Generated_Image_1zukku1zukku1zuk.png?raw=true');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: var(--font-body);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1600px; }

/* ── Page Title ── */
.page-eyebrow {
  font-family: var(--font-caption);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-tertiary);
  text-align: center;
  display: block;
  margin-bottom: 0.4rem;
  animation: fadeUp 0.5s ease both;
}
.page-eyebrow .status-dot {
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  background-color: var(--green); margin-right: 7px;
  box-shadow: 0 0 0 4px rgba(48,209,88,0.15);
}

.page-title {
  font-family: var(--font-display) !important;
  font-size: 2.6rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.02em !important;
  color: var(--text-primary) !important;
  text-align: center !important;
  margin: 0 0 0.25rem !important;
  animation: fadeUp 0.6s ease 0.05s both;
  text-shadow: 0 1px 12px rgba(255,255,255,0.6);
}

.page-subtitle {
  font-family: var(--font-body);
  font-size: 0.92rem;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 2.2rem;
  font-weight: 500;
  animation: fadeUp 0.7s ease 0.1s both;
}

/* ── Frosted glass card ── */
.card {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl);
  padding: 22px 20px 20px;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.6);
  border: 1px solid var(--glass-border);
  text-align: center;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  animation: springUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,0.7);
  border-color: rgba(255,255,255,0.8);
  background: var(--glass-bg-hover);
}

/* ── Card Typography ── */
.val { font-family: var(--font-display); font-size: 2.2rem; font-weight: 800; margin: 4px 0 4px; line-height: 1; color: var(--text-primary); letter-spacing: -0.02em; }
.val-sm { font-family: var(--font-display); font-size: 1.55rem; font-weight: 800; margin: 4px 0 4px; line-height: 1; color: var(--text-primary); letter-spacing: -0.01em; }
.label { font-family: var(--font-caption); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-tertiary); }

.delta { font-family: var(--font-body); font-size: 0.78rem; font-weight: 700; margin-top: 10px; padding: 5px 13px; border-radius: 50px; display: inline-block; box-shadow: 0 2px 8px rgba(15,23,42,0.06); }
.delta-pos { background: rgba(48, 209, 88, 0.16); color: #1E9145; border: 1px solid rgba(48, 209, 88, 0.3); }
.delta-neg { background: rgba(255, 55, 95, 0.14); color: #E0264F; border: 1px solid rgba(255, 55, 95, 0.28); }

/* ── Section header ── */
.section-header { font-family: var(--font-display); font-size: 1.6rem; font-weight: 800; color: var(--text-primary); margin: 0 0 0.3rem; text-align: center; letter-spacing: -0.01em; animation: fadeUp 0.5s both; text-shadow: 0 1px 12px rgba(255,255,255,0.6); }
.section-sub { font-family: var(--font-caption); font-size: 0.8rem; color: var(--text-tertiary); text-align: center; margin-top: 0; margin-bottom: 1.6rem; letter-spacing: 0.04em; text-transform: uppercase; font-weight: 600; }

/* ── Tab bar → iOS segmented control (frosted) ── */
div[data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.45) !important;
  backdrop-filter: var(--glass-blur-sm) !important;
  -webkit-backdrop-filter: var(--glass-blur-sm) !important;
  border-radius: 16px !important;
  padding: 6px !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card) !important;
  margin-bottom: 2rem !important;
  flex-wrap: wrap !important;
  gap: 2px;
}
div[data-baseweb="tab"] { border-radius: 11px !important; transition: all 0.25s ease !important; }
div[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.35) !important; }
div[data-baseweb="tab"][aria-selected="true"] { background: rgba(255,255,255,0.92) !important; box-shadow: 0 2px 6px rgba(15,23,42,0.10), 0 1px 1px rgba(15,23,42,0.04) !important; }
div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-family: var(--font-body) !important; color: var(--text-secondary) !important; font-size: 0.9rem !important; font-weight: 600 !important; }
div[data-baseweb="tab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }

/* ── Chart wrapper (frosted) ── */
.stPlotlyChart {
  background: var(--glass-bg) !important;
  backdrop-filter: var(--glass-blur) !important;
  -webkit-backdrop-filter: var(--glass-blur) !important;
  border-radius: var(--radius-xl) !important;
  padding: 18px !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255,255,255,0.6) !important;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
  animation: springUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both !important;
}
.stPlotlyChart:hover { box-shadow: var(--shadow-card-hover), inset 0 1px 0 rgba(255,255,255,0.7) !important; }

/* ── Animations ── */
@keyframes springUpFade {
  0% { opacity: 0; transform: translateY(18px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Staggered load */
.card:nth-child(1) { animation-delay: 0.03s; }
.card:nth-child(2) { animation-delay: 0.06s; }
.card:nth-child(3) { animation-delay: 0.09s; }
.card:nth-child(4) { animation-delay: 0.12s; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 10px; }

/* DataFrame Styling (frosted) */
[data-testid="stDataFrame"] {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-card);
  padding: 10px;
}

/* st.info boxes (frosted) */
div[data-testid="stAlert"] {
  background: var(--glass-bg) !important;
  backdrop-filter: var(--glass-blur-sm) !important;
  -webkit-backdrop-filter: var(--glass-blur-sm) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-card) !important;
  color: var(--text-secondary) !important;
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
        legend=dict(font=dict(color='#1D1D1F', size=11), bgcolor='rgba(255,255,255,0.9)', bordercolor='rgba(60,60,67,0.12)', borderwidth=1, x=0.01, y=0.99, orientation='h'),
        xaxis=dict(
            color='rgba(60,60,67,0.55)', gridcolor='rgba(60,60,67,0.07)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.6)",
            showgrid=True, zeroline=False
        ),
        yaxis=dict(
            color='rgba(60,60,67,0.55)', gridcolor='rgba(60,60,67,0.07)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.6)",
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
    except:
        return pd.DataFrame()

df = load_data()

# ─────────────────────────────────────────────
#  "COMPLETED DAYS ONLY" VIEW
# ─────────────────────────────────────────────
# The sheet contains rows for future/upcoming dates that haven't been logged
# yet (blank cells). As the sheet has grown, more of these trailing blank
# rows now sit after your most recent real entry. Tabs that grabbed data via
# df.iloc[-1] / df.iloc[-7:] / df.mean() etc. on the *raw* dataframe were
# picking up those blank rows instead of your actual latest data — that's
# what was causing Lifetime / Averages / Sit Rep / Forecast to show zeros.
#
# Tab 1 (Review) already worked around this by filtering on Steps (col 12)
# being non-blank. We apply that same "completed day" filter once here and
# reuse it everywhere that needs "the latest real day" or "an average over
# real days" rather than raw sheet rows.
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
    src = df if source is None else source
    return pd.to_numeric(src.iloc[:, idx].astype(str).str.replace('%', '').str.replace(',', ''), errors='coerce')

def clean_float(val):
    try:
        cleaned = re.sub(r'[^\d\.-]', '', str(val))
        if cleaned in ['', '-', '.']: return 0.0
        return float(cleaned)
    except:
        return 0.0

def safe(x):
    """Coerce NaN/None to 0.0 so we never leak the string 'nan' into HTML/JS attributes."""
    try:
        return float(x) if pd.notna(x) else 0.0
    except (TypeError, ValueError):
        return 0.0

def fmt_num(value, decimals=0, suffix=''):
    """
    Pre-render a number exactly the way the JS odometer would at the end of
    its animation (comma-separated, fixed decimals, suffix). This is used as
    the *initial* content of .count-up divs so the correct value is visible
    immediately even if the JS animation never runs (e.g. if the iframe's
    window.parent.document access gets blocked by a Streamlit/browser
    sandboxing change). The JS still animates on top of this when it works.
    """
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
#  MAIN APP
# ─────────────────────────────────────────────
if not df.empty:

    # ── Header ──
    st.markdown("""
    <span class='page-eyebrow'><span class='status-dot'></span>SYNCED WITH GOOGLE SHEETS</span>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='page-title'>Health Summary</h1></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='page-subtitle'>Your daily wellness, tracked and trending</div>
    """, unsafe_allow_html=True)

    # ── Tab bar (17 Tabs) ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16, tab17 = st.tabs([
        "🛡️ Review", "📊 Lifetime", "🔥 Calories", "💧 Hydration", "⚖️ Weight",
        "📉 Trend", "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ BP", "🎯 Target", "🏆 Trophies", "🧠 Analytics", "📋 Sit Rep", "🔮 Forecast", "⚡ Momentum", "🗄️ Data Log"
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

            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

            macro_labels  = ["Protein", "Carbs", "Fat", "Alcohol"]
            macro_colors  = ["#FF375F", "#0A84FF", "#FFD60A", "#BF5AF2"]
            macro_indices = [16, 17, 18, 19]
            m = st.columns(4)
            for i, (lbl, color, idx) in enumerate(zip(macro_labels, macro_colors, macro_indices)):
                val_raw = clean_float(y.iloc[idx])
                m[i].markdown(f"""
                  <div class='card' style='border-bottom: 3px solid {color};'>
                    <div class='label'>{lbl}</div>
                    <div class='val-sm count-up' data-target='{val_raw}' data-decimals='1' data-suffix='%'>{fmt_num(val_raw, 1, '%')}</div>
                  </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab2:
        # Today's row is added first thing in the morning with date/weight
        # filled in, while calories/steps/etc. are only completed at day's
        # end — that's expected and normal, so we read straight off the raw
        # last row here, same as the original app did.
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
            st.markdown(card("Total Loss", display_val=f"{l.iloc[7]}"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("To Target", num_target=clean_float(l.iloc[8]), decimals=1, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("To Target", display_val=f"{l.iloc[9]}"), unsafe_allow_html=True)
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
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)', bordercolor='rgba(60,60,67,0.12)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Caloric Intake", "≤1,633 GREEN // >1,700 RED"), use_container_width=True)

        # Rolling averages, computed only over days that actually have a
        # logged value (dropna) so trailing blank/future sheet rows never
        # dilute the window — same "completed days" principle as df_valid.
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
            marker=dict(
                color=hyd_series,
                colorscale=[[0, '#0A84FF'], [1, '#64D2FF']],
                line=dict(width=1, color='rgba(255,255,255,0.6)')
            ),
        ))

        fig.add_hline(y=3000, line_dash="dash", line_color="#0A84FF", annotation_text="3,000 ml TARGET", annotation_font_color="#0A84FF")

        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)', bordercolor='rgba(60,60,67,0.12)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Hydration", "MEASURED IN MILLILITERS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 5 — Weight
    # ══════════════════════════════════════════
    with tab5:
        w_series = get_num(3).dropna()
        w_max = float(w_series.max()) + 2 if not w_series.empty else 210

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            name="Weight", mode='lines+markers',
            line=dict(color='#1D1D1F', width=2),
            marker=dict(color='#BF5AF2', size=8, symbol='circle', line=dict(color='#ffffff', width=1.5)),
            zorder=3
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series), 0], y=w_series, mode='lines', line=dict(color='rgba(191,90,242,0.35)', width=10), hoverinfo='skip', showlegend=False, zorder=2))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series), 0], y=w_series, mode='lines', line=dict(color='rgba(191,90,242,0.12)', width=20), hoverinfo='skip', showlegend=False, zorder=1))

        fig.add_hline(y=170, line_dash="dash", line_color="#0A84FF", annotation_text="🎯 GOAL: 170 lbs", annotation_font_color="#0A84FF", annotation_position="top left")

        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)', bordercolor='rgba(60,60,67,0.12)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory", "DAILY ACTUALS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Gain / Loss Trend
    # ══════════════════════════════════════════
    with tab6:
        trend = get_num(5)
        colors_trend = ['#30D158' if v < 0 else '#FF375F' for v in trend.fillna(0)]
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

        # Same "completed days only" rolling average approach as Calories.
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
        macro_cfg = [(16, "Protein", "#FF375F", "rgba(255,55,95,0.10)"), (17, "Carbs", "#0A84FF", "rgba(10,132,255,0.10)"), (18, "Fat", "#FFD60A", "rgba(255,214,10,0.12)")]
        for idx, name, color, fill in macro_cfg:
            series = get_num(idx)
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0], y=series, name=name, mode='lines',
                line=dict(color=color, width=3, shape='spline'),
                fill='tozeroy', fillcolor=fill,
            ))
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Macro Composition", "SMOOTHED SPLINE PROJECTIONS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 9 — Averages
    # ══════════════════════════════════════════
    with tab9:
        avg_loss = (get_num(3).iloc[0] - get_num(3).iloc[-1]) / (len(df) / 7)
        st.markdown("<div class='section-header'>Historical Data</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Avg Cals / Day", num_target=get_num(1).mean(), decimals=0), unsafe_allow_html=True)
            st.markdown(card("Avg Protein", num_target=get_num(16).mean(), decimals=0, suffix="%"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("Avg Steps / Day", num_target=get_num(12).mean(), decimals=0), unsafe_allow_html=True)
            st.markdown(card("Avg Carbs", num_target=get_num(17).mean(), decimals=0, suffix="%"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Avg Loss / Week", num_target=avg_loss, decimals=2, suffix=" lbs"), unsafe_allow_html=True)
            st.markdown(card("Avg Fat", num_target=get_num(18).mean(), decimals=0, suffix="%"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 10 — Blood Pressure
    # ══════════════════════════════════════════
    with tab10:
        sys_data = get_num(21)
        dia_data = get_num(22)
        fig = go.Figure()
        fig.add_hrect(y0=60, y1=80, fillcolor='rgba(48,209,88,0.06)', layer="below", line_width=0)
        fig.add_hrect(y0=80, y1=90, fillcolor='rgba(255,214,10,0.07)', layer="below", line_width=0)
        fig.add_hrect(y0=90, y1=180, fillcolor='rgba(255,55,95,0.06)', layer="below", line_width=0)

        fig.add_hline(y=120, line_dash="dash", line_color="#30D158", annotation_text="SYS IDEAL", annotation_font_color="#1E9145")
        fig.add_hline(y=80, line_dash="dash", line_color="#0A84FF", annotation_text="DIA IDEAL", annotation_font_color="#0A84FF")

        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=sys_data, name="Systolic", mode='lines+markers', connectgaps=True, line=dict(color='#FF375F', width=3), marker=dict(size=8, color='#FF375F', line=dict(color='#ffffff', width=1.5))))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=dia_data, name="Diastolic", mode='lines+markers', connectgaps=True, line=dict(color='#0A84FF', width=3), marker=dict(size=8, color='#0A84FF', line=dict(color='#ffffff', width=1.5))))

        fig.update_layout(yaxis=dict(range=[60, 180]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Blood Pressure Monitor", "VITAL SIGNS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 11 — Target Gauge
    # ══════════════════════════════════════════
    with tab11:
        st.markdown("<div class='section-header'>Mission Progress</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Distance to 170 lbs</div>", unsafe_allow_html=True)

        w_series = get_num(3).dropna()
        if len(w_series) > 1:
            current_w = w_series.iloc[-1]
            start_w = w_series.iloc[0]
            goal_w = 170

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
            st.markdown("<div class='card' style='padding: 4px; box-shadow: var(--shadow-card);'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 12 — Trophy Room
    # ══════════════════════════════════════════
    with tab12:
        st.markdown("<div class='section-header'>The Trophy Room</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Unlock milestones through consistency</div>", unsafe_allow_html=True)

        total_days = len(df)
        cals_in = get_num(1)
        steps_arr = get_num(12)
        sys_arr = get_num(21)
        dia_arr = get_num(22)

        total_loss_lbs = clean_float(df.iloc[-1].iloc[6]) if not df.empty else 0
        min_weight = get_num(3).min()

        hyd_df = df[df[0] >= pd.Timestamp("2026-05-27")]
        hyd_arr_filtered = pd.to_numeric(hyd_df.iloc[:, 24], errors='coerce')
        perfect_hyd_days = (hyd_arr_filtered >= 3000).sum()
        hyd_days_tracked = len(hyd_df)

        perfect_cals_days = ((cals_in > 0) & (cals_in <= 1633)).sum()
        perfect_steps_days = (steps_arr >= 10000).sum()
        ideal_bp_days = ((sys_arr > 0) & (sys_arr <= 120) & (dia_arr > 0) & (dia_arr <= 80)).sum()

        def get_pct(days, total):
            return (days / total * 100) if total > 0 else 0

        badges = [
            {"title": "Iron Will", "desc": f"{perfect_cals_days} Days ({get_pct(perfect_cals_days, total_days):.1f}%) ≤ 1,633 kcal", "unlocked": perfect_cals_days > 0, "icon": "🔥"},
            {"title": "Marathoner", "desc": f"{perfect_steps_days} Days ({get_pct(perfect_steps_days, total_days):.1f}%) ≥ 10k Steps", "unlocked": perfect_steps_days > 0, "icon": "👟"},
            {"title": "Aqua Lung", "desc": f"{perfect_hyd_days} Days ({get_pct(perfect_hyd_days, hyd_days_tracked):.1f}%) ≥ 3L Water", "unlocked": perfect_hyd_days > 0, "icon": "💧"},
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
                val_color = "#1E9145"
                status = "UNLOCKED"
            else:
                extra = "opacity: 0.5; background: var(--bg-card-soft);"
                val_color = "var(--text-tertiary)"
                status = "LOCKED"

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
        st.markdown("<div class='section-sub'>Cause and Effect Analysis — Last 90 Days</div>", unsafe_allow_html=True)

        # This tab used to average over your *entire* history. With many
        # months of data, a single new day barely moves a lifetime average —
        # e.g. day 251 changing an average of 250 days looks like nothing
        # happened. That's why it looked static/hardcoded even though it was
        # genuinely recalculating every time. Windowing to the most recent
        # 90 completed days (same df_valid filter used elsewhere, so trailing
        # blank sheet rows are excluded) makes it responsive to how you've
        # actually been doing lately, not diluted by day 1.
        analytics_window = df_valid.tail(90).reset_index(drop=True)

        w_series = get_num(3, analytics_window)
        cals_series = get_num(1, analytics_window)
        steps_series = get_num(12, analytics_window)
        hyd_series = get_num(24, analytics_window)
        prot_series = get_num(16, analytics_window)

        # Shift weight by -1 to get the 'next day' weight for correlation
        next_day_weight_diff = w_series.shift(-1) - w_series
        valid_days_mask = next_day_weight_diff.notna()

        # 1. Caloric Impact
        good_cal_mask = (cals_series <= 1633) & valid_days_mask
        bad_cal_mask = (cals_series > 1633) & valid_days_mask

        avg_change_good_cals = next_day_weight_diff[good_cal_mask].mean()
        avg_change_bad_cals = next_day_weight_diff[bad_cal_mask].mean()
        avg_change_good_cals = avg_change_good_cals if pd.notna(avg_change_good_cals) else 0
        avg_change_bad_cals = avg_change_bad_cals if pd.notna(avg_change_bad_cals) else 0

        cal_insight_color = "#1E9145" if avg_change_good_cals < 0 else "#FF9F0A"
        cal_str_good = f"{avg_change_good_cals:+.2f} lbs"
        cal_str_bad = f"{avg_change_bad_cals:+.2f} lbs"

        # 2. Step Impact
        good_step_mask = (steps_series >= 10000) & valid_days_mask
        success_rate = (next_day_weight_diff[good_step_mask] < 0).sum() / good_step_mask.sum() * 100 if good_step_mask.sum() > 0 else 0

        # 3. Hydration Impact
        good_hyd_mask = (hyd_series >= 3000) & valid_days_mask
        bad_hyd_mask = (hyd_series < 3000) & (hyd_series > 0) & valid_days_mask
        hyd_success_good = (next_day_weight_diff[good_hyd_mask] < 0).sum() / good_hyd_mask.sum() * 100 if good_hyd_mask.sum() > 0 else 0
        hyd_success_bad = (next_day_weight_diff[bad_hyd_mask] < 0).sum() / bad_hyd_mask.sum() * 100 if bad_hyd_mask.sum() > 0 else 0

        # 4. Protein Power
        high_prot_mask = (prot_series >= 30) & valid_days_mask
        low_prot_mask = (prot_series < 30) & (prot_series > 0) & valid_days_mask
        avg_change_high_prot = next_day_weight_diff[high_prot_mask].mean()
        avg_change_low_prot = next_day_weight_diff[low_prot_mask].mean()
        avg_change_high_prot = avg_change_high_prot if pd.notna(avg_change_high_prot) else 0
        avg_change_low_prot = avg_change_low_prot if pd.notna(avg_change_low_prot) else 0

        # 5. Day of the week profiler
        temp_df = pd.DataFrame({'day': analytics_window.iloc[:, 0].dt.day_name(), 'diff': next_day_weight_diff})
        day_means = temp_df.groupby('day')['diff'].mean().dropna()
        if not day_means.empty:
            best_day = day_means.idxmin()
            worst_day = day_means.idxmax()
        else:
            best_day, worst_day = "N/A", "N/A"

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 28px; margin-bottom: 16px;'>
            <div style='font-size: 1.8rem; margin-bottom: 8px;'>🔥</div>
            <div class='val-sm' style='margin-bottom: 12px; color: #0A84FF;'>Caloric Efficiency Engine</div>
            <div style='font-family: var(--font-body); font-size: 1.05rem; color: var(--text-secondary); line-height: 1.6;'>
                When your daily intake stays <b style='color:var(--text-primary);'>at or below your 1,633 target</b>, your following day's weight changes by an average of <span style='color: {cal_insight_color}; font-weight: 700;'>{cal_str_good}</span>.
                Conversely, when you exceed the calorie limit, your next day's weight changes by an average of <span style='color: #E0264F; font-weight: 700;'>{cal_str_bad}</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 28px; margin-bottom: 16px;'>
            <div style='font-size: 1.8rem; margin-bottom: 8px;'>👟</div>
            <div class='val-sm' style='margin-bottom: 12px; color: #0A84FF;'>Kinetic Success Rate</div>
            <div style='font-family: var(--font-body); font-size: 1.05rem; color: var(--text-secondary); line-height: 1.6;'>
                Hitting your 10,000 step goal yields a <span style='color: #1E9145; font-weight: 700; font-size: 1.15em;'>{success_rate:.0f}%</span> success rate for a weight drop on the scale the very next morning. Consistency here directly influences the trendline.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 28px; margin-bottom: 16px;'>
            <div style='font-size: 1.8rem; margin-bottom: 8px;'>💧</div>
            <div class='val-sm' style='margin-bottom: 12px; color: #0A84FF;'>The Hydration Catalyst</div>
            <div style='font-family: var(--font-body); font-size: 1.05rem; color: var(--text-secondary); line-height: 1.6;'>
                Drinking 3L or more of water gives you a <span style='color: #1E9145; font-weight: 700;'>{hyd_success_good:.0f}%</span> chance of dropping weight the next day. On days you miss your water target, that drops to <span style='color: #FF9F0A; font-weight: 700;'>{hyd_success_bad:.0f}%</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 28px; margin-bottom: 16px;'>
            <div style='font-size: 1.8rem; margin-bottom: 8px;'>🥩</div>
            <div class='val-sm' style='margin-bottom: 12px; color: #0A84FF;'>Protein Power Correlation</div>
            <div style='font-family: var(--font-body); font-size: 1.05rem; color: var(--text-secondary); line-height: 1.6;'>
                On days where protein makes up 30%+ of your macros, your next day's average scale shift is <span style='font-weight: 700; color:var(--text-primary);'>{avg_change_high_prot:+.2f} lbs</span>. On days under 30%, the shift averages <span style='font-weight: 700; color:var(--text-primary);'>{avg_change_low_prot:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 28px; margin-bottom: 16px;'>
            <div style='font-size: 1.8rem; margin-bottom: 8px;'>📅</div>
            <div class='val-sm' style='margin-bottom: 12px; color: #0A84FF;'>The Weekly Profiler</div>
            <div style='font-family: var(--font-body); font-size: 1.05rem; color: var(--text-secondary); line-height: 1.6;'>
                Historically, <span style='color: #1E9145; font-weight: 700;'>{best_day}s</span> are when you see the biggest drops on the scale. By contrast, <span style='color: #E0264F; font-weight: 700;'>{worst_day}s</span> tend to be your most resistant days.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 14 — Weekly Sit Rep
    # ══════════════════════════════════════════
    with tab14:
        st.markdown("<div class='section-header'>Weekly Sit Rep</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Last 7 Days vs Previous 7 Days</div>", unsafe_allow_html=True)

        if len(df) >= 14:
            last_7 = df.iloc[-7:]
            prev_7 = df.iloc[-14:-7]

            # Extract data
            l7_cals = pd.to_numeric(last_7.iloc[:, 1], errors='coerce').mean()
            p7_cals = pd.to_numeric(prev_7.iloc[:, 1], errors='coerce').mean()

            l7_steps = pd.to_numeric(last_7.iloc[:, 12], errors='coerce').mean()
            p7_steps = pd.to_numeric(prev_7.iloc[:, 12], errors='coerce').mean()

            # Use raw start vs end to get change in weight (so drops are negative numbers)
            l7_w_start = pd.to_numeric(last_7.iloc[0, 3], errors='coerce')
            l7_w_end = pd.to_numeric(last_7.iloc[-1, 3], errors='coerce')
            l7_change = l7_w_end - l7_w_start

            p7_w_start = pd.to_numeric(prev_7.iloc[0, 3], errors='coerce')
            p7_w_end = pd.to_numeric(prev_7.iloc[-1, 3], errors='coerce')
            p7_change = p7_w_end - p7_w_start

            # Deltas
            cal_diff = l7_cals - p7_cals
            step_diff = l7_steps - p7_steps
            change_diff = l7_change - p7_change

            col1, col2, col3 = st.columns(3)
            with col1:
                # invert=True means an UP arrow (increase) is painted RED, DOWN is GREEN
                st.markdown(card("Avg Cals (7 Days)", num_target=l7_cals, decimals=0, suffix=" kcal", delta_val=cal_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)
            with col2:
                # invert=False (default) means an UP arrow (increase) is painted GREEN, DOWN is RED
                st.markdown(card("Avg Steps (7 Days)", num_target=l7_steps, decimals=0, delta_val=step_diff, delta_label="vs Prev", invert=False), unsafe_allow_html=True)
            with col3:
                # invert=True so if loss is bigger (more negative), the arrow is DOWN but painted GREEN
                st.markdown(card("Weight Change (7 Days)", display_val=f"{safe(l7_change):+.1f} lbs", delta_val=change_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)

        else:
            st.info("System requires at least 14 days of telemetry to generate a comparative Sit Rep.")

    # ══════════════════════════════════════════
    #  TAB 15 — Forecast Projection
    # ══════════════════════════════════════════
    with tab15:
        st.markdown("<div class='section-header'>Forecasting Engine</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Estimated Time of Arrival (ETA) to 170 lbs</div>", unsafe_allow_html=True)

        w_series = get_num(3).dropna()
        if len(w_series) >= 14:
            # Use a linear regression (least-squares trend line) over a
            # wider recent window rather than just comparing the first vs.
            # last day. Comparing two single points is very noisy — one bad
            # (or good) day at either end of the window can flip the whole
            # read to "neutral/positive" even when the overall trend is
            # clearly downward. A regression line smooths that out.
            window = min(21, len(w_series))
            recent = w_series.tail(window).reset_index(drop=True)
            x = np.arange(len(recent))
            slope, _intercept = np.polyfit(x, recent.values, 1)  # lbs per day, negative = losing
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
                        Based on your {window}-day trend of dropping {loss_rate_per_day*7:.1f} lbs per week.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif current_w <= 170:
                st.markdown("<div class='card'><div class='val' style='color:#1E9145;'>TARGET ACHIEVED</div></div>", unsafe_allow_html=True)
            else:
                st.info(f"Your {window}-day trend is currently flat or trending up ({loss_rate_per_day*7:+.1f} lbs/week). Maintain a continuous deficit to generate an ETA.")
        else:
            st.info("Requires at least 14 days of logged weight data to calculate a reliable projection.")

    # ══════════════════════════════════════════
    #  TAB 16 — Momentum (Daily Health Score)
    # ══════════════════════════════════════════
    # A single composite score (0-100) per day, built from four things you're
    # already tracking every day: calories, steps, hydration, protein. Each
    # contributes up to 25 points, scaled by how close you got to its target
    # (partial credit, not just pass/fail) — so a day at 9,200 steps still
    # scores well instead of getting nothing for missing 10k by a little.
    # Runs on df_valid (completed days only) so trailing blank sheet rows
    # can't drag a "streak" down to zero.
    with tab16:
        st.markdown("<div class='section-header'>Momentum</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Daily Health Score — Calories + Steps + Hydration + Protein</div>", unsafe_allow_html=True)

        momentum_days = df_valid
        if len(momentum_days) >= 1:
            cal_m   = get_num(1, momentum_days).replace(0, np.nan)
            steps_m = get_num(12, momentum_days)
            hyd_m   = get_num(24, momentum_days)
            prot_m  = get_num(16, momentum_days)

            cal_score   = (1633 / cal_m).clip(upper=1).fillna(0) * 25
            step_score  = (steps_m / 10000).clip(upper=1).fillna(0) * 25
            hyd_score   = (hyd_m / 3000).clip(upper=1).fillna(0) * 25
            prot_score  = (prot_m / 30).clip(upper=1).fillna(0) * 25

            daily_score = (cal_score + step_score + hyd_score + prot_score).round(0).clip(upper=100)

            def score_band(s):
                if s >= 75: return ("On Track", "#30D158", "rgba(48,209,88,0.14)")
                elif s >= 50: return ("Getting There", "#FF9F0A", "rgba(255,159,10,0.14)")
                else: return ("Needs Focus", "#FF375F", "rgba(255,55,95,0.12)")

            latest_score = safe(daily_score.iloc[-1])
            latest_date  = str(momentum_days.iloc[-1, 0])[:10]
            latest_label, latest_color, latest_fill = score_band(latest_score)

            good_day = daily_score >= 75
            # Current streak: consecutive ≥75 days trailing the most recent entry
            current_streak = 0
            for v in good_day.tolist()[::-1]:
                if v: current_streak += 1
                else: break
            # Best streak ever: longest unbroken run of ≥75 days anywhere in history
            streak_groups = (~good_day).cumsum()
            best_streak = int(good_day.groupby(streak_groups).sum().max()) if len(good_day) else 0

            best_idx = daily_score.idxmax()
            best_score = safe(daily_score.loc[best_idx])
            best_date = str(momentum_days.loc[best_idx].iloc[0])[:10]

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Today's Score</div>
                    <div class='val' style='color:{latest_color};'>{latest_score:.0f}<span style='font-size:0.5em; opacity:0.6;'>/100</span></div>
                    <div class='delta' style='background:{latest_fill}; color:{latest_color}; border:1px solid {latest_color}55;'>{latest_label}</div>
                  </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(card("Current Streak", display_val=f"{current_streak} {'day' if current_streak == 1 else 'days'}", delta_val=None), unsafe_allow_html=True)
            with c3:
                st.markdown(card("Best Streak Ever", display_val=f"{best_streak} {'day' if best_streak == 1 else 'days'}"), unsafe_allow_html=True)

            st.markdown(f"""
              <div class='card' style='text-align:left; padding:24px 28px; margin-top:4px;'>
                <div style='display:flex; align-items:center; gap:18px;'>
                  <div style='font-size:2.2rem;'>🏅</div>
                  <div>
                    <div class='label' style='margin-bottom:4px;'>Personal Best Day</div>
                    <div style='font-family:var(--font-body); font-size:0.98rem; color:var(--text-secondary);'>
                      <b style='color:var(--text-primary);'>{best_date}</b> scored <b style='color:#1E9145;'>{best_score:.0f}/100</b> — your strongest day on record for hitting calories, steps, hydration and protein together.
                    </div>
                  </div>
                </div>
              </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

            trend_window = min(90, len(momentum_days))
            recent_dates = momentum_days.iloc[:, 0].tail(trend_window)
            recent_scores = daily_score.tail(trend_window)
            recent_colors = [score_band(s)[1] for s in recent_scores]

            fig = go.Figure()
            fig.add_hrect(y0=75, y1=100, fillcolor='rgba(48,209,88,0.06)', layer="below", line_width=0)
            fig.add_hrect(y0=50, y1=75, fillcolor='rgba(255,159,10,0.06)', layer="below", line_width=0)
            fig.add_hrect(y0=0, y1=50, fillcolor='rgba(255,55,95,0.06)', layer="below", line_width=0)
            fig.add_trace(go.Scatter(
                x=recent_dates, y=recent_scores, mode='lines+markers', name='Daily Score',
                line=dict(color='#0A84FF', width=2.5),
                marker=dict(color=recent_colors, size=7, line=dict(color='#ffffff', width=1.5)),
                fill='tozeroy', fillcolor='rgba(10,132,255,0.08)',
            ))
            fig.add_hline(y=75, line_dash="dash", line_color="#30D158", annotation_text="ON TRACK", annotation_font_color="#1E9145")
            fig.update_layout(yaxis=dict(range=[0, 100]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.03)'), type="date"))
            st.plotly_chart(apply_theme(fig, "Momentum Trend", f"LAST {trend_window} DAYS // SCORE OUT OF 100"), use_container_width=True)
        else:
            st.info("Log a few days of calories, steps, hydration and protein to start building a Momentum score.")

    # ══════════════════════════════════════════
    #  TAB 17 — Raw Telemetry Log
    # ══════════════════════════════════════════
    with tab17:
        st.markdown("<div class='section-header'>Raw Telemetry</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Latest 30 Days Data Log</div>", unsafe_allow_html=True)

        # Format the dataframe for display
        display_df = df.copy()
        display_df[0] = display_df[0].dt.strftime('%Y-%m-%d')
        display_df = display_df.iloc[::-1].head(30) # Newest first
        display_df.columns = [str(i) for i in range(len(display_df.columns))] # temp columns to avoid issues

        # Pick the most important columns to show so it fits nicely
        cols_to_show = {
            '0': 'Date', '1': 'Cals In', '3': 'Weight (lbs)', '12': 'Steps',
            '16': 'Protein %', '17': 'Carbs %', '18': 'Fat %', '24': 'Water (ml)'
        }

        clean_df = display_df[list(cols_to_show.keys())].rename(columns=cols_to_show)

        st.dataframe(
            clean_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

    # ─────────────────────────────────────────────
    #  JavaScript Odometer Injector (Tab-Aware)
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
                setTimeout(runOdometer, 50);
                break;
            }
            target = target.parentNode;
        }
    });
    </script>
    """
    components.html(js_code, height=0, width=0)

else:
    st.error("Data link severed. Check credentials.")
