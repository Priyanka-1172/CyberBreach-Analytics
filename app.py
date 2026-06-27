import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib

# ── Page config ───────────────────────────────────────
st.set_page_config(
    page_title="Dark Web Analytics",
    page_icon="🔐",
    layout="wide"
)

# ── Load data and model ───────────────────────────────
df = pd.read_csv(r"C:\Users\admin\Desktop\dark web analytics project\clean_breaches.csv")
model = joblib.load(r"C:\Users\admin\Desktop\dark web analytics project\model.pkl")

# Fix Year column
df["Year"] = df["Year"].astype(str).str[:4]
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

# ── Sidebar navigation ────────────────────────────────
st.sidebar.title("🔐 Dark Web Analytics")
page = st.sidebar.radio("Go to", [
    "📊 Overview",
    "📈 Trends",
    "🔮 Predict Severity"
])

# ================================================================
# PAGE 1: OVERVIEW
# ================================================================
if page == "📊 Overview":
    st.title("🔐 Data Breach Analytics Dashboard")
    st.markdown("Analyzing **295 data breaches** from 2004–2021")

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Breaches",    len(df))
    col2.metric("Total Records Leaked", f"{df['Records'].sum()/1e9:.1f}B")
    col3.metric("Most Breached",     df["Industry"].value_counts().index[0])
    col4.metric("Top Attack Method", df["Method"].value_counts().index[0])

    st.divider()

    # Chart 1 — Industry
    st.subheader("Most Breached Industries")
    fig, ax = plt.subplots(figsize=(10, 4))
    counts = df["Industry"].value_counts()
    bars = ax.bar(counts.index, counts.values, color="crimson")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.3,
                str(int(bar.get_height())),
                ha="center", fontweight="bold")
    ax.set_ylabel("Number of Breaches")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig)

    st.divider()

    # Chart 2 — Attack Methods
    st.subheader("Most Common Attack Methods")
    fig2, ax2 = plt.subplots(figsize=(9, 4))
    methods = df["Method"].value_counts().head(6)
    bars2 = ax2.bar(methods.index, methods.values, color="darkred")
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.3,
                 str(int(bar.get_height())),
                 ha="center", fontweight="bold")
    ax2.set_ylabel("Number of Breaches")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig2)

# ================================================================
# PAGE 2: TRENDS
# ================================================================
elif page == "📈 Trends":
    st.title("📈 Breach Trends Over Time")

    # Yearly trend
    st.subheader("Breaches Per Year")
    fig, ax = plt.subplots(figsize=(10, 4))
    yearly = df[df["Year"] > 2000]["Year"].value_counts().sort_index()
    ax.plot(yearly.index, yearly.values,
            color="crimson", marker="o", linewidth=2)
    for x, y in zip(yearly.index, yearly.values):
        ax.text(x, y + 0.3, str(y), ha="center", fontsize=8, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Breaches")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    st.divider()

    # Records leaked per industry
    st.subheader("Total Records Leaked Per Industry")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    records = df.groupby("Industry")["Records"].sum().sort_values(ascending=False)
    bars = ax2.bar(records.index, records.values, color="crimson")
    for bar in bars:
        label = f"{bar.get_height()/1e6:.0f}M"
        ax2.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.5,
                 label, ha="center", fontsize=9, fontweight="bold")
    ax2.set_ylabel("Records Leaked")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig2)

    st.divider()

    # Raw data table
    st.subheader("Browse All Breaches")
    industry_filter = st.selectbox(
        "Filter by Industry", ["All"] + sorted(df["Industry"].unique().tolist())
    )
    filtered = df if industry_filter == "All" else df[df["Industry"] == industry_filter]
    st.dataframe(
        filtered[["Entity", "Year", "Records", "Industry", "Method"]],
        use_container_width=True
    )

# ================================================================
# PAGE 3: PREDICT SEVERITY
# ================================================================
elif page == "🔮 Predict Severity":
    st.title("🔮 Predict Breach Severity")
    st.markdown("Fill in the details below to predict if a breach will be **Large** or **Small**")

    col1, col2, col3 = st.columns(3)

    with col1:
        industry = st.selectbox("Industry", sorted(df["Industry"].unique().tolist()))
    with col2:
        method = st.selectbox("Attack Method", sorted(df["Method"].unique().tolist()))
    with col3:
        year = st.slider("Year", 2004, 2025, 2023)

    if st.button("🔮 Predict Now", use_container_width=True):
        # Convert inputs to numbers using same factorize mapping
        industry_code = sorted(df["Industry"].unique().tolist()).index(industry)
        method_code   = sorted(df["Method"].unique().tolist()).index(method)

        input_data = pd.DataFrame(
            [[industry_code, method_code, year]],
            columns=["Industry_code", "Method_code", "Year"]
        )

        prediction   = model.predict(input_data)[0]
        probability  = model.predict_proba(input_data)[0]
        confidence   = max(probability) * 100

        st.divider()

        if prediction == "Large":
            st.error(f"🚨 LARGE BREACH predicted — {confidence:.0f}% confidence")
            st.markdown("This combination historically leads to **massive data exposure (1M+ records)**")
        else:
            st.success(f"✅ SMALL BREACH predicted — {confidence:.0f}% confidence")
            st.markdown("This combination historically leads to **contained exposure (<1M records)**")

        st.info(f"**Input:** {industry} industry | {method} attack | Year {year}")
