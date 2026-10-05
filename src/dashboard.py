import streamlit as st
import requests
import pandas as pd


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

# Configure the Streamlit page.
st.set_page_config(
    page_title="FraudLense",
    page_icon="🔍",
    layout="wide"
)


# ---------------------------------------------------------
# FASTAPI CONFIGURATION
# ---------------------------------------------------------

# FastAPI base URL.
API_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------

# Display the application title.
st.title("🔍 FraudLense")

# Explain the purpose of the application.
st.write(
    "Use machine learning to predict whether a transaction is fraudulent."
)


# ---------------------------------------------------------
# BATCH SCREENING
# ---------------------------------------------------------

# Display the batch screening section.
st.header("Batch Transaction Screening")

# Explain the expected CSV format.
st.write(
    "Upload a CSV containing multiple transactions with the "
    "Time, V1–V28, and Amount columns."
)


# ---------------------------------------------------------
# FILE UPLOAD
# ---------------------------------------------------------

# Allow the user to upload a CSV file.
uploaded_file = st.file_uploader(
    "Upload transaction CSV",
    type=["csv"]
)


# ---------------------------------------------------------
# REQUIRED MODEL FEATURES
# ---------------------------------------------------------

# Define the exact features required by the XGBoost model.
required_columns = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7",
    "V8", "V9", "V10", "V11", "V12", "V13", "V14",
    "V15", "V16", "V17", "V18", "V19", "V20", "V21",
    "V22", "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount"
]


# ---------------------------------------------------------
# PROCESS UPLOADED FILE
# ---------------------------------------------------------

# Continue only if a file has been uploaded.
if uploaded_file is not None:

    # Read the uploaded CSV into a DataFrame.
    transaction_df = pd.read_csv(uploaded_file)

    # Check whether any required columns are missing.
    missing_columns = [
        column
        for column in required_columns
        if column not in transaction_df.columns
    ]

    # Stop if required columns are missing.
    if missing_columns:

        st.error(
            f"Missing columns: {', '.join(missing_columns)}"
        )

        st.stop()

    # Display the number of uploaded transactions.
    st.info(
        f"{len(transaction_df)} transactions ready for screening."
    )

    # -----------------------------------------------------
    # SCREEN TRANSACTIONS
    # -----------------------------------------------------

    # Create the screening button.
    if st.button("Screen Transactions"):

        # Send the complete CSV file to FastAPI.
        response = requests.post(
            f"{API_URL}/predict/batch",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/csv"
                )
            }
        )

        # Check whether the API request was successful.
        if response.status_code != 200:

            st.error(
                f"Batch prediction failed. "
                f"Status code: {response.status_code}"
            )

            st.stop()

        # Convert the API response into a Python dictionary.
        result = response.json()

        # Store the complete screening result in session state.
        # This allows the result to survive Streamlit reruns.
        st.session_state["screening_result"] = result

        # Store the flagged transactions separately.
        st.session_state["flagged_transactions"] = (
            result["flagged_transactions"]
        )


# ---------------------------------------------------------
# LOAD PREVIOUS SCREENING RESULT
# ---------------------------------------------------------

# Retrieve the screening result from session state.
result = st.session_state.get("screening_result")

# Retrieve flagged transactions from session state.
flagged_transactions = st.session_state.get(
    "flagged_transactions"
)


# ---------------------------------------------------------
# SCREENING SUMMARY
# ---------------------------------------------------------

# Display the summary only after screening has been completed.
if result is not None:

    st.subheader("Screening Summary")

    # Create three columns for the summary metrics.
    col1, col2, col3 = st.columns(3)

    # Display total transaction count.
    with col1:

        st.metric(
            "Total Transactions",
            result["total_transactions"]
        )

    # Display high-risk transaction count.
    with col2:

        st.metric(
            "High Risk",
            result["high_risk_transactions"]
        )

    # Display low-risk transaction count.
    with col3:

        st.metric(
            "Low Risk",
            result["low_risk_transactions"]
        )


# ---------------------------------------------------------
# FLAGGED TRANSACTIONS
# ---------------------------------------------------------

# Continue only when high-risk transactions exist.
if flagged_transactions:

    st.subheader("🚨 Flagged Transactions")

    # Convert flagged transactions into a DataFrame.
    flagged_df = pd.DataFrame(flagged_transactions)

    # Display the flagged transactions.
    # The table itself does not need to be clickable.
    st.dataframe(
        flagged_df,
        use_container_width=True
    )

    st.divider()

    # -----------------------------------------------------
    # INVESTIGATION SELECTION
    # -----------------------------------------------------

    st.subheader("🔎 Investigate a Transaction")

    # Create a list containing the IDs of flagged transactions.
    transaction_ids = [
        int(transaction["transaction_id"])
        for transaction in flagged_transactions
    ]

    # Let the analyst choose one flagged transaction.
    selected_transaction_id = st.selectbox(
        "Select Transaction ID",
        transaction_ids,
        key="investigation_transaction"
    )

    # Create the investigation button.
    if st.button("🔎 Open Investigation"):

        # Save the selected transaction ID.
        st.session_state["selected_transaction_id"] = (
            selected_transaction_id
        )

        # Navigate to the investigation page.
        st.switch_page(
            "pages/investigation.py"
        )


# ---------------------------------------------------------
# NO FLAGGED TRANSACTIONS
# ---------------------------------------------------------

# Display a message when screening completed but
# no transactions were flagged.
elif result is not None:

    st.success(
        "✅ No high-risk transactions were detected."
    )