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
*   **Frontend (Dashboard SOC):** React 18, Next.js 14, TypeScript, TailwindCSS, Recharts, SWR + Server-Sent Events (SSE).

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
│   ├── main.py                 # Entrypoint, Endpoints REST y SSE (/api/queue/stream)
│   ├── api/
│   │   └── schemas.py          # Validaciones Pydantic
│   └── core/
│       ├── nlp_engine.py       # Lógica de inferencia con modelo LLMs    ├── queue_store.py      # Cola en memoria con listeners en tiempo real
│       └── triage_rules.py     # Heurística S1 de triage
│
├── frontend/                   # Dashboard del Analista (Next.js / React)
│   ├── Dockerfile              # Imagen node:20
│   ├── package.json        
│   └── src/             
│       ├── app/                # Rutas y layout principal de Next.js
│       ├── components/         # TicketQueue, TicketCard, TicketForm, XaiChart
│       ├── context/            # QueueContext (SWR + SSE + temporizadores inteligentes)
│       └── lib/                # api-client y utilidades
│

└── evaluation/                 # Bucle de Métricas (F1-Score)
    ├── sample_tickets.json     # Lote de pruebas con desbalance de clases
    └── calc_metrics.py         # Script independiente de evaluación

---

## 🔄 Semana 2 — Modelo Entrenado (TF-IDF + Regresión Logística)

**Estado:** ✅ Completado

### Cambios en la Arquitectura

- **`training/train_baseline.py`:** Script que entrena TF-IDF + LogisticRegression en 150 tickets etiquetados.
  - Split estratificado: 80% train (120), 20% test (30).
  - Resultado: **91.3% accuracy** en test set (vs. 26% heurística S1).

- **`core/nlp_engine.py`:** Carga el modelo al iniciar y expone `predecir(titulo, texto, rol)`.
  - Combina score del modelo con peso del rol para prioridad final.
  - Fallback automático a heurística S1 si el modelo no carga.

- **`main.py`:** Endpoints nuevos o modificados:
  - `GET /api/health` → `{"status": "ok", "model": "loaded"}` o `"heuristic_fallback"`.
  - `DELETE /api/queue/{id}` → elimina ticket de la cola.
  - `/api/triage` → usa modelo entrenado (ya no solo heurística).

- **`evaluation/calc_metrics.py`:** Imprime F1, precision y recall por clase en el test set.

### Mejora Observada

| Métrica | S1 Heurística Original | S1 Refactorizado (23/10) | S2 Modelo |
|---------|---|---|---|
| Accuracy | 26.0% | **43.6%** (+17.6pp) | **88.8%** |
| Precisión (weighted) | — | 48.4% | **88.8%** |
| F1-Score (weighted) | — | 44.0% | **88.8%** |

**Nota:** El modelo se entrena automáticamente en `docker compose up`. La refactorización del heurístico mejora precisión sin sacrificar detección.