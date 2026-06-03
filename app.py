import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components
import time
import re

st.set_page_config(page_title="Hardy House Command", layout="wide", initial_sidebar_state="collapsed")

# ── Boot Sequence Notification ──
if 'booted' not in st.session_state:
    st.toast('System Online. Welcome to Hardy House Command.', icon='🚀')
    time.sleep(0.5)
    st.toast('Telemetry Synced. All sensors nominal.', icon='🟢')
    st.session_state.booted = True

# ─────────────────────────────────────────────
#  PREMIUM CSS — macOS Dark Mode & Liquid Glass
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700;800&family=Space+Mono&display=swap');

/* ── Root tokens ── */
:root {
  --glass-bg:        rgba(20, 20, 25, 0.45);
  --glass-bg-hover:  rgba(30, 30, 35, 0.65);
  --glass-border:    rgba(255,255,255,0.15);
  --glass-border-hi: rgba(255,255,255,0.3);
  --glass-shadow:    0 8px 32px rgba(0,0,0,0.5), 0 1px 0 rgba(255,255,255,0.1) inset;
  --glass-shadow-lg: 0 20px 50px rgba(0,0,0,0.8), 0 1px 0 rgba(255,255,255,0.2) inset;
  --blur:            blur(24px) saturate(180%);
  --blur-sm:         blur(12px) saturate(160%);

  --text-primary:   #ffffff;
  --text-secondary: rgba(255,255,255,0.9);
  
  --font-display: 'Syne', sans-serif;
  --font-body:    'Instrument Sans', sans-serif;
  --font-mono:    'Space Mono', monospace;
  
  --radius-xl: 24px;
  --radius-lg: 16px;
}

/* ── Base reset ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Background ── */
.stApp {
  background-image: url('https://raw.githubusercontent.com/nodramallama89/Weight-tracker/main/BG.jpg');
  background-size: cover;
  background-attachment: fixed;
  background-position: center;
  font-family: var(--font-body);
}

.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, rgba(10,132,255,0.1) 0%, transparent 70%),
              linear-gradient(135deg, rgba(0,0,0,0.5) 0%, rgba(0,5,15,0.85) 100%);
  pointer-events: none;
  z-index: 0;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1600px; z-index: 1; position: relative; }

/* ── Typewriter Page Title ── */
.typewriter-text {
  font-family: var(--font-display) !important;
  font-size: 2.8rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em !important;
  color: var(--text-primary) !important;
  text-align: center !important;
  margin-bottom: 0.3rem !important;
  background: linear-gradient(135deg, #ffffff 30%, #5ac8fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  border-right: 4px solid #5ac8fa;
  animation: typing 2s steps(30, end), blink-caret 0.75s step-end infinite;
}

@keyframes typing { from { width: 0 } to { width: 100% } }
@keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: #5ac8fa; } }

/* ── GLASS CARD WITH 3D HOVER ── */
.card {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-radius: var(--radius-xl);
  padding: 24px 20px 20px;
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  border-top-color: rgba(255,255,255,0.25);
  text-align: center;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: springUpFade 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: var(--glass-shadow-lg);
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hi);
}

/* Shimmer sweep on load */
.card::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(105deg, transparent 20%, rgba(255,255,255,0.12) 50%, transparent 80%);
  animation: shimmer 3s infinite 0.5s;
  pointer-events: none;
}

