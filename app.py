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
        
        # Pull raw values so we can rely on index positions rather than exact header names
        values = worksheet.get_all_values()
        if len(values) > 1:
            df = pd.DataFrame(values[1:], columns=values[0])
            # Ensure dataframe has at least 23 columns (up to W) to avoid index errors
            while len(df.columns) < 23:
                df[len(df.columns)] = ""
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()

def upsert_data_to_sheet(date_str, calories, weight, steps, active_cal, protein, carbs, fat, alcohol, notes, sys_bp, dia_bp):
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        
        dates = worksheet.col_values(1)
        
        if date_str in dates:
            # DATE FOUND: Update specific cells
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
            # DATE NOT FOUND: Append new row and dynamically inject formulas
            row = len(dates) + 1
            
            new_row = [
                date_str,                                    # A (0)
                calories,                                    # B (1)
                f"=B{row}-P{row}",                           # C (2) - Net calories
                weight,                                      # D (3)
                f'=INT(D{row}/14) & "st " & MOD(D{row},14) & "lbs"', # E (4) - Weight ST
                f"=D{row}-D{row-1}",                         # F (5) - Gain/Loss
                f'=IF(D{row}="", "", $D$2-D{row})',          # G (6) - Total loss lbs
                f'=IF(D{row}="", "", INT(($D$2-D{row})/14) & "st " & MOD(($D$2-D{row}),14) & "lbs")', # H (7)
                f"=D{row}-175",                              # I (8) - To target lbs
                f'=IF(D{row}>175, INT((D{row}-175)/14) & "st " & MOD((D{row}-175),14) & "lbs", "Goal Reached!")', # J (9)
                f"=ROUND((D{row}*703)/(69^2), 1)",           # K (10) - BMI
                f"=K{row}-25.8",                             # L (11) - To target BMI
                steps,                                       # M (12)
                f"=(M{row} * 2.4) / 5280",                   # N (13) - Approx miles
                "",                                          # O (14) - Blank column based on your list
                active_cal,                                  # P (15)
                protein,                                     # Q (16)
                carbs,                                       # R (17)
                fat,                                         # S (18)
                alcohol,                                     # T (19)
                notes,                                       # U (20)
                sys_bp,                                      # V (21)
                dia_bp                                       # W (22)
            ]
            
            # Using USER_ENTERED forces Google Sheets to execute the formulas
            worksheet.update(values=[new_row], range_name=f"A{row}:W{row}", value_input_option='USER_ENTERED')
            st.cache_data.clear()
            return "appended"
            
    except Exception as e:
        st.error(f"Error writing to Google Sheets: {e}")
        return "error"

st.title("Personal Journey Tracker")

df = load_data()

# --- Sidebar for Data Entry ---
st.sidebar.header("Log Daily Data")

selected_date = st.sidebar.date_input("Select Date", datetime.date.today())
date_str = selected_date.strftime("%d/%m/%Y")

# Default values
e_weight = 200
e_calories = TARGET_CALORIES
e_steps = 10000
e_active = 0
e_protein = 0
e_carbs = 0
e_fat = 0
e_alcohol = 0
e_notes = ""
e_sys = 120
e_dia = 80

# Pre-fill values if date exists (using index numbers so header changes won't break it)
if not df.empty:
    # Filter by Date (Column A / index 0)
    day_data = df[df.iloc[:, 0] == date_str]
    if not day_data.empty:
        latest = day_data.iloc[-1]
        
        def safe_int(val, default):
            try:
                return int(float(val)) if str(val).strip() != "" else default
            except:
                return default

        e_calories = safe_int(latest.iloc[1], e_calories)    # B
        e_weight = safe_int(latest.iloc[3], e_weight)        # D
        e_steps = safe_int(latest.iloc[12], e_steps)         # M
        e_active = safe_int(latest.iloc[15], e_active)       # P
        e_protein = safe_int(latest.iloc[16], e_protein)     # Q
        e_carbs = safe_int(latest.iloc[17], e_carbs)         # R
        e_fat = safe_int(latest.iloc[18], e_fat)             # S
        e_alcohol = safe_int(latest.iloc[19], e_alcohol)     # T
        e_notes = str(latest.iloc[20])                       # U
        e_sys = safe_int(latest.iloc[21], e_sys)             # V
        e_dia = safe_int(latest.iloc[22], e_dia)             # W

