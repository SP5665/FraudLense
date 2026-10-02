import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from xgboost import XGBClassifier

# Load dataset
df = pd.read_csv("data/creditcard.csv")

# Separate features and target
X = df.drop("Class", axis=1)
y = df["Class"]

# First split: training + test
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Split training data into actual training + validation
X_train_model, X_val, y_train_model, y_val = train_test_split(
    X_train,
    y_train,
    test_size=0.2,
    random_state=42,
    stratify=y_train
)

# Calculate class imbalance
normal_count = (y_train_model == 0).sum()
fraud_count = (y_train_model == 1).sum()

scale_pos_weight = normal_count / fraud_count

# Create model
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,
    eval_metric="logloss",
    random_state=42
)

# Train model
model.fit(X_train_model, y_train_model)

# Get fraud probabilities on validation set based on the trained model
y_prob = model.predict_proba(X_val)[:, 1]

# Test different thresholds
thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

print("\nThreshold Analysis")
print("-" * 90)

for threshold in thresholds:

    # Make predictions based on the threshold.
    y_pred = (y_prob >= threshold).astype(int)

    # Precision: of the transactions flagged as fraud, how many are actually fraud
    # Recall: of the actual fraud transactions, how many were flagged as fraud
    # F1-Score: the harmonic mean of precision and recall
    precision = precision_score(y_val, y_pred, zero_division=0)
    recall = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)

    # Confusion matrix values
    tn, fp, fn, tp = confusion_matrix(y_val, y_pred).ravel()

    # tn (True Negatives), fp (False Positives), fn (False Negatives), tp (True Positives)
    # Flagged = transactions sent as fraud for investigation = FP + TP
    flagged = fp + tp

    print(
        f"Threshold: {threshold:.1f} | "
        f"Precision: {precision:.3f} | "
        f"Recall: {recall:.3f} | "
        f"F1: {f1:.3f} | "
        f"FP: {fp} | "
        f"FN: {fn} | "
        f"Flagged: {flagged}"
    )