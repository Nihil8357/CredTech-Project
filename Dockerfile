FROM python:3.10

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]