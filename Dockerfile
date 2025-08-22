FROM python:3.10

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy both backend and frontend
COPY backend/ backend/
COPY frontend/ frontend/

EXPOSE 7860

# Launch Streamlit frontend (recommended entry point for Spaces)
CMD ["streamlit", "run", "frontend/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]