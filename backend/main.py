# backend/main.py
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import pandas as pd
import pickle
import shap 


from .data_ingestion import ingest_all_data_for_ticker

DATABASE_NAME = "credit_data.db"
app = FastAPI(title="CredTech API")

from pathlib import Path

model = None
explainer = None
try:
    # Build a path from this file's location to the project root, then to model.pkl
    MODEL_PATH = Path(__file__).parent.parent / "model.pkl"
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully from:", MODEL_PATH)

    # Create a SHAP explainer for our model
    explainer = shap.TreeExplainer(model)
    print("SHAP explainer created successfully.")

except FileNotFoundError:
    print(f"Error: model.pkl not found at {MODEL_PATH}. Make sure it's in the main project directory.")
except Exception as e:
    print(f"An error occurred while loading the model: {e}")


COMPANIES_TO_TRACK = {
    "AAPL": "Apple",
    "GOOGL": "Google",
    "MSFT": "Microsoft",
    "TSLA": "Tesla"
}

def scheduled_ingestion_job():
    print("Scheduler running: Ingesting data for all tracked companies.")
    for ticker, name in COMPANIES_TO_TRACK.items():
        ingest_all_data_for_ticker(ticker, name)

@app.on_event("startup")
def start_scheduler():
    scheduled_ingestion_job() 
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_ingestion_job, 'interval', minutes=15)
    scheduler.start()
    print("Scheduler started. Data will be ingested every 15 minutes.")

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the CredTech Explainable Credit Intelligence API"}

@app.get("/history/{ticker}")
def get_historical_data(ticker: str):
    conn = sqlite3.connect(DATABASE_NAME)
    query = f"SELECT * FROM credit_metrics WHERE ticker = '{ticker.upper()}' ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict(orient='records')

@app.get("/latest/{ticker}")
def get_latest_data(ticker: str):
    conn = sqlite3.connect(DATABASE_NAME)
    query = f"""
    SELECT metric_name, metric_value
    FROM credit_metrics
    WHERE ticker = '{ticker.upper()}'
    AND timestamp = (SELECT MAX(timestamp) FROM credit_metrics WHERE ticker = '{ticker.upper()}')
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.set_index('metric_name').to_dict()['metric_value']

@app.get("/score/{ticker}")
def get_score(ticker: str):
    """
    Generates a credit score and explanation. 
    If data is not in the DB, it fetches it on-demand.
    """
    ticker = ticker.upper()
    conn = sqlite3.connect(DATABASE_NAME)
    
    # Check if we have recent data
    query = f"SELECT metric_name, metric_value FROM credit_metrics WHERE ticker = '{ticker}'"
    df = pd.read_sql_query(query, conn)

    # If no data is found, fetch it now
    if df.empty:
        print(f"No data for {ticker} found in DB. Fetching on-demand...")
        ingest_all_data_for_ticker(ticker)
        # Re-query the database after ingestion
        df = pd.read_sql_query(query, conn)
        if df.empty:
            return {"error": f"Could not fetch any data for the ticker {ticker}."}

    conn.close()
    
    # --- The rest of the function proceeds as before ---
    if model is None or explainer is None:
        return {"error": "Model or explainer not loaded."}
    
    # Prepare the data
    features = df.set_index('metric_name').to_dict()['metric_value']
    feature_df = pd.DataFrame([features])
    
    expected_columns = ['debtToEquity', 'returnOnAssets', 'grossMargin', 'operatingMargin', 
                        'marketCap', 'GDP_latest', 'FED_funds_latest', 'news_sentiment']
    for col in expected_columns:
        if col not in feature_df.columns:
            feature_df[col] = 0
    
    feature_df = feature_df[expected_columns]

    # Make prediction
    prediction = model.predict(feature_df)[0]
    prediction_proba = model.predict_proba(feature_df)[0]
    credit_score = int(prediction_proba[1] * 100)

    # Generate explanation using SHAP
    shap_values = explainer.shap_values(feature_df)
    
    shap_values_for_class_1 = shap_values[1] if isinstance(shap_values, list) else shap_values
    base_value = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value
    
    explanation = {
        "base_value": float(base_value),
        "feature_contributions": {col: float(shap_values_for_class_1[0][i]) for i, col in enumerate(expected_columns)}
    }

    return {
        "ticker": ticker,
        "prediction_label": "Good" if prediction == 1 else "Bad",
        "credit_score": credit_score,
        "explanation": explanation
    }