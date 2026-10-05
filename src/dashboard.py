import streamlit as st
import requests

# Configure the Streamlit page.
st.set_page_config(
    page_title="FraudLense",
    page_icon="🔍",
    layout="wide"
)

# FastAPI base URL.
API_URL = "http://127.0.0.1:8000"

# Display the application title.
st.title("🔍 FraudLense")

# Display a short description.
st.write(
    "AI-powered fraud detection and investigation dashboard."
)

# Call FastAPI to retrieve all transactions.
response = requests.get(
    f"{API_URL}/transactions"
)

# Check whether the API request was successful.
if response.status_code != 200:
    st.error("Unable to connect to the FraudLense API.")
    st.stop()

# Convert the API response into a Python dictionary.
data = response.json()

# Extract the transaction list.
transactions = data["transactions"]

# Stop if there are no transactions in the database.
if not transactions:
    st.info("No transactions found.")
    st.stop()

# Extract transaction IDs for the selection box.
transaction_ids = [
    transaction["transaction_id"]
    for transaction in transactions
]

# Let the investigator select a transaction.
selected_id = st.selectbox(
    "Select a transaction",
    transaction_ids
)

# Fetch complete details for the selected transaction.
details_response = requests.get(
    f"{API_URL}/transactions/{selected_id}/details"
)

# Check whether the details request was successful.
if details_response.status_code != 200:
    st.error("Unable to retrieve transaction details.")
    st.stop()

# Convert the response into a Python dictionary.
details = details_response.json()

# Extract the three sections.
transaction = details["transaction"]
prediction = details["prediction"]
investigation = details["investigation"]

# Display transaction information.
st.subheader("Transaction Details")

col1, col2 = st.columns(2)

with col1:
    st.write("**Transaction ID:**", transaction["transaction_id"])
    st.write("**Amount:**", transaction["amount"])

with col2:
    st.write("**Transaction Time:**", transaction["transaction_time"])
    st.write("**Created At:**", transaction["created_at"])

# Display prediction information.
st.subheader("Fraud Detection")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Fraud Probability",
        f"{prediction['fraud_probability'] * 100:.4f}%"
    )

with col2:
    st.metric(
        "Risk Level",
        prediction["risk_level"]
    )

with col3:
    st.metric(
        "Model",
        prediction["model_version"]
    )

# Display investigation information.
st.subheader("Investigation")

if investigation is None:

    # The transaction has not been investigated yet.
    st.info("No investigation has been created for this transaction.")

else:

    st.write(
        "**Status:**",
        investigation["status"]
    )

    st.write(
        "**Analyst Decision:**",
        investigation["analyst_decision"]
    )

    st.write(
        "**Analyst Notes:**",
        investigation["analyst_notes"]
    )