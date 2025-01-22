# Build stage for React frontend
FROM node:18 AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm cache clean --force && \ 

npm install --no-audit --no-fund --legacy-peer-deps --loglevel=error

COPY frontend/ ./
RUN GENERATE_SOURCEMAP=false npm run build

# Python backend
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend build
COPY --from=frontend-build /frontend/build /app/static

# Copy backend code
COPY . .

# Create directory for supervisor configs
RUN mkdir -p /etc/supervisor/conf.d

# Make port available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=development

# Add a health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/ || exit 1

# Start supervisor
CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]