# backend/data_ingestion.py
import yfinance as yf
import pandas_datareader.data as web
import datetime
import sqlite3
from newsapi import NewsApiClient

DATABASE_NAME = "credit_data.db"
# IMPORTANT: Get your free key from newsapi.org
NEWS_API_KEY = "7d5f79f6faf7400bbda1c03ec6631bf5" 

# In backend/data_ingestion.py

def save_metrics(ticker, metrics_dict):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now()
    
    # Prepare data for bulk insert
    metrics_to_save = []
    for key, value in metrics_dict.items():
        if value is not None:
            metrics_to_save.append((timestamp, ticker, key, value))

    # Use executemany for efficiency and safety
    if metrics_to_save:
        cursor.executemany(
            "INSERT INTO credit_metrics (timestamp, ticker, metric_name, metric_value) VALUES (?, ?, ?, ?)",
            metrics_to_save
        )

    conn.commit()
    conn.close()

def fetch_yfinance_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        data = {
            'debtToEquity': info.get('debtToEquity'),
            'returnOnAssets': info.get('returnOnAssets'),
            'grossMargin': info.get('grossMargins'),
            'operatingMargin': info.get('operatingMargins'),
            'marketCap': info.get('marketCap')
        }
        save_metrics(ticker_symbol, data)
        print(f"Successfully fetched yfinance data for {ticker_symbol}")
    except Exception as e:
        print(f"Error fetching yfinance data for {ticker_symbol}: {e}")

# In backend/data_ingestion.py

def fetch_fred_data(ticker_symbol):
    try:
        start = datetime.datetime.now() - datetime.timedelta(days=365) # Look back further
        end = datetime.datetime.now()
        gdp = web.DataReader('GDP', 'fred', start, end)
        fed_funds = web.DataReader('DFF', 'fred', start, end)
        
        data = {}
        # Add a check to make sure we got data back
        if not gdp.empty:
            data['GDP_latest'] = gdp['GDP'].iloc[-1]
        if not fed_funds.empty:
            data['FED_funds_latest'] = fed_funds['DFF'].iloc[-1]

        if data: # Only save if we found some data
            save_metrics(ticker_symbol, data)
            print(f"Successfully fetched FRED data for {ticker_symbol}")
        else:
            print(f"Could not fetch FRED data for {ticker_symbol}")

    except Exception as e:
        print(f"Error fetching FRED data: {e}")

def fetch_news_sentiment(ticker_symbol, company_name):
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        headlines = newsapi.get_everything(q=company_name, language='en', sort_by='publishedAt', page_size=10)
        
        positive_words = ['success', 'growth', 'profit', 'gain', 'strong', 'upgrade']
        negative_words = ['loss', 'warns', 'decline', 'risk', 'fail', 'downgrade', 'scandal']
        sentiment_score = 0

        for article in headlines['articles']:
            content = (article['title'] + ' ' + article['description']).lower() if article['description'] else article['title'].lower()
            sentiment_score += sum(content.count(w) for w in positive_words)
            sentiment_score -= sum(content.count(w) for w in negative_words)
        
        data = {'news_sentiment': sentiment_score}
        save_metrics(ticker_symbol, data)
        print(f"Successfully fetched news sentiment for {company_name}")
    except Exception as e:
        print(f"Error fetching news for {company_name}: {e}")

def ingest_all_data_for_ticker(ticker, company_name=None):
    """Fetches all data for a ticker. If company_name is not provided, it tries to find it."""
    print(f"--- Starting data ingestion for {ticker} ---")
    
    # If no company name is given, try to get it from yfinance
    if not company_name:
        try:
            company_info = yf.Ticker(ticker).info
            company_name = company_info.get('longName', ticker)
        except Exception:
            company_name = ticker # Fallback to ticker if name lookup fails

    fetch_yfinance_data(ticker)
    fetch_fred_data(ticker)
    fetch_news_sentiment(ticker, company_name)
    print(f"--- Finished data ingestion for {ticker} ---")