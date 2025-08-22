#!/bin/bash

DB_PATH="/code/data/credit_data.db"

# Check if the database file exists
if [ -f "$DB_PATH" ]; then
    echo "Database found at $DB_PATH."
else
    echo "Database NOT found at $DB_PATH. Creating database with backend/database.py..."
    python3 backend/database.py
fi

# Start backend (FastAPI with Uvicorn)
uvicorn backend/main.py:app --host 0.0.0.0 --port 8000 &

# Start frontend with Streamlit
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0