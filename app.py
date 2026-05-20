import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="Hardy House Command", layout="wide", initial_sidebar_state="collapsed")

# ── Inject global CSS + fonts ──────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap" rel="stylesheet">
<style>
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }
.stApp { background: #050810; background-image: linear-gradient(rgba(0,200,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(0,200,255,0.025) 1px, transparent 1px); background-size: 60px 60px; animation: gridDrift 30s linear infinite; }
@keyframes gridDrift { to { background-position: 60px 60px; } }
.stApp::after { content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 9998; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px); }
.stApp::before { content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0; background: radial-gradient(600px circle at 0% 0%, rgba(0,200,255,0.07), transparent 60%), radial-gradient(500px circle at 100% 100%, rgba(255,107,0,0.07), transparent 60%), radial-gradient(300px circle at 50% 50%, rgba(0,255,136,0.04), transparent 60%); }
div[data-baseweb="tab-list"] { background: rgba(0,0,0,0.5) !important; border-radius: 12px !important; padding: 6px !important; border: 1px solid rgba(0,200,255,0.15) !important; gap: 4px !important; }
div[data-baseweb="tab-list"] button { background: transparent !important; border-radius: 8px !important; border: none !important; color: rgba(180,210,240,0.5) !important; font-family: 'Rajdhani', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 1px !important; text-transform: uppercase !important; transition: all 0.25s !important; }
div[data-baseweb="tab-list"] button:hover { color: #00c8ff !important; background: rgba(0,200,255,0.07) !important; }
div[data-baseweb="tab-list"] button[aria-selected="true"] { background: rgba(0,200,255,0.12) !important; color: #00c8ff !important; box-shadow: 0 0 16px rgba(0,200,255,0.25), inset 0 0 0 1px rgba(0,200,255,0.4) !important; }
div[data-baseweb="tab-list"] button p { color: inherit !important; font-family: inherit !important; font-size: inherit !important; font-weight: inherit !important; letter-spacing: inherit !important; text-transform: inherit !important; }
div[data-baseweb="tab-highlight"] { display: none !important; }
div[data-testid="stTabsContent"] { background: transparent !important; border: none !important; padding: 0 !important; }
div[data-testid="stTabsContent"] > div { background: transparent !important; }
.hh-card { background: rgba(8,14,30,0.85); border: 1px solid rgba(0,200,255,0.15); border-radius: 16px; padding: 22px 18px; text-align: center; position: relative; overflow: hidden; backdrop-filter: blur(20px); transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s; margin-bottom: 4px; }
.hh-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--accent, #00c8ff), transparent); opacity: 0; transition: opacity 0.3s; }
.hh-card::after { content: ''; position: absolute; top: 0; right: 0; width: 24px; height: 24px; border-top: 2px solid var(--accent, #00c8ff); border-right: 2px solid var(--accent, #00c8ff); border-radius: 0 16px 0 0; opacity: 0.35; }
.hh-card:hover { border-color: rgba(0,200,255,0.45); box-shadow: 0 0 24px rgba(0,200,255,0.2); transform: translateY(-3px); }
.hh-card:hover::before { opacity: 1; }
.hh-card.orange { --accent: #ff6b00; }
.hh-card.orange:hover { border-color: rgba(255,107,0,0.45); box-shadow: 0 0 24px rgba(255,107,0,0.2); }
.hh-card.green  { --accent: #00ff88; }
.hh-card.green:hover  { border-color: rgba(0,255,136,0.45); box-shadow: 0 0 24px rgba(0,255,136,0.2); }
.hh-label { font-family: 'Rajdhani', sans-serif; font-size: 0.62rem; letter-spacing: 3px; text-transform: uppercase; color: rgba(180,210,240,0.5); margin-bottom: 8px; }
.hh-val { font-family: 'Orbitron', monospace; font-size: 1.9rem; font-weight: 700; color: white; line-height: 1; text-shadow: 0 0 20px rgba(255,255,255,0.25); }
.hh-val.cyan   { color: #00c8ff; text-shadow: 0 0 20px rgba(0,200,255,0.5); }
.hh-val.orange { color: #ff6b00; text-shadow: 0 0 20px rgba(255,107,0,0.5); }
.hh-val.green  { color: #00ff88; text-shadow: 0 0 20px rgba(0,255,136,0.5); }
.hh-val.red    { color: #ff3355; }
.hh-delta { font-size: 0.8rem; margin-top: 6px; font-family: 'Rajdhani', sans-serif; font-weight: 600; }
.delta-good { color: #00ff88; }
.delta-bad  { color: #ff3355; }
.hh-chart-wrap { background: rgba(8,14,30,0.85); border: 1px solid rgba(0,200,255,0.13); border-radius: 20px; padding: 24px; backdrop-filter: blur(20px); position: relative; overflow: hidden; margin-bottom: 6px; }
.hh-chart-wrap::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, #00c8ff 30%, #ff6b00 70%, transparent); opacity: 0.35; }
.hh-chart-title { font-family: 'Orbitron', monospace; font-size: 0.78rem; letter-spacing: 3px; text-transform: uppercase; color: #00c8ff; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
.hh-chart-title::before { content: ''; width: 4px; height: 14px; background: #00c8ff; box-shadow: 0 0 10px rgba(0,200,255,0.6); border-radius: 2px; flex-shrink: 0; }
.hh-section { font-family: 'Orbitron', monospace; font-size: 1.1rem; font-weight: 700; color: white; letter-spacing: 3px; margin: 24px 0 18px; display: flex; align-items: center; gap: 14px; }
.hh-section::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0,200,255,0.5), transparent); }
.hh-header { text-align: center; padding: 40px 24px 28px; position: relative; }
.hh-header::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 360px; height: 1px; background: linear-gradient(90deg, transparent, #00c8ff, transparent); box-shadow: 0 0 20px rgba(0,200,255,0.4); }
.hh-header-label { font-family: 'Rajdhani', sans-serif; font-size: 0.65rem; letter-spacing: 8px; text-transform: uppercase; color: #00c8ff; margin-bottom: 8px; animation: fadeUp 0.8s ease forwards; }
.hh-header h1 { font-family: 'Orbitron', monospace !important; font-size: clamp(1.8rem, 4vw, 3rem) !important; font-weight: 900 !important; color: white !important; letter-spacing: 4px !important; text-shadow: 0 0 30px rgba(0,200,255,0.5), 0 0 60px rgba(0,200,255,0.2) !important; animation: fadeUp 0.8s 0.2s ease both; }
.hh-header h1 span { color: #00c8ff; }
.hh-header-sub { margin-top: 8px; font-family: 'Rajdhani', sans-serif; font-size: 0.8rem; letter-spacing: 4px; color: rgba(180,210,240,0.45); text-transform: uppercase; animation: fadeUp 0.8s 0.4s ease both; }
.hh-live { margin-top: 12px; font-family: 'Orbitron', monospace; font-size: 0.7rem; color: rgba(0,200,255,0.7); letter-spacing: 2px; animation: fadeUp 0.8s 0.6s ease both; }
.pulse-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #00ff88; box-shadow: 0 0 8px #00ff88; margin-right: 6px; animation: pulseDot 1.5s ease-in-out infinite; }
@keyframes pulseDot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.6)} }
@keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
.hh-prog-label { display:flex; justify-content:space-between; margin-bottom:5px; }
.hh-prog-ltext { font-family:'Rajdhani',sans-serif; font-size:0.65rem; letter-spacing:2px; text-transform:uppercase; color:rgba(180,210,240,0.45); }
.hh-prog-val   { font-family:'Orbitron',monospace; font-size:0.75rem; color:#00c8ff; }
.hh-prog-track { height:5px; background:rgba(255,255,255,0.06); border-radius:3px; overflow:hidden; margin-bottom:14px; }
.hh-prog-fill  { height:100%; border-radius:3px; transition:width 1.8s cubic-bezier(0.25,1,0.5,1); position:relative; }
.hh-prog-fill.cyan   { background: linear-gradient(90deg,rgba(0,200,255,0.3),#00c8ff); }
.hh-prog-fill.orange { background: linear-gradient(90deg,rgba(255,107,0,0.3),#ff6b00); }
.hh-prog-fill.green  { background: linear-gradient(90deg,rgba(0,255,136,0.3),#00ff88); }
.hh-bp-big { font-family:'Orbitron',monospace; font-size:3.2rem; font-weight:900; line-height:1; }
.hh-bp-unit { font-size:0.65rem; letter-spacing:3px; color:rgba(180,210,240,0.45); margin-top:6px; }
.hh-bp-status { font-size:0.8rem; margin-top:6px; font-family:'Rajdhani',sans-serif; font-weight:600; }
.hh-counter { display:inline-block; }
.hh-wrap { padding: 0 24px 60px; }
</style>
""", unsafe_allow_html=True)

# ── Data Safety Helper ────────────────────────────────────────────────────────
def is_valid(val):
    """Checks if a cell is genuinely populated, avoiding Pandas 'nan' trap."""
    s = str(val).strip().lower()
    return s not in ['', 'nan', 'none', '<na>']

# ── Google Sheets loader ───────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_data():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        ws = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        data = ws.get_all_values()
        
        if not data or len(data) < 2:
            return pd.DataFrame()

        # Load purely by index to avoid duplicate header conflicts
        df = pd.DataFrame(data[1:])
        
        # TRUNCATION ENGINE: Kill empty future rows.
        # Find the last row where Cals (1), Weight (3), Gain (5), or Steps (12) has data
        mask = pd.Series(False, index=df.index)
        for col_idx in [1, 3, 5, 12]:
            if col_idx < len(df.columns):
                mask = mask | df.iloc[:, col_idx].apply(is_valid)
                
        if mask.any():
            last_valid_idx = mask[mask].index[-1]
            df = df.loc[:last_valid_idx].copy()
        else:
            df = pd.DataFrame()

        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("⚠️ No active data loaded. Check your secrets and sheet connection.")
    st.stop()

# ── Value Extractors ───────────────────────────────────────────────────────────
def gcol(idx):
    """Return an entire column as a cleaned numeric array, replacing blanks with None."""
    if idx >= len(df.columns): return [None] * len(df)
    s = df.iloc[:, idx].astype(str)
    s = s.str.replace('%', '', regex=False).str.replace(',', '', regex=False).str.strip()
    s = s.replace(['', 'nan', 'NaN', 'None', 'none', '<NA>'], pd.NA)
    s = pd.to_numeric(s, errors='coerce')
    return [None if pd.isna(v) else round(float(v), 4) for v in s]

def gval(row_series, idx):
    """Safely extract a single scalar number from a row, ignoring letters/symbols."""
    if idx >= len(row_series): return 0.0
    try:
        v = str(row_series.iloc[idx]).strip()
        if not is_valid(v): return 0.0
        v = re.sub(r'[^\d\.-]', '', v)
        if not v or v == '-' or v == '.': return 0.0
        return float(v)
    except:
        return 0.0

def get_str(row_series, idx):
    """Extract a safe string for text-based values like Stone/Lbs text."""
    if idx >= len(row_series): return ""
    try:
        s = str(row_series.iloc[idx]).strip()
        return "" if not is_valid(s) else s
    except:
        return ""

dates_raw = df.iloc[:, 0].astype(str).tolist()
def short_date(d):
    parts = d.split('/')
    return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else d
dates = [short_date(d) for d in dates_raw]

n = len(df) # Since we truncated, this is accurately your days on the diet!
last = df.iloc[-1]
last_date = dates_raw[-1] if dates_raw else "–"

# ── GSAP + Chart.js injection helper ──────────────────────────────────────────
CHART_SCRIPTS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
"""

def chart_html(title, chart_js_body, height=360):
    """Wrap a Chart.js canvas + script in the house style."""
    return f"""
{CHART_SCRIPTS}
<div class="hh-chart-wrap" style="font-family:'Rajdhani',sans-serif;">
  <div class="hh-chart-title">{title}</div>
  <canvas id="myChart" style="max-height:{height}px;"></canvas>
</div>
<script>
(function(){{
  const CYAN='#00c8ff', ORANGE='#ff6b00', GREEN='#00ff88', RED='#ff3355', WHITE='#ffffff';
  const defaults = {{
    responsive:true, maintainAspectRatio:true,
    animation:{{ duration:1200, easing:'easeInOutQuart' }},
    plugins:{{
      legend:{{ labels:{{ color:'rgba(180,210,240,0.75)', usePointStyle:true, pointStyleWidth:10,
        padding:20, font:{{ size:12, family:"'Rajdhani',sans-serif", weight:'600' }} }} }},
      tooltip:{{ backgroundColor:'rgba(5,8,16,0.95)', borderColor:'rgba(0,200,255,0.3)',
        borderWidth:1, titleColor:CYAN, bodyColor:'rgba(180,210,240,0.9)',
        padding:12, cornerRadius:10,
        titleFont:{{ family:"'Orbitron',monospace", size:11 }},
        bodyFont:{{ family:"'Rajdhani',sans-serif", size:13, weight:'600' }} }}
    }},
    scales:{{
      x:{{ grid:{{ color:'rgba(255,255,255,0.04)' }},
           ticks:{{ color:'rgba(180,210,240,0.45)', maxTicksLimit:14, font:{{size:10}} }},
           border:{{ color:'rgba(255,255,255,0.1)' }} }},
      y:{{ grid:{{ color:'rgba(255,255,255,0.04)' }},
           ticks:{{ color:'rgba(180,210,240,0.45)', font:{{size:10}} }},
           border:{{ color:'rgba(255,255,255,0.1)' }} }}
    }}
  }};
  function neon(color, w=2.5){{
    return {{ borderColor:color, borderWidth:w, pointBackgroundColor:color,
             pointRadius:2, pointHoverRadius:6, tension:0.4 }};
  }}
  const ctx = document.getElementById('myChart').getContext('2d');
  {chart_js_body}
}})();
</script>
"""

def counter_js(el_id, target, decimals=0, suffix='', duration=1400):
    return f"""
(function(){{
  const el = document.getElementById('{el_id}');
  if(!el) return;
  const start = performance.now();
  const t = {target};
  function tick(now){{
    const p = Math.min((now-start)/{duration},1);
    const e = p===1?1:1-Math.pow(2,-10*p);
    el.textContent = (t*e).toFixed({decimals}) + '{suffix}';
    if(p<1) requestAnimationFrame(tick);
  }}
  requestAnimationFrame(tick);
}})();
"""

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hh-header">
  <div class="hh-header-label">Mission Control</div>
  <h1>HARDY HOUSE <span>COMMAND</span></h1>
  <div class="hh-header-sub">Personal Health Intelligence System</div>
  <div class="hh-live"><span class="pulse-dot"></span>LIVE · UPDATED {last_date.upper()}</div>
</div>
<div class="hh-wrap">
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9,tab10 = st.tabs([
    "🛡️ Review","📊 Life","🔥 Calories","⚖️ Weight","📉 Gain/Loss",
    "🚀 Velocity","👟 Steps","🥗 Macros","📈 Averages","❤️ BP"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Ensure we get a row where Steps (12) were actually filled out
    completed_rows = df[df.iloc[:, 12].apply(is_valid)]
    
    if completed_rows.empty:
        st.warning("No completed day data yet.")
    else:
        y = completed_rows.iloc[-1]
        cals  = gval(y, 1)
        steps = gval(y, 12)
        cal_diff  = cals - 1633
        step_diff = steps - 10000
        cal_color  = "#ff3355" if cal_diff > 0 else "#00ff88"
        step_color = "#00ff88" if step_diff >= 0 else "#ff3355"
        cal_arrow  = "▲" if cal_diff > 0 else "▼"
        step_arrow = "▲" if step_diff >= 0 else "▼"

        st.markdown('<div class="hh-section">YESTERDAY\'S DEBRIEF</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="hh-card orange">
              <div class="hh-label">Calories Consumed</div>
              <div class="hh-val orange" id="r-cals">0</div>
              <div class="hh-delta"><span style="color:{cal_color}">{cal_arrow} {abs(cal_diff):.0f} vs 1,633 target</span></div>
            </div>
            <script>{counter_js('r-cals', cals, 0)}</script>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="hh-card green">
              <div class="hh-label">Steps</div>
              <div class="hh-val green" id="r-steps">0</div>
              <div class="hh-delta"><span style="color:{step_color}">{step_arrow} {abs(step_diff):,.0f} vs 10,000 target</span></div>
            </div>
            <script>{counter_js('r-steps', steps, 0)}</script>
            """, unsafe_allow_html=True)

        protein = gval(y, 16)
        carbs   = gval(y, 17)
        fat     = gval(y, 18)
        alc_raw = str(y.iloc[19]).replace(',','').replace('%','').strip() if 19 < len(y) else ""
        alc     = float(alc_raw) if alc_raw and is_valid(alc_raw) else 0.0
        alc_display = f"{alc:.0f} kcal" if alc > 0 else "None"

        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(f'<div class="hh-card"><div class="hh-label">Protein</div><div class="hh-val cyan">{protein:.1f}%</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="hh-card"><div class="hh-label">Net Carbs</div><div class="hh-val">{carbs:.1f}%</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="hh-card orange"><div class="hh-label">Fat</div><div class="hh-val orange">{fat:.1f}%</div></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="hh-card"><div class="hh-label">Alcohol</div><div class="hh-val">{alc_display}</div></div>', unsafe_allow_html=True)

        # 7-day calorie trend mini chart
        last7 = df.tail(7)
        l7_cals  = [gval(last7.iloc[i],1) for i in range(len(last7))]
        l7_dates = [short_date(str(last7.iloc[i,0])) for i in range(len(last7))]
        l7_colors = ["rgba(255,51,85,0.55)" if c > 1633 else "rgba(255,107,0,0.5)" for c in l7_cals]
        l7_borders= ["#ff3355" if c > 1633 else "#ff6b00" for c in l7_cals]

        chart_body = f"""
new Chart(ctx, {{
  type:'bar',
  data:{{
    labels:{json.dumps(l7_dates)},
    datasets:[
      {{ label:'Calories', data:{json.dumps(l7_cals)},
         backgroundColor:{json.dumps(l7_colors)}, borderColor:{json.dumps(l7_borders)},
         borderWidth:2, borderRadius:6, order:2 }},
      {{ label:'Target 1,633', data:{json.dumps([1633]*len(l7_cals))},
         type:'line', borderColor:'rgba(0,200,255,0.55)', borderWidth:2,
         borderDash:[6,4], pointRadius:0, fill:false, order:1 }}
    ]
  }},
  options:{{...defaults}}
}});
"""
        components.html(chart_html("7-DAY CALORIE TREND", chart_body), height=410, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LIFE
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    # Ensure Life targets the row where Total Loss (6) is actually entered
    life_rows = df[df.iloc[:, 6].apply(is_valid)]
    last_life = life_rows.iloc[-1] if not life_rows.empty else last

    total_loss_lbs = gval(last_life, 6)
    total_loss_st  = get_str(last_life, 7)
    to_target_lbs  = gval(last_life, 8)
    to_target_st   = get_str(last_life, 9)
    bmi_cur        = gval(last_life, 10)
    bmi_target     = gval(last_life, 11)

    target_loss_lbs = total_loss_lbs + to_target_lbs
    loss_pct  = min(100, round((total_loss_lbs / target_loss_lbs * 100) if target_loss_lbs else 0, 1))
    
    # Safely get first BMI recorded
    bmi_col = gcol(10)
    start_bmi = next((v for v in bmi_col if v is not None and v > 0), 1)
    
    bmi_range = start_bmi - bmi_target if (start_bmi - bmi_target) != 0 else 1
    bmi_pct   = min(100, max(0, round((start_bmi - bmi_cur) / bmi_range * 100, 1)))
    days_pct  = min(100, round(n / 180 * 100, 1))

    st.markdown('<div class="hh-section">LIFETIME INTELLIGENCE</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="hh-card"><div class="hh-label">Days on Mission</div><div class="hh-val cyan" id="l-days">0</div></div><script>{counter_js("l-days",n,0)}</script>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="hh-card green"><div class="hh-label">Total Lost (lbs)</div><div class="hh-val green" id="l-loss">0</div></div><script>{counter_js("l-loss",total_loss_lbs,1)}</script>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="hh-card green"><div class="hh-label">Total Lost (St)</div><div class="hh-val green">{total_loss_st}</div></div>', unsafe_allow_html=True)

    c4,c5,c6 = st.columns(3)
    with c4:
        st.markdown(f'<div class="hh-card orange"><div class="hh-label">To Target (lbs)</div><div class="hh-val orange" id="l-tolbs">0</div></div><script>{counter_js("l-tolbs",to_target_lbs,1)}</script>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="hh-card orange"><div class="hh-label">To Target (St)</div><div class="hh-val orange">{to_target_st}</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="hh-card"><div class="hh-label">Current BMI</div><div class="hh-val cyan">{bmi_cur}</div></div>', unsafe_allow_html=True)

    prog_html = f"""
<div class="hh-chart-wrap" style="font-family:'Rajdhani',sans-serif;">
  <div class="hh-chart-title">MISSION PROGRESS</div>
  <div class="hh-prog-label"><span class="hh-prog-ltext">Weight Loss</span><span class="hh-prog-val">{loss_pct}%</span></div>
  <div class="hh-prog-track"><div class="hh-prog-fill green" id="pb-loss" style="width:0%"></div></div>
  <div class="hh-prog-label"><span class="hh-prog-ltext">BMI Progress</span><span class="hh-prog-val">{bmi_pct}%</span></div>
  <div class="hh-prog-track"><div class="hh-prog-fill cyan" id="pb-bmi" style="width:0%"></div></div>
  <div class="hh-prog-label"><span class="hh-prog-ltext">Days (vs 180 day goal)</span><span class="hh-prog-val">{n} days</span></div>
  <div class="hh-prog-track"><div class="hh-prog-fill orange" id="pb-days" style="width:0%"></div></div>
</div>
<script>
setTimeout(function(){{
  document.getElementById('pb-loss').style.width  = '{loss_pct}%';
  document.getElementById('pb-bmi').style.width   = '{bmi_pct}%';
  document.getElementById('pb-days').style.width  = '{days_pct}%';
}}, 200);
</script>
"""
    components.html(prog_html, height=220, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CALORIES
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    cals_data = gcol(1)
    net_data  = gcol(2)
    cal_colors  = ["rgba(255,51,85,0.45)" if (v or 0) > 1633 else "rgba(255,107,0,0.4)" for v in cals_data]
    cal_borders = ["#ff3355" if (v or 0) > 1633 else "#ff6b00" for v in cals_data]

    chart_body = f"""
new Chart(ctx, {{
  type:'bar',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Calories', data:{json.dumps(cals_data)},
         backgroundColor:{json.dumps(cal_colors)}, borderColor:{json.dumps(cal_borders)},
         borderWidth:1.5, borderRadius:3, order:2 }},
      {{ label:'Net Calories', data:{json.dumps(net_data)},
         type:'line', ...neon(CYAN,2),
         backgroundColor:'rgba(0,200,255,0.05)', fill:true, order:1 }},
      {{ label:'Target 1,633', data:{json.dumps([1633]*n)},
         type:'line', borderColor:'rgba(255,255,255,0.2)', borderWidth:1.5,
         borderDash:[6,4], pointRadius:0, fill:false, order:0 }}
    ]
  }},
  options:{{...defaults}}
}});
"""
    components.html(chart_html("CALORIES CONSUMED vs NET", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — WEIGHT
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    weight_data = gcol(3)
    # 7-day rolling avg
    def rolling_avg(arr, w=7):
        out = []
        for i,v in enumerate(arr):
            sl = [x for x in arr[max(0,i-w+1):i+1] if x is not None]
            out.append(round(sum(sl)/len(sl),2) if sl else None)
        return out
    roll7 = rolling_avg(weight_data)

    chart_body = f"""
new Chart(ctx, {{
  type:'line',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Weight (lbs)', data:{json.dumps(weight_data)},
         ...neon(WHITE,2.5), backgroundColor:'rgba(255,255,255,0.04)', fill:true }},
      {{ label:'7-Day Avg', data:{json.dumps(roll7)},
         ...neon(CYAN,2), borderDash:[6,3], fill:false, pointRadius:0 }}
    ]
  }},
  options:{{...defaults}}
}});
"""
    components.html(chart_html("WEIGHT TRAJECTORY (lbs)", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — GAIN/LOSS
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    gl_data = gcol(5)
    cum = []
    running = 0
    for v in gl_data:
        running += (v or 0)
        cum.append(round(-running, 4))   # positive = loss

    chart_body = f"""
new Chart(ctx, {{
  type:'line',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Cumulative Loss (lbs)', data:{json.dumps(cum)},
         ...neon(ORANGE,3), backgroundColor:'rgba(255,107,0,0.07)', fill:true }}
    ]
  }},
  options:{{...defaults}}
}});
"""
    components.html(chart_html("CUMULATIVE GAIN / LOSS", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — VELOCITY
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    w = gcol(3)
    vel = [None] + [round(-(w[i] - w[i-1]), 4) if (w[i] is not None and w[i-1] is not None) else None for i in range(1,len(w))]
    vel_colors  = ["rgba(0,255,136,0.5)" if (v or 0) > 0 else "rgba(255,51,85,0.5)" for v in vel]
    vel_borders = ["#00ff88" if (v or 0) > 0 else "#ff3355" for v in vel]

    chart_body = f"""
new Chart(ctx, {{
  type:'bar',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Daily Velocity (lbs)', data:{json.dumps(vel)},
         backgroundColor:{json.dumps(vel_colors)}, borderColor:{json.dumps(vel_borders)},
         borderWidth:1.5, borderRadius:3 }}
    ]
  }},
  options:{{
    ...defaults,
    plugins:{{ ...defaults.plugins }},
    scales:{{
      x:{{ ...defaults.scales.x }},
      y:{{ ...defaults.scales.y,
           afterDataLimits: (axis) => {{ axis.min -= 0.1; axis.max += 0.1; }} }}
    }}
  }}
}});
"""
    components.html(chart_html("DAILY WEIGHT VELOCITY (lbs/day)", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — STEPS
# ═══════════════════════════════════════════════════════════════════════════════
with tab7:
    steps_data  = gcol(12)
    active_data = gcol(15)
    s_colors  = ["rgba(0,255,136,0.45)" if (v or 0) >= 10000 else "rgba(0,200,255,0.35)" for v in steps_data]
    s_borders = ["#00ff88" if (v or 0) >= 10000 else "#00c8ff" for v in steps_data]

    chart_body = f"""
new Chart(ctx, {{
  type:'bar',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Steps', data:{json.dumps(steps_data)},
         backgroundColor:{json.dumps(s_colors)}, borderColor:{json.dumps(s_borders)},
         borderWidth:1.5, borderRadius:3, yAxisID:'y' }},
      {{ label:'Active Calories', data:{json.dumps(active_data)},
         type:'line', ...neon(ORANGE,2.5), fill:false, yAxisID:'y2' }},
      {{ label:'10k Target', data:{json.dumps([10000]*n)},
         type:'line', borderColor:'rgba(255,255,255,0.18)', borderWidth:1.5,
         borderDash:[5,5], pointRadius:0, fill:false, yAxisID:'y' }}
    ]
  }},
  options:{{
    ...defaults,
    scales:{{
      x:{{ ...defaults.scales.x }},
      y:{{ ...defaults.scales.y, position:'left' }},
      y2:{{ ...defaults.scales.y, position:'right', grid:{{ drawOnChartArea:false }} }}
    }}
  }}
}});
"""
    components.html(chart_html("STEPS & ACTIVE CALORIES", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — MACROS
# ═══════════════════════════════════════════════════════════════════════════════
with tab8:
    chart_body = f"""
