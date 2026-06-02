import streamlit as st
import pandas as pd
import gspread
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Hardy House Command", layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────
#  PREMIUM CSS — iOS / macOS Liquid Glass HUD
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700;800&display=swap');

/* ── Root tokens ── */
:root {
  --glass-bg:        rgba(255,255,255,0.06);
  --glass-bg-hover:  rgba(255,255,255,0.10);
  --glass-border:    rgba(255,255,255,0.12);
  --glass-border-hi: rgba(255,255,255,0.22);
  --glass-shadow:    0 8px 32px rgba(0,0,0,0.45), 0 1px 0 rgba(255,255,255,0.06) inset;
  --glass-shadow-lg: 0 20px 60px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.08) inset;
  --blur:            blur(24px) saturate(180%);
  --blur-sm:         blur(12px) saturate(160%);

  --accent-blue:   #0a84ff;
  --accent-green:  #30d158;
  --accent-red:    #ff453a;
  --accent-orange: #ff9f0a;
  --accent-purple: #bf5af2;
  --accent-teal:   #5ac8fa;
  --accent-yellow: #ffd60a;

  --text-primary:   rgba(255,255,255,0.95);
  --text-secondary: rgba(255,255,255,0.55);
  --text-tertiary:  rgba(255,255,255,0.30);

  --font-display: 'Syne', sans-serif;
  --font-body:    'Instrument Sans', sans-serif;
  --radius-xl: 22px;
  --radius-lg: 16px;
  --radius-md: 12px;
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

/* Overlay gradient for depth */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(0,0,0,0.35) 0%,
    rgba(0,6,20,0.50) 50%,
    rgba(0,0,0,0.40) 100%
  );
  pointer-events: none;
  z-index: 0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1600px; }

/* ── Page title ── */
h1 {
  font-family: var(--font-display) !important;
  font-size: 2.6rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em !important;
  color: var(--text-primary) !important;
  text-align: center !important;
  margin-bottom: 0.3rem !important;
  background: linear-gradient(135deg, #ffffff 30%, rgba(255,255,255,0.65));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ── GLASS CARD ── */
.card {
  background: var(--glass-bg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border-radius: var(--radius-xl);
  padding: 22px 20px 18px;
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  border-top-color: rgba(255,255,255,0.18);
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(.23,1,.32,1),
              box-shadow 0.3s cubic-bezier(.23,1,.32,1),
              background 0.3s ease,
              border-color 0.3s ease;
  animation: fadeSlideUp 0.55s cubic-bezier(.23,1,.32,1) both;
}

.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
}

/* Shimmer sweep on load */
.card::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(
    105deg,
    transparent 40%,
    rgba(255,255,255,0.06) 50%,
    transparent 60%
  );
  animation: shimmer 2.8s ease-in-out 0.3s 1 both;
  pointer-events: none;
}

.card:hover {
  transform: translateY(-3px) scale(1.008);
  box-shadow: var(--glass-shadow-lg);
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hi);
}

/* ── Card typography ── */
.val {
  font-family: var(--font-display);
  font-size: 2.1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 6px 0 2px;
  color: var(--text-primary);
  line-height: 1;
}

.val-sm {
  font-family: var(--font-display);
  font-size: 1.65rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 6px 0 2px;
  color: var(--text-primary);
  line-height: 1;
}

.label {
  font-family: var(--font-body);
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  opacity: 0.55;
  color: var(--text-primary);
}

.delta {
  font-family: var(--font-body);
  font-size: 0.78rem;
  font-weight: 500;
  margin-top: 6px;
  padding: 3px 10px;
  border-radius: 50px;
  display: inline-block;
}

.delta-pos {
  background: rgba(48, 209, 88, 0.15);
  color: var(--accent-green);
  border: 1px solid rgba(48, 209, 88, 0.25);
}

.delta-neg {
  background: rgba(255, 69, 58, 0.15);
  color: var(--accent-red);
  border: 1px solid rgba(255, 69, 58, 0.20);
}

/* ── Section header ── */
.section-header {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--text-primary);
  margin: 0 0 1.2rem;
  text-align: center;
  animation: fadeSlideUp 0.4s cubic-bezier(.23,1,.32,1) both;
}

