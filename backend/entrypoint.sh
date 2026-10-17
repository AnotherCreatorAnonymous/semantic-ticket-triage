#!/bin/bash
set -e

echo "🚀 SOC Triage Backend - Inicializando..."

# Revisar si el modelo existe
if [ ! -f "baseline.pkl" ]; then
    echo "📚 Modelo no encontrado. Entrenando..."
    python training/train_baseline.py
    echo "✅ Modelo entrenado exitosamente"
else
    echo "✅ Modelo encontrado, usando baseline.pkl"
fi

echo "🔥 Iniciando FastAPI en puerto 8000..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
