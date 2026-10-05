import streamlit as st
import requests
import pandas as pd

# Configure the Streamlit page.
st.set_page_config(
    page_title="FraudLense - Audit Log",
    page_icon="📋",
    layout="wide"
)

# FastAPI base URL.
API_URL = "http://127.0.0.1:8000"

# Display the page title.
st.title("📋 Audit Log")

# Explain the purpose of the page.
st.write(
    "View actions performed during fraud investigations."
)

# Request audit logs from FastAPI.
response = requests.get(
    f"{API_URL}/audit-logs"
)

# Check whether the API request was successful.
if response.status_code != 200:
    st.error(
        f"Failed to load audit logs. "
        f"Status code: {response.status_code}"
    )
    st.stop()

# Convert the API response into a Python dictionary.
result = response.json()

# Get the audit log entries.
logs = result["logs"]

# Display the number of audit entries.
st.metric(
    "Total Audit Entries",
    result["count"]
)

# Display the audit entries.
if logs:

    # Convert the logs into a DataFrame.
    audit_df = pd.DataFrame(logs)

    # Display the audit log table.
    st.dataframe(
        audit_df,
        use_container_width=True,
        hide_index=True
    )

else:

    # Display a message if no logs exist.
    st.info("No audit log entries found.")