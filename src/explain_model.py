import pandas as pd
import shap
import xgboost as xgb

# Load dataset
df = pd.read_csv("data/creditcard.csv")

# Separate features and target
X = df.drop("Class", axis=1)
y = df["Class"]

# Load trained model
model = xgb.XGBClassifier()
model.load_model("models/fraud_model.json")

# Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Get fraud probabilities for all transactions
fraud_probabilities = model.predict_proba(X)[:, 1]

# Find index of transaction with highest fraud probability
high_risk_index = fraud_probabilities.argmax()

transaction = X.iloc[[high_risk_index]]

print("Transaction index:", high_risk_index)
print("Actual class:", y.iloc[high_risk_index])
print("Fraud probability:", fraud_probabilities[high_risk_index])

# Calculate SHAP values for this transaction
shap_values = explainer.shap_values(transaction)

# Get SHAP values for the transaction
values = shap_values[0]

# Create feature contribution table
explanation = pd.DataFrame({
    "Feature": X.columns,
    "SHAP Value": values
})

# Calculate absolute SHAP value
explanation["Absolute SHAP"] = explanation["SHAP Value"].abs()

# Sort by strongest contribution, absolute SHAP value
explanation = explanation.sort_values(
    "Absolute SHAP",
    ascending=False
)

print("\nTop contributing features:")
print(
    explanation[
        ["Feature", "SHAP Value"]
    ].head(10)
)