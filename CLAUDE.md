# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📋 Project Overview

**SOC-XAI:** Semantic triage of IT/Security tickets with Explainable AI.  
**Status:** S1 complete + S1 improvements; S2 ML baseline complete; S3 React frontend (in progress).

### Architecture

Frontend (React/Next.js :8501) ↔ Backend (FastAPI :8000)
- **Backend:** main.py (endpoints) → api/schemas.py (Pydantic) → core/(triage_rules | nlp_engine | queue_store)
- **Frontend:** React 18 + Next.js 14 + TypeScript + Tailwind CSS (reemplaza Streamlit)
  - Componentes: TicketCard, TicketForm, TicketQueue, XaiChart, HealthIndicator
  - Hooks: useQueue, useRoles (SWR para estado reactivo)
  - Tipos: espejo de schemas.py
  - Proxy rewrites: sin CORS necesario en backend
- **Queue:** In-memory, thread-safe (threading.Lock), sorted by priority
- **Tests:** pytest S1-S2 (12/12 passing) + React unit tests (pendiente)

### Key Decisions

| Decision | Why |
|----------|-----|
| **Pydantic Enums** (RolUsuario, NivelPrioridad) | Type-safe; 422 for invalid input (never 500) |
| **def endpoints** (not sync) | Thread pool execution; heavy ML model won't block others |
| **XAI contract from S1** (xplicacion_xai: Dict[str, float]) | LIME plugs in S3 without frontend changes |
| **UUID + UTC timestamps** | Base for audit, delete, override (S2–S4) |
| **Thread-safe queue** | Multiple concurrent endpoints accessing _tickets |
| **React + Next.js** | Type-safe frontend, SSR-ready, Tailwind CSS, SWR for state |
| **Proxy rewrites** | Backend needs no CORS; frontend calls /api/* locally |

---

## 🔨 Common Commands

### Local Setup (Recomendado para desarrollo)

**Backend:**
```bash
cd backend
uv sync
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (en otra terminal):**
```bash
cd frontend
npm install
npm run dev        # Runs on http://localhost:8501
```

### Docker

```bash
docker compose up --build -d      # Start
docker compose down               # Stop
docker compose logs -f api-cognitiva    # Backend logs
docker compose logs -f dashboard-soc    # Frontend logs
```

### Testing

**Backend (local):**
```bash
cd backend && uv run --with pytest pytest tests/ -v
```

**Backend (Docker):**
```bash
docker compose exec api-cognitiva pytest tests/ -v
```

**Frontend (local):**
```bash
cd frontend && npm test
```

### API (Swagger)
http://localhost:8000/docs → Try endpoints interactively

### S2 Commands
```bash
docker compose exec api-cognitiva python training/train_baseline.py
docker compose exec api-cognitiva python evaluation/calc_metrics.py
```

---

## 📁 File Map

| File | Purpose |
|------|---------|
| backend/core/triage_rules.py | S1 heuristic (role + keywords) |
| backend/core/nlp_engine.py | S2: load & run trained model |
| backend/api/schemas.py | Pydantic contracts (Enums, Request/Response) |
| backend/main.py | REST endpoints |
| backend/core/queue_store.py | Thread-safe in-memory queue |
| frontend/src/components/ | React components (TicketCard, Form, Queue, etc.) |
| frontend/src/hooks/ | useQueue, useRoles (SWR) |
| frontend/src/lib/ | api-client, priority, xai, format utilities |
| evaluation/sample_tickets.json | 150 labeled tickets (train/test dataset) |
| evaluation/calc_metrics.py | S2: compute F1/precision/recall |
| training/train_baseline.py | S2: fit TF-IDF + LogisticRegression |

---

## 🧪 Test Strategy

**Rule:** Every bug found → add regression test.

- **S1:** Role validation, length limits, keyword detection, queue order, diacritics
- **S2:** Model inference, confidence scores, metrics on test set
- **S3–S4:** LIME, override, feedback

---

## 📊 Current State

✅ **S1 Done:** Heuristic, 150-ticket dataset, 12 tests passing  
✅ **S1 Improvements:** Thread-safe queue, Enum schema, regex fix for .lock  
✅ **S2 Done:** TF-IDF + LogReg, /api/health, DELETE /queue/{id}, tests 17 OK  
✅ **S3 In Progress:** React frontend (Next.js + TypeScript + Tailwind)  
⏳ **S3 Next:** Unit tests, Docker stability, docs  

---

## 🔄 Git Workflow

**Branch:** feature/<Name> (e.g., feature/David)

**Commit format:**
```
S<week>: <short desc>

- Detail 1
- Detail 2

Why: <motivation>

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

---

## 📚 References

- **Roadmap:** [plan-entregas.md](plan-entregas.md)
- **Dataset guide:** [evaluation/GUIA_ETIQUETADO.md](evaluation/GUIA_ETIQUETADO.md)
- **README:** Full setup instructions

