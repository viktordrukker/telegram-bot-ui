# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 53197 available to the world outside this container
EXPOSE 53986

# Define environment variable
ENV FLASK_APP=telegram_bot_ui.py

# Run the application
# Add a health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:53986/ || exit 1

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=53986"]