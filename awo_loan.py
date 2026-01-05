import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AWO Loan Excel Viewer", layout="wide")
st.title("AWO Loan Data – GitHub Excel Viewer")

# ---------------- GITHUB RAW EXCEL ----------------
EXCEL_URL = "https://raw.githubusercontent.com/Walfaanaa/AWO_Free_loan_app/main/loan_file.xlsx"

# ---------------- LOAD EXCEL SAFELY ----------------
@st.cache_data
def load_excel_safe():
    try:
        # Load ALL sheets
        xls = pd.ExcelFile(EXCEL_URL, engine="openpyxl")
        sheets = xls.sheet_names

        return xls, sheets

    except Exception as e:
        st.error(f"Failed to open Excel file: {e}")
        return None, []

xls, sheet_names = load_excel_safe()

# ---------------- SHEET SELECTION ----------------
if not sheet_names:
    st.stop()

sheet = st.selectbox("Select Excel Sheet", sheet_names)

# ---------------- LOAD RAW DATA (NO HEADERS) ----------------
raw_df = pd.read_excel(
    EXCEL_URL,
    sheet_name=sheet,
    header=None,
    engine="openpyxl"
)

st.subheader("🔍 Raw Excel View (Debug)")
st.dataframe(raw_df, use_container_width=True)

# ---------------- FIND REAL HEADER ROW ----------------
header_row = None
for i in range(min(10, len(raw_df))):
    non_empty = raw_df.iloc[i].notna().sum()
    if non_empty >= 3:
        header_row = i
        break

if header_row is None:
    st.error("Could not detect header row automatically.")
    st.stop()

# ---------------- RELOAD WITH REAL HEADER ----------------
df = pd.read_excel(
    EXCEL_URL,
    sheet_name=sheet,
    header=header_row,
    engine="openpyxl"
)

# Drop fully empty columns
df = df.dropna(axis=1, how="all")

# Fix index
df.index = range(1, len(df) + 1)

# ---------------- DISPLAY CLEAN DATA ----------------
st.subheader("✅ Cleaned Loan Data")
st.success(f"Header detected at row {header_row + 1}")
st.dataframe(df, use_container_width=True)

# ---------------- COLUMN INFO ----------------
with st.expander("📋 Column Names"):
    st.write(list(df.columns))

# ---------------- REFRESH ----------------
if st.button("🔄 Reload Latest Excel from GitHub"):
    st.cache_data.clear()
    st.rerun()
