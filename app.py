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
        
        # Open the specific worksheet tab named 'Main sheet'
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        
        # get_all_records() automatically uses row 1 as dictionary keys
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()

def append_data_to_sheet(new_row_list):
    try:
        client = get_gsheets_client()
        sheet_url = st.secrets["spreadsheet_url"]
        worksheet = client.open_by_url(sheet_url).worksheet("Main sheet")
        # append_row adds the data to the next available empty row
        worksheet.append_row(new_row_list)
        # Clear the cache so the dashboard updates immediately with the new data
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error writing to Google Sheets: {e}")
        return False

st.title("Personal Journey Tracker")

# --- Sidebar for Data Entry ---
st.sidebar.header("Log Daily Data")
with st.sidebar.form("entry_form"):
    date = st.date_input("Date", datetime.date.today())
    
    # Weight tracked in whole pounds
    weight = st.number_input("Weight (lbs)", min_value=50, max_value=500, value=200, step=1, format="%d")
    steps = st.number_input("Steps", min_value=0, value=10000, step=100)
    calories = st.number_input("Calories", min_value=0, value=TARGET_CALORIES, step=1)
    
    st.markdown("### Macros")
    st.caption(f"Target Split: 25% P / 50% C / 25% F")
    protein = st.number_input("Protein (g)", min_value=0, value=TARGET_PROTEIN_G, step=1)
    carbs = st.number_input("Carbs (g)", min_value=0, value=TARGET_CARB_G, step=1)
    fat = st.number_input("Fat (g)", min_value=0, value=TARGET_FAT_G, step=1)
    
    submitted = st.form_submit_button("Log Entry to Google Sheets")
    
    if submitted:
        # Format the date as DD/MM/YYYY to match your existing sheet formatting
        date_str = date.strftime("%d/%m/%Y")
        
        # Prepare the list in the exact order of the sheet columns. 
        new_row = [date_str, calories, "", weight, "", "", "", "", "", "", "", "", steps]
        
        with st.spinner("Writing to Google Sheets..."):
            success = append_data_to_sheet(new_row)
            
        if success:
            st.sidebar.success(f"Data for {date_str} logged successfully!")

# --- Main Dashboard ---
df = load_data()

if not df.empty:
    # Ensure Date column is datetime for correct sorting and charting
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    
    # --- THE FIX: Clean up numeric columns ---
    # This forces blank cells ("") to become proper numbers (0) so the math doesn't crash
    df['Weight (lbs)'] = pd.to_numeric(df['Weight (lbs)'], errors='coerce').fillna(0)
    df['Calories consumed (tgt 1633)'] = pd.to_numeric(df['Calories consumed (tgt 1633)'], errors='coerce').fillna(0)
    df['Steps'] = pd.to_numeric(df['Steps'], errors='coerce').fillna(0)
    
    # Drop rows where the Date is missing (this clears out all those blank rows at the bottom of your sheet)
    df = df.dropna(subset=['Date'])
    
    df = df.sort_values(by="Date")
    
    # Check again if we have data after cleaning out the blank rows
    if not df.empty:
        # Top level metrics
        latest = df.iloc[-1]
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
            st.line_chart(data=df.set_index('Date')['Weight (lbs)'])
            
        with tab2:
            st.bar_chart(data=df.set_index('Date')['Calories consumed (tgt 1633)'])
            
        with tab3:
            st.bar_chart(data=df.set_index('Date')['Steps'])

        st.markdown("---")
        st.subheader("Google Sheet Data")
        # Display the dataframe with the most recent entries at the top
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("No valid dates found in the sheet. Make sure your dates are formatted as DD/MM/YYYY.")
else:
    st.info("No data found in the Google Sheet. Please ensure your sheet has headers and use the sidebar to log your first entry!")
