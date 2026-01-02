FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Render/Railway provides PORT env var dynamically
EXPOSE 8000

# Stamp database as current (skip problematic migrations) and start the application
CMD ["/bin/sh", "-c", "alembic stamp head && python seed.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
