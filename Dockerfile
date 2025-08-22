FROM python:3.10

WORKDIR /code

ENV HOME=/code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/
COPY model.pkl .
RUN mkdir -p /code/data

EXPOSE 8000 8501

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]