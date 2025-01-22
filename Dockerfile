# Build stage for React frontend
FROM node:18 AS frontend-build
WORKDIR /frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm cache clean --force && \
    npm install --no-audit --no-fund --legacy-peer-deps --loglevel=error

# Copy frontend source and build
COPY frontend/ ./
RUN GENERATE_SOURCEMAP=false npm run build && \
    ls -la build/ && \
    echo "Frontend build completed"

# Python backend
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/static /app/logs /etc/supervisor/conf.d

# Copy frontend build and set permissions
COPY --from=frontend-build /frontend/build /app/static/
RUN chown -R root:root /app/static && \
    chmod -R 755 /app/static && \
    ls -la /app/static/

# Copy backend code
COPY . .

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Make port available
EXPOSE 5000

# Add health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/ || exit 1

# Start supervisor
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]