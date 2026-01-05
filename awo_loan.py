import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AWO Loan Data Viewer",
    layout="wide"
)

st.title("AWO Loan Data (Loaded from GitHub Excel)")

# ---------------- GITHUB RAW EXCEL LINK ----------------
GITHUB_EXCEL_URL = (
    "https://raw.githubusercontent.com/"
    "Walfaanaa/AWO_Free_loan_app/main/loan_file.xlsx"
)

# ---------------- LOAD EXCEL FROM GITHUB ----------------
@st.cache_data(show_spinner=True)
def load_excel_from_github():
    try:
        df = pd.read_excel(
            GITHUB_EXCEL_URL,
            engine="openpyxl",
            sheet_name=0  # first sheet
        )

        # Normalize date columns if they exist
        for col in ["disbursed_date", "due_date", "return_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    except Exception as e:
        st.error(f"❌ Failed to load Excel file: {e}")
        return pd.DataFrame()

# ---------------- LOAD DATA ----------------
df = load_excel_from_github()

# ---------------- DISPLAY STATUS ----------------
if df.empty:
    st.warning("No data found in the Excel file.")
else:
    st.success(f"Loaded {len(df)} records from GitHub Excel")

    # Display column info (debug-friendly)
    with st.expander("🔍 Column Information"):
        st.write(df.dtypes)

    # Show data with 1-based index
    df_display = df.copy()
    df_display.index = range(1, len(df_display) + 1)

    st.subheader("Loan Records")
    st.dataframe(df_display, use_container_width=True)

# ---------------- REFRESH BUTTON ----------------
st.divider()
if st.button("🔄 Reload Latest Data from GitHub"):
    st.cache_data.clear()
    st.rerun()