.section-sub {
  font-family: var(--font-body);
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
  margin-top: -0.8rem;
  margin-bottom: 1.4rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* ── Tab bar ── */
div[data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: var(--blur-sm) !important;
  -webkit-backdrop-filter: var(--blur-sm) !important;
  border-radius: 16px !important;
  padding: 5px !important;
  border: 1px solid var(--glass-border) !important;
  box-shadow: var(--glass-shadow) !important;
  gap: 2px !important;
  margin-bottom: 1.6rem !important;
}

div[data-baseweb="tab"] {
  border-radius: 11px !important;
  transition: background 0.25s ease, transform 0.2s ease !important;
}

div[data-baseweb="tab"]:hover {
  background: rgba(255,255,255,0.08) !important;
}

div[data-baseweb="tab"][aria-selected="true"] {
  background: rgba(255,255,255,0.13) !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3), 0 1px 0 rgba(255,255,255,0.12) inset !important;
}

div[data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
  font-family: var(--font-body) !important;
  color: var(--text-primary) !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em !important;
}

div[data-baseweb="tab-highlight"] {
  display: none !important;
}

/* ── Chart wrapper ── */
.stPlotlyChart {
  background: var(--glass-bg) !important;
  backdrop-filter: var(--blur) !important;
  -webkit-backdrop-filter: var(--blur) !important;
  border-radius: var(--radius-xl) !important;
  padding: 8px !important;
  border: 1px solid var(--glass-border) !important;
  border-top-color: rgba(255,255,255,0.16) !important;
  box-shadow: var(--glass-shadow) !important;
  transition: box-shadow 0.3s ease !important;
  animation: fadeSlideUp 0.6s cubic-bezier(.23,1,.32,1) 0.1s both !important;
}

.stPlotlyChart:hover {
  box-shadow: var(--glass-shadow-lg) !important;
}