/* ── Card Typography (HIGH CONTRAST) ── */
.val { font-family: var(--font-display); font-size: 2.3rem; font-weight: 700; margin: 6px 0 4px; line-height: 1; color: #ffffff; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
.val-sm { font-family: var(--font-display); font-size: 1.7rem; font-weight: 700; margin: 6px 0 4px; line-height: 1; color: #ffffff; }
.label { font-family: var(--font-mono); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; color: #ffffff; opacity: 0.95; }

.delta { font-family: var(--font-body); font-size: 0.8rem; font-weight: 700; margin-top: 10px; padding: 6px 14px; border-radius: 50px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.3); color: #ffffff; }
.delta-pos { background: rgba(48, 209, 88, 0.25); border: 1px solid rgba(48, 209, 88, 0.5); text-shadow: 0 1px 3px rgba(0,0,0,0.8); }
.delta-neg { background: rgba(255, 69, 58, 0.25); border: 1px solid rgba(255, 69, 58, 0.5); text-shadow: 0 1px 3px rgba(0,0,0,0.8); }

/* ── Section header ── */
.section-header { font-family: var(--font-display); font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin: 0 0 1.2rem; text-align: center; animation: springUpFade 0.5s both; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
.section-sub { font-family: var(--font-mono); font-size: 0.85rem; color: #5ac8fa; text-align: center; margin-top: -0.8rem; margin-bottom: 1.5rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; }

/* ── Tab bar (HIGH CONTRAST) ── */
div[data-baseweb="tab-list"] {
  background: rgba(0,0,0,0.3) !important;
  backdrop-filter: var(--blur-sm) !important;
  border-radius: 18px !important;
  padding: 8px !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.6) !important;
  margin-bottom: 2rem !important;
  flex-wrap: wrap !important;
}
div[data-baseweb="tab"] { border-radius: 12px !important; transition: all 0.3s ease !important; }
div[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.15) !important; transform: translateY(-2px); }
div[data-baseweb="tab"][aria-selected="true"] { background: rgba(10,132,255,0.3) !important; box-shadow: 0 0 20px rgba(10,132,255,0.5), inset 0 0 0 1px rgba(10,132,255,0.6) !important; }
div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-family: var(--font-body) !important; color: #ffffff !important; font-size: 0.95rem !important; font-weight: 700 !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }

/* ── Chart wrapper ── */
.stPlotlyChart {
  background: rgba(15,15,20,0.4) !important;
  backdrop-filter: var(--blur) !important;
  border-radius: var(--radius-xl) !important;
  padding: 16px !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  box-shadow: 0 15px 40px rgba(0,0,0,0.7) !important;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
  animation: springUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both !important;
}
.stPlotlyChart:hover { box-shadow: 0 25px 60px rgba(0,0,0,0.9), 0 0 20px rgba(10,132,255,0.2) !important; border-color: rgba(255,255,255,0.3) !important; transform: translateY(-4px) !important; }

/* ── Animations ── */
@keyframes springUpFade { 
  0% { opacity: 0; transform: translateY(40px) scale(0.95); filter: blur(4px); } 
  100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); } 
}
@keyframes shimmer { 0% { left: -100%; } 100% { left: 200%; } }
@keyframes breathingGlow { 0% { box-shadow: 0 0 20px rgba(10,132,255,0.3); } 50% { box-shadow: 0 0 50px rgba(10,132,255,0.7); } 100% { box-shadow: 0 0 20px rgba(10,132,255,0.3); } }

/* Staggered load */
.card:nth-child(1) { animation-delay: 0.05s; }
.card:nth-child(2) { animation-delay: 0.10s; }
.card:nth-child(3) { animation-delay: 0.15s; }
.card:nth-child(4) { animation-delay: 0.20s; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.3); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
def apply_theme(fig, title="", subtitle=""):
    full_title = f"<b>{title}</b>" + (f"<br><span style='font-size:12px;color:rgba(255,255,255,0.6);font-family:Space Mono'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(family="Syne, sans-serif", color='#ffffff', size=20), x=0.03, xanchor='left', y=0.96),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Instrument Sans, sans-serif", color='rgba(255,255,255,0.85)', size=12),
        legend=dict(font=dict(color='#ffffff', size=11), bgcolor='rgba(0,0,0,0.6)', bordercolor='rgba(255,255,255,0.3)', borderwidth=1, x=0.01, y=0.99, orientation='h'),
        xaxis=dict(
            color='rgba(255,255,255,0.7)', gridcolor='rgba(255,255,255,0.08)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.8)",
            showgrid=True, zeroline=False
        ),
        yaxis=dict(
            color='rgba(255,255,255,0.7)', gridcolor='rgba(255,255,255,0.08)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="rgba(10,132,255,0.8)",
            zeroline=False
        ),
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(10,15,30,0.95)', bordercolor='#0a84ff', font=dict(color='#ffffff', size=13, family='Space Mono, monospace')),
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
#  HELPERS
# ─────────────────────────────────────────────
def get_num(idx):
    return pd.to_numeric(df.iloc[:, idx].astype(str).str.replace('%', '').str.replace(',', ''), errors='coerce')

def clean_float(val):
    try:
        cleaned = re.sub(r'[^\d\.-]', '', str(val))
        if cleaned in ['', '-', '.']: return 0.0
        return float(cleaned)
    except:
        return 0.0

def card(label, display_val="", num_target=None, decimals=0, suffix="", delta_val=None, delta_label="", size="normal", invert=False):
    val_class = "val" if size == "normal" else "val-sm"
    
    if num_target is not None:
        val_class += " count-up"
        val_html = f"<div class='{val_class}' data-target='{num_target}' data-decimals='{decimals}' data-suffix='{suffix}'>0</div>"
    else:
        val_html = f"<div class='{val_class}'>{display_val}</div>"

    delta_html = ""
    if delta_val is not None:
        # Invert logic allows us to dictate that an UP arrow (gain/increase) is RED, and DOWN is GREEN.
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

    # ── Animated Header ──
    st.markdown("""
    <div style='text-align:center; margin-bottom:0.2rem; animation: springUpFade 0.5s ease both;'>
      <span style='font-family:Space Mono,monospace; font-size:0.75rem; font-weight:700; letter-spacing:0.2em; color:#ffffff; opacity: 0.8;'>
        <span style='display:inline-block; width:8px; height:8px; background-color:#30d158; border-radius:50%; margin-right:8px; box-shadow: 0 0 12px #30d158; animation: blink-caret 1s infinite;'></span>
        SYSTEM_ACTIVE
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='typewriter-text'>Command Centre</h1></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-bottom:2.5rem; animation: springUpFade 0.8s ease 0.5s both;'>
      <span style='font-family:Space Mono,monospace; font-size:0.85rem; color:#5ac8fa; font-weight: 700;'>
        [ DATA_SYNC: GOOGLE_SHEETS // TELEMETRY: NOMINAL ]
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab bar (14 Tabs) ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs([
        "🛡️ Review", "📊 Lifetime", "🔥 Calories", "💧 Hydration", "⚖️ Weight",
        "📉 Trend", "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ BP", "🎯 Target", "🏆 Trophies", "🧠 Analytics", "📋 Sit Rep"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Review (Yesterday's Debrief)
    # ══════════════════════════════════════════
    with tab1:
        completed = df[df.iloc[:, 12] != ""]
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "LATEST_DATA"
            cals  = clean_float(y.iloc[1])
            steps = clean_float(y.iloc[12])

            st.markdown("<div class='section-header'>Yesterday's Debrief</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>[{date_str}]</div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            cal_delta  = cals  - 1633
            step_delta = steps - 10000
            with c1:
                cal_arrow    = "▲" if cal_delta > 0 else "▼"
                cal_pill_cls = "delta-neg" if cal_delta > 0 else "delta-pos"
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Calories Consumed</div>
                    <div class='val count-up' data-target='{cals}' data-decimals='0' data-suffix=' kcal'>0</div>
                    <div class='delta {cal_pill_cls}'>{cal_arrow} {abs(cal_delta):,.0f} vs Target</div>
                  </div>""", unsafe_allow_html=True)
            with c2:
                step_arrow    = "▲" if step_delta >= 0 else "▼"
                step_pill_cls = "delta-pos" if step_delta >= 0 else "delta-neg"
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Steps Taken</div>
                    <div class='val count-up' data-target='{steps}' data-decimals='0' data-suffix=''>0</div>
                    <div class='delta {step_pill_cls}'>{step_arrow} {abs(step_delta):,.0f} vs Target</div>
                  </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

            macro_labels  = ["Protein", "Carbs", "Fat", "Alcohol"]
            macro_colors  = ["#ff453a", "#5ac8fa", "#ffd60a", "#bf5af2"]
            macro_indices = [16, 17, 18, 19]
            m = st.columns(4)
            for i, (lbl, color, idx) in enumerate(zip(macro_labels, macro_colors, macro_indices)):
                val_raw = clean_float(y.iloc[idx])
                m[i].markdown(f"""
                  <div class='card' style='border-bottom: 4px solid {color}; box-shadow: 0 10px 20px rgba(0,0,0,0.5), 0 5px 15px {color}33;'>
                    <div class='label'>{lbl}</div>
                    <div class='val-sm count-up' data-target='{val_raw}' data-decimals='1' data-suffix='%'>0</div>
                  </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab2:
        l = df.iloc[-1]
        st.markdown("<div class='section-header'>Lifetime Stats</div>", unsafe_allow_html=True)

        st.markdown(f"""
          <div class='card' style='background:linear-gradient(135deg,rgba(10,132,255,0.25),rgba(0,0,0,0.6));
               border-color:rgba(10,132,255,0.7); margin-bottom:1.5rem; animation: breathingGlow 4s infinite, springUpFade 0.7s both;'>
            <div class='label' style='color:#5ac8fa; font-size:0.85rem; letter-spacing:0.3em;'>// ACTIVE_STREAK</div>
            <div class='count-up' data-target='{len(df)}' data-decimals='0' style='font-family:Syne,sans-serif; font-size:4.8rem; font-weight:800;
                        color:#ffffff; margin:10px 0; line-height:1; 
                        text-shadow: 0 0 20px #0a84ff, 0 0 40px #5ac8fa;'>0</div>
            <div style='font-family:Space Mono,monospace; font-size:0.85rem; color:#ffffff; font-weight:700;'>CONSECUTIVE DAYS LOGGED</div>
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
        colorscale = [[0.0, '#1a5c34'], [norm(1633), '#30d158'], [norm(1634), '#ff9f0a'], [norm(1700), '#ff6b1a'], [norm(1701), '#ff453a'], [1.0, '#cc1100']]
        clean_cs = []
        seen = set()
        for pos, col in colorscale:
            if pos not in seen:
                seen.add(pos)
                clean_cs.append([pos, col])

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=cal_series, name="Calories In",
            marker=dict(color=cal_series, colorscale=clean_cs, cmin=cal_min, cmax=cal_max, line=dict(width=0)), opacity=0.9,
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(2), name="Net Calories", mode='lines', line=dict(color='#ffffff', width=2.5, dash='dot')))
        fig.add_hline(y=1633, line_dash="dash", line_color="#30d158", annotation_text="Target 1,633", annotation_font_color="#30d158")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Caloric Intake", "≤1,633 GREEN // >1,700 RED"), use_container_width=True)

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
                colorscale=[[0, '#0a84ff'], [1, '#5ac8fa']], 
                line=dict(width=1, color='rgba(255,255,255,0.3)')
            ),
        ))
        
        fig.add_hline(y=3000, line_dash="dash", line_color="#5ac8fa", annotation_text="3,000 ml TARGET", annotation_font_color="#5ac8fa")
        
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)'), type="date"))
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
            line=dict(color='#ffffff', width=2),
            marker=dict(color='#bf5af2', size=8, symbol='diamond', line=dict(color='#ffffff', width=1)),
            zorder=3
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series), 0], y=w_series, mode='lines', line=dict(color='rgba(191,90,242,0.5)', width=12), hoverinfo='skip', showlegend=False, zorder=2))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series), 0], y=w_series, mode='lines', line=dict(color='rgba(191,90,242,0.2)', width=24), hoverinfo='skip', showlegend=False, zorder=1))

        fig.add_hline(y=170, line_dash="dash", line_color="#5ac8fa", annotation_text="🎯 GOAL: 170 lbs", annotation_font_color="#5ac8fa", annotation_position="top left")

        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory", "DAILY ACTUALS // NEON HUD ACTIVATED"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Gain / Loss Trend
    # ══════════════════════════════════════════
    with tab6:
        trend = get_num(5)
        colors_trend = ['#30d158' if v < 0 else '#ff453a' for v in trend.fillna(0)]
        fig = go.Figure()
        fig.add_hrect(y0=-5, y1=0, fillcolor='rgba(48,209,88,0.08)', layer="below", line_width=0)
        fig.add_hrect(y0=0,  y1=5, fillcolor='rgba(255,69,58,0.08)', layer="below", line_width=0)
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=trend, mode='lines+markers',
            line=dict(color='#ff9f0a', width=2),
            marker=dict(color=colors_trend, size=7, symbol='cross', line=dict(color='#ffffff', width=1)),
            name="Net Trend", fill='tozeroy', fillcolor='rgba(255,159,10,0.15)',
        ))
        fig.add_hline(y=0, line_dash="solid", line_color="#ffffff", line_width=2)
        fig.update_layout(yaxis=dict(range=[-5, 5]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Weight Variance", "RANGE ±5 LBS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 7 — Steps
    # ══════════════════════════════════════════
    with tab7:
        steps_data  = get_num(12)
        def step_color(s):
            if s >= 10000: return '#30d158'
            elif s >= 8001: return '#ff9f0a'
            else: return '#ff453a'
        step_colors = [step_color(s) for s in steps_data.fillna(0)]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=steps_data, name="Steps",
            marker=dict(color=step_colors, line=dict(width=1, color='rgba(255,255,255,0.3)')),
        ))
        fig.add_hline(y=10000, line_dash="dash", line_color="#30d158", annotation_text="10K TARGET", annotation_font_color="#30d158")
        fig.add_hline(y=8000, line_dash="dot", line_color="#ff453a", annotation_text="8K FLOOR", annotation_font_color="#ff453a")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Daily Steps", "STATUS: TRACKING"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 8 — Macros
    # ══════════════════════════════════════════
    with tab8:
        fig = go.Figure()
        macro_cfg = [(16, "Protein", "#ff453a", "rgba(255,69,58,0.15)"), (17, "Carbs", "#5ac8fa", "rgba(90,200,250,0.15)"), (18, "Fat", "#ffd60a", "rgba(255,214,10,0.15)")]
        for idx, name, color, fill in macro_cfg:
            series = get_num(idx)
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0], y=series, name=name, mode='lines',
                line=dict(color=color, width=3, shape='spline'),
                fill='tozeroy', fillcolor=fill,
            ))
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
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
        fig.add_hrect(y0=60, y1=80, fillcolor='rgba(48,209,88,0.08)', layer="below", line_width=0)
        fig.add_hrect(y0=80, y1=90, fillcolor='rgba(255,214,10,0.08)', layer="below", line_width=0)
        fig.add_hrect(y0=90, y1=180, fillcolor='rgba(255,69,58,0.08)', layer="below", line_width=0)
        
        fig.add_hline(y=120, line_dash="dash", line_color="#30d158", annotation_text="SYS IDEAL", annotation_font_color="#30d158")
        fig.add_hline(y=80, line_dash="dash", line_color="#5ac8fa", annotation_text="DIA IDEAL", annotation_font_color="#5ac8fa")

        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=sys_data, name="Systolic", mode='lines+markers', connectgaps=True, line=dict(color='#ff453a', width=3), marker=dict(size=8, color='#ff453a', line=dict(color='#ffffff', width=1.5))))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=dia_data, name="Diastolic", mode='lines+markers', connectgaps=True, line=dict(color='#5ac8fa', width=3), marker=dict(size=8, color='#5ac8fa', line=dict(color='#ffffff', width=1.5))))

        fig.update_layout(yaxis=dict(range=[60, 180]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
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
                title = {'text': "Current Weight (lbs)", 'font': {'color': 'rgba(255,255,255,0.7)', 'size': 18, 'family': 'Space Mono'}},
                delta = {'reference': start_w, 'increasing': {'color': '#ff453a'}, 'decreasing': {'color': '#30d158'}},
                gauge = {
                    'axis': {'range': [goal_w - 5, start_w + 5], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
                    'bar': {'color': "#5ac8fa"},
                    'bgcolor': "rgba(0,0,0,0.4)",
                    'borderwidth': 2,
                    'bordercolor': "rgba(255,255,255,0.2)",
                    'steps': [
                        {'range': [goal_w, goal_w + 10], 'color': "rgba(48,209,88,0.2)"},
                        {'range': [goal_w + 10, start_w], 'color': "rgba(255,159,10,0.15)"}
                    ],
                    'threshold': {'line': {'color': "#bf5af2", 'width': 5}, 'thickness': 0.85, 'value': goal_w}
                }
            ))
            
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white', family='Syne'), height=450, margin=dict(t=60, b=40))
            st.markdown("<div class='card' style='padding: 0; border: none; background: transparent; box-shadow: none;'>", unsafe_allow_html=True)
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
                glow = "box-shadow: 0 0 25px rgba(48,209,88,0.3); border-color: rgba(48,209,88,0.6);"
                val_color = "#30d158"
                status = "UNLOCKED"
            else:
                glow = "opacity: 0.4; filter: grayscale(100%); background: rgba(0,0,0,0.6);"
                val_color = "#ffffff"
                status = "LOCKED"
                
            return f"""
            <div class='card' style='{glow} transition: all 0.3s ease; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size:2.5rem; margin-bottom:8px; text-shadow: 0 5px 15px rgba(0,0,0,0.5);'>{b['icon']}</div>
                <div class='label' style='color:{val_color}; margin-bottom:4px; letter-spacing:0.15em;'>{status}</div>
                <div class='val-sm' style='font-size:1.1rem; margin-bottom:2px;'>{b['title']}</div>
                <div style='font-family:Space Mono,monospace; font-size:0.7rem; color:rgba(255,255,255,0.7);'>{b['desc']}</div>
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
        st.markdown("<div class='section-sub'>Cause and Effect Analysis</div>", unsafe_allow_html=True)

        w_series = get_num(3)
        cals_series = get_num(1)
        steps_series = get_num(12)
        hyd_series = get_num(24)
        prot_series = get_num(16)

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
        
        cal_insight_color = "#30d158" if avg_change_good_cals < 0 else "#ff9f0a"
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
        temp_df = pd.DataFrame({'day': df.iloc[:, 0].dt.day_name(), 'diff': next_day_weight_diff})
        day_means = temp_df.groupby('day')['diff'].mean().dropna()
        if not day_means.empty:
            best_day = day_means.idxmin()
            worst_day = day_means.idxmax()
        else:
            best_day, worst_day = "N/A", "N/A"

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px;'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>🔥</div>
            <div class='val-sm' style='margin-bottom: 15px; color: #5ac8fa;'>Caloric Efficiency Engine</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.9); line-height: 1.6;'>
                When your daily intake stays <b>at or below your 1,633 target</b>, your following day's weight changes by an average of <span style='color: {cal_insight_color}; font-weight: bold;'>{cal_str_good}</span>. 
                Conversely, when you exceed the calorie limit, your next day's weight changes by an average of <span style='color: #ff453a; font-weight: bold;'>{cal_str_bad}</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px;'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>👟</div>
            <div class='val-sm' style='margin-bottom: 15px; color: #5ac8fa;'>Kinetic Success Rate</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.9); line-height: 1.6;'>
                Hitting your 10,000 step goal yields a <span style='color: #30d158; font-weight: bold; font-size: 1.2em;'>{success_rate:.0f}%</span> success rate for a weight drop on the scale the very next morning. Consistency here directly influences the trendline.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px;'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>💧</div>
            <div class='val-sm' style='margin-bottom: 15px; color: #5ac8fa;'>The Hydration Catalyst</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.9); line-height: 1.6;'>
                Drinking 3L or more of water gives you a <span style='color: #30d158; font-weight: bold;'>{hyd_success_good:.0f}%</span> chance of dropping weight the next day. On days you miss your water target, that drops to <span style='color: #ff9f0a; font-weight: bold;'>{hyd_success_bad:.0f}%</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px;'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>🥩</div>
            <div class='val-sm' style='margin-bottom: 15px; color: #5ac8fa;'>Protein Power Correlation</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.9); line-height: 1.6;'>
                On days where protein makes up 30%+ of your macros, your next day's average scale shift is <span style='font-weight: bold;'>{avg_change_high_prot:+.2f} lbs</span>. On days under 30%, the shift averages <span style='font-weight: bold;'>{avg_change_low_prot:+.2f} lbs</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px;'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>📅</div>
            <div class='val-sm' style='margin-bottom: 15px; color: #5ac8fa;'>The Weekly Profiler</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.9); line-height: 1.6;'>
                Historically, <span style='color: #30d158; font-weight: bold;'>{best_day}s</span> are when you see the biggest drops on the scale. By contrast, <span style='color: #ff453a; font-weight: bold;'>{worst_day}s</span> tend to be your most resistant days.
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
                st.markdown(card("Weight Change (7 Days)", display_val=f"{l7_change:+.1f} lbs", delta_val=change_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)

        else:
            st.info("System requires at least 14 days of telemetry to generate a comparative Sit Rep.")


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
                
                let suffixHtml = suffix ? "<span style='font-size:0.65em; opacity:0.6; margin-left:4px;'>" + suffix + "</span>" : "";
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
    st.error("SYSTEM FAILURE: Data link severed. Check credentials.")
