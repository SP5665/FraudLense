import os
import pandas as pd
import requests
import streamlit as st

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

# Configure the Streamlit page.
st.set_page_config(
    page_title="FraudLense",
    page_icon="🔍",
    layout="wide"
)

# FastAPI base URL.
API_URL = "http://127.0.0.1:8000"

# Folder where uploaded CSV files will be stored.
UPLOAD_FOLDER = "uploads"

# Create the uploads folder if it does not already exist.
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

# Display the application title.
st.title("🔍 FraudLense")

st.write(
    "Use machine learning to screen transactions "
    "and identify potentially fraudulent activity."
)

# ---------------------------------------------------------
# REQUIRED MODEL FEATURES
# ---------------------------------------------------------

# These are the features expected by the trained model.
required_columns = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7",
    "V8", "V9", "V10", "V11", "V12", "V13", "V14",
    "V15", "V16", "V17", "V18", "V19", "V20", "V21",
    "V22", "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount"
]

# ---------------------------------------------------------
# NEW CSV UPLOAD
# ---------------------------------------------------------

st.header("📤 Upload New CSV")

st.write(
    "Upload a new CSV file to screen its transactions "
    "and store the results in MySQL."
)

# Allow the user to select a CSV file.
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    key="new_csv"
)

if uploaded_file is not None:

    # Read the uploaded CSV so we can validate its columns.
    transaction_df = pd.read_csv(
        uploaded_file
    )

    # Check whether all required model columns are present.
    missing_columns = [
        column
        for column in required_columns
        if column not in transaction_df.columns
    ]

    if missing_columns:

        # Stop the upload if required columns are missing.
        st.error(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    else:

        # Display how many transactions were found.
        st.info(
            f"{len(transaction_df)} transactions found "
            f"in `{uploaded_file.name}`."
        )

        # Create the local path for this uploaded CSV.
        file_path = os.path.join(
            UPLOAD_FOLDER,
            uploaded_file.name
        )

        # Prevent the same filename from being uploaded again.
        if os.path.exists(file_path):

            st.warning(
                f"`{uploaded_file.name}` has already been uploaded. "
                "Select it from the existing CSV dropdown below "
                "instead of uploading it again."
            )

        else:

            # Only start screening when the user clicks the button.
            if st.button(
                "🚀 Upload & Screen New CSV",
                key="screen_new_csv"
            ):

                try:

                    # Get the uploaded file contents once.
                    file_contents = uploaded_file.getvalue()

                    # Save the CSV locally.
                    with open(
                        file_path,
                        "wb"
                    ) as file:

                        file.write(
                            file_contents
                        )

                    # Send the CSV to FastAPI.
                    # FastAPI performs prediction and database insertion.
                    response = requests.post(
                        f"{API_URL}/predict/batch",
                        files={
                            "file": (
                                uploaded_file.name,
                                file_contents,
                                "text/csv"
                            )
                        },
                        data={
                            "source_file": uploaded_file.name
                        },
                        timeout=120
                    )

                    # Check whether FastAPI succeeded.
                    if response.status_code != 200:

                        st.error(
                            "Batch prediction failed. "
                            f"Status code: {response.status_code}"
                        )

                        # Remove the local file because the request failed.
                        if os.path.exists(file_path):

                            os.remove(
                                file_path
                            )

                    else:

                        # Convert the API response into a dictionary.
                        result = response.json()

                        # Store the screening result in session state.
                        st.session_state[
                            "screening_result"
                        ] = result

                        # Store flagged transactions separately
                        # for easy access by the dashboard.
                        st.session_state[
                            "flagged_transactions"
                        ] = result[
                            "flagged_transactions"
                        ]

                        # Remember which CSV produced these results.
                        st.session_state[
                            "selected_source_file"
                        ] = uploaded_file.name

                        st.success(
                            "CSV uploaded and screened successfully."
                        )

                        # Refresh the page so the results appear.
                        st.rerun()

                except requests.RequestException as error:

                    # Handle connection and timeout errors.
                    st.error(
                        f"Could not connect to FastAPI: {error}"
                    )

                    # Remove the local file if the request failed.
                    if os.path.exists(file_path):

                        os.remove(
                            file_path
                        )

# ---------------------------------------------------------
# EXISTING CSV FILES
# ---------------------------------------------------------

st.header("📂 Previously Uploaded CSVs")

# Get all CSV files currently stored in the uploads folder.
uploaded_csvs = sorted(
    [
        filename
        for filename in os.listdir(UPLOAD_FOLDER)
        if filename.lower().endswith(".csv")
    ]
)

if uploaded_csvs:

    # Create a dropdown containing previously uploaded CSV files.
    selected_csv = st.selectbox(
        "Select an existing CSV",
        uploaded_csvs
    )

    # Load results already stored in MySQL.
    if st.button(
        "📊 Load Existing Results",
        key="load_existing_results"
    ):

        try:

            # This is a GET request.
            # It only reads existing database records.
            # It does NOT insert anything.
            response = requests.get(
                f"{API_URL}/transactions/by-source",
                params={
                    "source_file": selected_csv
                },
                timeout=30
            )

            # Check whether the API request succeeded.
            if response.status_code != 200:

                st.error(
                    "Failed to load existing results. "
                    f"Status code: {response.status_code}"
                )

            else:

                # Convert the API response into a dictionary.
                result = response.json()

                # Store the existing results in session state.
                st.session_state[
                    "screening_result"
                ] = result

                st.session_state[
                    "flagged_transactions"
                ] = result[
                    "flagged_transactions"
                ]

                # Remember which CSV is currently selected.
                st.session_state[
                    "selected_source_file"
                ] = selected_csv

                st.success(
                    f"Loaded existing results for `{selected_csv}`."
                )

        except requests.RequestException as error:

            # Handle connection and timeout errors.
            st.error(
                f"Could not connect to FastAPI: {error}"
            )

else:

    # Inform the user when no CSV files have been uploaded yet.
    st.info(
        "No uploaded CSV files yet. "
        "Upload a new CSV above to begin."
    )

# ---------------------------------------------------------
# SCREENING RESULTS
# ---------------------------------------------------------

# Retrieve the current screening result from session state.
result = st.session_state.get(
    "screening_result"
)

# Retrieve the flagged transactions from session state.
flagged_transactions = st.session_state.get(
    "flagged_transactions"
)

if result is not None:

    st.divider()

    # Display which CSV the results belong to.
    source_file = st.session_state.get(
        "selected_source_file"
    )

    if source_file:

        st.subheader(
            f"📄 Results: {source_file}"
        )

    # -----------------------------------------------------
    # SCREENING SUMMARY
    # -----------------------------------------------------

    st.subheader(
        "Screening Summary"
    )

    # Create three columns for the screening statistics.
    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Transactions",
            result["total_transactions"]
        )

    with col2:

        st.metric(
            "High Risk",
            result["high_risk_transactions"]
        )

    with col3:

        st.metric(
            "Low Risk",
            result["low_risk_transactions"]
        )

    # -----------------------------------------------------
    # FLAGGED TRANSACTIONS
    # -----------------------------------------------------

    if flagged_transactions:

        st.subheader(
            "🚨 Flagged Transactions"
        )

        # Convert flagged transactions into a DataFrame.
        flagged_df = pd.DataFrame(
            flagged_transactions
        )

        # Display the flagged transactions.
        st.dataframe(
            flagged_df,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # INVESTIGATION
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "🔎 Investigate a Transaction"
        )

        # Extract transaction IDs from the flagged results.
        transaction_ids = [
            int(transaction["transaction_id"])
            for transaction in flagged_transactions
        ]

        # Let the user select a flagged transaction.
        selected_transaction_id = st.selectbox(
            "Select Transaction ID",
            transaction_ids
        )

        # Open the investigation page.
        if st.button(
            "🔎 Open Investigation"
        ):

            # Store the selected transaction ID.
            st.session_state[
                "selected_transaction_id"
            ] = selected_transaction_id

            # Navigate to the investigation page.
            st.switch_page(
                "pages/investigation.py"
            )

    else:

        # Display this when the screening found no HIGH-risk transactions.
        st.success(
            "No high-risk transactions were detected."
        )

