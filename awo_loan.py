import streamlit as st
import pandas as pd
import os
from dateutil.relativedelta import relativedelta

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AWO Loan App (Persistent)",
    layout="wide"
)

st.title("AWO Loan Data – Persistent Storage")

GITHUB_EXCEL_URL = (
    "https://raw.githubusercontent.com/"
    "Walfaanaa/AWO_Free_loan_app/main/loan_file.xlsx"
)

PERSISTENT_FILE = "awo_loans_persistent.csv"

DURATION_MONTHS = 10  # loan duration

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

    # Normalize date columns
    for col in ["disbursed_date", "return_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df.to_csv(PERSISTENT_FILE, index=False)
    return df

# ---------------- RUN ----------------
df = load_data()

# ---------------- CALCULATE DUE DATE ----------------
# Add 'due_date' based on disbursed_date + 10 months
if "disbursed_date" in df.columns:
    df["due_date"] = df["disbursed_date"] + pd.DateOffset(months=DURATION_MONTHS)
else:
    st.error("❌ No disbursed_date column found!")

# ---------------- PENALTY CALCULATION ----------------
def calculate_penalty(row):
    loan_amount = row.get("loan_amount", 0)  # replace with your column name
    due_date = row.get("due_date")
    return_date = row.get("return_date")

    if pd.isna(due_date):
        return "❌ No due date"

    # Returned on time → no penalty
    if pd.notna(return_date) and return_date <= due_date:
        return 0

    # Not returned or late → calculate months overdue
    today = pd.Timestamp.today()
    effective_return = return_date if pd.notna(return_date) else today

    months_overdue = (effective_return.year - due_date.year) * 12 + (effective_return.month - due_date.month)
    months_overdue = max(months_overdue, 0)  # minimum 0

    penalty = loan_amount * 0.10 * months_overdue
    return round(penalty, 2)

df["penalty"] = df.apply(calculate_penalty, axis=1)

# ---------------- DISPLAY ----------------
df_display = df.copy()
df_display.index = range(1, len(df_display) + 1)

st.success("✅ Data loaded successfully with due date & penalty calculation")
st.dataframe(df_display, use_container_width=True)

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
