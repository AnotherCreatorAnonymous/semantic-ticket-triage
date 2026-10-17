# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📋 Project Overview

**SOC-XAI:** Semantic triage of IT/Security tickets with Explainable AI.  
**Status:** S1 (Week 1) complete + S1 improvements (feature/David); S2 (ML baseline) in progress.

### Architecture

Frontend (Streamlit :8501) ↔ Backend (FastAPI :8000)
- **Backend:** main.py (endpoints) → api/schemas.py (Pydantic) → core/(triage_rules | nlp_engine | queue_store)
- **Frontend:** app.py (UI) → api_client.py (HTTP wrapper)
- **Queue:** In-memory, thread-safe (threading.Lock), sorted by priority (descending)
- **Tests:** pytest integration + unit tests (12/12 passing)

### Key Decisions

| Decision | Why |
|----------|-----|
| **Pydantic Enums** (RolUsuario, NivelPrioridad) | Type-safe; 422 for invalid input (never 500) |
| **def endpoints** (not sync) | Thread pool execution; heavy ML model won't block others |
| **XAI contract from S1** (xplicacion_xai: Dict[str, float]) | LIME plugs in S3 without frontend changes |
| **UUID + UTC timestamps** | Base for audit, delete, override (S2–S4) |
| **Thread-safe queue** | Multiple concurrent endpoints accessing _tickets |

---

## 🔨 Common Commands

### Docker
`ash
docker compose up --build -d      # Start (first time: 10–30 min)
docker compose down               # Stop
docker compose logs -f api-cognitiva    # Backend logs
docker compose logs -f dashboard-soc    # Frontend logs
`

### Testing
`ash
# All tests
docker compose exec api-cognitiva pytest tests/ -v

# Single test
docker compose exec api-cognitiva pytest tests/test_triage.py::test_extension_lock_suelto -v

# Local (no Docker)
cd backend && uv run --with pytest pytest tests/ -v
`

### API (Swagger)
http://localhost:8000/docs → Try endpoints interactively

### S2 Commands
`ash
docker compose exec api-cognitiva python training/train_baseline.py
docker compose exec api-cognitiva python evaluation/calc_metrics.py
`

---

## 📁 File Map

| File | Purpose |
|------|---------|
| ackend/core/triage_rules.py | S1 heuristic (role + keywords); replaced by nlp_engine.py in S2 |
| ackend/core/nlp_engine.py | S2: load & run trained model; same signature as triage_rules |
| ackend/api/schemas.py | Pydantic contracts (RolUsuario, NivelPrioridad Enums) |
| ackend/main.py | REST endpoints; calls core/ logic |
| ackend/core/queue_store.py | Thread-safe in-memory queue |
| rontend/app.py | Streamlit UI; no business logic |
| ackend/tests/test_triage.py | 12 integration + unit tests |
| valuation/sample_tickets.json | 150 labeled tickets (shuffle before train/test split) |
| valuation/calc_metrics.py | S2: compute F1/precision/recall on test set |
| 	raining/train_baseline.py | S2: fit TF-IDF + LogisticRegression |

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
⚠️ **Known issue:** Category leak (level 1 = solicitud, level 2 = operativo)  
⏳ **S2 In Progress:** Model training, metrics, /api/health, DELETE /queue/{id}

---

## 🔄 Git Workflow

**Branch:** eature/<Name> (e.g., eature/David)

**Commit format:**
`
S<week>: <short desc>

- Detail 1
- Detail 2

Why: <motivation>

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
`

---

## 📚 References

- **Roadmap:** [plan-entregas.md](plan-entregas.md)
- **Dataset guide:** [valuation/GUIA_ETIQUETADO.md](evaluation/GUIA_ETIQUETADO.md)
- **README:** Full setup instructions
