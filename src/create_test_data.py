import pandas as pd
from sklearn.model_selection import train_test_split

# Load the original credit card dataset.
df = pd.read_csv("data/creditcard.csv")

# Separate the input features from the actual fraud label.
X = df.drop("Class", axis=1)
y = df["Class"]

# Recreate the exact train-test split used during model training.
_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Add the actual labels back to the test data.
# These labels are used only for evaluation, not for prediction.
test_data = X_test.copy()
test_data["Class"] = y_test

# Save the unseen test set for application testing.
test_data.to_csv(
    "data/test_data.csv",
    index=False
)

# Display basic information about the generated test set.
print("Test dataset created successfully!")
print("Shape:", test_data.shape)
print("Fraud transactions:", (test_data["Class"] == 1).sum())
print("Normal transactions:", (test_data["Class"] == 0).sum())