# ---------------------------------------------------------
# DATABASE TABLES
# ---------------------------------------------------------

st.divider()

st.header("📊 Database Tables")

st.write(
    "View the data stored in each FraudLense MySQL table."
)

# Create four buttons for the four database tables.
col1, col2, col3, col4 = st.columns(4)

with col1:
    view_transactions = st.button(
        "📋 Transactions",
        use_container_width=True
    )

with col2:
    view_predictions = st.button(
        "🤖 Predictions",
        use_container_width=True
    )

with col3:
    view_investigations = st.button(
        "🔎 Investigations",
        use_container_width=True
    )

with col4:
    view_audit_logs = st.button(
        "📝 Audit Logs",
        use_container_width=True
    )


# ---------------------------------------------------------
# TRANSACTIONS
# ---------------------------------------------------------

if view_transactions:

    try:
        response = requests.get(
            f"{API_URL}/database/transactions",
            timeout=30
        )

        if response.status_code == 200:

            result = response.json()

            # Get the transaction data returned by FastAPI.
            transaction_data = result.get("transactions", {})

            # If the transactions data is nested,
            # get the actual transaction list.
            if isinstance(transaction_data, dict):
                transaction_data = transaction_data.get(
                    "transactions",
                    []
                )

            # Convert the returned records directly into a DataFrame.
            transactions_df = pd.DataFrame(
                transaction_data
            )

            # If "count" somehow exists as a column,
            # remove it from the displayed table.
            if "count" in transactions_df.columns:
                transactions_df = transactions_df.drop(
                    columns=["count"]
                )

            st.success(
                f"{len(transactions_df)} transactions found."
            )

            st.dataframe(
                transactions_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.error(
                f"Failed to load transactions. "
                f"Status code: {response.status_code}"
            )

    except requests.RequestException as error:

        st.error(
            f"Could not connect to FastAPI: {error}"
        )


# ---------------------------------------------------------
# PREDICTIONS
# ---------------------------------------------------------

if view_predictions:

    try:
        response = requests.get(
            f"{API_URL}/database/predictions",
            timeout=30
        )

        if response.status_code == 200:

            result = response.json()

            # Get only the prediction records.
            predictions = result.get(
                "predictions",
                []
            )

            predictions_df = pd.DataFrame(
                predictions
            )

            st.success(
                f"{len(predictions_df)} predictions found."
            )

            if not predictions_df.empty:

                st.dataframe(
                    predictions_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No predictions found.")

        else:
            st.error(
                f"Failed to load predictions. "
                f"Status code: {response.status_code}"
            )

    except requests.RequestException as error:

        st.error(
            f"Could not connect to FastAPI: {error}"
        )


# ---------------------------------------------------------
# INVESTIGATIONS
# ---------------------------------------------------------

if view_investigations:

    try:
        response = requests.get(
            f"{API_URL}/database/investigations",
            timeout=30
        )

        if response.status_code == 200:

            result = response.json()

            # Get only the investigation records.
            investigations = result.get(
                "investigations",
                []
            )

            investigations_df = pd.DataFrame(
                investigations
            )

            st.success(
                f"{len(investigations_df)} investigations found."
            )

            if not investigations_df.empty:

                st.dataframe(
                    investigations_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No investigations found.")

        else:
            st.error(
                f"Failed to load investigations. "
                f"Status code: {response.status_code}"
            )

    except requests.RequestException as error:

        st.error(
            f"Could not connect to FastAPI: {error}"
        )


# ---------------------------------------------------------
# AUDIT LOGS
# ---------------------------------------------------------

if view_audit_logs:

    try:
        # Request all audit logs from FastAPI.
        response = requests.get(
            f"{API_URL}/database/audit-logs",
            timeout=30
        )

        # Check whether the request was successful.
        if response.status_code == 200:

            # Convert the API response into a dictionary.
            result = response.json()

            # Get the logs from the API response.
            logs_data = result.get(
                "logs",
                []
            )

            # If the logs are nested inside another dictionary,
            # get the actual list of audit log records.
            if isinstance(logs_data, dict):
                logs_data = logs_data.get(
                    "logs",
                    []
                )

            # Convert the actual audit log records into a DataFrame.
            logs_df = pd.DataFrame(
                logs_data
            )

            # Remove the count column if it is present.
            if "count" in logs_df.columns:
                logs_df = logs_df.drop(
                    columns=["count"]
                )

            # Display the total number of audit logs.
            st.success(
                f"{len(logs_df)} audit log entries found."
            )

            # Display the audit log table.
            if not logs_df.empty:

                st.dataframe(
                    logs_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info(
                    "No audit log entries found."
                )

        else:
            # Show an error if FastAPI returned an unsuccessful status.
            st.error(
                f"Failed to load audit logs. "
                f"Status code: {response.status_code}"
            )

    except requests.RequestException as error:

        # Show an error if FastAPI cannot be reached.
        st.error(
            f"Could not connect to FastAPI: {error}"
        )