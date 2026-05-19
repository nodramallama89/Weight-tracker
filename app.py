import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# App config
st.set_page_config(page_title="Journey Tracker", layout="wide")

TARGET_CALORIES = 1633

# --- Google Sheets Authentication & Connection ---
def get_gsheets_client():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(credentials)

@st.cache_data(ttl=60)
def load_data():
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        values = worksheet.get_all_values()
        if len(values) > 1:
            df = pd.DataFrame(values[1:], columns=values[0])
            while len(df.columns) < 23:
                df[len(df.columns)] = ""
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def upsert_data_to_sheet(date_str, calories, weight, steps, active_cal, protein, carbs, fat, alcohol, notes, sys_bp, dia_bp):
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        dates = worksheet.col_values(1)
        
        if date_str in dates:
            row = dates.index(date_str) + 1
            updates = [
                {'range': f'B{row}', 'values': [[calories]]},
                {'range': f'D{row}', 'values': [[weight]]},
                {'range': f'M{row}', 'values': [[steps]]},
                {'range': f'P{row}', 'values': [[active_cal]]},
                {'range': f'Q{row}', 'values': [[protein]]},
                {'range': f'R{row}', 'values': [[carbs]]},
                {'range': f'S{row}', 'values': [[fat]]},
                {'range': f'T{row}', 'values': [[alcohol]]},
                {'range': f'U{row}', 'values': [[notes]]},
                {'range': f'V{row}', 'values': [[sys_bp]]},
                {'range': f'W{row}', 'values': [[dia_bp]]},
            ]
            worksheet.batch_update(updates, value_input_option='USER_ENTERED')
            st.cache_data.clear()
            return "updated"
        else:
            row = len(dates) + 1
            new_row = [
                date_str, calories, f"=B{row}-P{row}", weight, 
                f'=INT(D{row}/14) & "st " & MOD(D{row},14) & "lbs"', 
                f"=D{row}-D{row-1}", f'=IF(D{row}="", "", $D$2-D{row})',
                f'=IF(D{row}="", "", INT(($D$2-D{row})/14) & "st " & MOD(($D$2-D{row}),14) & "lbs")',
                f"=D{row}-175", f'=IF(D{row}>175, INT((D{row}-175)/14) & "st " & MOD((D{row}-175),14) & "lbs", "Goal Reached!")',
                f"=ROUND((D{row}*703)/(69^2), 1)", f"=K{row}-25.8", steps,
                f"=(M{row} * 2.4) / 5280", "", active_cal, protein, carbs, fat, alcohol, notes, sys_bp, dia_bp
            ]
            worksheet.update(values=[new_row], range_name=f"A{row}:W{row}", value_input_option='USER_ENTERED')
            st.cache_data.clear()
            return "appended"
    except Exception as e:
        st.error(f"Error writing: {e}")
        return "error"

st.title("Personal Journey Tracker")
df = load_data()

st.sidebar.header("Log Daily Data")
selected_date = st.sidebar.date_input("Select Date", datetime.date.today())
date_str = selected_date.strftime("%d/%m/%Y")

e_weight, e_calories, e_steps, e_active, e_protein, e_carbs, e_fat, e_alcohol, e_notes, e_sys, e_dia = 200, TARGET_CALORIES, 10000, 0, 0, 0, 0, 0, "", 120, 80

if not df.empty:
    day_data = df[df.iloc[:, 0] == date_str]
    if not day_data.empty:
        latest = day_data.iloc[-1]
        def safe_val(idx, default):
            try: return int(float(latest.iloc[idx])) if str(latest.iloc[idx]).strip() != "" else default
            except: return default
        e_calories, e_weight, e_steps, e_active, e_protein, e_carbs, e_fat, e_alcohol, e_notes, e_sys, e_dia = \
            safe_val(1, e_calories), safe_val(3, e_weight), safe_val(12, e_steps), safe_val(15, e_active), \
            safe_val(16, e_protein), safe_val(17, e_carbs), safe_val(18, e_fat), safe_val(19, e_alcohol), \
            str(latest.iloc[20]), safe_val(21, e_sys), safe_val(22, e_dia)

with st.sidebar.form("entry_form"):
    weight = st.number_input("Weight (lbs)", value=e_weight, step=1)
    calories = st.number_input("Calories", value=e_calories, step=1)
    active_cal = st.number_input("Active Calories", value=e_active, step=1)
    steps = st.number_input("Steps", value=e_steps, step=100)
    col1, col2, col3 = st.columns(3)
    with col1: protein = st.number_input("Protein %", value=e_protein)
    with col2: carbs = st.number_input("Carbs %", value=e_carbs)
    with col3: fat = st.number_input("Fat %", value=e_fat)
    alcohol = st.number_input("Alcohol (Kcal)", value=e_alcohol)
    b_col1, b_col2 = st.columns(2)
    with b_col1: sys_bp = st.number_input("Systolic BP", value=e_sys)
    with b_col2: dia_bp = st.number_input("Diastolic BP", value=e_dia)
    notes = st.text_area("Notes", value=e_notes)
    admin_pin_input = st.text_input("Admin PIN", type="password")
    submitted = st.form_submit_button("Save to Google Sheets")
    
    if submitted:
        # Final secure check
        if admin_pin_input != str(st.secrets.get("admin_pin", "")):
            st.error("Incorrect PIN.")
        else:
            with st.spinner("Writing..."):
                res = upsert_data_to_sheet(date_str, calories, weight, steps, active_cal, protein, carbs, fat, alcohol, notes, sys_bp, dia_bp)
                if res == "updated": st.success("Updated!")
                elif res == "appended": st.success("Logged!")

if not df.empty:
    dashboard_df = df.copy()
    dashboard_df = dashboard_df.rename(columns={dashboard_df.columns[0]: 'Date', dashboard_df.columns[1]: 'Calories', dashboard_df.columns[3]: 'Weight', dashboard_df.columns[12]: 'Steps'})
    dashboard_df['Date'] = pd.to_datetime(dashboard_df['Date'], format='%d/%m/%Y', errors='coerce')
    dashboard_df['Weight'] = pd.to_numeric(dashboard_df['Weight'], errors='coerce').fillna(0)
    dashboard_df['Calories'] = pd.to_numeric(dashboard_df['Calories'], errors='coerce').fillna(0)
    dashboard_df['Steps'] = pd.to_numeric(dashboard_df['Steps'], errors='coerce').fillna(0)
    dashboard_df = dashboard_df.dropna(subset=['Date']).sort_values(by="Date")
    
    if not dashboard_df.empty:
        latest = dashboard_df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Weight", f"{int(latest['Weight'])} lbs")
        col2.metric("Latest Calories", f"{int(latest['Calories'])} kcal")
        col3.metric("Latest Steps", f"{int(latest['Steps'])}")
        st.subheader("Google Sheet Data")
        display_df = dashboard_df.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(display_df.sort_values(by="Date", ascending=False), use_container_width=True)
