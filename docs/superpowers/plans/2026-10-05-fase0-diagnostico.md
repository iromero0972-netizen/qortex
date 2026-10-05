# QORTEX · Fase 0: diagnóstico — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correr el conector contra NetSuite real (solo lectura), entregar el reporte de calidad de datos y mostrar el dashboard con datos reales a Víctor.

**Architecture:** El conector es el único módulo que habla con NetSuite y solo usa SuiteQL y GET. Los agentes son funciones puras probadas con datos sintéticos. La salida es un JSON validado por esquema que carga un dashboard HTML estático.

**Tech Stack:** Python 3.11+, `requests` + `requests-oauthlib` (OAuth1 TBA HMAC-SHA256), pytest, `jsonschema`. HTML/JS sin build.

**Spec:** `docs/superpowers/specs/2026-10-05-qortex-design.md`

**DoD de la Fase 0 (Acta §6):** `qortex_data.json` real cargado, reporte de calidad entregado y Víctor lo revisó en sesión.

---

## ⚠️ Este plan no trae código de los activos existentes

El conector, el dashboard y las queries ya existen fuera del repo. **La tarea 1 los sube tal
cual**, y las siguientes los endurecen. No reescribas desde cero lo que ya funciona; compara contra
el archivo real antes de cambiar nada.

### Estado de ejecución

| Tarea | Estado | Commits |
|---|---|---|
| 1 · Importar activos tal cual | **bloqueada**: B1, faltan los archivos | |
| 2 · Candado de solo lectura | pendiente | |
| 3 · Queries SuiteQL como archivos | pendiente | |
| 4 · Esquema de `qortex_data.json` | pendiente | |
| 5 · Agentes como funciones puras + pruebas | pendiente | |
| 6 · Reporte de calidad de datos | pendiente | |
| 7 · Dashboard: validar al cargar + `noindex` | pendiente | |
| 8 · Corrida real y sesión con Víctor | **bloqueada**: B4 (rol y credenciales) | |

---

## Estructura de ficheros (objetivo)

| Fichero | Responsabilidad |
|---|---|
| `qortex_conector.py` | Único módulo que habla con NetSuite |
| `qortex/readonly.py` | Sesión HTTP que rechaza todo lo que no sea SuiteQL o GET |
| `qortex/agentes/{demanda,proveedores,riesgo,comprador,tesoreria}.py` | Funciones puras |
| `qortex/calidad.py` | Chequeos del reporte de calidad |
| `queries/*.sql` | Las 5 consultas SuiteQL |
| `schema/qortex_data.schema.json` | Contrato del JSON |
| `index.html` | Dashboard |
| `tests/` | pytest; `tests/fixtures/` solo con datos sintéticos |

---

## Task 1: Importar los activos tal cual

- [ ] Copiar al repo `index.html`, `qortex_conector.py` y las 5 queries, sin cambiarlos.
- [ ] `git grep -nE "(consumer|token)_(key|secret)\s*=\s*['\"][A-Za-z0-9]"` → sin salida.
- [ ] `git grep -nE "requests\.(put|patch|delete)|method=['\"](PUT|PATCH|DELETE)"` → anotar cada hallazgo; no se corrige aquí.
- [ ] Commit: `importar dashboard, conector y queries tal como estaban`.

**DoD:** los tres activos están versionados, idénticos al original, y sin secretos.

## Task 2: Candado de solo lectura

- [ ] Test primero (`tests/test_readonly.py`):
  - `GET https://<cuenta>.suitetalk.api.netsuite.com/services/rest/record/v1/item/1` → permitido.
  - `POST …/services/rest/query/v1/suiteql` → permitido.
  - `POST …/record/v1/purchaseOrder` → `ReadOnlyViolation`.
  - `PUT`, `PATCH` y `DELETE` a cualquier ruta → `ReadOnlyViolation`.
  - SuiteQL que no empieza por `SELECT` o `WITH` (tras quitar comentarios) → `ReadOnlyViolation`.
