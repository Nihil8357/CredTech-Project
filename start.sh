#!/bin/bash
# Start backend (FastAPI with Uvicorn)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start frontend with Streamlit
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0