new Chart(ctx, {{
  type:'line',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Protein %', data:{json.dumps(gcol(16))}, ...neon(RED,2.5),   fill:false }},
      {{ label:'Net Carbs %', data:{json.dumps(gcol(17))}, ...neon(CYAN,2.5), fill:false }},
      {{ label:'Fat %',     data:{json.dumps(gcol(18))}, ...neon(ORANGE,2.5),fill:false }}
    ]
  }},
  options:{{...defaults}}
}});
"""
    components.html(chart_html("MACRO SPLIT OVER TIME (%)", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 9 — AVERAGES
# ═══════════════════════════════════════════════════════════════════════════════
with tab9:
    def safe_avg(lst):
        vals = [v for v in lst if v is not None and v > 0]
        return round(sum(vals)/len(vals), 2) if vals else 0

    avg_cals    = safe_avg(gcol(1))
    avg_steps   = safe_avg(gcol(12))
    avg_protein = safe_avg(gcol(16))
    avg_carbs   = safe_avg(gcol(17))
    avg_fat     = safe_avg(gcol(18))

    w_all = gcol(3)
    w_start = next((v for v in w_all if v is not None and v > 0), 0)
    w_end   = next((v for v in reversed(w_all) if v is not None and v > 0), 0)
    
    # Calculate strictly off active weight entries
    valid_days = len([v for v in w_all if v is not None and v > 0])
    weeks_elapsed = valid_days / 7 if valid_days > 0 else 1
    avg_weekly = round((w_start - w_end) / weeks_elapsed, 2)

    st.markdown('<div class="hh-section">HISTORICAL AVERAGES</div>', unsafe_allow_html=True)
    r1c1,r1c2,r1c3 = st.columns(3)
    with r1c1: st.markdown(f'<div class="hh-card orange"><div class="hh-label">Avg Cals / Day</div><div class="hh-val orange" id="a-cals">0</div></div><script>{counter_js("a-cals",avg_cals,0)}</script>', unsafe_allow_html=True)
    with r1c2: st.markdown(f'<div class="hh-card green"><div class="hh-label">Avg Steps / Day</div><div class="hh-val green" id="a-steps">0</div></div><script>{counter_js("a-steps",avg_steps,0)}</script>', unsafe_allow_html=True)
    with r1c3: st.markdown(f'<div class="hh-card"><div class="hh-label">Avg Loss / Week</div><div class="hh-val cyan">{avg_weekly} lbs</div></div>', unsafe_allow_html=True)

    r2c1,r2c2,r2c3 = st.columns(3)
    with r2c1: st.markdown(f'<div class="hh-card"><div class="hh-label">Avg Protein</div><div class="hh-val cyan">{avg_protein:.1f}%</div></div>', unsafe_allow_html=True)
    with r2c2: st.markdown(f'<div class="hh-card"><div class="hh-label">Avg Net Carbs</div><div class="hh-val">{avg_carbs:.1f}%</div></div>', unsafe_allow_html=True)
    with r2c3: st.markdown(f'<div class="hh-card orange"><div class="hh-label">Avg Fat</div><div class="hh-val orange">{avg_fat:.1f}%</div></div>', unsafe_allow_html=True)

    # Rolling avg chart
    cals_all = gcol(1)
    roll_cals = rolling_avg(cals_all)
    chart_body = f"""