- [ ] Ver fallar. Implementar `qortex/readonly.py` (subclase de `requests.Session` que valida en `request()`).
- [ ] El conector usa solo esta sesión. Test: `grep` en CI de que el conector no importa `requests` directo.
- [ ] Ver pasar. Commit.

**DoD:** no hay forma de que el conector escriba en NetSuite sin que falle un test.

## Task 3: Queries SuiteQL como archivos

- [ ] Cada query en `queries/NN_nombre.sql`, con paginación (`limit`/`offset` de la API, máximo 1000 por página).
- [ ] Test: todas pasan el candado de la tarea 2 y llevan filtro de Location cuando aplica.
- [ ] Commit.

## Task 4: Esquema de `qortex_data.json`

- [ ] Escribir `schema/qortex_data.schema.json` a partir de lo que el dashboard ya consume.
- [ ] `tests/fixtures/qortex_data.ejemplo.json` sintético (10 SKUs, 2 proveedores) que cumple el esquema.
- [ ] Test: el ejemplo valida; sin `skus` falla; con `origen` distinto de `supuesto`/`confirmado` falla.
- [ ] Commit.

## Task 5: Agentes como funciones puras

Una sub-tarea por agente, siempre test primero, con valores calculados a mano:

- [ ] **Comprador:** EOQ con D=1200, S=50 y H=2 da 244,9; redondeo a múltiplo 12 da 252; el tope de vida útil recorta.
- [ ] **Riesgo:** SS y ROP con d=100/mes, σd=20, LT=2 meses, σLT=0,5 y z=1,645; semáforo en los tres bordes.
- [ ] **Proveedores:** lead time medio y desviación; descarta recepciones anteriores a la OC y las reporta.
- [ ] **Demanda:** Holt-Winters con serie sintética estacional; con menos de 24 meses cae al plan B y lo marca.
- [ ] **Tesorería:** costo puesto en almacén con cada componente; calendario 30% anticipo / 70% contra BL.
- [ ] Commit por agente.

**DoD:** `pytest` en verde; ninguna función de `qortex/agentes/` importa `requests` ni abre archivos.

## Task 6: Reporte de calidad de datos

- [ ] Un chequeo por cada fila del spec §6, con test sobre fixtures sintéticas que traen el defecto.
- [ ] Salida en `reporte_calidad.txt`: resumen arriba y los 10 peores casos por chequeo.
- [ ] Commit.

## Task 7: Dashboard

- [ ] Al cargar el JSON, validarlo contra el esquema y mostrar el campo que falla.
- [ ] `<meta name="robots" content="noindex, nofollow">`.
- [ ] Los supuestos se pintan distinto de los datos confirmados.
- [ ] Probar en navegador con el JSON de ejemplo y con uno inválido.
- [ ] Commit.

## Task 8: Corrida real y sesión con Víctor

Requiere B4 (rol de solo lectura y credenciales en 1Password).

- [ ] `op run --env-file=.env.example -- python3 qortex_conector.py` → `supuestos_proveedores.json`.
- [ ] Quamtex completa los supuestos.
- [ ] Segunda corrida → `qortex_data.json` + `reporte_calidad.txt`. Validar contra el esquema.
- [ ] `git status` → ningún archivo de datos aparece como para versionar.
- [ ] Sesión con Víctor: dashboard + reporte. Anotar la fecha en `SEGUIMIENTO.md`.

**DoD:** el de la Fase 0, arriba. Evidencia en `SEGUIMIENTO.md`: fecha de la sesión, número de SKUs
cargados, conteo de defectos por chequeo. Sin datos del cliente en el repo.

## Al terminar

- Actualizar `docs/PROJECT_STATE.md`.
- Brainstorming del Quick Win (OC real para el proveedor con más faltantes) → spec → plan.
