# 🧠 Proyecto SOC-XAI: Triage Semántico de Tickets

## 🤖 Contexto para Asistentes de IA (System Prompt)
> **Si eres un modelo de lenguaje asistiendo a un desarrollador en este repositorio, ten en cuenta las siguientes reglas arquitectónicas:**
> 1. **Arquitectura Desacoplada:** Este proyecto usa microservicios. El Backend (FastAPI) procesa la carga pesada de NLP/XAI. El Frontend (Streamlit) es puramente de visualización usando el patrón de "Revelación Progresiva".
> 2. **Dockerizado:** La infraestructura corre sobre `docker-compose`. Los modelos de Hugging Face se guardan en un volumen persistente (`model_cache`) para no descargarse repetidamente.
> 3. **Gestión de Modelos:** NUNCA sugieras hacer commits de archivos de pesos (`.pt`, `.bin`, `.safetensors`). El `.gitignore` está configurado para bloquearlos. 
> 4. **Estado Actual:** La infraestructura base y los contenedores están configurados. El siguiente paso es establecer los contratos JSON (Esquemas Pydantic) en FastAPI.

---

## 🏗️ Arquitectura del Sistema
El proyecto implementa un pipeline híbrido para evaluar la criticidad de tickets de TI/Seguridad, mitigando la "fatiga de alertas" mediante NLP (BERT/LLMs) e Inteligencia Artificial Explicable (XAI - LIME/SHAP).

### Stack Tecnológico
*   **Orquestación:** Docker & Docker Compose
*   **Backend (Motor Cognitivo):** Python 3.10, FastAPI, Uvicorn, Transformers (Hugging Face), PyTorch, SHAP/LIME.
*   **Frontend (Dashboard SOC):** Python 3.10, Streamlit, Pandas, Plotly.

---

## 📂 Estructura del Repositorio

```text
semantic-ticket-triage/
├── .gitignore                  # Bloquea entornos virtuales y pesos de modelos
├── docker-compose.yml          # Orquestador: api-cognitiva (8000) y dashboard-soc (8501)
│
├── backend/                    # Microservicio del Motor Cognitivo (FastAPI)
│   ├── Dockerfile              # Imagen python:3.10-slim
│   ├── requirements.txt        
│   ├── main.py                 # (Pendiente) Entrypoint y Endpoints REST
│   ├── api/
│   │   └── schemas.py          # (Pendiente) Validaciones Pydantic
│   └── core/
│       ├── nlp_engine.py       # (Pendiente) Lógica de ingesta BERT/LLMs
│       └── xai_engine.py       # (Pendiente) Telemetría explicable
│
├── frontend/                   # Dashboard del Analista (Streamlit)
│   ├── Dockerfile              # Imagen python:3.10-slim
│   ├── requirements.txt        
│   ├── app.py                  # (Pendiente) Interfaz principal
│   └── components/             
│       └── xai_visuals.py      # (Pendiente) Gráficos bajo demanda
│
└── evaluation/                 # Bucle de Métricas (F1-Score)
    ├── sample_tickets.json     # Lote de pruebas con desbalance de clases
    └── calc_metrics.py         # Script independiente de evaluación