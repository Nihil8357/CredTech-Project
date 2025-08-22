#!/bin/bash
# Start backend (assuming a Python-based backend, e.g., FastAPI or Flask)
python backend/main.py &

# Start frontend with Streamlit
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0