with st.sidebar.form("entry_form"):
    
    st.subheader("Core Metrics")
    weight = st.number_input("Weight (lbs)", min_value=50, max_value=500, value=e_weight, step=1)
    calories = st.number_input("Calories Consumed", min_value=0, value=e_calories, step=1)
    active_cal = st.number_input("Active Calories", min_value=0, value=e_active, step=1)
    steps = st.number_input("Steps", min_value=0, value=e_steps, step=100)
    
    st.markdown("---")
    st.subheader("Macros (% of Target)")
    col1, col2, col3 = st.columns(3)
    with col1: protein = st.number_input("Protein", min_value=0, max_value=300, value=e_protein, step=1)
    with col2: carbs = st.number_input("Carbs", min_value=0, max_value=300, value=e_carbs, step=1)
    with col3: fat = st.number_input("Fat", min_value=0, max_value=300, value=e_fat, step=1)
    
    st.markdown("---")
    st.subheader("Health & Extras")
    alcohol = st.number_input("Alcohol (Kcal)", min_value=0, value=e_alcohol, step=1)
    
    b_col1, b_col2 = st.columns(2)
    with b_col1: sys_bp = st.number_input("Systolic BP", min_value=50, max_value=250, value=e_sys, step=1)
    with b_col2: dia_bp = st.number_input("Diastolic BP", min_value=30, max_value=150, value=e_dia, step=1)
    
    notes = st.text_area("Notes", value=e_notes)
    
    st.markdown("---")
    admin_pin_input = st.text_input("Admin PIN", type="password")
    submitted = st.form_submit_button("Save to Google Sheets")
    
    if submitted:
        if admin_pin_input != str(st.secrets.get("admin_pin", "0000")):
            st.error("Incorrect PIN. Data not saved.")
        else:
            with st.spinner("Writing to Google Sheets..."):
                result = upsert_data_to_sheet(date_str, calories, weight, steps, active_cal, protein, carbs, fat, alcohol, notes, sys_bp, dia_bp)
                
            if result == "updated":
                st.success(f"Data for {date_str} successfully updated!")
            elif result == "appended":
                st.success(f"New entry for {date_str} successfully logged!")

# --- Main Dashboard ---
if not df.empty:
    dashboard_df = df.copy()
    
    # Rename columns using explicit index references to prevent plotting crashes
    dashboard_df = dashboard_df.rename(columns={
        dashboard_df.columns[0]: 'Date',
        dashboard_df.columns[1]: 'Calories',
        dashboard_df.columns[3]: 'Weight',
        dashboard_df.columns[12]: 'Steps'
    })
    
    dashboard_df['Date'] = pd.to_datetime(dashboard_df['Date'], format='%d/%m/%Y', errors='coerce')
    dashboard_df['Weight'] = pd.to_numeric(dashboard_df['Weight'], errors='coerce').fillna(0)
    dashboard_df['Calories'] = pd.to_numeric(dashboard_df['Calories'], errors='coerce').fillna(0)
    dashboard_df['Steps'] = pd.to_numeric(dashboard_df['Steps'], errors='coerce').fillna(0)
    
    dashboard_df = dashboard_df.dropna(subset=['Date']).sort_values(by="Date")
    
    if not dashboard_df.empty:
        latest = dashboard_df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Latest Weight", f"{int(latest['Weight'])} lbs")
        cal_delta = int(latest['Calories'] - TARGET_CALORIES)
        col2.metric("Latest Calories", f"{int(latest['Calories'])} kcal", delta=f"{cal_delta} from target", delta_color="inverse")
        col3.metric("Latest Steps", f"{int(latest['Steps'])}")
        
        st.markdown("---")
        
        st.subheader("Trends")
        tab1, tab2, tab3 = st.tabs(["Weight Trend", "Calorie Intake", "Steps"])
        
        with tab1: st.line_chart(data=dashboard_df.set_index('Date')['Weight'])
        with tab2: st.bar_chart(data=dashboard_df.set_index('Date')['Calories'])
        with tab3: st.bar_chart(data=dashboard_df.set_index('Date')['Steps'])

        st.markdown("---")
        st.subheader("Google Sheet Data")
        display_df = dashboard_df.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(display_df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("No valid dates found in the sheet. Make sure your dates are formatted as DD/MM/YYYY.")
else:
    st.info("No data found in the Google Sheet.")
