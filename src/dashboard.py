import streamlit as st
import requests
import pandas as pd

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

# Explain the main purpose of the application.
st.write(
    "Use machine learning to predict whether a transaction is fraudulent."
)

# Create the main prediction section.
st.header("Predict a Transaction")

# Explain the expected CSV format.
st.write(
    "Upload a CSV containing one transaction with the Time, V1–V28, "
    "and Amount columns."
)

# Allow the user to upload a transaction file.
uploaded_file = st.file_uploader(
    "Upload transaction CSV",
    type=["csv"]
)

# Continue only when a file has been uploaded.
if uploaded_file is not None:

    # Read the uploaded CSV into a DataFrame.
    transaction_df = pd.read_csv(uploaded_file)

    # Define the exact features required by the prediction API.
    required_columns = [
        "Time",
        "V1", "V2", "V3", "V4", "V5", "V6", "V7",
        "V8", "V9", "V10", "V11", "V12", "V13", "V14",
        "V15", "V16", "V17", "V18", "V19", "V20", "V21",
        "V22", "V23", "V24", "V25", "V26", "V27", "V28",
        "Amount"
    ]

    # Check whether all required columns are present.
    missing_columns = [
        column
        for column in required_columns
        if column not in transaction_df.columns
    ]

    # Stop if the uploaded file is missing required columns.
    if missing_columns:
        st.error(
            f"Missing columns: {', '.join(missing_columns)}"
        )
        st.stop()

    # The prediction endpoint currently handles one transaction at a time.
    if len(transaction_df) != 1:
        st.error(
            "Please upload a CSV containing exactly one transaction."
        )
        st.stop()

    # Keep only the columns required by the model.
    transaction_df = transaction_df[required_columns]

    # Display the uploaded transaction before prediction.
    st.subheader("Transaction")

    st.dataframe(
        transaction_df,
        use_container_width=True
    )

    # Create the prediction button.
    if st.button("Predict Transaction"):

        # Convert the single row into a dictionary.
        transaction = transaction_df.iloc[0].to_dict()

        # Send the transaction to the FastAPI prediction endpoint.
        response = requests.post(
            f"{API_URL}/predict",
            json=transaction
        )

        # Check whether the prediction request was successful.
        if response.status_code != 200:
            st.error(
                f"Prediction failed. Status code: "
                f"{response.status_code}"
            )
            st.stop()

        # Convert the API response into a Python dictionary.
        result = response.json()

        # Display the prediction result.
        st.subheader("Prediction Result")

        # Convert probability into a percentage for display.
        probability = result["fraud_probability"] * 100

        # Display the fraud probability.
        st.metric(
            "Fraud Probability",
            f"{probability:.4f}%"
        )

        # Display the risk level.
        if result["risk_level"] == "HIGH":
            st.error("⚠️ HIGH RISK — Potential Fraud")

        else:
            st.success("✅ LOW RISK — Likely Legitimate")

        # Display the transaction ID stored in MySQL.
        st.write(
            "**Transaction ID:**",
            result["transaction_id"]
        )