# Use Python 3.13 for best performance and compatibility with QuantumBotX v2.1.0
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (build-essential for math/financial libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV BROKER_TYPE=CCXT
ENV PYTHONUNBUFFERED=1

# Default environment to Production when using Docker
ENV FLASK_ENV=production

# Run the application
CMD ["python", "run.py"]
