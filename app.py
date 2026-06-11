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
#  CYBERPUNK NEON CSS — Midgar Terminal Vibe
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700;800&family=Space+Mono&display=swap');

/* ── Root tokens ── */
:root {
  --bg-dark:         #0a0b10;
  --glass-bg:        rgba(15, 16, 25, 0.65);
  --glass-bg-hover:  rgba(25, 28, 40, 0.85);
  
  --neon-cyan:       #00F0FF;
  --neon-pink:       #FF00A0;
  --neon-green:      #00FF66;
  --neon-yellow:     #FFEA00;
  
  --glass-border:    rgba(0, 240, 255, 0.15);
  --glass-border-hi: rgba(0, 240, 255, 0.5);
  --glass-shadow:    0 8px 32px rgba(0,0,0,0.8), inset 0 0 10px rgba(0, 240, 255, 0.05);
  --glass-shadow-lg: 0 15px 50px rgba(0,0,0,0.9), inset 0 0 20px rgba(0, 240, 255, 0.2);
  
  --blur:            blur(24px) saturate(180%);
  --blur-sm:         blur(12px) saturate(160%);

  --text-primary:   #ffffff;
  --text-secondary: rgba(255,255,255,0.7);
  
  --font-display: 'Syne', sans-serif;
  --font-body:    'Instrument Sans', sans-serif;
  --font-mono:    'Space Mono', monospace;
  
  --radius-xl: 16px;
  --radius-lg: 12px;
}

/* ── Base reset ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Background ── */
.stApp {
  background-color: var(--bg-dark);
  background-image: 
    radial-gradient(circle at 15% 50%, rgba(0, 240, 255, 0.08), transparent 25%),
    radial-gradient(circle at 85% 30%, rgba(255, 0, 160, 0.08), transparent 25%);
  background-size: cover;
  background-attachment: fixed;
  font-family: var(--font-body);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1600px; z-index: 1; position: relative; }

/* ── Typewriter Page Title ── */
.typewriter-text {
  font-family: var(--font-display) !important;
  font-size: 3rem !important;
  font-weight: 800 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase;
  color: #fff !important;
  text-align: center !important;
  margin-bottom: 0.3rem !important;
  text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan);
  
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  border-right: 4px solid var(--neon-pink);
  animation: typing 2s steps(30, end), blink-caret 0.75s step-end infinite;
}

@keyframes typing { from { width: 0 } to { width: 100% } }
@keyframes blink-caret { from, to { border-color: transparent } 50% { border-color: var(--neon-pink); } }

/* ── GLASS CARD WITH 3D HOVER ── */
.card {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-radius: var(--radius-xl);
  padding: 24px 20px 20px;
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  text-align: center;
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: var(--glass-shadow-lg);
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hi);
}

/* Shimmer sweep */
.card::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(105deg, transparent 20%, rgba(0,240,255,0.1) 50%, transparent 80%);
  animation: shimmer 4s infinite 0.5s;
  pointer-events: none;
}

