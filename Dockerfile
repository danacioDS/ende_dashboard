# Dockerfile for Ende Dashboard - Production
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install into a clean prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# -------------------------
# Runtime image
# -------------------------
FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -s /sbin/nologin appuser

# Copy installed python packages
COPY --from=builder /install /usr/local

COPY . .

# Create writable directories and fix ownership after COPY
RUN mkdir -p /app/logs /tmp/.streamlit \
    && chown -R appuser:appuser /app /tmp/.streamlit

ENV PYTHONUNBUFFERED=1
ENV HOME=/home/appuser
ENV STREAMLIT_HOME=/tmp/.streamlit

EXPOSE 8501

USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "bienvenidos.py", "--server.port=8501", "--server.address=0.0.0.0"]
