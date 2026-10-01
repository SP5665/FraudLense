import pandas as pd
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("data/creditcard.csv")

# Separate features and target
X = df.drop("Class", axis=1)
y = df["Class"]

# Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Display sizes
print("Training data:", X_train.shape)
print("Testing data:", X_test.shape)

print("\nFraud in training data:")
print(y_train.value_counts())

print("\nFraud in testing data:")
print(y_test.value_counts())

# Calculate class imbalance ratio
normal_count = (y_train == 0).sum()
fraud_count = (y_train == 1).sum()

scale_pos_weight = normal_count / fraud_count

print("\nScale pos weight:")
print(scale_pos_weight)