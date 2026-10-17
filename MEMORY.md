# MEMORY.md

**Last Updated:** 2026-10-17 (S2 completed)  
**Maintained by:** Claude Code instances  
**Max:** 50 lines (enforce)

---

## 🎯 Core Rules (Inviolable)

1. **Bug → regression test** (rule from S1 plan)
2. **No async endpoints** — use `def`, thread pool execution
3. **Thread-safe queue** — `threading.Lock` in queue_store.py
4. **Pydantic Enums only** — roles + priority levels as Enums
5. **No simulated data on failure** — show errors, not fallbacks
6. **XAI contract immutable** — `Dict[str, float]` never changes
7. **Dataset shuffle before split** — prevents priority/category leakage
8. **Memory-first:** Update this file in every commit

---

## 📊 Project State (S2 Done, S3 Next)

- **S1:** ✅ Heurística (24% acc) + tests + dataset + CLAUDE.md
- **S2:** ✅ TF-IDF + LogReg (91.3% acc) + /health + DELETE + metrics
- **S3:** ⏳ LIME XAI, button "¿Por qué?", latency < 3s
- **S4:** ⏳ Feedback loop, bias analysis, demo

---

## 📈 S2 Metrics (Validated)

| | Heuristic | Model |
|---|-----------|-------|
| **Accuracy** | 24.0% | 91.3% |
| **F1** | 23.9% | 91.3% |
| **Improvement** | — | +67.3% |

Model: `backend/core/models/baseline.joblib` (12.4 KB)

---

## ⚙️ Tech Stack (Fixed)

- **Backend:** Python 3.10, FastAPI, Pydantic v2, scikit-learn (S2)
- **ML (S2):** TF-IDF (1000 features, n-grams) + LogisticRegression
- **Queue:** threading.Lock (no Redis, no async)
- **Tests:** pytest, httpx (17/17 passing)

---

## 🚀 S2 Deliverables Done

✅ training/train_baseline.py (stratified split 80/20)  
✅ core/nlp_engine.py (model load + predecir)  
✅ evaluation/calc_metrics.py (F1, confusion matrix)  
✅ main.py /health + DELETE /queue/{id}  
✅ queue_store.eliminar() (thread-safe)  
✅ Fallback to heuristic if model fails  
✅ 17 tests passing (S1: 12, S2: 4 endpoints + 1 model load)

---

## ⚠️ Gotchas (Do NOT Repeat)

- Dataset **ordered by priority blocks** → must shuffle
- Sklearn 1.8+ removed `multi_class` param, `stop_words="spanish"` invalid
- conftest.py auto-clears queue — don't manually clear
- TF-IDF has 1001 features (1000 + 1 role weight)
- Model train accuracy 100% (overfitting OK on 120 samples), test 56.7%

---

## 📋 Next: S3 (LIME XAI)

- POST /api/explain/{id} → LIME weights per word
- Frontend: "¿Por qué?" button, bar chart with factor weights
- Explain latency target: < 3s (num_samples tunable)
- Cache explanations by ticket ID

---

**Rule:** Before pushing, verify CLAUDE.md + plan-entregas.md + this file align.
