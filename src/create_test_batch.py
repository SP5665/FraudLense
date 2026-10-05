import pandas as pd

# Load the complete test dataset.
test_data = pd.read_csv("data/test_data.csv")

# Separate normal and fraud transactions using the ground-truth Class column.
normal_data = test_data[test_data["Class"] == 0]
fraud_data = test_data[test_data["Class"] == 1]

# Create a batch containing only normal transactions.
normal_batch = normal_data.head(100)

normal_batch.to_csv(
    "data/test_batch_normal.csv",
    index=False
)

# Create a batch containing known fraud transactions.
fraud_batch = fraud_data.head(20)

fraud_batch.to_csv(
    "data/test_batch_fraud.csv",
    index=False
)

# Create a mixed batch containing both normal and fraud transactions.
mixed_batch = pd.concat(
    [
        normal_data.head(100),
        fraud_data.head(20)
    ]
)

mixed_batch.to_csv(
    "data/test_batch_mixed.csv",
    index=False
)

# Display information about the created batches.
print("Test batches created successfully!")

print("\nNormal batch:")
print(normal_batch.shape)
print("Fraud transactions:", (normal_batch["Class"] == 1).sum())

print("\nFraud batch:")
print(fraud_batch.shape)
print("Fraud transactions:", (fraud_batch["Class"] == 1).sum())

print("\nMixed batch:")
print(mixed_batch.shape)
print("Fraud transactions:", (mixed_batch["Class"] == 1).sum())