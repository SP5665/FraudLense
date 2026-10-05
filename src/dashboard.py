import os

import pandas as pd
import requests
import streamlit as st


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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Display the application title.
st.title("🔍 FraudLense")

st.write(
    "Use machine learning to screen transactions "
    "and identify potentially fraudulent activity."
)


# ---------------------------------------------------------
# REQUIRED MODEL FEATURES
# ---------------------------------------------------------

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


uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    key="new_csv"
)


if uploaded_file is not None:

    # Read the uploaded CSV so we can validate its columns.
    transaction_df = pd.read_csv(uploaded_file)

    # Check whether required columns are present.
    missing_columns = [
        column
        for column in required_columns
        if column not in transaction_df.columns
    ]

    # Stop the upload if required columns are missing.
    if missing_columns:

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

        # Check whether this filename already exists.
        file_path = os.path.join(
            UPLOAD_FOLDER,
            uploaded_file.name
        )

        if os.path.exists(file_path):

            # Prevent accidentally inserting the same CSV again.
            st.warning(
                f"`{uploaded_file.name}` has already been uploaded. "
                "Select it from the existing CSV dropdown below "
                "instead of uploading it again."
            )

        else:

            # Only insert into MySQL when this button is clicked.
            if st.button(
                "🚀 Upload & Screen New CSV",
                key="screen_new_csv"
            ):

                try:

                    # Save the CSV locally.
                    with open(file_path, "wb") as file:

                        file.write(
                            uploaded_file.getvalue()
                        )

                    # Send the CSV to FastAPI for prediction
                    # and database insertion.
                    response = requests.post(
                        f"{API_URL}/predict/batch",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                "text/csv"
                            )
                        },
                        data={
                            "source_file": uploaded_file.name
                        }
                    )

                    # Check whether FastAPI succeeded.
                    if response.status_code != 200:

                        st.error(
                            "Batch prediction failed. "
                            f"Status code: {response.status_code}"
                        )

                        # Remove the local file if the database
                        # operation failed.
                        if os.path.exists(file_path):
                            os.remove(file_path)

                    else:

                        # Convert the API response to a dictionary.
                        result = response.json()

                        # Store the result in Streamlit session state.
                        st.session_state[
                            "screening_result"
                        ] = result

                        st.session_state[
                            "flagged_transactions"
                        ] = result[
                            "flagged_transactions"
                        ]

                        st.session_state[
                            "selected_source_file"
                        ] = uploaded_file.name

                        st.success(
                            "CSV uploaded and screened successfully."
                        )

                        # Refresh the page so the results appear.
                        st.rerun()

                except requests.RequestException as error:

                    st.error(
                        f"Could not connect to FastAPI: {error}"
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

    # Create a dropdown containing previously uploaded files.
    selected_csv = st.selectbox(
        "Select an existing CSV",
        uploaded_csvs
    )

    # Load the selected CSV's already-stored results.
    if st.button(
        "📊 Load Existing Results",
        key="load_existing_results"
    ):

        try:

            # IMPORTANT:
            # This is a GET request.
            # It only reads existing database records.
            # It does NOT insert anything.
            response = requests.get(
                f"{API_URL}/transactions/by-source",
                params={
                    "source_file": selected_csv
                }
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

                st.session_state[
                    "selected_source_file"
                ] = selected_csv

                st.success(
                    f"Loaded existing results for `{selected_csv}`."
                )

        except requests.RequestException as error:

            st.error(
                f"Could not connect to FastAPI: {error}"
            )

else:

    st.info(
        "No uploaded CSV files yet. "
        "Upload a new CSV above to begin."
    )


# ---------------------------------------------------------
# SCREENING RESULTS
# ---------------------------------------------------------

result = st.session_state.get(
    "screening_result"
)

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

    # Display screening summary.
    st.subheader("Screening Summary")

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

        st.subheader("🚨 Flagged Transactions")

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

        st.success(
            "No high-risk transactions were detected."
        )