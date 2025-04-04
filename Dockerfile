FROM python:3.7.9-slim

WORKDIR /app

# Install system dependencies required for lxml
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories and make run.sh executable
RUN mkdir -p /app/conf /app/data /app/logs && \
    chmod +x run.sh

CMD ["./run.sh"] 