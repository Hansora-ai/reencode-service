FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements (if you have one)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set environment variables
ENV PORT=8080

# Run with Gunicorn and log errors to stdout
CMD ["gunicorn", "-w", "1", "-k", "gthread", "--timeout", "600", "--bind", "0.0.0.0:8080", "--error-logfile", "-", "main:app"]
