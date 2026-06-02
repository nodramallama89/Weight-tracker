import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import time

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

def card(label, value, delta_val=None, delta_label="", color=None, size="normal"):
    val_class = "val" if size == "normal" else "val-sm"
    delta_html = ""
    if delta_val is not None:
        cls   = "delta-pos" if delta_val >= 0 else "delta-neg"
        arrow = "▲" if delta_val >= 0 else "▼"
        delta_html = f"<div class='delta {cls}'>{arrow} {abs(delta_val):,.0f} {delta_label}</div>"
    return f"""
    <div class='card'>
      <div class='label'>{label}</div>
      <div class='{val_class}'>{value}</div>
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

    # ── Tab bar ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🛡️ Review", "📊 Lifetime", "🔥 Calories", "⚖️ Weight",
        "📉 Trend", "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ BP"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Review (Yesterday's Debrief)
    # ══════════════════════════════════════════
    with tab1:
        completed = df[df.iloc[:, 12] != ""]
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "LATEST_DATA"
            cals  = float(str(y.iloc[1]).replace(',', ''))
            steps = float(str(y.iloc[12]).replace(',', ''))

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
                    <div class='val'>{cals:,.0f} <span style='font-size:1rem; opacity:0.6'>kcal</span></div>
                    <div class='delta {cal_pill_cls}'>{cal_arrow} {abs(cal_delta):,.0f} vs Target</div>
                  </div>""", unsafe_allow_html=True)
            with c2:
                step_arrow    = "▲" if step_delta >= 0 else "▼"
                step_pill_cls = "delta-pos" if step_delta >= 0 else "delta-neg"
                st.markdown(f"""
                  <div class='card'>
                    <div class='label'>Steps Taken</div>
                    <div class='val'>{steps:,.0f}</div>
                    <div class='delta {step_pill_cls}'>{step_arrow} {abs(step_delta):,.0f} vs Target</div>
                  </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

            macro_labels  = ["Protein", "Carbs", "Fat", "Alcohol"]
            macro_colors  = ["#ff453a", "#5ac8fa", "#ffd60a", "#bf5af2"]
            macro_indices = [16, 17, 18, 19]
            m = st.columns(4)
            for i, (lbl, color, idx) in enumerate(zip(macro_labels, macro_colors, macro_indices)):
                val_raw = str(y.iloc[idx]).replace('%', '')
                m[i].markdown(f"""
                  <div class='card' style='border-bottom: 4px solid {color}; box-shadow: 0 10px 20px rgba(0,0,0,0.5), 0 5px 15px {color}33;'>
                    <div class='label'>{lbl}</div>
                    <div class='val-sm'>{val_raw}%</div>
                  </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab2:
        l = df.iloc[-1]
        st.markdown("<div class='section-header'>Lifetime Stats</div>", unsafe_allow_html=True)

        # Breathing Glow Hero Card
        st.markdown(f"""
          <div class='card' style='background:linear-gradient(135deg,rgba(10,132,255,0.25),rgba(0,0,0,0.6));
               border-color:rgba(10,132,255,0.7); margin-bottom:1.5rem; animation: breathingGlow 4s infinite, springUpFade 0.7s both;'>
            <div class='label' style='color:#5ac8fa; font-size:0.85rem; letter-spacing:0.3em;'>// ACTIVE_STREAK</div>
            <div style='font-family:Syne,sans-serif; font-size:4.8rem; font-weight:800;
                        color:#ffffff; margin:10px 0; line-height:1; 
                        text-shadow: 0 0 20px #0a84ff, 0 0 40px #5ac8fa;'>{len(df)}</div>
            <div style='font-family:Space Mono,monospace; font-size:0.85rem; color:#ffffff; font-weight:700;'>CONSECUTIVE DAYS LOGGED</div>
          </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Total Loss", f"{l.iloc[6]} lbs"), unsafe_allow_html=True)
            st.markdown(card("Total Loss", f"{l.iloc[7]} st"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("To Target", f"{l.iloc[8]} lbs"), unsafe_allow_html=True)
            st.markdown(card("To Target", f"{l.iloc[9]} st"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Current BMI", f"{l.iloc[10]}"), unsafe_allow_html=True)
            st.markdown(card("To Target BMI", f"{l.iloc[11]}"), unsafe_allow_html=True)

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
    #  TAB 4 — Weight (The Neon Upgrade)
    # ══════════════════════════════════════════
    with tab4:
        w_series = get_num(3).dropna()
        w_max = float(w_series.max()) + 2 if not w_series.empty else 210
        
        fig = go.Figure()
        
        # 1. The Core Line (Thin, bright white/purple)
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            name="Weight", mode='lines+markers',
            line=dict(color='#ffffff', width=2),
            marker=dict(color='#bf5af2', size=8, symbol='diamond', line=dict(color='#ffffff', width=1)),
            zorder=3
        ))
        
        # 2. The Outer Glow (Thick, highly transparent line)
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            mode='lines', line=dict(color='rgba(191,90,242,0.5)', width=12),
            hoverinfo='skip', showlegend=False, zorder=2
        ))
        
        # 3. The Ambient Aura (Even thicker, very transparent)
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            mode='lines', line=dict(color='rgba(191,90,242,0.2)', width=24),
            hoverinfo='skip', showlegend=False, zorder=1
        ))

        # Target Goal Projection
        fig.add_hline(y=170, line_dash="dash", line_color="#5ac8fa", 
                      annotation_text="🎯 GOAL: 170 lbs", annotation_font_color="#5ac8fa", 
                      annotation_position="top left")

        fig.update_layout(
            yaxis=dict(range=[168, w_max]),
            xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(255,255,255,0.2)'), type="date")
        )
        st.plotly_chart(apply_theme(fig, "Weight Trajectory", "DAILY ACTUALS // NEON HUD ACTIVATED"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 5 — Gain / Loss Trend
    # ══════════════════════════════════════════
    with tab5:
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
    #  TAB 6 — Steps
    # ══════════════════════════════════════════
    with tab6:
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
    #  TAB 7 — Macros
    # ══════════════════════════════════════════
    with tab7:
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
    #  TAB 8 — Averages
    # ══════════════════════════════════════════
    with tab8:
        avg_loss = (get_num(3).iloc[0] - get_num(3).iloc[-1]) / (len(df) / 7)
        st.markdown("<div class='section-header'>Historical Data</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Avg Cals / Day", f"{get_num(1).mean():,.0f}"), unsafe_allow_html=True)
            st.markdown(card("Avg Protein", f"{get_num(16).mean():.0f}%"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("Avg Steps / Day", f"{get_num(12).mean():,.0f}"), unsafe_allow_html=True)
            st.markdown(card("Avg Carbs", f"{get_num(17).mean():.0f}%"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Avg Loss / Week", f"{avg_loss:.2f} lbs"), unsafe_allow_html=True)
            st.markdown(card("Avg Fat", f"{get_num(18).mean():.0f}%"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 9 — Blood Pressure
    # ══════════════════════════════════════════
    with tab9:
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

else:
    st.error("SYSTEM FAILURE: Data link severed. Check credentials.")
