FFROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# App
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Use Gunicorn with Flask, Railway provides $PORT env var
CMD gunicorn main:app --bind 0.0.0.0:$PORT
