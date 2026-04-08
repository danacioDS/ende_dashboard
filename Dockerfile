# Dockerfile para Streamlit Dashboard

# 1️⃣ Base image
FROM python:3.11-slim

# 2️⃣ Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# 3️⃣ Directorio de trabajo
WORKDIR /app

# 4️⃣ Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Copiar y actualizar pip
COPY requirements.txt .
RUN pip install --upgrade pip

# 6️⃣ Instalar dependencias de Python
RUN pip install -r requirements.txt

# 7️⃣ Copiar el resto de la aplicación
COPY . .

# 8️⃣ Exponer el puerto de Streamlit
EXPOSE 8501

# 9️⃣ Healthcheck (opcional)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 🔟 CMD para ejecutar Streamlit
# Cambia "Bienvenidos.py" por el archivo principal de tu dashboard si cambia
CMD ["streamlit", "run", "Bienvenidos.py", "--server.port=8501", "--server.address=0.0.0.0"]