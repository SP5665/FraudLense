import os
import pandas as pd
import shap
import xgboost as xgb
from dotenv import load_dotenv
from .database import insert_transaction, insert_prediction

# Load variables from the .env file.
load_dotenv()

# Read the fraud threshold from the environment.
FRAUD_THRESHOLD = float(
    os.getenv("FRAUD_THRESHOLD", "0.5")
)

# Load the trained XGBoost model.
model = xgb.XGBClassifier()
model.load_model("models/fraud_model.json")

# Create the SHAP explainer once when the application starts.
explainer = shap.TreeExplainer(model)

# Keep the feature order identical to the training dataset.
FEATURE_COLUMNS = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7",
    "V8", "V9", "V10", "V11", "V12", "V13", "V14",
    "V15", "V16", "V17", "V18", "V19", "V20", "V21",
    "V22", "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount"
]

def predict_transaction(transaction):
    """
    Predict whether a transaction is fraudulent,
    store the result in MySQL, and generate SHAP
    explanations for high-risk transactions.
    """

    # Convert the transaction dictionary into a DataFrame.
    transaction_df = pd.DataFrame([transaction])

    # Ensure the model receives the same feature order that was used during training.
    transaction_df = transaction_df[FEATURE_COLUMNS]

    # Get the probability that this transaction belongs to the fraud class.
    fraud_probability = model.predict_proba(
        transaction_df
    )[0][1]

    # Compare the probability with our configured threshold.
    if fraud_probability >= FRAUD_THRESHOLD:
        risk_level = "HIGH"
    else:
        risk_level = "LOW"

    # Store the transaction in MySQL.
    transaction_id = insert_transaction(transaction)

    # Store the model prediction in MySQL.
    prediction_id = insert_prediction(
        transaction_id,
        float(fraud_probability),
        risk_level,
        "xgboost_v1"
    )

    # Start with no explanation for low-risk transactions.
    explanation = []

    # Calculate SHAP only for transactions that cross the fraud threshold.
    if fraud_probability >= FRAUD_THRESHOLD:

        # Calculate SHAP values for this transaction.
        shap_values = explainer.shap_values(transaction_df)

        # Get the SHAP values for this single transaction.
        values = shap_values[0]

        # Create a table containing each feature and its contribution to the prediction.
        explanation_df = pd.DataFrame({
            "feature": FEATURE_COLUMNS,
            "shap_value": values
        })

        # Calculate the absolute contribution so we can identify the strongest factors.
        explanation_df["absolute_shap"] = (
            explanation_df["shap_value"].abs()
        )

        # Sort from strongest contribution to weakest.
        explanation_df = explanation_df.sort_values(
            "absolute_shap",
            ascending=False
        )

        # Return the five strongest contributors.
        top_features = explanation_df.head(5)

        # Convert the result into JSON-friendly dictionaries.
        explanation = [
            {
                "feature": row["feature"],
                "shap_value": float(row["shap_value"])
            }
            for _, row in top_features.iterrows()
        ]

    # Return the complete prediction result.
    return {
        "transaction_id": transaction_id,
        "prediction_id": prediction_id,
        "fraud_probability": float(fraud_probability),
        "risk_level": risk_level,
        "explanation": explanation
    }