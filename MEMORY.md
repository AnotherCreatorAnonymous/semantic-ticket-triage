# MEMORY.md

**Last Updated:** 2026-10-17  
**Maintained by:** Claude Code instances  
**Max Size:** 50 lines (enforce rigorously)

---

## 🎯 Core Rules (Inviolable)

1. **Every bug found → regression test** (s/test_triage.py; rule from S1 plan)
2. **No async endpoints** — use def, run in thread pool (architecture decision)
3. **Thread-safe queue** — always use 	hreading.Lock in queue_store.py
4. **Pydantic Enums only** — roles + priority levels as Enums, never free strings
5. **No simulated data on backend failure** — show errors, not fallbacks
6. **XAI contract immutable** — \xplicacion_xai: Dict[str, float]\ format never changes

---

## 📊 Project State (S2 Focus)

- **S1 Status:** ✅ Complete + improved (regex .lock, thread-safe, Enum schema, 12 tests)
- **S2 Scope:** TF-IDF + LogReg, metrics (target F1 ≥ 0.75), endpoints /health, DELETE /queue/{id}
- **S2 Critical:** Dataset shuffle before train/test split (currently ordered by priority blocks)
- **Known Issue:** Category leaks (level 1 = solicitud, level 2 = operativo) — **DO NOT IGNORE**

---

## 🔧 Tech Stack (Fixed)

| Layer | Tech | Versions |
|-------|------|----------|
| Backend | Python 3.10, FastAPI, Pydantic v2 | Fixed in Dockerfile |
| Frontend | Python 3.10, Streamlit, Plotly | Fixed in Dockerfile |
| Queue | 	hreading.Lock (no async, no Redis) | In-memory only (MVP acceptable) |
| Tests | pytest, httpx, TestClient | In requirements-dev.txt |
| ML (S2) | scikit-learn (TF-IDF, LogReg) | No PyTorch for baseline |

---

## 🚀 S2 Priorities (Week 2)

1. 	raining/train_baseline.py — shuffle dataset, stratified split, fit model, save joblib
2. core/nlp_engine.py — load model, predecir() returns same signature as triage_rules
3. valuation/calc_metrics.py — F1/precision/recall on test set
4. main.py — switch /api/triage to use nlp_engine; add /api/health, DELETE /queue/{id}
5. **Tests:** 3+ tests for model inference (confidence ranges, unknown roles)

---

## 📋 Remember (Decision Log)

- **S1 Regex Fix (2026-10-17):** .lock without filename now detected (T121 test case)
- **S1 Enum Schema (2026-10-17):** NivelPrioridad Enum prevents free-string bugs
- **S1 Thread-Safety (2026-10-17):** 	hreading.Lock in queue_store for concurrent access
- **S1 Float XAI (2026-10-17):** Weights unified to float (2.0, not 2) for consistency

---

## ⚠️ Gotchas (Do NOT Repeat)

- Dataset is **ordered by priority blocks** → must shuffle before split
- Test conftest.py clears queue auto — don't manually clear in tests
- Frontend never hardcodes roles — fetch from /api/roles
- def endpoints run in thread pool, not async → model inference OK
- Category leak means model may learn solicitud/operativo instead of severity

---

## 🔗 Critical Files (Change = Update This File)

- ackend/core/triage_rules.py — keyword lists, weights
- ackend/api/schemas.py — Enum definitions
- ackend/core/queue_store.py — locking strategy
- plan-entregas.md — roadmap status
- valuation/sample_tickets.json — dataset changes

**Rule:** Before pushing, scan CLAUDE.md + plan-entregas.md + MEMORY.md for consistency.
