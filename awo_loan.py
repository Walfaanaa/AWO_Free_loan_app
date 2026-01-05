import streamlit as st
import pandas as pd
import os

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

# ---------------- LOAD DATA ----------------
def load_data():
    # ✅ If persistent file exists → ALWAYS use it
    if os.path.exists(PERSISTENT_FILE):
        df = pd.read_csv(PERSISTENT_FILE)

        # ✅ Safely convert date columns (only if they exist)
        for col in ["disbursed_date", "due_date", "return_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    # 🔁 First run only → load from GitHub Excel
    df = pd.read_excel(
        GITHUB_EXCEL_URL,
        engine="openpyxl"
    )

    # ✅ Normalize date columns safely
    for col in ["disbursed_date", "due_date", "return_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 🔒 SAVE ONCE → survives reruns (until cloud reset)
    df.to_csv(PERSISTENT_FILE, index=False)
    return df


# ---------------- LOAD ----------------
df = load_data()

# ---------------- DISPLAY ----------------
df_display = df.copy()
df_display.index = range(1, len(df_display) + 1)

st.success("✅ Data loaded successfully (persistent while app is running)")
st.dataframe(df_display, use_container_width=True)

# ---------------- DEBUG (OPTIONAL) ----------------
with st.expander("🔍 Show column names"):
    st.write(df.columns.tolist())

# ---------------- MANUAL RESET ----------------
st.divider()
st.subheader("Danger Zone")

if st.button("⚠️ Reset data from GitHub (DANGEROUS)"):
    if os.path.exists(PERSISTENT_FILE):
        os.remove(PERSISTENT_FILE)

    st.warning("Persistent data deleted. Reloading from GitHub...")
    st.rerun()
