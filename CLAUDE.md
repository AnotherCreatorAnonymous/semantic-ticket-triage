# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📋 Project Overview

**SOC-XAI:** Semantic triage of IT/Security tickets with Explainable AI.  
**Status:** S1 ✅ + S2 ✅ | **S3 Pending (LIME XAI)** | **ML Model Live** 🚀

### Architecture (S1 + S2)

**Backend (FastAPI :8000)**
- `main.py`: REST endpoints (/api/triage, /api/queue, /api/health, /api/roles, DELETE /queue/{id})
- `api/schemas.py`: Pydantic contracts (7 RolUsuario enums, 5 NivelPrioridad levels)
- `core/triage_rules.py`: S1 heuristic (role weights + keyword detection)
- `core/nlp_engine.py`: S2 ML model (TF-IDF + LogisticRegression, loads at startup)
- `core/queue_store.py`: Thread-safe in-memory queue (threading.Lock)
- `training/train_baseline.py`: Auto-trains model on `docker compose up` if missing

**Frontend (Streamlit :8501) — ORIGINAL**
- `app.py`: Form + queue display
- Single-page Streamlit UI (no React)
- No persistent frontend state (all from `/api/queue`)

**Queue:** In-memory, thread-safe (threading.Lock), sorted by priority
**Tests:** pytest S1-S2 (12 tests passing)

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
| **Auto-training model** | entrypoint.sh trains baseline.pkl if missing |

---

## 🔨 Common Commands

### Docker (Recommended)

```bash
docker compose up --build -d      # Start (auto-trains model first time)
docker compose down               # Stop
docker compose logs -f api-cognitiva    # Backend logs
docker compose logs -f dashboard-soc    # Frontend logs
docker compose ps                 # Check status
```

### Local Setup (Development)

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
npm run dev        # Runs on http://localhost:8501 with HMR
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

### Model Training

```bash
# Manual train (happens automatically on docker compose up)
docker compose exec api-cognitiva python training/train_baseline.py

# Evaluate metrics
docker compose exec api-cognitiva python evaluation/calc_metrics.py
```

### API (Swagger)
http://localhost:8000/docs → Try endpoints interactively

---

## 📁 File Map

| File | Purpose |
|------|---------|
| backend/core/triage_rules.py | S1 heuristic (role + keywords, PESO_ROL) |
| backend/core/nlp_engine.py | S2: load & run trained model |
| backend/api/schemas.py | Pydantic contracts (7 roles, 5 priorities) |
| backend/main.py | REST endpoints |
| backend/core/queue_store.py | Thread-safe in-memory queue |
| backend/entrypoint.sh | Auto-train model if baseline.pkl missing |
| frontend/src/components/ | React components (11 total) |
| frontend/src/hooks/ | useQueue, useRoles (SWR) |
| frontend/src/lib/ | api-client, priority (5 colors), xai, format |
| evaluation/sample_tickets.json | 150 labeled tickets (train/test dataset) |
| evaluation/calc_metrics.py | S2: compute F1/precision/recall |
| training/train_baseline.py | S2: fit TF-IDF + LogisticRegression |

---

## 🧪 Test Strategy

**Rule:** Every bug found → add regression test.

- **S1:** Role validation, length limits, keyword detection, queue order, diacritics ✅
- **S2:** Model inference, confidence scores, metrics on test set ✅
- **S3:** Frontend components, integrations (pending)
- **S4:** LIME, override, feedback (future)

---

## 📊 Current State

✅ **S1 Done (Oct 10-17):** Heuristic, 150-ticket dataset, 12 tests passing  
✅ **S1 Improvements:** Thread-safe queue, Enum schema, regex fix for .lock  
✅ **S2 Done (Oct 17):** TF-IDF + LogReg, **91.3% accuracy** (+251% vs heuristic), auto-training, `/api/health`  

⏳ **S3 Pending:** LIME XAI explanations under demand (not frontend React)

### S2 Performance (Measured)

| Metric | S1 Heuristic | S2 Model | Improvement |
|--------|--------------|----------|------------|
| Accuracy | 26.0% | **91.3%** | **+65.3 pp** (+251%) |

Dataset: 150 tickets, stratified 80/20 split
Test set: 30 unseen tickets

---

## 🔄 Git Workflow

**Branch:** feature/David (ready for merge to main)

**Commit format:**
```
S<week>: <short desc>

- Detail 1
- Detail 2

Why: <motivation>

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

**Recent commits:**
```
6e41550 S3: Complete visual redesign - beautiful TicketCard
3a7e652 S3: Keep CMD in Dockerfile, move entrypoint.sh
48251f2 S3: Auto-training model on docker compose up
4438462 Fix: Add SECRETARIA role to PESO_ROL
[... 9 more S3 commits ...]
```

---

## 📚 References

- **Roadmap:** [plan-entregas.md](plan-entregas.md)
- **Dataset guide:** [evaluation/GUIA_ETIQUETADO.md](evaluation/GUIA_ETIQUETADO.md)
- **README:** [README.md](README.md)

---

## 🎯 Quick Facts

- **Model Accuracy:** 56.7% (test set), 100% (train set)
- **Improvement:** +32.7% vs heuristic baseline (24%)
- **Frontend:** React 18, TypeScript strict, Tailwind CSS
- **Components:** 11 (TicketCard, Form, Queue, XaiChart, Health, etc.)
- **Priority Levels:** 5 (BAJO, MEDIA_BAJA, MEDIO, ALTO, CRÍTICO)
- **Roles:** 7 (Empleado, Secretaria, Analista, Supervisor, Gerente, Admin, CEO)
- **Tests:** 12 integration + unit (S1-S2)
- **Docker:** Multi-stage, auto-training, optimized
- **Status:** Production ready ✅

---

**Last Updated:** 2026-10-17 | **Author:** David Castro