new Chart(ctx, {{
  type:'line',
  data:{{
    labels:{json.dumps(dates)},
    datasets:[
      {{ label:'Daily Cals', data:{json.dumps(cals_all)},
         ...neon('rgba(255,107,0,0.25)',1), fill:false, pointRadius:0 }},
      {{ label:'7-Day Rolling Avg', data:{json.dumps(roll_cals)},
         ...neon(ORANGE,3), fill:false }},
      {{ label:'Target 1,633', data:{json.dumps([1633]*n)},
         borderColor:'rgba(0,200,255,0.35)', borderWidth:1.5,
         borderDash:[6,4], pointRadius:0, fill:false }}
    ]
  }},
  options:{{...defaults}}
}});
"""
    components.html(chart_html("7-DAY ROLLING AVERAGE — CALORIES", chart_body), height=420, scrolling=False)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 10 — BLOOD PRESSURE
# ═══════════════════════════════════════════════════════════════════════════════
with tab10:
    sys_all = gcol(21)
    dia_all = gcol(22)
    last_sys = next((v for v in reversed(sys_all) if v is not None and v > 0), 0)
    last_dia = next((v for v in reversed(dia_all) if v is not None and v > 0), 0)

    if last_sys == 0:
        sys_status, sys_col = "NO DATA", "#cccccc"
    else:
        sys_status = "✓ NORMAL" if last_sys < 120 else "⚠ ELEVATED" if last_sys < 130 else "⚠ HIGH"
        sys_col = "#00ff88" if last_sys < 120 else ("#ffd32a" if last_sys < 130 else "#ff3355")

    if last_dia == 0:
        dia_status, dia_col = "NO DATA", "#cccccc"
    else:
        dia_status = "✓ NORMAL" if last_dia < 80 else "⚠ HIGH"
        dia_col = "#00ff88" if last_dia < 80 else "#ff3355"

    st.markdown('<div class="hh-section">BLOOD PRESSURE MONITORING</div>', unsafe_allow_html=True)
    bc1,bc2 = st.columns(2)
    with bc1:
        st.markdown(f"""
        <div class="hh-card">
          <div class="hh-label" style="letter-spacing:3px;">Systolic</div>
          <div class="hh-bp-big" style="color:#ff3355;" id="bp-sys">0</div>
          <div class="hh-bp-unit">mmHg</div>
          <div class="hh-bp-status" style="color:{sys_col}">{sys_status}</div>
        </div>
        <script>{counter_js('bp-sys', last_sys, 0)}</script>
        """, unsafe_allow_html=True)
    with bc2:
        st.markdown(f"""
        <div class="hh-card">
          <div class="hh-label" style="letter-spacing:3px;">Diastolic</div>
          <div class="hh-bp-big" style="color:#00c8ff;" id="bp-dia">0</div>
          <div class="hh-bp-unit">mmHg</div>
          <div class="hh-bp-status" style="color:{dia_col}">{dia_status}</div>
        </div>
        <script>{counter_js('bp-dia', last_dia, 0)}</script>
        """, unsafe_allow_html=True)

    # Filter to rows that have BP data
    bp_dates = [dates[i] for i,v in enumerate(sys_all) if v is not None and v > 0]
    bp_sys   = [v for v in sys_all if v is not None and v > 0]
    bp_dia   = [v for v in dia_all if v is not None and v > 0]

    chart_body = f"""
new Chart(ctx, {{
  type:'line',
  data:{{
    labels:{json.dumps(bp_dates)},
    datasets:[
      {{ label:'Systolic',  data:{json.dumps(bp_sys)},  ...neon(RED,3),  fill:false }},
      {{ label:'Diastolic', data:{json.dumps(bp_dia)},  ...neon(CYAN,3), fill:false }},
      {{ label:'Target Sys (120)', data:{json.dumps([120]*len(bp_dates))},
         borderColor:'rgba(255,51,85,0.25)', borderWidth:1.5, borderDash:[6,4],
         pointRadius:0, fill:false }},
      {{ label:'Target Dia (80)', data:{json.dumps([80]*len(bp_dates))},
         borderColor:'rgba(0,200,255,0.25)', borderWidth:1.5, borderDash:[6,4],
         pointRadius:0, fill:false }}
    ]
  }},
  options:{{
    ...defaults,
    scales:{{
      x:{{ ...defaults.scales.x }},
      y:{{ ...defaults.scales.y, min:50, max:170 }}
    }}
  }}
}});
"""
    components.html(chart_html("BLOOD PRESSURE HISTORY", chart_body), height=420, scrolling=False)

# Close hh-wrap div
st.markdown("</div>", unsafe_allow_html=True)
