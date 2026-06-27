import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import matplotlib.pyplot as plt

# ── Load clean data ────────────────────────────────────
df = pd.read_csv(r"C:\Users\admin\Desktop\dark web analytics project\clean_breaches.csv")

# ── Create target: was this a Large or Small breach? ──
# Large = more than 1 million records leaked
df["Severity"] = df["Records"].apply(lambda x: "Large" if x > 1000000 else "Small")

print("Severity breakdown:")
print(df["Severity"].value_counts())

# ── Convert text → numbers (ML only understands numbers) 
df["Industry_code"] = pd.factorize(df["Industry"])[0]
df["Method_code"]   = pd.factorize(df["Method"])[0]

# ── Features and Target ────────────────────────────────
# Fix Year column — "2018-2019" → 2018 (take just the first year)
df["Year"] = df["Year"].astype(str).str[:4]
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

X = df[["Industry_code", "Method_code", "Year"]]
y = df["Severity"]

# ── Split 80% train, 20% test ─────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining on {len(X_train)} rows, testing on {len(X_test)} rows")

# ── Train the model ────────────────────────────────────
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ── Test it ────────────────────────────────────────────
y_pred = model.predict(X_test)
print("\n📊 Model Results:")
print(classification_report(y_test, y_pred))

# ── Feature importance chart ───────────────────────────
# This shows WHICH factor matters most for predictions
feature_names = ["Industry", "Attack Method", "Year"]
importances = model.feature_importances_

plt.figure(figsize=(7, 4))
bars = plt.bar(feature_names, importances, color="crimson")

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.001,
        f"{height:.2f}",
        ha="center", fontsize=11, fontweight="bold"
    )

plt.title("Which Factor Predicts Breach Severity Most?")
plt.ylabel("Importance Score")
plt.tight_layout()
plt.savefig(r"C:\Users\admin\Desktop\dark web analytics project\chart5_feature_importance.png")
plt.show()
print("✅ Feature importance chart saved!")

# ── Save the trained model ─────────────────────────────
joblib.dump(model, r"C:\Users\admin\Desktop\dark web analytics project\model.pkl")
print("✅ Model saved as model.pkl!")

# ── Try a prediction manually ─────────────────────────
# Let's predict: if a Healthcare company gets hacked in 2023
# Industry_code for Healthcare, Method_code for hacked, Year 2023
sample = pd.DataFrame([[1, 0, 2023]], columns=["Industry_code", "Method_code", "Year"])
prediction = model.predict(sample)
print(f"\n🔮 Sample prediction (Healthcare, hacked, 2023): {prediction[0]} breach")
