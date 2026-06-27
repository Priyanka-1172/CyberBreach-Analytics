import pandas as pd
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv("DataBreaches(2004-2021).csv")

# ── Chart 1: Which industry gets breached the most? ──
plt.figure(figsize=(10, 5))
df["Organization type"].value_counts().plot(kind="bar", color="crimson")
plt.title("Most Breached Industries (2004-2021)")
plt.xlabel("Industry")
plt.ylabel("Number of Breaches")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart1_industries.png")   # saves as image
plt.show()
print("Chart 1 done!")

# ── Chart 2: Are breaches increasing over time? ──
plt.figure(figsize=(10, 5))
df["Year"].value_counts().sort_index().plot(kind="line", color="crimson", marker="o")
plt.title("Data Breaches Per Year (2004-2021)")
plt.xlabel("Year")
plt.ylabel("Number of Breaches")
plt.tight_layout()
plt.savefig("chart2_yearly.png")
plt.show()
print("Chart 2 done!")

# ── Chart 3: How do hackers get in? ──
plt.figure(figsize=(8, 5))
df["Method"].value_counts().plot(kind="bar", color="darkred")
plt.title("Most Common Attack Methods")
plt.xlabel("Method")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("chart3_methods.png")
plt.show()
print("Chart 3 done!")
