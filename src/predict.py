import pandas as pd
import xgboost as xgb

from database import insert_transaction, insert_prediction


# Load the trained XGBoost model
model = xgb.XGBClassifier()
model.load_model("models/fraud_model.json")


def predict_transaction(transaction):

    # Convert the transaction dictionary into a DataFrame.
    # XGBoost expects the same feature structure used during training.
    transaction_df = pd.DataFrame([transaction])

    # Make sure the columns are in the same order as the training data.
    transaction_df = transaction_df[
        [
            "Time",
            "V1", "V2", "V3", "V4", "V5", "V6", "V7",
            "V8", "V9", "V10", "V11", "V12", "V13", "V14",
            "V15", "V16", "V17", "V18", "V19", "V20", "V21",
            "V22", "V23", "V24", "V25", "V26", "V27", "V28",
            "Amount"
        ]
    ]

    # Get the probability that the transaction belongs to the fraud class (Class = 1).
    fraud_probability = model.predict_proba(
        transaction_df
    )[0][1]

    # For now, use the 0.5 threshold used by XGBoost's default binary prediction.
    if fraud_probability >= 0.5:
        risk_level = "HIGH"
    else:
        risk_level = "LOW"

    # Store the transaction in MySQL first.
    transaction_id = insert_transaction(transaction)

    # Store the model's prediction separately.
    prediction_id = insert_prediction(
        transaction_id,
        float(fraud_probability),
        risk_level,
        "xgboost_v1"
    )

    return {
        "transaction_id": transaction_id,
        "prediction_id": prediction_id,
        "fraud_probability": float(fraud_probability),
        "risk_level": risk_level
    }