import streamlit as st
import pandas as pd
import os

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AWO Loan App (Persistent)", layout="wide")
st.title("AWO Loan Data – Persistent Storage")

GITHUB_EXCEL_URL = (
    "https://raw.githubusercontent.com/"
    "Walfaanaa/AWO_Free_loan_app/main/loan_file.xlsx"
)

PERSISTENT_FILE = "awo_loans_persistent.csv"

# ---------------- LOAD DATA ----------------
def load_data():
    # ✅ If persistent file exists → ALWAYS use it
    if os.path.exists(PERSISTENT_FILE):
        df = pd.read_csv(
            PERSISTENT_FILE,
            parse_dates=["disbursed_date", "due_date", "return_date"]
        )
        return df

    # 🔁 First run only → load from GitHub
    df = pd.read_excel(
        GITHUB_EXCEL_URL,
        engine="openpyxl"
    )

    # Normalize dates
    for col in ["disbursed_date", "due_date", "return_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 🔒 SAVE ONCE → NEVER LOST
    df.to_csv(PERSISTENT_FILE, index=False)
    return df

df = load_data()

# ---------------- DISPLAY ----------------
df_display = df.copy()
df_display.index = range(1, len(df_display) + 1)

st.success("✅ Data is now persistent and will NEVER disappear")
st.dataframe(df_display, use_container_width=True)

# ---------------- MANUAL RESET (OPTIONAL) ----------------
st.divider()
if st.button("⚠️ Reset data from GitHub (DANGEROUS)"):
    if os.path.exists(PERSISTENT_FILE):
        os.remove(PERSISTENT_FILE)
    st.warning("Persistent data deleted. Reloading from GitHub.")
    st.rerun()
