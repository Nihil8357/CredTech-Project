FROM python:3.10

WORKDIR /code

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ backend/
COPY frontend/ frontend/

# Expose ports for backend and frontend
EXPOSE 8000 8501

# Use a shell script to start both services
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]