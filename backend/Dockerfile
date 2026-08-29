FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fontconfig \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-xlib-2.0-0 \
    fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install IBM Plex fonts for PDF reports (WeasyPrint / fontconfig)
RUN mkdir -p /usr/share/fonts/truetype/ibmplex \
    && cp /app/app/assets/fonts/*.ttf /usr/share/fonts/truetype/ibmplex/ \
    && fc-cache -f

# Create data directories
RUN mkdir -p /data_storage/raw_audits \
    /data_storage/aggregated \
    /data_storage/reports \
    /data_storage/exports \
    /data_storage/logs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
