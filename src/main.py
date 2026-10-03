from fastapi import FastAPI
from pydantic import BaseModel
from .predict import predict_transaction

# Create the FastAPI application.
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

# Health-check endpoint.
@app.get("/")
def home():
    return {
        "message": "FraudLense API is running"
    }

# Prediction endpoint.
@app.post("/predict")
def predict(transaction: Transaction):
    """
    Receive a transaction and return the fraud prediction.
    """

    # Convert the Pydantic object into a normal dictionary.
    transaction_data = transaction.model_dump()

    # Send the transaction through our existing prediction pipeline.
    result = predict_transaction(transaction_data)

    # Return the prediction to the API client.
    return result