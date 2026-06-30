from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os

app = FastAPI(title="CyberBreach Analytics API")

# ── Allow frontend to talk to backend ─────────────────
# This is called CORS — without it browser blocks the connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load data and model once at startup ───────────────
BASE = os.path.dirname(os.path.abspath(__file__))
df    = pd.read_csv(os.path.join(BASE, "..", "clean_breaches.csv"))
model = joblib.load(os.path.join(BASE, "..", "model.pkl"))

# Fix year column
df["Year"] = df["Year"].astype(str).str[:4]
df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

# ================================================================
# ENDPOINT 1: GET /overview
# Returns the 4 big numbers for the Overview page
# ================================================================
@app.get("/overview")
def get_overview():
    return {
        "total_breaches":      int(len(df)),
        "total_records":       f"{df['Records'].sum()/1e9:.1f}B",
        "most_breached":       df["Industry"].value_counts().index[0],
        "top_attack_method":   df["Method"].value_counts().index[0],
        "industry_counts":     df["Industry"].value_counts().to_dict(),
        "method_counts":       df["Method"].value_counts().head(6).to_dict(),
    }

# ================================================================
# ENDPOINT 2: GET /trends
# Returns yearly breach counts + records per industry
# ================================================================
@app.get("/trends")
def get_trends():
    yearly = df[df["Year"] > 2000]["Year"].value_counts().sort_index()
    records = df.groupby("Industry")["Records"].sum().sort_values(ascending=False)
    return {
        "yearly_counts":   yearly.to_dict(),
        "records_by_industry": {k: int(v) for k, v in records.items()},
        "industries":      sorted(df["Industry"].unique().tolist()),
        "methods":         sorted(df["Method"].unique().tolist()),
    }

# ================================================================
# ENDPOINT 3: POST /predict
# Takes industry + method + year, returns severity prediction
# ================================================================
class PredictRequest(BaseModel):
    industry: str
    method:   str
    year:     int

@app.post("/predict")
def predict_severity(req: PredictRequest):
    industries = sorted(df["Industry"].unique().tolist())
    methods    = sorted(df["Method"].unique().tolist())

    # Convert text to number codes
    industry_code = industries.index(req.industry) if req.industry in industries else 0
    method_code   = methods.index(req.method)       if req.method   in methods   else 0

    input_data = pd.DataFrame(
        [[industry_code, method_code, req.year]],
        columns=["Industry_code", "Method_code", "Year"]
    )

    prediction  = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0]
    confidence  = round(max(probability) * 100, 1)

    return {
        "severity":   prediction,
        "confidence": confidence,
        "industry":   req.industry,
        "method":     req.method,
        "year":       req.year,
    }

# ================================================================
# ENDPOINT 4: GET /breaches
# Returns raw breach table with optional industry filter
# ================================================================
@app.get("/breaches")
def get_breaches(industry: str = "All"):
    filtered = df if industry == "All" else df[df["Industry"] == industry]
    return filtered[["Entity", "Year", "Records", "Industry", "Method"]]\
        .fillna("Unknown").to_dict(orient="records")



# ================================================================
# ENDPOINT 5: GET /search?company=adobe
# Returns breach details for a specific company
# ================================================================
@app.get("/search")
def search_breach(company: str = ""):
    if not company:
        return {"results": []}
    
    # Case-insensitive search
    mask    = df["Entity"].str.lower().str.contains(company.lower(), na=False)
    results = df[mask].copy()
    
    if results.empty:
        return {"results": [], "message": f"No breaches found for '{company}'"}
    
    return {
        "results": results[[
            "Entity", "Year", "Records", "Industry", "Method"
        ]].fillna("Unknown").to_dict(orient="records"),
        "total": len(results)
    }

# ================================================================
# ENDPOINT 6: POST /comments  — add a comment
# GET  /comments?company=adobe — get comments for a company
# ================================================================

# Simple in-memory comment store (resets when server restarts)
# In a real app you'd use a database
comments_store = {}

class Comment(BaseModel):
    company:  str
    username: str
    text:     str

@app.post("/comments")
def add_comment(comment: Comment):
    if comment.company not in comments_store:
        comments_store[comment.company] = []
    
    import datetime
    comments_store[comment.company].append({
        "username": comment.username,
        "text":     comment.text,
        "time":     datetime.datetime.now().strftime("%d %b %Y, %H:%M")
    })
    return {"message": "Comment added!", "total": len(comments_store[comment.company])}

@app.get("/comments")
def get_comments(company: str = ""):
    return {
        "comments": comments_store.get(company, []),
        "total":    len(comments_store.get(company, []))
    }


# ================================================================
# ENDPOINT 7: GET /compare?industry1=Healthcare&industry2=Finance
# Returns side by side stats for two industries
# ================================================================
@app.get("/compare")
def compare_industries(industry1: str = "Healthcare", industry2: str = "Finance"):
    
    def get_stats(industry):
        d = df[df["Industry"] == industry]
        if d.empty:
            return None
        return {
            "industry":        industry,
            "total_breaches":  int(len(d)),
            "total_records":   int(d["Records"].sum()),
            "avg_records":     int(d["Records"].mean()),
            "max_records":     int(d["Records"].max()),
            "largest_breach":  str(d.loc[d["Records"].idxmax(), "Entity"]),
            "worst_year":      int(d["Year"].value_counts().index[0]),
            "top_method":      str(d["Method"].value_counts().index[0]),
            "large_breaches":  int((d["Records"] > 1000000).sum()),
            "small_breaches":  int((d["Records"] <= 1000000).sum()),
            "yearly_counts":   d["Year"].value_counts().sort_index().to_dict(),
        }

    stats1 = get_stats(industry1)
    stats2 = get_stats(industry2)

    if not stats1 or not stats2:
        return {"error": "Industry not found"}

    return {
        "industry1": stats1,
        "industry2": stats2,
        "industries_available": sorted(df["Industry"].unique().tolist())
    }

# ================================================================
# ENDPOINT 8: GET /leaderboard
# Returns top 10 biggest breaches by records leaked
# ================================================================
@app.get("/leaderboard")
def get_leaderboard():
    top10 = df.nlargest(10, "Records")[
        ["Entity", "Year", "Records", "Industry", "Method"]
    ].fillna("Unknown")
    
    records = top10.to_dict(orient="records")
    
    # Add rank and medal
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, r in enumerate(records):
        r["rank"]   = i + 1
        r["medal"]  = medals[i]
    
    return {
        "leaderboard": records,
        "total_records_top10": int(top10["Records"].sum())
    }