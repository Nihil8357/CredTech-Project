import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from newsapi import NewsApiClient
import plotly.express as px

# --- Configuration ---
st.set_page_config(
    page_title="CredTech Explainable Credit Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .insight-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    .insight-header {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .alert-banner {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .news-item {
        background: white;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    .plotly-chart {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://127.0.0.1:8000"
NEWS_API_KEY = "7d5f79f6faf7400bbda1c03ec6631bf5"

# --- Functions to call APIs ---
@st.cache_data(ttl=600)
def get_score_data(ticker):
    """Fetches score and explanation data from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/score/{ticker}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend API at {API_BASE_URL}. Please ensure the backend server is running. Error: {e}")
        return None

@st.cache_data(ttl=600)
def get_history_data(ticker):
    """Fetches historical metric data from the backend."""
    try:
        response = requests.get(f"{API_BASE_URL}/history/{ticker}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        return None

@st.cache_data(ttl=600)
def get_news_headlines(company_name):
    """Fetches live news headlines directly from NewsAPI."""
    if not NEWS_API_KEY or NEWS_API_KEY == "PASTE_YOUR_NEWS_API_KEY_HERE":
        return ["NewsAPI key not configured."]
    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        headlines = newsapi.get_everything(q=company_name, language='en', sort_by='relevancy', page_size=5)
        return [article['title'] for article in headlines['articles']]
    except Exception as e:
        return [f"Could not fetch news: {e}"]

# --- Visualization & Helper Functions ---
def create_waterfall_chart(explanation):
    contributions = explanation['feature_contributions']
    sorted_contributions = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
    x_labels = [item[0] for item in sorted_contributions]
    y_values = [item[1] for item in sorted_contributions]
    
    fig = go.Figure(go.Waterfall(
        name="Contribution", 
        orientation="v",
        measure=["relative"] * len(x_labels),
        x=x_labels, 
        text=[f"{val:.2f}" for val in y_values], 
        y=y_values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#10b981"}},
        decreasing={"marker": {"color": "#ef4444"}},
    ))
    
    fig.update_layout(
        title={
            'text': "Feature Contribution to Credit Score",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#1f2937'}
        },
        showlegend=False, 
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'},
        xaxis={'tickangle': -45},
        yaxis={'gridcolor': '#f3f4f6'}
    )
    return fig

def check_for_alerts(history_df):
    if history_df is None or history_df.empty:
        return
        
    sentiment_history = history_df[history_df['metric_name'] == 'news_sentiment'].sort_values('timestamp').tail(2)
    if len(sentiment_history) == 2:
        change = sentiment_history['metric_value'].iloc[1] - sentiment_history['metric_value'].iloc[0]
        if abs(change) > 5:
            st.markdown(f"""
            <div class="alert-banner">
                🚨 <strong>Risk Alert:</strong> News sentiment score changed significantly by {change:.0f} points in the last update.
            </div>
            """, unsafe_allow_html=True)

# --- Main Dashboard ---
st.markdown("""
<div class="main-header">
    <div class="main-title">📊 CredTech Intelligence Platform</div>
    <div class="main-subtitle">Real-Time Explainable Credit Risk Analysis</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🔍 Company Analysis")
st.sidebar.markdown("---")

# Company mapping for better news search
COMPANY_MAP = {"AAPL": "Apple", "GOOGL": "Google", "MSFT": "Microsoft", "TSLA": "Tesla"}
ticker_symbol = st.sidebar.text_input("Enter Company Ticker", "AAPL", help="Enter stock ticker symbol (e.g., AAPL, GOOGL, MSFT)").upper()
company_name = COMPANY_MAP.get(ticker_symbol, ticker_symbol)

st.sidebar.markdown("---")
analyze_button = st.sidebar.button("🚀 Analyze Company", type="primary", use_container_width=True)

if analyze_button:
    with st.spinner('🔄 Analyzing company data...'):
        score_data = get_score_data(ticker_symbol)
        history_df = get_history_data(ticker_symbol)
    
    if score_data and "error" not in score_data:
        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #1e3a8a; margin: 0;">📈 Analysis for {company_name} ({ticker_symbol})</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Check for alerts
        if history_df is not None and not history_df.empty:
            check_for_alerts(history_df)

        # Key Metrics Row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Credit Score</div>
                <div class="metric-value">{score_data['credit_score']}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Prediction Label</div>
                <div class="metric-value" style="font-size: 2rem;">{score_data['prediction_label']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            risk_level = "🟢 Low Risk" if score_data['credit_score'] > 80 else "🟡 Medium Risk" if score_data['credit_score'] > 60 else "🔴 High Risk"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Risk Assessment</div>
                <div class="metric-value" style="font-size: 1.5rem;">{risk_level}</div>
            </div>
            """, unsafe_allow_html=True)

        # Tabs for detailed analysis
        tab1, tab2, tab3 = st.tabs(["📊 Score Explanation", "📈 Historical Trends", "📰 Market Intelligence"])

        with tab1:
            st.markdown("""
            <div class="insight-box">
                <div class="insight-header">💡 Credit Score Breakdown</div>
                This waterfall chart shows how each financial factor contributed to the final credit score.
                Positive contributions (green) improve the score, while negative contributions (red) decrease it.
            </div>
            """, unsafe_allow_html=True)
            
            waterfall_fig = create_waterfall_chart(score_data['explanation'])
            st.plotly_chart(waterfall_fig, use_container_width=True, config={'displayModeBar': False})
            
            # Key insights
            contributions = score_data['explanation']['feature_contributions']
            top_positive = max(contributions.items(), key=lambda x: x[1] if x[1] > 0 else -float('inf'))
            top_negative = min(contributions.items(), key=lambda x: x[1] if x[1] < 0 else float('inf'))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="insight-box" style="border-left-color: #10b981;">
                    <div class="insight-header">🚀 Strongest Factor</div>
                    <strong>{top_positive[0]}</strong><br>
                    Contributes +{top_positive[1]:.2f} points to the credit score
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if top_negative[1] < 0:
                    st.markdown(f"""
                    <div class="insight-box" style="border-left-color: #ef4444;">
                        <div class="insight-header">⚠️ Risk Factor</div>
                        <strong>{top_negative[0]}</strong><br>
                        Reduces score by {top_negative[1]:.2f} points
                    </div>
                    """, unsafe_allow_html=True)

        with tab2:
            st.markdown("""
            <div class="insight-box">
                <div class="insight-header">📈 Historical Performance Analysis</div>
                Track key financial metrics and market sentiment trends over time to identify patterns and potential risks.
            </div>
            """, unsafe_allow_html=True)
            
            if history_df is not None and not history_df.empty:
                # Create pivot table for time series data
                chart_df = history_df.pivot(index='timestamp', columns='metric_name', values='metric_value')
                chart_df.index = pd.to_datetime(chart_df.index)
                chart_df = chart_df.resample('H').mean().interpolate()
                
                # Create enhanced line chart
                fig = go.Figure()
                
                metrics_config = {
                    'grossMargin': {'color': '#3b82f6', 'name': 'Gross Margin %'},
                    'operatingMargin': {'color': '#10b981', 'name': 'Operating Margin %'},
                    'debtToEquity': {'color': '#ef4444', 'name': 'Debt-to-Equity Ratio'},
                    'news_sentiment': {'color': '#f59e0b', 'name': 'News Sentiment Score'}
                }
                
                for metric in ['grossMargin', 'operatingMargin', 'debtToEquity', 'news_sentiment']:
                    if metric in chart_df.columns:
                        config = metrics_config[metric]
                        fig.add_trace(go.Scatter(
                            x=chart_df.index,
                            y=chart_df[metric],
                            mode='lines+markers',
                            name=config['name'],
                            line=dict(color=config['color'], width=3),
                            marker=dict(size=6)
                        ))
                
                fig.update_layout(
                    title={
                        'text': 'Historical Financial Metrics Trends',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#1f2937'}
                    },
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'family': 'Inter, sans-serif'},
                    xaxis={'gridcolor': '#f3f4f6', 'title': 'Date'},
                    yaxis={'gridcolor': '#f3f4f6', 'title': 'Metric Value'},
                    legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("⚠️ Historical data is not available for this ticker.")

        with tab3:
            st.markdown("""
            <div class="insight-box">
                <div class="insight-header">📰 Live Market Intelligence</div>
                Real-time news sentiment analysis helps identify market factors that could impact creditworthiness.
                The news sentiment score in the model is derived from headlines like these.
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner('📡 Fetching latest market news...'):
                headlines = get_news_headlines(company_name)
            
            st.markdown("### 📋 Recent Headlines")
            for i, headline in enumerate(headlines, 1):
                st.markdown(f"""
                <div class="news-item">
                    <strong>{i}.</strong> {headline}
                </div>
                """, unsafe_allow_html=True)

    elif score_data and "error" in score_data:
        st.error(f"❌ Could not retrieve score for {ticker_symbol}. Error: {score_data['error']}")
    else:
        st.error("❌ Failed to connect to the backend service. Please check if the server is running.")

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="color: #1e3a8a; margin-bottom: 1rem;">🚀 Welcome to CredTech Intelligence</h3>
        <p style="color: #6b7280; font-size: 1.1rem; margin-bottom: 2rem;">
            Enter a company ticker symbol in the sidebar and click <strong>"Analyze Company"</strong> to begin comprehensive credit risk analysis.
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <strong>Real-time Analysis</strong><br>
                <small>Live market data integration</small>
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
                <strong>AI-Powered Insights</strong><br>
                <small>Explainable credit scoring</small>
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <strong>Market Intelligence</strong><br>
                <small>News sentiment analysis</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
    <strong>CredTech Intelligence Platform</strong> | Powered by Insight Loop
</div>
""", unsafe_allow_html=True)