/* ── Card Typography ── */
.val { font-family: var(--font-display); font-size: 2.5rem; font-weight: 800; margin: 8px 0 4px; line-height: 1; color: #ffffff; text-shadow: 0 0 15px rgba(255,255,255,0.3); }
.val-sm { font-family: var(--font-display); font-size: 1.8rem; font-weight: 800; margin: 6px 0 4px; line-height: 1; color: #ffffff; }
.label { font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em; color: var(--text-secondary); }

.delta { font-family: var(--font-mono); font-size: 0.75rem; font-weight: 700; margin-top: 12px; padding: 6px 14px; border-radius: 4px; display: inline-block; text-transform: uppercase; letter-spacing: 0.1em; }
.delta-pos { background: rgba(0, 255, 102, 0.1); border: 1px solid var(--neon-green); color: var(--neon-green); box-shadow: 0 0 10px rgba(0,255,102,0.2); }
.delta-neg { background: rgba(255, 0, 160, 0.1); border: 1px solid var(--neon-pink); color: var(--neon-pink); box-shadow: 0 0 10px rgba(255,0,160,0.2); }

/* ── Section header ── */
.section-header { font-family: var(--font-display); font-size: 1.8rem; font-weight: 800; color: #fff; margin: 0 0 1.2rem; text-align: center; text-transform: uppercase; letter-spacing: 0.1em; text-shadow: 0 0 10px rgba(255,255,255,0.3); }
.section-sub { font-family: var(--font-mono); font-size: 0.85rem; color: var(--neon-pink); text-align: center; margin-top: -0.8rem; margin-bottom: 1.5rem; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 700; }

/* ── Tab bar ── */
div[data-baseweb="tab-list"] {
  background: rgba(10,11,16,0.8) !important;
  backdrop-filter: var(--blur-sm) !important;
  border-radius: 8px !important;
  padding: 8px !important;
  border: 1px solid rgba(0,240,255,0.2) !important;
  box-shadow: 0 0 20px rgba(0,0,0,0.8) !important;
  margin-bottom: 2rem !important;
  flex-wrap: wrap !important;
}
div[data-baseweb="tab"] { border-radius: 4px !important; transition: all 0.3s ease !important; }
div[data-baseweb="tab"]:hover { background: rgba(0,240,255,0.1) !important; }
div[data-baseweb="tab"][aria-selected="true"] { background: rgba(0,240,255,0.2) !important; box-shadow: 0 0 15px rgba(0,240,255,0.4), inset 0 0 0 1px var(--neon-cyan) !important; }
div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p { font-family: var(--font-mono) !important; color: #ffffff !important; font-size: 0.85rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.1em;}
div[data-baseweb="tab-highlight"] { display: none !important; }

/* ── Chart wrapper ── */
.stPlotlyChart {
  background: rgba(15,16,25,0.5) !important;
  backdrop-filter: var(--blur) !important;
  border-radius: var(--radius-xl) !important;
  padding: 16px !important;
  border: 1px solid rgba(0,240,255,0.15) !important;
  box-shadow: 0 15px 40px rgba(0,0,0,0.7) !important;
  transition: all 0.4s ease !important;
}
.stPlotlyChart:hover { box-shadow: 0 25px 60px rgba(0,0,0,0.9), 0 0 30px rgba(0,240,255,0.1) !important; border-color: rgba(0,240,255,0.4) !important; transform: translateY(-2px) !important; }

/* ── Animations ── */
@keyframes shimmer { 0% { left: -100%; } 100% { left: 200%; } }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
::-webkit-scrollbar-thumb { background: var(--neon-cyan); border-radius: 10px; }

/* DataFrame Styling */
[data-testid="stDataFrame"] {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  padding: 10px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME (CYBERPUNK)
# ─────────────────────────────────────────────
def apply_theme(fig, title="", subtitle=""):
    full_title = f"<b style='color:#fff; text-transform:uppercase; letter-spacing:2px;'>{title}</b>" + (f"<br><span style='font-size:11px;color:#FF00A0;font-family:Space Mono;letter-spacing:1px;'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(text=full_title, font=dict(family="Syne, sans-serif", size=18), x=0.03, xanchor='left', y=0.96),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Space Mono, monospace", color='rgba(255,255,255,0.7)', size=11),
        legend=dict(font=dict(color='#ffffff', size=10), bgcolor='rgba(10,11,16,0.8)', bordercolor='rgba(0,240,255,0.3)', borderwidth=1, x=0.01, y=0.99, orientation='h'),
        xaxis=dict(
            color='rgba(255,255,255,0.5)', gridcolor='rgba(0,240,255,0.05)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="#FF00A0",
            showgrid=True, zeroline=False
        ),
        yaxis=dict(
            color='rgba(255,255,255,0.5)', gridcolor='rgba(0,240,255,0.05)',
            showspikes=True, spikemode="across", spikethickness=1, spikedash="solid", spikecolor="#FF00A0",
            zeroline=False
        ),
        margin=dict(l=20, r=20, t=70, b=20),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='rgba(10,11,16,0.95)', bordercolor='#00F0FF', font=dict(color='#ffffff', size=12, family='Space Mono, monospace')),
    )
    return fig


# ─────────────────────────────────────────────
#  DATA LOADING & SAFEGUARDS
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

# Column padding safeguard to prevent index errors
if not df.empty:
    while len(df.columns) <= 25:
        df[len(df.columns)] = ""

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_num(idx):
    if idx >= len(df.columns): return pd.Series([0.0] * len(df))
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
    <div style='text-align:center; margin-bottom:0.2rem;'>
      <span style='font-family:Space Mono,monospace; font-size:0.75rem; font-weight:700; letter-spacing:0.3em; color:#00FF66; text-shadow: 0 0 5px #00FF66;'>
        <span style='display:inline-block; width:8px; height:8px; background-color:#00FF66; border-radius:50%; margin-right:8px; box-shadow: 0 0 12px #00FF66; animation: blink-caret 1s infinite;'></span>
        SYS.LINK.ESTABLISHED
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;'><h1 class='typewriter-text'>HARDY.OS COMMAND</h1></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-bottom:2.5rem;'>
      <span style='font-family:Space Mono,monospace; font-size:0.85rem; color:#00F0FF; font-weight: 700; letter-spacing: 0.1em;'>
        [ UPLINK: SECURE // TELEMETRY: NOMINAL ]
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab bar (16 Tabs) ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16 = st.tabs([
        "🛡️ Dashboard", "📊 Lifetime", "🔥 Calories", "💧 Hydration", "⚖️ Weight",
        "📉 Trend", "👟 Steps", "🥗 Macros", "📈 Averages", "❤️ BP", "🎯 Target", "🏆 Trophies", "🧠 Analytics", "📋 Sit Rep", "🔮 Forecast", "🗄️ Data Log"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — THE CYBERPUNK DASHBOARD
    # ══════════════════════════════════════════
    with tab1:
        completed = df[df.iloc[:, 12] != ""]
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "LATEST"
            
            # Extract core metrics
            cals = clean_float(y.iloc[1])
            weight = clean_float(y.iloc[3])
            steps = clean_float(y.iloc[12])
            water = clean_float(y.iloc[24])
            
            # RPG Calculations for the visual
            cals_s = get_num(1).fillna(9999)
            steps_s = get_num(12).fillna(0)
            water_s = get_num(24).fillna(0)
            weight_s = get_num(3).dropna()

            total_exp = len(df)*50 + (cals_s<=1633).sum()*100 + (steps_s>=10000).sum()*100 + (water_s>=3000).sum()*50
            total_loss = (weight_s.iloc[0] - weight_s.iloc[-1]) if len(weight_s)>0 else 0
            if total_loss > 0: total_exp += int(total_loss * 500)
            
            current_level = int((total_exp / 150) ** 0.6) + 1
            exp_current = int(150 * ((current_level - 1) ** (1/0.6)))
            exp_next = int(150 * (current_level ** (1/0.6)))
            exp_pct = min(100, max(0, ((total_exp - exp_current) / (exp_next - exp_current)) * 100))

            step_pct = min(100, (steps / 10000) * 100)
            water_pct = min(100, (water / 3000) * 100)
            
            step_color = "#00FF66" if steps >= 10000 else "#00F0FF"
            water_color = "#00F0FF" if water >= 3000 else "#FFEA00"

            st.markdown("<div class='section-header'>Terminal Status</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>[ LOG_DATE: {date_str} ]</div>", unsafe_allow_html=True)

            # TOP DASHBOARD ROW: RPG Stats & Donut Rings
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px;">
                
                <div class="card" style="display:flex; flex-direction:column; justify-content:center; text-align:left; padding:30px; border-left: 4px solid var(--neon-pink);">
                    <div style="font-family:'Space Mono'; color:var(--neon-pink); font-size:0.8rem; letter-spacing:2px; margin-bottom:5px;">USER // BRYAN</div>
                    <div style="display:flex; align-items:baseline; justify-content:space-between; margin-bottom: 15px;">
                        <div style="font-family:'Syne'; font-size:4rem; font-weight:800; color:#fff; line-height:1; text-shadow: 0 0 20px rgba(255,255,255,0.2);">LV.{current_level}</div>
                        <div style="font-family:'Space Mono'; color:var(--neon-cyan); font-size:1rem;">{total_exp:,} EXP</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.5); height: 8px; border-radius: 4px; border: 1px solid rgba(0,240,255,0.2); overflow: hidden;">
                        <div style="background: var(--neon-cyan); width: {exp_pct}%; height: 100%; box-shadow: 0 0 10px var(--neon-cyan);"></div>
                    </div>
                    <div style="text-align:right; font-family:'Space Mono'; font-size:0.7rem; color:#aaa; margin-top:5px;">NEXT: {exp_next - total_exp:,}</div>
                </div>

                <div class="card" style="display:flex; align-items:center; justify-content:center; gap: 30px; padding:30px;">
                    <div style="width: 140px; height: 140px; border-radius: 50%; background: conic-gradient({step_color} {step_pct}%, #1a1a24 {step_pct}%); display:flex; align-items:center; justify-content:center; box-shadow: 0 0 20px {step_color}40;">
                       <div style="width: 120px; height: 120px; background: var(--bg-dark); border-radius: 50%; display:flex; align-items:center; justify-content:center; flex-direction:column; box-shadow: inset 0 0 20px rgba(0,0,0,0.8);">
                           <span style="color:#fff; font-family:'Syne'; font-size:1.8rem; font-weight:800; line-height:1;">{steps:,.0f}</span>
                           <span style="color:{step_color}; font-family:'Space Mono'; font-size:0.6rem; letter-spacing:1px; margin-top:4px;">STEPS</span>
                       </div>
                    </div>
                    <div style="text-align:left;">
                        <div style="font-family:'Space Mono'; color:#aaa; font-size:0.75rem; letter-spacing:1px;">TARGET: 10K</div>
                        <div style="font-family:'Syne'; color:#fff; font-size:1.5rem; font-weight:700; margin-top:5px;">KINETICS</div>
                        <div style="font-family:'Space Mono'; color:{step_color}; font-size:0.85rem; margin-top:5px;">{step_pct:.1f}% SYNC</div>
                    </div>
                </div>

                <div class="card" style="display:flex; align-items:center; justify-content:center; gap: 30px; padding:30px;">
                    <div style="width: 140px; height: 140px; border-radius: 50%; background: conic-gradient({water_color} {water_pct}%, #1a1a24 {water_pct}%); display:flex; align-items:center; justify-content:center; box-shadow: 0 0 20px {water_color}40;">
                       <div style="width: 120px; height: 120px; background: var(--bg-dark); border-radius: 50%; display:flex; align-items:center; justify-content:center; flex-direction:column; box-shadow: inset 0 0 20px rgba(0,0,0,0.8);">
                           <span style="color:#fff; font-family:'Syne'; font-size:1.8rem; font-weight:800; line-height:1;">{water:,.0f}</span>
                           <span style="color:{water_color}; font-family:'Space Mono'; font-size:0.6rem; letter-spacing:1px; margin-top:4px;">ML</span>
                       </div>
                    </div>
                    <div style="text-align:left;">
                        <div style="font-family:'Space Mono'; color:#aaa; font-size:0.75rem; letter-spacing:1px;">TARGET: 3L</div>
                        <div style="font-family:'Syne'; color:#fff; font-size:1.5rem; font-weight:700; margin-top:5px;">HYDRATION</div>
                        <div style="font-family:'Space Mono'; color:{water_color}; font-size:0.85rem; margin-top:5px;">{water_pct:.1f}% SYNC</div>
                    </div>
                </div>

            </div>
            """, unsafe_allow_html=True)

            # BOTTOM DASHBOARD ROW: Data Cards
            c1, c2, c3, c4 = st.columns(4)
            cal_delta = cals - 1633
            
            with c1:
                st.markdown(card("Current Mass", display_val=f"{weight:,.0f}", suffix=" lbs"), unsafe_allow_html=True) # Intentionally whole lbs
            with c2:
                cal_arrow = "▲" if cal_delta > 0 else "▼"
                cal_pill_cls = "delta-neg" if cal_delta > 0 else "delta-pos"
                st.markdown(f"""
                  <div class='card' style='border-top: 2px solid var(--neon-pink);'>
                    <div class='label'>Intake Energy</div>
                    <div class='val count-up' data-target='{cals}' data-decimals='0' data-suffix=' kcal'>0</div>
                    <div class='delta {cal_pill_cls}'>{cal_arrow} {abs(cal_delta):,.0f} vs Cap</div>
                  </div>""", unsafe_allow_html=True)
            with c3:
                prot = clean_float(y.iloc[16])
                st.markdown(card("Protein Output", num_target=prot, decimals=1, suffix="%"), unsafe_allow_html=True)
            with c4:
                carbs = clean_float(y.iloc[17])
                st.markdown(card("Carb Output", num_target=carbs, decimals=1, suffix="%"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab2:
        l = df.iloc[-1]
        st.markdown("<div class='section-header'>Lifetime Stats</div>", unsafe_allow_html=True)

        st.markdown(f"""
          <div class='card' style='background: rgba(0, 240, 255, 0.05); border-color: var(--neon-cyan); margin-bottom:1.5rem;'>
            <div class='label' style='color:var(--neon-cyan); font-size:0.85rem;'>// ACTIVE_STREAK</div>
            <div class='count-up' data-target='{len(df)}' data-decimals='0' style='font-family:Syne,sans-serif; font-size:4.8rem; font-weight:800; color:#ffffff; margin:10px 0; line-height:1; text-shadow: 0 0 20px var(--neon-cyan);'>0</div>
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
        colorscale = [[0.0, '#00FF66'], [norm(1633), '#00FF66'], [norm(1634), '#FFEA00'], [norm(1700), '#FF00A0'], [1.0, '#FF00A0']]
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
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=get_num(2), name="Net Calories", mode='lines', line=dict(color='#00F0FF', width=2.5, dash='dot')))
        fig.add_hline(y=1633, line_dash="dash", line_color="#00FF66", annotation_text="Target 1,633", annotation_font_color="#00FF66")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)', bordercolor='rgba(0,240,255,0.2)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Caloric Intake", "≤1,633 GREEN // >1,700 NEON PINK"), use_container_width=True)

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
                colorscale=[[0, '#00A0FF'], [1, '#00F0FF']], 
                line=dict(width=1, color='rgba(0,240,255,0.3)')
            ),
        ))
        fig.add_hline(y=3000, line_dash="dash", line_color="#00F0FF", annotation_text="3,000 ml TARGET", annotation_font_color="#00F0FF")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
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
            line=dict(color='#FF00A0', width=3),
            marker=dict(color='#00F0FF', size=8, symbol='diamond', line=dict(color='#ffffff', width=1)),
            zorder=3
        ))
        fig.add_trace(go.Scatter(x=df.iloc[:len(w_series), 0], y=w_series, mode='lines', line=dict(color='rgba(255,0,160,0.3)', width=14), hoverinfo='skip', showlegend=False, zorder=2))

        fig.add_hline(y=170, line_dash="dash", line_color="#00F0FF", annotation_text="🎯 GOAL: 170 lbs", annotation_font_color="#00F0FF", annotation_position="top left")
        fig.update_layout(yaxis=dict(range=[168, w_max]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Mass Trajectory", "DAILY ACTUALS // NEON HUD ACTIVATED"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Gain / Loss Trend
    # ══════════════════════════════════════════
    with tab6:
        trend = get_num(5)
        colors_trend = ['#00FF66' if v < 0 else '#FF00A0' for v in trend.fillna(0)]
        fig = go.Figure()
        fig.add_hrect(y0=-5, y1=0, fillcolor='rgba(0,255,102,0.05)', layer="below", line_width=0)
        fig.add_hrect(y0=0,  y1=5, fillcolor='rgba(255,0,160,0.05)', layer="below", line_width=0)
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=trend, mode='lines+markers',
            line=dict(color='#FFEA00', width=2),
            marker=dict(color=colors_trend, size=7, symbol='cross', line=dict(color='#ffffff', width=1)),
            name="Net Trend", fill='tozeroy', fillcolor='rgba(255,234,0,0.1)',
        ))
        fig.add_hline(y=0, line_dash="solid", line_color="#00F0FF", line_width=2)
        fig.update_layout(yaxis=dict(range=[-5, 5]), xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Mass Variance", "RANGE ±5 LBS"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 7 — Steps
    # ══════════════════════════════════════════
    with tab7:
        steps_data  = get_num(12)
        def step_color(s):
            if s >= 10000: return '#00FF66'
            elif s >= 8001: return '#FFEA00'
            else: return '#FF00A0'
        step_colors = [step_color(s) for s in steps_data.fillna(0)]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=steps_data, name="Steps",
            marker=dict(color=step_colors, line=dict(width=1, color='rgba(0,0,0,0.5)')),
        ))
        fig.add_hline(y=10000, line_dash="dash", line_color="#00FF66", annotation_text="10K TARGET", annotation_font_color="#00FF66")
        fig.add_hline(y=8000, line_dash="dot", line_color="#FF00A0", annotation_text="8K FLOOR", annotation_font_color="#FF00A0")
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True, bgcolor='rgba(0,0,0,0.4)'), type="date"))
        st.plotly_chart(apply_theme(fig, "Kinetics Log", "STATUS: TRACKING"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 8 — Macros
    # ══════════════════════════════════════════
    with tab8:
        fig = go.Figure()
        macro_cfg = [(16, "Protein", "#FF00A0", "rgba(255,0,160,0.1)"), (17, "Carbs", "#00F0FF", "rgba(0,240,255,0.1)"), (18, "Fat", "#FFEA00", "rgba(255,234,0,0.1)")]
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
        fig.add_hrect(y0=60, y1=80, fillcolor='rgba(0,255,102,0.05)', layer="below", line_width=0)
        fig.add_hrect(y0=80, y1=90, fillcolor='rgba(255,234,0,0.05)', layer="below", line_width=0)
        fig.add_hrect(y0=90, y1=180, fillcolor='rgba(255,0,160,0.05)', layer="below", line_width=0)
        
        fig.add_hline(y=120, line_dash="dash", line_color="#00FF66", annotation_text="SYS IDEAL", annotation_font_color="#00FF66")
        fig.add_hline(y=80, line_dash="dash", line_color="#00F0FF", annotation_text="DIA IDEAL", annotation_font_color="#00F0FF")

        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=sys_data, name="Systolic", mode='lines+markers', connectgaps=True, line=dict(color='#FF00A0', width=3), marker=dict(size=8, color='#FF00A0', line=dict(color='#ffffff', width=1.5))))
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=dia_data, name="Diastolic", mode='lines+markers', connectgaps=True, line=dict(color='#00F0FF', width=3), marker=dict(size=8, color='#00F0FF', line=dict(color='#ffffff', width=1.5))))

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
                title = {'text': "Current Mass (lbs)", 'font': {'color': 'rgba(255,255,255,0.7)', 'size': 18, 'family': 'Space Mono'}},
                delta = {'reference': start_w, 'increasing': {'color': '#FF00A0'}, 'decreasing': {'color': '#00FF66'}},
                gauge = {
                    'axis': {'range': [goal_w - 5, start_w + 5], 'tickcolor': "white", 'tickfont': {'color': 'white'}},
                    'bar': {'color': "#00F0FF"},
                    'bgcolor': "rgba(0,0,0,0.4)",
                    'borderwidth': 2,
                    'bordercolor': "rgba(0,240,255,0.2)",
                    'steps': [
                        {'range': [goal_w, goal_w + 10], 'color': "rgba(0,255,102,0.1)"},
                        {'range': [goal_w + 10, start_w], 'color': "rgba(255,234,0,0.1)"}
                    ],
                    'threshold': {'line': {'color': "#FF00A0", 'width': 5}, 'thickness': 0.85, 'value': goal_w}
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
                glow = "box-shadow: 0 0 20px rgba(0,255,102,0.2); border-color: var(--neon-green);"
                val_color = "var(--neon-green)"
                status = "UNLOCKED"
            else:
                glow = "opacity: 0.3; filter: grayscale(100%); background: rgba(0,0,0,0.6);"
                val_color = "#ffffff"
                status = "LOCKED"
                
            return f"""
            <div class='card' style='{glow} transition: all 0.3s ease; height: 180px; display: flex; flex-direction: column; justify-content: center;'>
                <div style='font-size:2.5rem; margin-bottom:8px; text-shadow: 0 0 15px rgba(0,0,0,0.8);'>{b['icon']}</div>
                <div class='label' style='color:{val_color}; margin-bottom:4px; letter-spacing:0.15em;'>{status}</div>
                <div class='val-sm' style='font-size:1.1rem; margin-bottom:2px;'>{b['title']}</div>
                <div style='font-family:Space Mono,monospace; font-size:0.7rem; color:rgba(255,255,255,0.5);'>{b['desc']}</div>
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

        next_day_weight_diff = w_series.shift(-1) - w_series
        valid_days_mask = next_day_weight_diff.notna()

        # Caloric
        good_cal_mask = (cals_series <= 1633) & valid_days_mask
        bad_cal_mask = (cals_series > 1633) & valid_days_mask
        avg_change_good_cals = next_day_weight_diff[good_cal_mask].mean()
        avg_change_bad_cals = next_day_weight_diff[bad_cal_mask].mean()
        cal_insight_color = "var(--neon-green)" if pd.notna(avg_change_good_cals) and avg_change_good_cals < 0 else "var(--neon-yellow)"
        cal_str_good = f"{avg_change_good_cals:+.2f} lbs" if pd.notna(avg_change_good_cals) else "0.00 lbs"
        cal_str_bad = f"{avg_change_bad_cals:+.2f} lbs" if pd.notna(avg_change_bad_cals) else "0.00 lbs"

        # Step
        good_step_mask = (steps_series >= 10000) & valid_days_mask
        success_rate = (next_day_weight_diff[good_step_mask] < 0).sum() / good_step_mask.sum() * 100 if good_step_mask.sum() > 0 else 0

        # Hydration
        good_hyd_mask = (hyd_series >= 3000) & valid_days_mask
        bad_hyd_mask = (hyd_series < 3000) & (hyd_series > 0) & valid_days_mask
        hyd_success_good = (next_day_weight_diff[good_hyd_mask] < 0).sum() / good_hyd_mask.sum() * 100 if good_hyd_mask.sum() > 0 else 0
        hyd_success_bad = (next_day_weight_diff[bad_hyd_mask] < 0).sum() / bad_hyd_mask.sum() * 100 if bad_hyd_mask.sum() > 0 else 0

        # Protein
        high_prot_mask = (prot_series >= 30) & valid_days_mask
        low_prot_mask = (prot_series < 30) & (prot_series > 0) & valid_days_mask
        avg_change_high_prot = next_day_weight_diff[high_prot_mask].mean()
        avg_change_low_prot = next_day_weight_diff[low_prot_mask].mean()
        str_high_prot = f"{avg_change_high_prot:+.2f} lbs" if pd.notna(avg_change_high_prot) else "0.00 lbs"
        str_low_prot = f"{avg_change_low_prot:+.2f} lbs" if pd.notna(avg_change_low_prot) else "0.00 lbs"

        # Days
        temp_df = pd.DataFrame({'day': df.iloc[:, 0].dt.day_name(), 'diff': next_day_weight_diff})
        day_means = temp_df.groupby('day')['diff'].mean().dropna()
        best_day = day_means.idxmin() if not day_means.empty else "N/A"
        worst_day = day_means.idxmax() if not day_means.empty else "N/A"

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px; border-left: 2px solid var(--neon-cyan);'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>🔥</div>
            <div class='val-sm' style='margin-bottom: 15px; color: var(--neon-cyan);'>Caloric Efficiency Engine</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.8); line-height: 1.6;'>
                When your daily intake stays <b>at or below your 1,633 target</b>, your following day's weight changes by an average of <span style='color: {cal_insight_color}; font-weight: bold; text-shadow: 0 0 10px {cal_insight_color};'>{cal_str_good}</span>. 
                Conversely, when you exceed the calorie limit, your next day's weight changes by an average of <span style='color: var(--neon-pink); font-weight: bold;'>{cal_str_bad}</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px; border-left: 2px solid var(--neon-cyan);'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>👟</div>
            <div class='val-sm' style='margin-bottom: 15px; color: var(--neon-cyan);'>Kinetic Success Rate</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.8); line-height: 1.6;'>
                Hitting your 10,000 step goal yields a <span style='color: var(--neon-green); font-weight: bold; font-size: 1.2em; text-shadow: 0 0 10px var(--neon-green);'>{success_rate:.0f}%</span> success rate for a weight drop on the scale the very next morning. Consistency here directly influences the trendline.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px; border-left: 2px solid var(--neon-cyan);'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>💧</div>
            <div class='val-sm' style='margin-bottom: 15px; color: var(--neon-cyan);'>The Hydration Catalyst</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.8); line-height: 1.6;'>
                Drinking 3L or more of water gives you a <span style='color: var(--neon-green); font-weight: bold;'>{hyd_success_good:.0f}%</span> chance of dropping weight the next day. On days you miss your water target, that drops to <span style='color: var(--neon-yellow); font-weight: bold;'>{hyd_success_bad:.0f}%</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px; border-left: 2px solid var(--neon-cyan);'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>🥩</div>
            <div class='val-sm' style='margin-bottom: 15px; color: var(--neon-cyan);'>Protein Power Correlation</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.8); line-height: 1.6;'>
                On days where protein makes up 30%+ of your macros, your next day's average scale shift is <span style='font-weight: bold; color:#fff;'>{str_high_prot}</span>. On days under 30%, the shift averages <span style='font-weight: bold; color:#fff;'>{str_low_prot}</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card' style='text-align: left; padding: 30px; margin-bottom: 20px; border-left: 2px solid var(--neon-cyan);'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>📅</div>
            <div class='val-sm' style='margin-bottom: 15px; color: var(--neon-cyan);'>The Weekly Profiler</div>
            <div style='font-family: var(--font-body); font-size: 1.1rem; color: rgba(255,255,255,0.8); line-height: 1.6;'>
                Historically, <span style='color: var(--neon-green); font-weight: bold;'>{best_day}s</span> are when you see the biggest drops on the scale. By contrast, <span style='color: var(--neon-pink); font-weight: bold;'>{worst_day}s</span> tend to be your most resistant days.
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
            
            l7_cals = pd.to_numeric(last_7.iloc[:, 1], errors='coerce').mean()
            p7_cals = pd.to_numeric(prev_7.iloc[:, 1], errors='coerce').mean()
            
            l7_steps = pd.to_numeric(last_7.iloc[:, 12], errors='coerce').mean()
            p7_steps = pd.to_numeric(prev_7.iloc[:, 12], errors='coerce').mean()
            
            l7_w_start = pd.to_numeric(last_7.iloc[0, 3], errors='coerce')
            l7_w_end = pd.to_numeric(last_7.iloc[-1, 3], errors='coerce')
            l7_change = l7_w_end - l7_w_start
            
            p7_w_start = pd.to_numeric(prev_7.iloc[0, 3], errors='coerce')
            p7_w_end = pd.to_numeric(prev_7.iloc[-1, 3], errors='coerce')
            p7_change = p7_w_end - p7_w_start

            cal_diff = l7_cals - p7_cals
            step_diff = l7_steps - p7_steps
            change_diff = l7_change - p7_change

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(card("Avg Cals (7 Days)", num_target=l7_cals, decimals=0, suffix=" kcal", delta_val=cal_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)
            with col2:
                st.markdown(card("Avg Steps (7 Days)", num_target=l7_steps, decimals=0, delta_val=step_diff, delta_label="vs Prev", invert=False), unsafe_allow_html=True)
            with col3:
                st.markdown(card("Mass Change (7 Days)", display_val=f"{l7_change:+.1f} lbs", delta_val=change_diff, delta_label="vs Prev", invert=True), unsafe_allow_html=True)
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
            recent_14 = w_series.tail(14)
            loss_rate_per_day = (recent_14.iloc[0] - recent_14.iloc[-1]) / len(recent_14)
            current_w = w_series.iloc[-1]
            
            if loss_rate_per_day > 0 and current_w > 170:
                days_to_goal = int((current_w - 170) / loss_rate_per_day)
                eta_date = pd.Timestamp.now() + pd.Timedelta(days=days_to_goal)
                
                st.markdown(f"""
                <div class='card' style='padding: 40px 20px; border: 1px solid var(--neon-cyan); box-shadow: 0 0 30px rgba(0,240,255,0.2);'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>🔮</div>
                    <div class='val' style='font-size: 2.5rem; color: var(--neon-cyan); text-shadow: 0 0 15px var(--neon-cyan);'>{eta_date.strftime('%B %d, %Y')}</div>
                    <div class='label' style='margin-top: 15px; font-size: 0.9rem;'>Projected Goal Achievement Date</div>
                    <div style='font-family: var(--font-body); font-size: 1rem; color: rgba(255,255,255,0.7); margin-top: 15px;'>
                        Based on your 14-day velocity of dropping {loss_rate_per_day*7:.1f} lbs per week. 
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif current_w <= 170:
                st.markdown("<div class='card'><div class='val' style='color:var(--neon-green); text-shadow: 0 0 10px var(--neon-green);'>TARGET ACHIEVED</div></div>", unsafe_allow_html=True)
            else:
                st.info("Velocity currently neutral or positive. Maintain a continuous deficit to generate an ETA.")
        else:
            st.info("Requires at least 14 days of logged weight data to calculate a reliable projection.")

    # ══════════════════════════════════════════
    #  TAB 16 — Raw Telemetry Log
    # ══════════════════════════════════════════
    with tab16:
        st.markdown("<div class='section-header'>Raw Telemetry</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Latest 30 Days Data Log</div>", unsafe_allow_html=True)
        
        display_df = df.copy()
        if not display_df.empty:
            display_df[0] = display_df[0].dt.strftime('%Y-%m-%d')
            display_df = display_df.iloc[::-1].head(30)
            display_df.columns = [str(i) for i in range(len(display_df.columns))]
            
            cols_to_show = {
                '0': 'Date', '1': 'Cals In', '3': 'Weight (lbs)', '12': 'Steps', 
                '16': 'Protein %', '17': 'Carbs %', '18': 'Fat %', '24': 'Water (ml)'
            }
            valid_cols = {k: v for k, v in cols_to_show.items() if k in display_df.columns}
            clean_df = display_df[list(valid_cols.keys())].rename(columns=valid_cols)
            
            st.dataframe(clean_df, use_container_width=True, hide_index=True, height=400)

    # ─────────────────────────────────────────────
    #  JavaScript Odometer Injector
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
