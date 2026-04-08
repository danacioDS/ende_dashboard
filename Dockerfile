FROM python:3.10-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better Docker caching)
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck (optional but professional)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command (Streamlit dashboard)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]