/* ── Pill badge ── */
.pill {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 50px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.pill-blue   { background: rgba(10,132,255,0.18); color: #5aabff; border: 1px solid rgba(10,132,255,0.25); }
.pill-green  { background: rgba(48,209,88,0.15);  color: #4be37a; border: 1px solid rgba(48,209,88,0.25); }
.pill-orange { background: rgba(255,159,10,0.15); color: #ffb830; border: 1px solid rgba(255,159,10,0.25); }
.pill-purple { background: rgba(191,90,242,0.15); color: #cf82f8; border: 1px solid rgba(191,90,242,0.25); }
.pill-red    { background: rgba(255,69,58,0.15);  color: #ff6b63; border: 1px solid rgba(255,69,58,0.25); }

/* ── Divider ── */
.glass-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--glass-border-hi), transparent);
  margin: 1.5rem 0;
  border: none;
}

/* ── Stat row (inline kpi strip) ── */
.stat-strip {
  background: var(--glass-bg);
  backdrop-filter: var(--blur-sm);
  -webkit-backdrop-filter: var(--blur-sm);
  border: 1px solid var(--glass-border);
  border-top-color: rgba(255,255,255,0.15);
  border-radius: var(--radius-lg);
  padding: 16px 24px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
  box-shadow: var(--glass-shadow);
  animation: fadeSlideUp 0.5s cubic-bezier(.23,1,.32,1) both;
}

.stat-item {
  text-align: center;
  flex: 1;
  position: relative;
}

.stat-item + .stat-item::before {
  content: '';
  position: absolute;
  left: 0; top: 10%; bottom: 10%;
  width: 1px;
  background: var(--glass-border);
}

/* ── Keyframes ── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0);    }
}

@keyframes shimmer {
  0%   { left: -100%; }
  100% { left: 200%;  }
}

@keyframes pulseRing {
  0%   { transform: scale(1);    opacity: 0.7; }
  70%  { transform: scale(1.35); opacity: 0;   }
  100% { transform: scale(1);    opacity: 0;   }
}

/* Staggered card animation delays */
.card:nth-child(1)  { animation-delay: 0.00s; }
.card:nth-child(2)  { animation-delay: 0.06s; }
.card:nth-child(3)  { animation-delay: 0.12s; }
.card:nth-child(4)  { animation-delay: 0.18s; }
.card:nth-child(5)  { animation-delay: 0.24s; }
.card:nth-child(6)  { animation-delay: 0.30s; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }

/* ── Column gap tighten ── */
[data-testid="column"] { padding: 0 6px !important; }

/* ── Responsive tweaks ── */
@media (max-width: 768px) {
  .val { font-size: 1.6rem; }
  .block-container { padding: 1rem 1rem 2rem; }
  h1 { font-size: 1.8rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
def apply_theme(fig, title="", subtitle=""):
    full_title = f"<b>{title}</b>" + (f"<br><span style='font-size:12px;color:rgba(255,255,255,0.4);font-weight:400'>{subtitle}</span>" if subtitle else "")
    fig.update_layout(
        title=dict(
            text=full_title,
            font=dict(family="Syne, sans-serif", color='rgba(255,255,255,0.92)', size=18),
            x=0.03, xanchor='left', y=0.96
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Instrument Sans, sans-serif", color='rgba(255,255,255,0.75)', size=12),
        legend=dict(
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.12)',
            borderwidth=1,
            x=0.01, y=0.99,
            orientation='h'
        ),
        xaxis=dict(
            color='rgba(255,255,255,0.5)',
            gridcolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='rgba(255,255,255,0.5)', size=11),
            linecolor='rgba(255,255,255,0.1)',
            zeroline=False,
            showgrid=True,
        ),
        yaxis=dict(
            color='rgba(255,255,255,0.5)',
            gridcolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='rgba(255,255,255,0.5)', size=11),
            linecolor='rgba(255,255,255,0.1)',
            zeroline=False,
        ),
        yaxis2=dict(
            color='rgba(255,255,255,0.5)',
            gridcolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='rgba(255,255,255,0.5)', size=11),
            linecolor='rgba(255,255,255,0.1)',
            zeroline=False,
        ),
        margin=dict(l=16, r=16, t=64, b=16),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(20,20,30,0.9)',
            bordercolor='rgba(255,255,255,0.15)',
            font=dict(color='white', size=12, family='Instrument Sans, sans-serif'),
        ),
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
    return pd.to_numeric(
        df.iloc[:, idx].astype(str).str.replace('%', '').str.replace(',', ''),
        errors='coerce'
    )

def card(label, value, delta_val=None, delta_label="", color=None, size="normal"):
    val_class = "val" if size == "normal" else "val-sm"
    val_color  = color or "var(--text-primary)"
    delta_html = ""
    if delta_val is not None:
        cls   = "delta-pos" if delta_val >= 0 else "delta-neg"
        arrow = "▲" if delta_val >= 0 else "▼"
        delta_html = f"<div class='delta {cls}'>{arrow} {abs(delta_val):,.0f} {delta_label}</div>"
    return f"""
    <div class='card'>
      <div class='label'>{label}</div>
      <div class='{val_class}' style='color:{val_color}'>{value}</div>
      {delta_html}
    </div>"""

def pill(text, color="blue"):
    return f"<span class='pill pill-{color}'>{text}</span>"


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
if not df.empty:

    # ── Global header ──
    st.markdown("""
    <div style='text-align:center; margin-bottom:0.2rem; animation: fadeSlideUp 0.4s ease both;'>
      <span style='font-family:Instrument Sans,sans-serif; font-size:0.72rem; font-weight:600;
                   letter-spacing:0.18em; text-transform:uppercase;
                   color:rgba(255,255,255,0.4);'>Hardy House</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h1>Command Centre</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-bottom:2rem; animation: fadeSlideUp 0.45s ease 0.05s both; opacity:0; animation-fill-mode:forwards;'>
      <span style='font-family:Instrument Sans,sans-serif; font-size:0.75rem;
                   color:rgba(255,255,255,0.35); letter-spacing:0.06em;'>
        Live health telemetry — synced from Google Sheets
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Tab bar ──
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🛡️ Review", "📊 Lifetime", "🔥 Calories", "⚖️ Weight",
        "📉 Trend", "🚀 Velocity", "👟 Steps", "🥗 Macros",
        "📈 Averages", "❤️ Blood Pressure"
    ])

    # ══════════════════════════════════════════
    #  TAB 1 — Review (Yesterday's Debrief)
    # ══════════════════════════════════════════
    with tab1:
        completed = df[df.iloc[:, 12] != ""]
        if not completed.empty:
            y = completed.iloc[-1]
            date_str = str(y.iloc[0])[:10] if pd.notna(y.iloc[0]) else "Latest"
            cals  = float(str(y.iloc[1]).replace(',', ''))
            steps = float(str(y.iloc[12]).replace(',', ''))

            st.markdown("<div class='section-header'>Yesterday's Debrief</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>{date_str}</div>", unsafe_allow_html=True)

            # Primary KPIs
            c1, c2 = st.columns(2)
            cal_delta = cals - 1633
            step_delta = steps - 10000
            with c1:
                col  = "#ff453a" if cal_delta > 0 else "#30d158"
                st.markdown(card("Calories Consumed", f"{cals:,.0f} kcal",
                                 delta_val=cal_delta, delta_label="vs 1,633"), unsafe_allow_html=True)
            with c2:
                col  = "#30d158" if step_delta >= 0 else "#ff453a"
                st.markdown(card("Steps Taken", f"{steps:,.0f}",
                                 delta_val=step_delta, delta_label="vs 10k"), unsafe_allow_html=True)

            st.markdown("<hr class='glass-divider'>", unsafe_allow_html=True)

            # Macro split
            st.markdown("""
              <div style='font-family:Instrument Sans,sans-serif; font-size:0.68rem;
                           font-weight:600; letter-spacing:0.14em; text-transform:uppercase;
                           color:rgba(255,255,255,0.38); text-align:center; margin-bottom:0.8rem;'>
                Macro Split
              </div>""", unsafe_allow_html=True)

            macro_labels  = ["Protein", "Carbs", "Fat", "Alcohol"]
            macro_colors  = ["#ff453a", "#5ac8fa", "#ffd60a", "#bf5af2"]
            macro_indices = [16, 17, 18, 19]
            m = st.columns(4)
            for i, (lbl, color, idx) in enumerate(zip(macro_labels, macro_colors, macro_indices)):
                val_raw = str(y.iloc[idx]).replace('%', '')
                m[i].markdown(f"""
                  <div class='card'>
                    <div class='label'>{lbl}</div>
                    <div class='val-sm' style='color:{color}'>{val_raw}%</div>
                  </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2 — Lifetime Stats
    # ══════════════════════════════════════════
    with tab2:
        l = df.iloc[-1]
        st.markdown("<div class='section-header'>Lifetime Stats</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>Since day one</div>", unsafe_allow_html=True)

        # Days on diet — hero card
        st.markdown(f"""
          <div class='card' style='background:linear-gradient(135deg,rgba(10,132,255,0.12),rgba(255,255,255,0.04));
               border-color:rgba(10,132,255,0.25); margin-bottom:1.4rem;'>
            <div class='label'>Days on Programme</div>
            <div style='font-family:Syne,sans-serif; font-size:3.8rem; font-weight:800;
                        letter-spacing:-0.04em; color:#5aabff; margin:6px 0 2px; line-height:1;'>{len(df)}</div>
            <div style='font-size:0.72rem; color:rgba(255,255,255,0.35);'>consecutive days logged</div>
          </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Total Loss", f"{l.iloc[6]} lbs", color="#30d158"), unsafe_allow_html=True)
            st.markdown(card("Total Loss", f"{l.iloc[7]} st",  color="#30d158"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("To Target", f"{l.iloc[8]} lbs", color="#ff9f0a"), unsafe_allow_html=True)
            st.markdown(card("To Target", f"{l.iloc[9]} st",  color="#ff9f0a"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Current BMI", f"{l.iloc[10]}",  color="#5ac8fa"), unsafe_allow_html=True)
            st.markdown(card("Target BMI",  f"{l.iloc[11]}",  color="#bf5af2"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 3 — Calories
    # ══════════════════════════════════════════
    with tab3:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=get_num(1),
            name="Calories In",
            marker=dict(
                color=get_num(1),
                colorscale=[[0,'#1a3a2a'],[0.5,'#ff9f0a'],[1,'#ff453a']],
                line=dict(width=0),
            ),
            opacity=0.9,
        ))
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=get_num(2),
            name="Net Calories",
            mode='lines',
            line=dict(color='rgba(255,255,255,0.9)', width=2.5, dash='dot'),
        ))
        fig.add_hline(y=1633, line_dash="dash", line_color="rgba(48,209,88,0.5)",
                      annotation_text="Target 1,633", annotation_font_color="rgba(48,209,88,0.8)")
        st.plotly_chart(apply_theme(fig, "Caloric Intake", "Daily intake vs target"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 4 — Weight
    # ══════════════════════════════════════════
    with tab4:
        w_series = get_num(3).dropna()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            mode='lines',
            line=dict(color='rgba(90,171,255,0.2)', width=1),
            showlegend=False,
        ))
        # Rolling 7-day avg
        rolling = w_series.rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(rolling), 0], y=rolling,
            name="7-Day Average",
            mode='lines',
            line=dict(color='#0a84ff', width=3),
            fill='tozeroy',
            fillcolor='rgba(10,132,255,0.06)',
        ))
        fig.add_trace(go.Scatter(
            x=df.iloc[:len(w_series), 0], y=w_series,
            name="Daily Weight",
            mode='markers',
            marker=dict(color='rgba(255,255,255,0.7)', size=4, line=dict(color='white', width=0.5)),
        ))
        st.plotly_chart(apply_theme(fig, "Weight Trajectory", "lbs — with 7-day rolling average"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 5 — Gain / Loss Trend
    # ══════════════════════════════════════════
    with tab5:
        trend = get_num(5)
        colors_trend = ['rgba(48,209,88,0.85)' if v < 0 else 'rgba(255,69,58,0.85)' for v in trend]
        fig = go.Figure()
        fig.add_hrect(y0=-999, y1=0, fillcolor='rgba(48,209,88,0.04)', layer="below", line_width=0)
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=trend,
            mode='lines+markers',
            line=dict(color='#ff9f0a', width=2.5),
            marker=dict(color=colors_trend, size=5, line=dict(color='rgba(0,0,0,0.3)', width=0.5)),
            name="Net Trend",
            fill='tozeroy',
            fillcolor='rgba(255,159,10,0.08)',
        ))
        fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)
        st.plotly_chart(apply_theme(fig, "Weight Loss Trend", "cumulative gain / loss in lbs"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 6 — Velocity
    # ══════════════════════════════════════════
    with tab6:
        velocity = get_num(3).diff() * -1
        bar_colors = ['rgba(48,209,88,0.80)' if x > 0 else 'rgba(255,69,58,0.80)'
                      for x in velocity.fillna(0)]
        fig = go.Figure()
        fig.add_hrect(y0=0, y1=999,  fillcolor='rgba(48,209,88,0.04)',  layer="below", line_width=0)
        fig.add_hrect(y0=-999, y1=0, fillcolor='rgba(255,69,58,0.04)',  layer="below", line_width=0)
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=velocity,
            name="Daily Δ",
            marker=dict(color=bar_colors, line=dict(width=0)),
            opacity=0.9,
        ))
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0],
            y=velocity.rolling(7, min_periods=1).mean(),
            name="7-Day Avg Velocity",
            mode='lines',
            line=dict(color='rgba(255,255,255,0.85)', width=2.5, dash='dot'),
        ))
        fig.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)")
        st.plotly_chart(apply_theme(fig, "Loss Velocity", "lbs/day — green = loss, red = gain"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 7 — Steps
    # ══════════════════════════════════════════
    with tab7:
        steps_data  = get_num(12)
        active_cals = get_num(15)
        step_colors = ['rgba(26,209,152,0.80)' if s >= 10000 else 'rgba(255,159,10,0.75)'
                       for s in steps_data.fillna(0)]
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=df.iloc[:, 0], y=steps_data,
            name="Steps",
            marker=dict(color=step_colors, line=dict(width=0)),
        ), secondary_y=False)
        fig.add_hline(y=10000, line_dash="dash", line_color="rgba(26,209,152,0.4)",
                      annotation_text="10k target", annotation_font_color="rgba(26,209,152,0.7)")
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=active_cals,
            name="Active Calories",
            mode='lines',
            line=dict(color='#ffd60a', width=2.5),
        ), secondary_y=True)
        st.plotly_chart(apply_theme(fig, "Daily Steps & Active Burn", "green bars = 10k+ goal met"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 8 — Macros
    # ══════════════════════════════════════════
    with tab8:
        fig = go.Figure()
        macro_cfg = [
            (16, "Protein", "#ff453a", "rgba(255,69,58,0.07)"),
            (17, "Carbs",   "#5ac8fa", "rgba(90,200,250,0.07)"),
            (18, "Fat",     "#ffd60a", "rgba(255,214,10,0.07)"),
        ]
        for idx, name, color, fill in macro_cfg:
            series = get_num(idx)
            fig.add_trace(go.Scatter(
                x=df.iloc[:, 0], y=series,
                name=name,
                mode='lines',
                line=dict(color=color, width=2.5),
                fill='tozeroy',
                fillcolor=fill,
            ))
        st.plotly_chart(apply_theme(fig, "Macro Breakdown", "% split over time — protein / carbs / fat"), use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 9 — Averages
    # ══════════════════════════════════════════
    with tab9:
        avg_loss = (get_num(3).iloc[0] - get_num(3).iloc[-1]) / (len(df) / 7)

        st.markdown("<div class='section-header'>Historical Averages</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-sub'>All-time programme statistics</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(card("Avg Calories / Day", f"{get_num(1).mean():,.0f} kcal", color="#ff9f0a"), unsafe_allow_html=True)
            st.markdown(card("Avg Protein",         f"{get_num(16).mean():.0f}%",     color="#ff453a"), unsafe_allow_html=True)
        with c2:
            st.markdown(card("Avg Steps / Day",     f"{get_num(12).mean():,.0f}",      color="#30d158"), unsafe_allow_html=True)
            st.markdown(card("Avg Carbs",            f"{get_num(17).mean():.0f}%",     color="#5ac8fa"), unsafe_allow_html=True)
        with c3:
            st.markdown(card("Avg Loss / Week",      f"{avg_loss:.2f} lbs",            color="#0a84ff"), unsafe_allow_html=True)
            st.markdown(card("Avg Fat",              f"{get_num(18).mean():.0f}%",     color="#ffd60a"), unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 10 — Blood Pressure
    # ══════════════════════════════════════════
    with tab10:
        sys_data = get_num(21)
        dia_data = get_num(22)
        fig = go.Figure()

        # Clinical range bands
        fig.add_hrect(y0=0,   y1=80,  fillcolor='rgba(48,209,88,0.06)',  layer="below", line_width=0, annotation_text="Normal Diastolic",  annotation_font_color="rgba(48,209,88,0.4)",  annotation_position="left")
        fig.add_hrect(y0=80,  y1=90,  fillcolor='rgba(255,214,10,0.05)', layer="below", line_width=0)
        fig.add_hrect(y0=120, y1=140, fillcolor='rgba(255,159,10,0.05)', layer="below", line_width=0, annotation_text="Elevated Systolic",  annotation_font_color="rgba(255,159,10,0.4)", annotation_position="right")
        fig.add_hrect(y0=140, y1=999, fillcolor='rgba(255,69,58,0.05)',  layer="below", line_width=0, annotation_text="Stage 2 Hypertension", annotation_font_color="rgba(255,69,58,0.4)", annotation_position="right")

        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=sys_data,
            name="Systolic",
            mode='lines+markers',
            connectgaps=True,
            line=dict(color='#ff453a', width=3),
            marker=dict(size=5, color='#ff453a'),
            fill='tozeroy',
            fillcolor='rgba(255,69,58,0.05)',
        ))
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0], y=dia_data,
            name="Diastolic",
            mode='lines+markers',
            connectgaps=True,
            line=dict(color='#5ac8fa', width=3),
            marker=dict(size=5, color='#5ac8fa'),
            fill='tozeroy',
            fillcolor='rgba(90,200,250,0.05)',
        ))

        # Target lines
        fig.add_hline(y=120, line_dash="dash", line_color="rgba(255,159,10,0.35)",
                      annotation_text="Systolic target 120", annotation_font_color="rgba(255,159,10,0.6)")
        fig.add_hline(y=80,  line_dash="dash", line_color="rgba(48,209,88,0.35)",
                      annotation_text="Diastolic target 80", annotation_font_color="rgba(48,209,88,0.6)")

        st.plotly_chart(apply_theme(fig, "Blood Pressure Monitor", "systolic / diastolic — mmHg"), use_container_width=True)

else:
    st.markdown("""
    <div style='display:flex; align-items:center; justify-content:center;
                min-height:60vh; flex-direction:column; gap:1rem;'>
      <div style='font-size:3rem;'>⚠️</div>
      <div style='font-family:Syne,sans-serif; font-size:1.4rem; font-weight:700;
                  color:rgba(255,255,255,0.8);'>Could not load data</div>
      <div style='font-family:Instrument Sans,sans-serif; font-size:0.85rem;
                  color:rgba(255,255,255,0.38);'>Check your Google Sheets credentials in Streamlit secrets</div>
    </div>""", unsafe_allow_html=True)
