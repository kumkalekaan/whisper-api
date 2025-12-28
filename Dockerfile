FROM python:3.13-slim

# Build araçları + PyAV dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App dosyasını kopyala
COPY main.py .

# Port
EXPOSE 8000

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
