import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import datetime

# App config
st.set_page_config(page_title="Journey Tracker", layout="wide")

# Goals Constants
TARGET_CALORIES = 1633
TARGET_PROTEIN_G = 102  # 25% of 1633 kcal
TARGET_CARB_G = 204     # 50% of 1633 kcal
TARGET_FAT_G = 45       # 25% of 1633 kcal

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

# Cache the data load so we don't hit Google's API limits on every button click
@st.cache_data(ttl=60)
def load_data():
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()

def upsert_data_to_sheet(date_str, calories, weight, steps):
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        
        try:
            # Try to find the date string exactly as it appears in column 1
            cell = worksheet.find(date_str, in_column=1)
            row = cell.row
            
            # DATE FOUND: Update specific cells so we don't overwrite any formulas in other columns
            # Column 2 = Calories, Column 4 = Weight, Column 13 = Steps
            worksheet.update_cell(row, 2, calories)
            worksheet.update_cell(row, 4, weight)
            worksheet.update_cell(row, 13, steps)
            
            st.cache_data.clear()
            return "updated"
            
        except Exception as e:
            # If the specific gspread CellNotFound error is thrown, it means it's a new date
            if "CellNotFound" in str(type(e)):
                # DATE NOT FOUND: Append a new row
                new_row = [date_str, calories, "", weight, "", "", "", "", "", "", "", "", steps]
                worksheet.append_row(new_row)
                st.cache_data.clear()
                return "appended"
            else:
                st.error(f"Error finding cell: {e}")
                return "error"
            
    except Exception as e:
        st.error(f"Error writing to Google Sheets: {e}")
        return "error"

st.title("Personal Journey Tracker")

# Load existing data to check against
df = load_data()

# --- Sidebar for Data Entry ---
st.sidebar.header("Log Daily Data")

# We place the date picker OUTSIDE the form so changing the date 
# instantly updates the form fields below with any existing data.
selected_date = st.sidebar.date_input("Select Date", datetime.date.today())
date_str = selected_date.strftime("%d/%m/%Y")

# Default values
existing_weight = 200
existing_calories = TARGET_CALORIES
existing_steps = 10000

# If data exists for this date, pre-fill the variables
if not df.empty:
    day_data = df[df['Date'] == date_str]
    if not day_data.empty:
        latest_entry = day_data.iloc[-1]
        
        # Safely extract existing numbers, ignoring blanks
        try:
            w_val = latest_entry.get('Weight (lbs)', '')
            if str(w_val).strip() != "": existing_weight = int(float(w_val))
        except: pass
        
        try:
            c_val = latest_entry.get('Calories consumed (tgt 1633)', '')
            if str(c_val).strip() != "": existing_calories = int(float(c_val))
        except: pass
        
        try:
            s_val = latest_entry.get('Steps', '')
            if str(s_val).strip() != "": existing_steps = int(float(s_val))
        except: pass

# The actual form
with st.sidebar.form("entry_form"):
    
    # Weight tracked in whole pounds
    weight = st.number_input("Weight (lbs)", min_value=50, max_value=500, value=existing_weight, step=1, format="%d")
    steps = st.number_input("Steps", min_value=0, value=existing_steps, step=100)
    calories = st.number_input("Calories", min_value=0, value=existing_calories, step=1)
    
    st.markdown("### Macros")
    st.caption(f"Target Split: 25% P / 50% C / 25% F")
    protein = st.number_input("Protein (g)", min_value=0, value=TARGET_PROTEIN_G, step=1)
    carbs = st.number_input("Carbs (g)", min_value=0, value=TARGET_CARB_G, step=1)
    fat = st.number_input("Fat (g)", min_value=0, value=TARGET_FAT_G, step=1)
    
    st.markdown("---")
    st.markdown("### Security")
    admin_pin_input = st.text_input("Admin PIN", type="password", help="Required to save or update data")
    
    submitted = st.form_submit_button("Save to Google Sheets")
    
    if submitted:
        # Check against the PIN in your secrets. If not set, it defaults to checking for "0000"
        if admin_pin_input != st.secrets.get("admin_pin", "0000"):
            st.error("Incorrect PIN. Data not saved.")
        else:
            with st.spinner("Writing to Google Sheets..."):
                result = upsert_data_to_sheet(date_str, calories, weight, steps)
                
            if result == "updated":
                st.success(f"Data for {date_str} successfully updated!")
            elif result == "appended":
                st.success(f"New entry for {date_str} successfully logged!")

# --- Main Dashboard ---
if not df.empty:
    # We work on a copy so we don't mess up the raw string dates needed for the sidebar search
    dashboard_df = df.copy()
    
    dashboard_df['Date'] = pd.to_datetime(dashboard_df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # Force blank cells to become proper numbers (0) so the math doesn't crash
    dashboard_df['Weight (lbs)'] = pd.to_numeric(dashboard_df['Weight (lbs)'], errors='coerce').fillna(0)
    dashboard_df['Calories consumed (tgt 1633)'] = pd.to_numeric(dashboard_df['Calories consumed (tgt 1633)'], errors='coerce').fillna(0)
    dashboard_df['Steps'] = pd.to_numeric(dashboard_df['Steps'], errors='coerce').fillna(0)
    
    # Drop rows where the Date is missing
    dashboard_df = dashboard_df.dropna(subset=['Date'])
    
    dashboard_df = dashboard_df.sort_values(by="Date")
    
    if not dashboard_df.empty:
        # Top level metrics
        latest = dashboard_df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Latest Weight", f"{int(latest['Weight (lbs)'])} lbs")
        
        cal_delta = int(latest['Calories consumed (tgt 1633)'] - TARGET_CALORIES)
        col2.metric("Latest Calories", f"{int(latest['Calories consumed (tgt 1633)'])} kcal", delta=f"{cal_delta} from target", delta_color="inverse")
        
        col3.metric("Latest Steps", f"{int(latest['Steps'])}")
        
        st.markdown("---")
        
        # Visualizations
        st.subheader("Trends")
        tab1, tab2, tab3 = st.tabs(["Weight Trend", "Calorie Intake", "Steps"])
        
        with tab1:
            st.line_chart(data=dashboard_df.set_index('Date')['Weight (lbs)'])
            
        with tab2:
            st.bar_chart(data=dashboard_df.set_index('Date')['Calories consumed (tgt 1633)'])
            
        with tab3:
            st.bar_chart(data=dashboard_df.set_index('Date')['Steps'])

        st.markdown("---")
        st.subheader("Google Sheet Data")
        # Format dates nicely for display
        display_df = dashboard_df.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
        st.dataframe(display_df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("No valid dates found in the sheet. Make sure your dates are formatted as DD/MM/YYYY.")
else:
    st.info("No data found in the Google Sheet. Please ensure your sheet has headers and use the sidebar to log your first entry!")
