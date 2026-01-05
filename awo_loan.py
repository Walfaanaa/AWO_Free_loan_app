import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AWO Loan App (Auto Penalty)",
    layout="wide"
)

st.title("AWO Loan Data – Auto Penalty System")

GITHUB_EXCEL_URL = (
    "https://raw.githubusercontent.com/"
    "Walfaanaa/AWO_Free_loan_app/main/loan_file.xlsx"
)

PERSISTENT_FILE = "awo_loans_persistent.csv"
DURATION_MONTHS = 10  # Loan duration
PENALTY_PERCENT = 0.10  # 10% per month overdue

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(PERSISTENT_FILE):
        df = pd.read_csv(PERSISTENT_FILE)

        # Convert date columns safely
        for col in ["disbursed_date", "return_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    # First run → load from GitHub
    df = pd.read_excel(GITHUB_EXCEL_URL, engine="openpyxl")

    for col in ["disbursed_date", "return_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df.to_csv(PERSISTENT_FILE, index=False)
    return df

df = load_data()

# ---------------- CALCULATE DUE DATE ----------------
if "disbursed_date" in df.columns:
    df["due_date"] = df["disbursed_date"] + pd.DateOffset(months=DURATION_MONTHS)
else:
    st.error("❌ No disbursed_date column found!")

# ---------------- CALCULATE PENALTY ----------------
def calculate_penalty(row):
    loan_amount = row.get("loan_amount", 0)  # replace with your actual loan amount column
    due_date = row.get("due_date")
    return_date = row.get("return_date")

    if pd.isna(due_date):
        return 0

    today = pd.Timestamp.today()
    effective_return = return_date if pd.notna(return_date) else today

    months_overdue = (effective_return.year - due_date.year) * 12 + (effective_return.month - due_date.month)
    months_overdue = max(months_overdue, 0)

    penalty = loan_amount * PENALTY_PERCENT * months_overdue
    return round(penalty, 2)

df["penalty"] = df.apply(calculate_penalty, axis=1)

# ---------------- DISPLAY TOTAL PENALTY ----------------
total_penalty = df["penalty"].sum()
st.subheader(f"💰 Total Penalty Owed: {total_penalty:,.2f}")

# ---------------- HIGHLIGHT OVERDUE LOANS ----------------
def highlight_overdue(row):
    if row["penalty"] > 0:
        return ["background-color: #FFCCCC"] * len(row)
    return [""] * len(row)

df_display = df.copy()
df_display.index = range(1, len(df_display) + 1)

st.dataframe(df_display.style.apply(highlight_overdue, axis=1), use_container_width=True)

# ---------------- DEBUG ----------------
with st.expander("🔍 Debug: show columns"):
    st.write(df.columns.tolist())

# ---------------- RESET ----------------
st.divider()
st.subheader("Danger Zone")
if st.button("⚠️ Reset data from GitHub (DANGEROUS)"):
    if os.path.exists(PERSISTENT_FILE):
        os.remove(PERSISTENT_FILE)
    st.warning("Persistent data deleted. Reloading from GitHub...")
    st.rerun()
