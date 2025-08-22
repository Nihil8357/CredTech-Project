# Stage 1: Build frontend
FROM node:18 AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend and serve frontend
FROM python:3.10
WORKDIR /backend

# Copy requirements.txt from repo root and install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend to backend/static
COPY --from=frontend-builder /frontend/build ./static

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]