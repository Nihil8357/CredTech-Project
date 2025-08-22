# Use multi-stage build for frontend
FROM node:18 AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Backend stage
FROM python:3.10
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r backend/requirements.txt
COPY backend/ .
COPY --from=frontend /app/frontend/build ./frontend_build

# Install process manager
RUN pip install uvicorn

# Command: run backend and serve frontend with backend
CMD uvicorn main:app --host 0.0.0.0 --port 7860