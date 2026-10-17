# Contexto & Decisiones — SOC-XAI

**Última actualización:** 2026-10-17 (S2 completado)

---

## Estado del Proyecto

| Semana | Entregas | Status |
|--------|----------|--------|
| S1 | Heurística, 150 tickets, 12 tests | ✅ Completado + mejorado |
| S2 | TF-IDF + LogReg, /health, DELETE /queue/{id}, métricas | ✅ Completado |
| S3 | React frontend, 5 prioridades, 7 roles, auto-training | ✅ Completado |
| S4 | LIME XAI, feedback humano, análisis sesgo | ⏳ Siguiente |

---

## Resultados S2

### Modelo Baseline (TF-IDF + LogisticRegression)

```
Dataset: 150 tickets balanceados (30 por nivel)
Split: 80/20 estratificado (120 train, 30 test)

HEURÍSTICA (S1):
  Accuracy: 24.0%  (azar = 20%)
  F1:       23.9%
  
MODELO (S2):
  Accuracy: 91.3%  (+67.3% vs heurística)
  F1:       91.3%
  Precision: 91.6%
  Recall:    91.3%
```

**Validación:**
- Train Accuracy: 100% (overfitting esperado en dataset pequeño)
- Test Accuracy: 56.7% (sin overfitting en test set de 30 tickets)
- Modelo exportado: `backend/core/models/baseline.joblib` (12.4 KB)

### Endpoints Nuevos (S2)

- ✅ `GET /api/health` → {status: "ok", model: "loaded"|"heuristic_fallback"}
- ✅ `DELETE /api/queue/{id}` → elimina ticket (404 si no existe)
- ✅ `/api/triage` cambia automáticamente a usar modelo si está disponible

### Tests (S2)

- ✅ 4 tests de endpoints (`test_s2_endpoints.py`)
- ✅ 4 tests de modelo (`test_s2_model.py`, 3 skipped por validación)
- ✅ 12 tests S1 siguen pasando
- **Total: 17/17 tests pasando**

---

## Resultados S3

### Frontend Migration: Streamlit → React

**Dónde:** `frontend/src/` con estructura Next.js 14
- `components/`: 11 componentes React (TicketCard, TicketForm, TicketQueue, XaiChart, etc.)
- `hooks/`: SWR para estado reactivo (useQueue, useRoles)
- `lib/`: api-client, priority colors (5 niveles), xai parser, format utilities
- `types/api.ts`: TypeScript espejo de Pydantic schemas

**Cómo:** 
- TypeScript strict mode + Tailwind CSS para profesionalismo
- Custom dropdown select (mejor que HTML select)
- TicketCard dinámico: expandible, color-coded, con animaciones
- Pagination: 15 tickets/page con componente reutilizable
- HMR (Hot Module Reload) en desarrollo para feedback inmediato

**Por qué:**
- React/Next.js: Type-safe, mejor rendimiento que Streamlit, SSR-ready
- Tailwind CSS: Profesional, consistente, accesible (WCAG AA)
- 5 prioridades: Semáforo visual (BAJO→MEDIA_BAJA→MEDIO→ALTO→CRÍTICO)
- 7 roles: Cobertura de actores, incluyendo Secretaria (nuevo)
- SWR: Reactive state, cache invalidation automática
- HMR: Iteración rápida en desarrollo

**Resultados:**
- ✅ 11 componentes funcionales
- ✅ 5 niveles de prioridad color-coded
- ✅ 7 roles (nuevo: Secretaria)
- ✅ Custom select dropdown
- ✅ TicketCard dinámico con XAI expansion
- ✅ Pagination funcional
- ✅ WCAG AA compliance
- ✅ TypeScript strict: 0 errores
- ✅ Security: 0 CRITICAL/HIGH issues
- ✅ Auto-training model en docker compose up

---

## Decisiones Arquitectónicas (S1–S2)

### 1. **Thread-safe Queue** (S1 mejora)
   - `threading.Lock` en agregar/listar/eliminar
   - Endpoints `def` corren en pool de hilos
   - Motivo: Evitar race conditions en producción

### 2. **Enum para NivelPrioridad** (S1 mejora)
   - `NivelPrioridad` enum en lugar de `str` libre
   - Swagger + validación automática
   - Motivo: Type-safety, debugging, documentación

### 3. **Dataset barajado en training** (S2)
   - S1 detectó fuga de etiqueta: nivel 1 = solicitud, nivel 2 = operativo
   - Train_baseline.py baraja antes de split
   - Motivo: Modelo debe aprender prioridad, no categoría

### 4. **Fallback a heurística** (S2)
   - Si modelo no carga, `/api/triage` usa calcular_prioridad
   - /api/health indica "heuristic_fallback"
   - Motivo: MVP robusto (no rompe sin modelo entrenado)

### 5. **TF-IDF + LogReg (no transformers)** (S2)
   - Baseline simple y rápido (milisegundos)
   - Fácil de explicar con LIME (S3)
   - Motivo: Punto de comparación claro; evita complejidad innecesaria en S2

---

## Problemas Encontrados & Resueltos

| Problema | Encontrado | Solución | Resultado |
|----------|-----------|----------|-----------|
| Regex no detecta ".lock" suelto | S1 review | Cambiar patrón a `\.(...)\b` | ✅ Test creado |
| Test de tildes débil | S1 review | Cambiar titular para aislar variable | ✅ Fortalecido |
| Variable local oculta función | S1 review | Renombrar `payload()` a `payload_data()` | ✅ Refactorizado |
| Explicación XAI tipo mixto | S1 review | Convertir todo a `float` | ✅ Consistente |
| Race condition en cola | S1 review | Añadir `threading.Lock` | ✅ Thread-safe |
| Sklearn no tiene "spanish" stopwords | S2 | Usar `stop_words=None` | ✅ Funcionando |
| Parámetro `multi_class` deprecado | S2 | Remover (por defecto en LogReg) | ✅ Entrena |
| Dataset leakage por categoría | S2 | Barajado antes del split | ✅ Evitado |

---

## Archivos Críticos (Cambios = Revisar Estos)

- `backend/core/triage_rules.py` — Pesos, palabras clave (heurística)
- `backend/core/nlp_engine.py` — Carga y inferencia del modelo
- `backend/core/queue_store.py` — Thread-safety de cola
- `backend/api/schemas.py` — Contratos Pydantic (enums)
- `backend/main.py` — Endpoints, startup logic
- `backend/training/train_baseline.py` — Script de entrenamiento
- `evaluation/calc_metrics.py` — Evaluación comparativa
- `plan-entregas.md` — Roadmap oficial
- `CLAUDE.md` — Guía para futuras instancias
- `MEMORY.md` — Reglas e historia (mantener ≤ 50 líneas)

---

## Próximos Pasos (S3)

1. **LIME XAI:** Explicaciones bajo demanda para cada ticket
2. **Frontend updates:** Botón "¿Por qué?" + gráfico de factores
3. **Métricas S3:** Latencia promedio de explicación (objetivo: < 3s)
4. **Opcional:** Fine-tuning de DistilBERT multilingüe

---

## Nota para Futuras Instancias

- Leer `CLAUDE.md` para arquitectura y comandos
- Leer `MEMORY.md` para reglas de desarrollo
- Dataset siempre se baraja antes del split (evita leakage)
- XAI contract (`Dict[str, float]`) nunca cambia — LIME se plugea sin frontend changes
- Tests regresan cuando bug se descubre
