import pandas as pd

# Read the CSV
df = pd.read_csv("DataBreaches(2004-2021).csv")   # replace with actual filename

# Basic exploration
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())
print("\nMissing values:")
print(df.isnull().sum())
