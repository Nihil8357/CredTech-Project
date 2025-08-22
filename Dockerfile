# Stage 1: Build frontend
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build backend and serve frontend
FROM python:3.10
WORKDIR /app

# Install backend dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build to backend/static
COPY --from=frontend-builder /app/frontend/build ./backend/static

# Expose port needed by Hugging Face Spaces (default: 7860)
EXPOSE 7860

# Start FastAPI app (that serves static files from /backend/static)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--root-path", ""]