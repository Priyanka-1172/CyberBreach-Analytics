import pandas as pd
import matplotlib.pyplot as plt

# ── Load raw data ─────────────────────────────────────
df = pd.read_csv(r"C:\Users\admin\Desktop\dark web analytics project\DataBreaches(2004-2021).csv")

# ── Clean industry names ───────────────────────────────
industry_map = {
    "healthcare": "Healthcare", "health care": "Healthcare",
    "medical": "Healthcare", "hospital": "Healthcare",
    "clinical laboratory": "Healthcare", "military, healthcare": "Healthcare",
    "financial": "Finance", "finance": "Finance", "banking": "Finance",
    "financial, credit reporting": "Finance", "financial service company": "Finance",
    "insurance": "Finance", "tech": "Technology", "technology": "Technology",
    "web": "Technology", "software": "Technology", "telecoms": "Technology",
    "telecommunications": "Technology", "social networking": "Technology",
    "social media": "Technology", "gaming": "Technology",
    "web, gaming": "Technology", "phone accessories": "Technology",
    "government": "Government", "military": "Government",
    "government, military": "Government", "government, healthcare": "Government",
    "retail": "Retail", "consumer goods": "Retail", "shopping": "Retail",
    "hotel": "Retail", "transport": "Retail",
    "academic": "Education", "education": "Education", "educational": "Education",
    "media": "Media", "news": "Media", "publishing": "Media", "media, retail": "Media",
    "energy": "Other", "legal": "Other", "app": "Other",
}

df["Industry"] = (
    df["Organization type"].str.lower().str.strip()
    .map(industry_map).fillna("Other")
)

df["Records"] = (
    df["Records"].astype(str)
    .str.replace(",", "").str.replace(" ", "")
)
df["Records"] = pd.to_numeric(df["Records"], errors="coerce").fillna(0).astype(int)

df.to_csv(r"C:\Users\admin\Desktop\dark web analytics project\clean_breaches.csv", index=False)
print("✅ Clean data saved!")
print(df["Industry"].value_counts())

# ================================================================
# CHART 1: Most Breached Industries — with numbers on bars
# ================================================================
fig, ax = plt.subplots(figsize=(10, 6))

counts = df["Industry"].value_counts()
bars = ax.bar(counts.index, counts.values, color="crimson")

# Add number on top of each bar
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,   # x position = center of bar
        height + 0.5,                          # y position = just above bar
        str(int(height)),                      # the number to show
        ha="center", va="bottom",             # alignment
        fontsize=11, fontweight="bold"
    )

ax.set_title("Most Breached Industries (2004-2021)", fontsize=14)
ax.set_xlabel("Industry")
ax.set_ylabel("Number of Breaches")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(r"C:\Users\admin\Desktop\dark web analytics project\chart1_industries.png")
plt.show()
print("✅ Chart 1 done!")

# ================================================================
# CHART 2: Breaches Per Year — with numbers on points
# ================================================================
fig, ax = plt.subplots(figsize=(10, 5))

yearly = df["Year"].value_counts().sort_index()
ax.plot(yearly.index, yearly.values, color="crimson", marker="o", linewidth=2)

# Add number next to each point
for x, y in zip(yearly.index, yearly.values):
    ax.text(x, y + 0.3, str(y), ha="center", fontsize=9, fontweight="bold")

ax.set_title("Data Breaches Per Year (2004-2021)", fontsize=14)
ax.set_xlabel("Year")
ax.set_ylabel("Number of Breaches")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(r"C:\Users\admin\Desktop\dark web analytics project\chart2_yearly.png")
plt.show()
print("✅ Chart 2 done!")

# ================================================================
# CHART 3: Attack Methods — with numbers on bars
# ================================================================
fig, ax = plt.subplots(figsize=(9, 5))

methods = df["Method"].value_counts().head(6)
bars = ax.bar(methods.index, methods.values, color="darkred")

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.3,
        str(int(height)),
        ha="center", va="bottom",
        fontsize=11, fontweight="bold"
    )

ax.set_title("Most Common Attack Methods", fontsize=14)
ax.set_xlabel("Method")
ax.set_ylabel("Number of Breaches")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(r"C:\Users\admin\Desktop\dark web analytics project\chart3_methods.png")
plt.show()
print("✅ Chart 3 done!")

# ================================================================
# CHART 4: Total Records Leaked Per Industry — with numbers
# ================================================================
fig, ax = plt.subplots(figsize=(10, 5))

records = df.groupby("Industry")["Records"].sum().sort_values(ascending=False)
bars = ax.bar(records.index, records.values, color="crimson")

for bar in bars:
    height = bar.get_height()
    # Show in millions (divide by 1,000,000)
    label = f"{height/1e6:.0f}M"
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.5,
        label,
        ha="center", va="bottom",
        fontsize=10, fontweight="bold"
    )

ax.set_title("Total Records Leaked Per Industry", fontsize=14)
ax.set_xlabel("Industry")
ax.set_ylabel("Total Records Leaked")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(r"C:\Users\admin\Desktop\dark web analytics project\chart4_records.png")
plt.show()
print("✅ Chart 4 done — all charts complete!")
