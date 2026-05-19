import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

st.set_page_config(page_title="Hardy House Command", layout="wide")

# CSS to make metrics look like cards
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

def get_gsheets_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_data():
    try:
        client = get_gsheets_client()
        worksheet = client.open_by_url(st.secrets["spreadsheet_url"]).worksheet("Main sheet")
        rows = worksheet.get_all_values()[1:]
        clean_rows = []
        for r in rows:
            if not r[0]: continue
            def to_num(val):
                try: return float(str(val).replace('%','').replace(',',''))
                except: return 0.0
            row_data = {
                "Date": pd.to_datetime(r[0], format='%d/%m/%Y'),
                "Cal": to_num(r[1]),
                "Weight": to_num(r[3]),
                "Steps": to_num(r[12]),
                "Prot": to_num(r[16]),
                "Carb": to_num(r[17]),
                "Fat": to_num(r[18]),
                "Alc": to_num(r[19])
            }
            if row_data["Steps"] > 0: clean_rows.append(row_data)
        return pd.DataFrame(clean_rows)
    except Exception as e:
        st.error(f"Error loading: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🛡️ Hardy House Command")
    
    # --- Calculations ---
    avg_cal = df['Cal'].mean()
    avg_steps = df['Steps'].mean()
    s7, s14, s30 = df.tail(7)['Steps'].mean(), df.tail(14)['Steps'].mean(), df.tail(30)['Steps'].mean()
    
    # Dynamic Loss Rate
    total_lbs_lost = df.iloc[0]['Weight'] - df.iloc[-1]['Weight']
    total_days = (df.iloc[-1]['Date'] - df.iloc[0]['Date']).days
    loss_per_week = (total_lbs_lost / total_days) * 7 if total_days > 0 else 0
    
    # Est target date
    weight_to_target = df.iloc[-1]['Weight'] - 175
    days_to_target = weight_to_target / (loss_per_week / 7) if loss_per_week > 0 else 0
    target_date = datetime.now() + timedelta(days=days_to_target)

    # --- UI Layout ---
    with st.container():
        st.subheader("Calorie & Step Targets")
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Calories", f"{avg_cal:.0f}", f"{avg_cal - 1633:.0f}", delta_color="inverse")
        c2.metric("Avg Steps (All time)", f"{avg_steps:,.0f}")
        c3.metric("Maintenance Var", f"{2500 - avg_cal:.0f} kcal gap")

    with st.container():
        st.subheader("Rolling Step Trends")
        r1, r2, r3 = st.columns(3)
        r1.metric("7D Avg Steps", f"{s7:,.0f}")
        r2.metric("14D Avg Steps", f"{s14:,.0f}", f"{s7-s14:,.0f} vs 14D", delta_color="normal")
        r3.metric("30D Avg Steps", f"{s30:,.0f}", f"{s7-s30:,.0f} vs 30D", delta_color="normal")

    with st.container():
        st.subheader("Diet Milestones")
        d1, d2, d3 = st.columns(3)
        d1.metric("Days on Diet", len(df))
        d2.metric("Avg Loss/Week", f"{loss_per_week:.2f} lbs")
        d3.metric("Est. Target Date", target_date.strftime('%b %d, %Y') if loss_per_week > 0 else "N/A")

    with st.expander("See Raw Data"):
        st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("Waiting for data...")
