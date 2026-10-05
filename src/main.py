import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from .predict import (
    predict_transaction,
    predict_transaction_batch,
    explain_transaction,
    FRAUD_THRESHOLD
)
from .database import (
    insert_transaction,
    insert_prediction,
    insert_investigation,
    transaction_exists,
    update_investigation_decision,
    insert_audit_log,
    get_transaction_id_for_investigation,
    get_transactions,
    get_transaction,
    get_prediction,
    get_investigation,
    get_audit_logs,
    get_batch_results_by_source_file
)

# Create the FastAPI application and define its metadata.
app = FastAPI(
    title="FraudLense API",
    description="API for the FraudLense fraud detection system",
    version="1.0.0"
)

# Define the structure of a transaction received by the API.
# FastAPI will automatically validate these fields.
class Transaction(BaseModel):
    Time: float
    Amount: float

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

# Define the structure of an investigation request received by the API.
class InvestigationRequest(BaseModel):

    # ID of the transaction that needs to be investigated.
    transaction_id: int

    # We will normally create investigations as OPEN.
    status: str = "OPEN"

# Define the structure of an investigation decision received by the API.
class InvestigationDecision(BaseModel):

    # The analyst's final decision.
    analyst_decision: str

    # Optional notes explaining the decision.
    analyst_notes: str | None = None

# Health-check endpoint.
@app.get("/")
def home():
    return {
        "message": "FraudLense API is running"
    }

# Prediction endpoint.
@app.post("/predict")
def predict(transaction: Transaction):

    # Convert the Pydantic object into a normal dictionary.
    transaction_data = transaction.model_dump()

    # Send the transaction through our existing prediction pipeline.
    result = predict_transaction(transaction_data)

    # Return the prediction to the API client.
    return result

# Investigation endpoint.
@app.post("/investigations")
def create_investigation(request: InvestigationRequest):

    # Check whether the requested transaction exists.
    if not transaction_exists(request.transaction_id):
        return {
            "error": "Transaction not found"
        }

    # Create the investigation in MySQL.
    investigation_id = insert_investigation(
        transaction_id=request.transaction_id,
        status=request.status
    )

    # Return information about the newly created investigation.
    return {
        "investigation_id": investigation_id,
        "transaction_id": request.transaction_id,
        "status": request.status
    }

# Endpoint for analysts to submit their final decision on an investigation and create an audit log.
@app.post("/investigations/{investigation_id}/decision")
def make_investigation_decision(
    investigation_id: int,
    decision: InvestigationDecision
):

    # Find the transaction associated with this investigation.
    transaction_id = get_transaction_id_for_investigation(
        investigation_id
    )

    # If the investigation does not exist, return an error.
    if transaction_id is None:
        return {
            "error": "Investigation not found"
        }

    # Update the investigation with the analyst's decision
    update_investigation_decision(
        investigation_id=investigation_id,
        analyst_decision=decision.analyst_decision,
        analyst_notes=decision.analyst_notes
    )

    # Record the analyst's action in the audit log.
    insert_audit_log(
        transaction_id=transaction_id,
        action="ANALYST_DECISION",
        details=(
            f"Investigation {investigation_id} closed with decision "
            f"{decision.analyst_decision}."
        )
    )

    # Return the final investigation information.
    return {
        "investigation_id": investigation_id,
        "transaction_id": transaction_id,
        "status": "CLOSED",
        "analyst_decision": decision.analyst_decision,
        "analyst_notes": decision.analyst_notes
    }

# Endpoint to retrieve all transactions stored in the database.
@app.get("/transactions")
def get_all_transactions():

    # Retrieve the transaction records from the database.
    transactions = get_transactions()

    # Return them to the API client.
    return {
        "count": len(transactions),
        "transactions": transactions
    }

# Endpoint to retrieve the fraud prediction for a specific transaction.
@app.get("/transactions/{transaction_id}/prediction")
def get_transaction_prediction(transaction_id: int):

    # Check whether the transaction exists.
    if not transaction_exists(transaction_id):
        return {
            "error": "Transaction not found"
        }

    # Get the latest prediction for this transaction.
    prediction = get_prediction(transaction_id)

    if prediction is None:
        return {
            "error": "Prediction not found"
        }

    # Return the prediction details.
    return prediction

# Endpoint to retrieve the latest investigation associated with a specific transaction.
@app.get("/transactions/{transaction_id}/investigation")
def get_transaction_investigation(transaction_id: int):

    if not transaction_exists(transaction_id):
        return {
            "error": "Transaction not found"
        }

    investigation = get_investigation(transaction_id)

    # A transaction may exist without an investigation.
    if investigation is None:
        return {
            "error": "Investigation not found"
        }

    return investigation

# Endpoint to retrieve all related details (transaction, prediction, investigation) for a specific transaction.
@app.get("/transactions/{transaction_id}/details")
def get_transaction_details(transaction_id: int):

    transaction = get_transaction(transaction_id)
    if transaction is None:
        return {
            "error": "Transaction not found"
        }

    # Get the latest fraud prediction for this transaction.
    prediction = get_prediction(transaction_id)

    # Get the latest investigation for this transaction.
    investigation = get_investigation(transaction_id)

    # Return all related information together.
    return {
        "transaction": transaction,
        "prediction": prediction,
        "investigation": investigation
    }

