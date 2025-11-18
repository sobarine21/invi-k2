import streamlit as st
import requests
import pandas as pd
import json
import time

st.set_page_config(page_title="BSE Financial Statements", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


# ------------------------------
# Fetch Financial Data from BSE
# ------------------------------
@st.cache_data(ttl=3600)
def fetch_bse_financials(bse_code):
    url = f"https://api.bseindia.com/BseIndiaAPI/api/FinancialsGetList/w?Type=F&Code={bse_code}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    
    if r.status_code != 200:
        return None
    
    try:
        return r.json()
    except:
        return None


# ------------------------------
# Process Data
# ------------------------------
def parse_financial_table(raw_data):
    if not raw_data or "Table" not in raw_data:
        return None

    rows = raw_data["Table"]
    df = pd.DataFrame(rows)
    return df


# ------------------------------
# Streamlit UI
# ------------------------------
st.title("📊 BSE Financial Statements Explorer")
st.markdown("""
Get **official financial statements** of any listed Indian company  
via **BSE JSON APIs** — No XBRL parsing required.
""")

bse_code = st.text_input("Enter BSE Code (e.g., 500325 for Reliance):")

if st.button("Fetch Data"):
    if not bse_code.strip():
        st.error("Please enter a valid BSE security code.")
    else:
        with st.spinner("Fetching official financial data from BSE..."):
            data = fetch_bse_financials(bse_code.strip())

        if not data:
            st.error("Failed to fetch data. Try another BSE code.")
        else:
            st.success("Data fetched successfully!")

            # Raw JSON expander
            with st.expander("🔍 View Raw JSON Data"):
                st.json(data)

            df = parse_financial_table(data)
            if df is not None:
                st.subheader("📘 Financial Results Table")
                st.dataframe(df, use_container_width=True)

                # CSV Download
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Financials as CSV",
                    csv,
                    f"bse_financials_{bse_code}.csv",
                    "text/csv",
                )
            else:
                st.error("No financial table data available.")


# Footer
st.markdown("---")
st.markdown("Built using **official BSE APIs** • 100% Open Source")
