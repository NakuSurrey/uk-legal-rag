# Use Python 3.10 to match your local setup exactly
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies that some Python packages need
RUN apt-get update && apt-get install -y \
    build-essential \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker caches this layer — saves rebuild time)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY src/ ./src/
COPY data/ ./data/

# Copy the supervisord config
COPY supervisord.conf .

# Create the chroma_db directory (will be populated on first run)
RUN mkdir -p chroma_db

# Pre-populate the vector database
RUN python src/build_db.py

# Expose both ports
EXPOSE 8000 8501

# Run supervisord to manage both FastAPI and Streamlit
CMD ["supervisord", "-c", "/app/supervisord.conf"]