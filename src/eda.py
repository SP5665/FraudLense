import pandas as pd
import matplotlib.pyplot as plt


# Load dataset
df = pd.read_csv("data/creditcard.csv")


# 1. Dataset shape
print("Dataset shape:")
print(df.shape)


# 2. Missing values
print("\nMissing values:")
print(df.isnull().sum().sum())


# 3. Class distribution
print("\nClass distribution:")
print(df["Class"].value_counts())


# 4. Class percentages
print("\nClass percentages:")
print(df["Class"].value_counts(normalize=True) * 100)


# 5. Amount statistics
print("\nAmount statistics:")
print(df["Amount"].describe())


# 6. Normal vs Fraud amount statistics
print("\nNormal transaction amount:")
print(df[df["Class"] == 0]["Amount"].describe())

print("\nFraud transaction amount:")
print(df[df["Class"] == 1]["Amount"].describe())


# 7. Compare transaction amounts
normal_amounts = df[df["Class"] == 0]["Amount"]
fraud_amounts = df[df["Class"] == 1]["Amount"]

plt.figure(figsize=(7, 5))

plt.boxplot(
    [normal_amounts, fraud_amounts],
    tick_labels=["Normal", "Fraud"],
    showfliers=False
)

plt.title("Transaction Amount Comparison")
plt.ylabel("Amount")

plt.show()

# 8. Compare V1-V28 between normal and fraud transactions

v_features = [f"V{i}" for i in range(1, 29)]

normal_means = df[df["Class"] == 0][v_features].mean()
fraud_means = df[df["Class"] == 1][v_features].mean()

comparison = pd.DataFrame({
    "Normal Mean": normal_means,
    "Fraud Mean": fraud_means
})

comparison["Difference"] = (
    comparison["Fraud Mean"] - comparison["Normal Mean"]
)

print("\nV1-V28 comparison:")
print(comparison)