# Endpoint to screen a batch of transactions from an uploaded CSV file.
@app.post("/predict/batch")
async def predict_batch(
    file: UploadFile = File(...),
    source_file: str = Form(...)
):
    """
    Screen a newly uploaded CSV file.

    Every transaction inserted into MySQL is tagged with
    the name of the CSV file it came from.
    """

    # Read the uploaded CSV file.
    contents = await file.read()

    # Convert the uploaded bytes into a pandas DataFrame.
    from io import BytesIO
    df = pd.read_csv(BytesIO(contents))

    # Define the features required by the XGBoost model.
    feature_columns = [
        "Time",
        "V1", "V2", "V3", "V4", "V5", "V6", "V7",
        "V8", "V9", "V10", "V11", "V12", "V13", "V14",
        "V15", "V16", "V17", "V18", "V19", "V20", "V21",
        "V22", "V23", "V24", "V25", "V26", "V27", "V28",
        "Amount"
    ]

    # Check whether the uploaded CSV contains every required column.
    missing_columns = [
        column
        for column in feature_columns
        if column not in df.columns
    ]

    # Stop if any required columns are missing.
    if missing_columns:
        return {
            "error": "Missing required columns",
            "missing_columns": missing_columns
        }

    # Keep only the features required by the model.
    X = df[feature_columns]

    # Generate fraud probabilities for all transactions.
    probabilities = predict_transaction_batch(X)

    # Convert probabilities into HIGH/LOW risk levels.
    risk_levels = [
        "HIGH" if probability >= FRAUD_THRESHOLD else "LOW"
        for probability in probabilities
    ]

    # Count HIGH-risk and LOW-risk transactions.
    high_risk_count = risk_levels.count("HIGH")
    low_risk_count = risk_levels.count("LOW")

    # Store flagged transactions so they can be displayed
    # on the Streamlit dashboard.
    flagged_transactions = []

    # Process every transaction in the uploaded CSV.
    for index, probability in enumerate(probabilities):

        # Get the current transaction row.
        row = df.iloc[index]

        # Create a dictionary containing the model features.
        transaction_data = {
            column: row[column]
            for column in feature_columns
        }

        # Insert the transaction into MySQL.
        # The CSV filename is stored with the transaction.
        transaction_id = insert_transaction(
            transaction_data,
            source_file=source_file
        )

        # Determine the risk level.
        risk_level = (
            "HIGH"
            if probability >= FRAUD_THRESHOLD
            else "LOW"
        )

        # Store the model prediction in MySQL.
        prediction_id = insert_prediction(
            transaction_id=transaction_id,
            fraud_probability=float(probability),
            risk_level=risk_level,
            model_version="xgboost_v1"
        )

        # Create an investigation for HIGH-risk transactions.
        if risk_level == "HIGH":

            # Create an OPEN investigation.
            investigation_id = insert_investigation(
                transaction_id=transaction_id,
                status="OPEN"
            )

            # Add the flagged transaction to the response.
            flagged_transactions.append({
                "index": index,
                "transaction_id": transaction_id,
                "prediction_id": prediction_id,
                "investigation_id": investigation_id,
                "fraud_probability": float(probability),
                "risk_level": risk_level
            })

    # Return the screening summary.
    return {
        "source_file": source_file,
        "total_transactions": len(df),
        "high_risk_transactions": high_risk_count,
        "low_risk_transactions": low_risk_count,
        "flagged_transactions": flagged_transactions
    }

# Endpoint to retrieve previously screened transactions for a CSV file.
@app.get("/transactions/by-source")
def get_transactions_by_source(source_file: str):
    """
    Retrieve previously screened transactions for a CSV file.

    This endpoint is read-only.
    It does NOT insert anything into MySQL.
    """

    # Retrieve existing results from MySQL.
    result = get_batch_results_by_source_file(source_file)

    # Return the stored results.
    return result

# Endpoint to retrieve a single transaction by its ID.
@app.get("/transactions/{transaction_id}")
def get_single_transaction(transaction_id: int):

    transaction = get_transaction(transaction_id)

    if transaction is None:
        return {
            "error": "Transaction not found"
        }

    return transaction

# Endpoint to generate a SHAP explanation for an existing transaction.
@app.get("/transactions/{transaction_id}/explanation")
def get_transaction_explanation(transaction_id: int):

    # Retrieve the transaction from MySQL.
    transaction = get_transaction(transaction_id)

    # Stop if the transaction does not exist.
    if transaction is None:
        return {"error": "Transaction not found"}

    # Convert database values to regular Python floats
    # so XGBoost and SHAP can process them correctly.
    transaction_data = {
        "Time": float(transaction["transaction_time"]),
        "Amount": float(transaction["amount"]),
        **{
            f"V{i}": float(transaction[f"v{i}"])
            for i in range(1, 29)
        }
    }

    # Generate the SHAP explanation.
    explanation = explain_transaction(transaction_data)

    # Return the top contributing features.
    return {
        "transaction_id": transaction_id,
        "explanation": explanation
    }

# Endpoint to retrieve all audit log entries from the database.
@app.get("/audit-logs")
def get_all_audit_logs():

    # Retrieve audit logs from MySQL.
    logs = get_audit_logs()

    # Return the logs along with the total count.
    return {
        "count": len(logs),
        "logs": logs
    }