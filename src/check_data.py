import pandas as pd

# Load dataset
df = pd.read_csv("data/creditcard.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nClass distribution:")
print(df["Class"].value_counts())