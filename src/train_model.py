import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score
)
from xgboost import XGBClassifier

# Load dataset
df = pd.read_csv("data/creditcard.csv")

# Separate features and target
X = df.drop("Class", axis=1)
y = df["Class"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Calculate class imbalance
normal_count = (y_train == 0).sum()
fraud_count = (y_train == 1).sum()

scale_pos_weight = normal_count / fraud_count

# Create XGBoost model
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

print("Model training completed!")

# Make predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# Classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ROC-AUC
roc_auc = roc_auc_score(y_test, y_prob)
print("\nROC-AUC:", roc_auc)

# PR-AUC
pr_auc = average_precision_score(y_test, y_prob)
print("PR-AUC:", pr_auc)