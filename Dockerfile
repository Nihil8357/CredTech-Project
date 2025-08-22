FROM python:3.10

WORKDIR /code

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ backend/
COPY frontend/ frontend/

# Copy your main launcher script
COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]