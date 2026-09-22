# backend/Dockerfile
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc y fuerza a que la salida estándar no se almacene en búfer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes matemáticos
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar los requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# El comando de arranque está sobrescrito en el docker-compose para usar --reload, 
# pero es buena práctica dejar el comando por defecto para producción.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]