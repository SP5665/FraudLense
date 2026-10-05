import streamlit as st
import requests

# Configure the Streamlit page.
st.set_page_config(
    page_title="FraudLense - Investigation",
    page_icon="🔎",
    layout="wide"
)

# FastAPI base URL.
API_URL = "http://127.0.0.1:8000"

# Display the page title.
st.title("🔎 Fraud Investigation")

# Get the transaction selected from the Dashboard.
transaction_id = st.session_state.get("selected_transaction_id")

# Stop if no transaction was selected.
if transaction_id is None:
    st.warning(
        "No transaction selected. Please select a flagged transaction "
        "from the Screening Dashboard."
    )
    st.stop()

# Display the selected transaction ID.
st.subheader(f"Transaction #{transaction_id}")

# ---------------------------------------------------------
# TRANSACTION DETAILS
# ---------------------------------------------------------

# Request transaction details from FastAPI.
response = requests.get(
    f"{API_URL}/transactions/{transaction_id}/details"
)

# Check whether the request was successful.
if response.status_code != 200:
    st.error(
        f"Failed to load transaction details. "
        f"Status code: {response.status_code}"
    )
    st.stop()

# Convert the API response into a Python dictionary.
result = response.json()

# Display transaction information.
st.header("Transaction Details")
st.json(result["transaction"])


# ---------------------------------------------------------
# MODEL PREDICTION
# ---------------------------------------------------------

st.header("Model Prediction")

# Get the prediction information.
prediction = result["prediction"]

# Create two columns for the prediction summary.
col1, col2 = st.columns(2)

with col1:

    # Convert probability into a percentage for display.
    probability = prediction["fraud_probability"] * 100

    st.metric(
        "Fraud Probability",
        f"{probability:.4f}%"
    )

with col2:

    # Display the model's risk classification.
    st.metric(
        "Risk Level",
        prediction["risk_level"]
    )


# ---------------------------------------------------------
# SHAP EXPLANATION
# ---------------------------------------------------------

st.header("🧠 SHAP Explanation")

# Request the SHAP explanation from FastAPI.
shap_response = requests.get(
    f"{API_URL}/transactions/{transaction_id}/explanation"
)

# Check whether the SHAP request was successful.
if shap_response.status_code != 200:

    st.error(
        f"Failed to load SHAP explanation. "
        f"Status code: {shap_response.status_code}"
    )

else:

    # Convert the SHAP response into a Python dictionary.
    shap_result = shap_response.json()

    # Get the list of top contributing features.
    explanation = shap_result["explanation"]

    # Explain what the SHAP values mean.
    st.write(
        "SHAP values show how individual features influenced "
        "the model's prediction. Positive values push the prediction "
        "toward fraud, while negative values push it away from fraud."
    )

    # Display the explanation as a table.
    for item in explanation:

        # Get the feature name.
        feature = item["feature"]

        # Get the SHAP contribution.
        shap_value = item["shap_value"]

        # Display the feature and its contribution.
        if shap_value > 0:

            st.write(
                f"**{feature}** → "
                f"🟥 +{shap_value:.4f} "
                f"(toward fraud)"
            )

        else:

            st.write(
                f"**{feature}** → "
                f"🟦 {shap_value:.4f} "
                f"(away from fraud)"
            )


# ---------------------------------------------------------
# INVESTIGATION
# ---------------------------------------------------------

st.header("🔎 Investigation")

# Get the existing investigation.
investigation = result["investigation"]

if investigation is not None:

    # Display the current investigation status.
    st.write(
        "**Status:**",
        investigation["status"]
    )

    # Display the existing analyst decision.
    st.write(
        "**Analyst Decision:**",
        investigation["analyst_decision"]
    )

    # Display existing analyst notes.
    st.write(
        "**Analyst Notes:**",
        investigation["analyst_notes"]
    )

else:

    st.info(
        "No investigation has been created for this transaction."
    )

# ---------------------------------------------------------
# ANALYST DECISION
# ---------------------------------------------------------

st.subheader("👤 Analyst Decision")

# Let the analyst choose the final decision.
analyst_decision = st.radio(
    "Decision",
    ["FRAUD", "LEGITIMATE"],
    horizontal=True
)

# Allow the analyst to enter optional notes.
analyst_notes = st.text_area(
    "Analyst Notes",
    placeholder="Enter your investigation notes..."
)

# Submit the analyst's decision.
if st.button("Submit Decision"):

    # Send the decision to the FastAPI backend.
    decision_response = requests.post(
        f"{API_URL}/investigations/"
        f"{investigation['investigation_id']}/decision",
        json={
            "analyst_decision": analyst_decision,
            "analyst_notes": analyst_notes
        }
    )

    # Check whether the API request was successful.
    if decision_response.status_code != 200:

        st.error(
            f"Failed to submit decision. "
            f"Status code: {decision_response.status_code}"
        )

    else:

        # Convert the API response into a Python dictionary.
        decision_result = decision_response.json()

        # Display a success message.
        st.success(
            "Investigation decision submitted successfully."
        )

        # Display the final decision.
        st.write(
            "**Decision:**",
            decision_result["analyst_decision"]
        )

        # Display the final notes.
        st.write(
            "**Notes:**",
            decision_result["analyst_notes"]
        )

        # Display the new investigation status.
        st.write(
            "**Status:**",
            decision_result["status"]
        )