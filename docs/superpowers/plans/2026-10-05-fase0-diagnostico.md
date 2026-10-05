---
tipo: plan
id: PLAN-FASE0
estado: APROBADO
version: 2.0
fecha: 2026-10-05
---

# QORTEX · Fase 0: diagnóstico — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cobrar la Fase 0, correr el conector contra NetSuite real en solo lectura, entregar el reporte de calidad con las líneas base del acta y mostrar el dashboard con datos reales a Víctor.

**Architecture:** Python extrae, prepara, mide la calidad y valida; el motor de políticas vive solo en `dashboard/motor.js` y recibe `qortex_data.json` como entrada validada (ADR-002). Todo lo que toca NetSuite pasa por el candado de lista blanca (ADR-004). Se publica solo un HTML de demo de un archivo (ADR-005).

**Tech Stack:** Python 3.12 con uv (`requests`, `requests-oauthlib`, `jsonschema`; dev `pytest`, `ruff`, `pre-commit`). Node ≥ 20 para `node --test`, el golden y generar el validador con Ajv (solo en desarrollo). Chart.js 4.4.1 vendorizado.

**Arquitectura:** `docs/ARQUITECTURA.md` (contrato §5, fórmulas §6, estructura §8, seguridad §10).

**DoD de la Fase 0** (acta, «Fases y precio»): `qortex_data.json` real cargado, reporte de calidad entregado y revisado con Víctor en sesión, con su confirmación escrita.

**Precio:** $2,500, 100 % por adelantado (decisión 4). **Horas estimadas:** 70,5 h (supuesto).

**v2 (5-oct-2026):** sustituye a la v1 tras la revisión de arquitectura (`docs/REVISION-2026-10-05.md`). Sale «los 5 agentes en Python»; entran la preparación en Python, las líneas base y los 9 arreglos del motor.

---

## ⚠️ Los bloques de código de este plan CADUCAN

Cuando una tarea se implementa y pasa revisión, la fuente de verdad es el repositorio, no este
fichero. El conector y las queries ya existen fuera del repo: la T1 los sube tal cual y no se
reescribe desde cero lo que ya funciona.

## Estado de ejecución

| Tarea | Horas | Depende de | Estado |
|---|---|---|---|
| T0 · Puerta comercial: precio, propuesta, reunión, cobro | — | — | pendiente (SEGUIMIENTO) |
| T0b · Correo de arranque al admin y a Compras | 1,5 | — | redactado (`docs/comercial/T0b-correo-arranque.md`); se envía tras el «sí» de Víctor |
| T0c · Demo publicada y protegida para la reunión | 1 | — | `demo/` lista y probada (Chart.js incrustado, noindex); falta `scripts/publicar_demo.sh` desde la terminal de Ignacio + contraseña |
| T1 · Importar conector y queries tal cual | 1 | B1 | parcial: dashboard en `e623751` |
| T1b · Andamiaje: `dashboard/`, src layout, Makefile, CI, guard | 4 | cobro | pendiente |
| T1c · ADR-002 a 005 y documentos alineados | 3 | decisiones | **hecha** (este commit) |
| T2 · Candado de lista blanca | 4 | T1, T1b | pendiente |
| T3 · Seis consultas, descubrimiento de esquema y sondas | 6 | T1, T2 | pendiente |
| T4 · Esquema, contrato R1–R6 y validador Ajv | 6,5 | T1b | pendiente |
| T5 · Preparación en Python | 9 | T3, T4 | pendiente |
| T6 · Calidad y líneas base | 11,5 | T5 | pendiente |
| T7 · `motor.js`: 9 arreglos, validación, IA apagada, XSS | 13 | T1b, T4 | pendiente |
| T8 · Build de un archivo y publicación | 2 | T7 | pendiente |
| T9 · Corridas reales 1 y 2 | 4 | B4, cobro, T5, T6 | pendiente |
| T10 · Sesión con Víctor y confirmación escrita | 4 | T8, T9 | pendiente |

**Antes del cobro solo se hacen T0b y T0c** (decisión 3; `CLAUDE.md`, «Prioridad comercial»). Si la
firma llega y B4 tarda, T1b, T4, T7 y T8 llenan la espera: no dependen de NetSuite.

---

## T0 · Puerta comercial

Precio ($2,500), propuesta, reunión a solas con Víctor y cobro se siguen en `SEGUIMIENTO.md`. La
propuesta incluye la cláusula de propiedad (decisión 10): KATIA conserva el código y Quamtex recibe
una licencia de uso perpetua. **T9 no arranca sin cobro.**

## T0b · Correo de arranque (1,5 h)

- [ ] Al admin de NetSuite: la lista exacta de permisos de ARQUITECTURA §10.1 (incluidos Setup ›
      Records Catalog y, si aplica, Inbound Shipment), usuario dedicado, token TBA y concurrencia.
- [ ] A Compras: plantilla de supuestos (Incoterm, moneda, tránsito, términos, flete, arancel,
      peso, peligrosos), formato del conteo físico (`salidas/conteo_fisico.csv`) y una cita de
      15 min para medir cuánto tardan en armar una OC.
- [ ] Preguntas: ¿Landed Cost?, ¿Inbound Shipments?, ¿cuántos meses de historia?, ¿campos custom
      de vida útil, país y peso?, ¿una o varias Locations?, ¿OneWorld o multimoneda?
- [ ] Fechas compromiso para B4, B5 y B6.

**DoD:** correo enviado; fecha compromiso de cada bloqueo anotada en `SEGUIMIENTO.md`.

## T0c · Demo para la reunión (1 h)

- [ ] Carpeta con solo `index.html` (datos demo), meta robots y `vercel.json` con `X-Robots-Tag`.
- [ ] Vercel Pro con Password Protection; `vercel deploy --prod` desde la terminal de Ignacio.
- [ ] Prueba en incógnito: pide contraseña y no aparece en buscadores.

**DoD:** URL protegida que abre en el teléfono. Cierra B7 para la demo; T8 la sustituye por `build/`.

## T1 · Importar conector y queries (1 h)

- [ ] Copiar `qortex_conector.py` y las 5 queries sin cambiarlos.
- [ ] `git grep -nE "(consumer|token)_(key|secret)\s*=\s*['\"][A-Za-z0-9]"` → sin salida.
- [ ] Anotar cada verbo distinto de GET/SuiteQL que aparezca; se corrige en T2.

**DoD:** activos versionados, idénticos al original y sin secretos.

## T1b · Andamiaje (4 h)

- [ ] `index.html` → `dashboard/index.html`; separar `motor.js` y `demo.js` sin cambiar la lógica;
      golden «antes» con `node scripts/golden.mjs`. `demo.js` con meses fijos (hoy un huso UTC+
      corre los meses, verificado con node).
- [ ] `uv init --package`, `requires-python >= 3.12`, src layout `src/qortex/`, `uv.lock`.
- [ ] `Makefile` con `setup`, `lint`, `test`, `guard`, `ci` y los objetivos de las etapas.
- [ ] CI con `make ci`: falla si no hay pruebas; corre pytest y `node --test`.
- [ ] `.gitignore` y `scripts/guard_datos.sh` ampliados (ARQUITECTURA §10.4); pre-commit con gitleaks y guard.

**DoD:** `make ci` en verde en local y en GitHub; el golden «antes» coincide con el motor de hoy.

## T1c · ADR y documentos (3 h) — hecha

ADR-002 a ADR-005; `CLAUDE.md` (reglas 3, 4 y 6); acta, `.env.example`, `DECISION_LOG`,
`PROJECT_STATE`, `SEGUIMIENTO`, índice de ADR, spec v2 y este plan v2, en un solo commit.

## T2 · Candado (4 h)

Según ADR-004. Pruebas primero:
- [ ] `GET …/services/rest/record/v1/item/1` y `GET …/record/v1/metadata-catalog` → permitidos.
- [ ] `POST …/services/rest/query/v1/suiteql` → permitido; `POST …/record/v1/purchaseOrder` → `ReadOnlyViolation`.
- [ ] `PUT`, `PATCH`, `DELETE` a cualquier ruta, `http://`, otro host y RESTlets → `ReadOnlyViolation`.
- [ ] Una redirección no se sigue; timeout aplicado; 429 con `Retry-After` reintenta; 4.º fallo, error.
- [ ] SuiteQL que no empieza por `SELECT`/`WITH` → `ReadOnlyViolation`.
- [ ] Solo `readonly.py` importa `requests`; los logs no contienen `Authorization` ni filas.

**DoD:** no hay forma de que el conector escriba en NetSuite sin que falle una prueba.

## T3 · Consultas (6 h)

- [ ] Descubrimiento de esquema: `GET metadata-catalog` y una sonda `ROWNUM <= 1` por tabla; un 403 nombra la tabla.
- [ ] Seis consultas en `src/qortex/queries/`: 1 inventario por Location (`quantityonhand`,
      `quantitycommitted`, `quantitybackordered`, `quantityonorder`, `averagecostmli`, `item.weight`);
      2 ventas a nivel línea con notas de crédito, **toda la historia disponible hasta 60 meses**
      (decisión 7), troceada por año; 3 OC con `expectedreceiptdate`, `exchangerate` e `incoterm`;
      4 recepciones enlazadas a su línea de OC; 5 proveedores con moneda, términos, incoterm e
      `itemvendor`; 6 pedidos de venta (demanda no servida).
- [ ] Paginación `limit` 1000; respuestas grabadas **sintéticas** para las pruebas.

**DoD:** pruebas de paginación, troceo y 401/403/429 en verde; tabla campo → columna en `queries/README.md`.

## T4 · Contrato (6,5 h)

- [ ] `schema/qortex_data.schema.json` según ARQUITECTURA §5.
- [ ] `contrato.py` y `validarCruzadas()` con R1–R6; vectores compartidos en `tests/contract/`.
- [ ] `scripts/compilar_validador.mjs` → `dashboard/validar_esquema.js`; CI falla si contiene `require(`.
- [ ] Fixture sintética de 10 SKUs × 2 proveedores.
- [ ] Prueba de `procedencia`: falla un valor fuera de `netsuite|calculado|supuesto|confirmado` y falla un supuesto sin entrada.

**DoD:** los mismos vectores pasan en pytest y en node.

## T5 · Preparación en Python (9 h)

- [ ] Lead time medio, σ y `lt_n` por proveedor; valor por origen marcado supuesto si `lt_n` < 5.
- [ ] Series mensuales netas; precio realizado; `costo_promedio`.
- [ ] Regla única de ETA (ARQUITECTURA §5, 4 casos) y conversión a USD con `tipo_cambio`.
- [ ] `salidas/supuestos.json` con valores por origen y presentación, todos `supuesto`. Arancel de
      China por defecto **28,5 %** (25 % + MFN, decisión 9).
- [ ] Clientes sin nombre; SKUs sin proveedor o sin supuestos fuera del JSON y al reporte.
- [ ] `calidad.metodo` y clase de demanda (ADI/CV²).
- [ ] Escribe `salidas/qortex_data.json` solo si valida.

**DoD:** pruebas de ETA, USD y lead time en verde; ningún hueco rellenado con 0.

## T6 · Calidad y líneas base (11,5 h)

- [ ] Los 7 chequeos del spec §6, con un test sobre fixtures sintéticas que traen el defecto.
- [ ] Líneas base del acta: exactitud contra `salidas/conteo_fisico.csv`, lista de SKUs A para
      recontar, nivel de servicio en A, faltantes A/B por mes, tiempo para armar una OC (dato
      declarado en la cita de T0b).
- [ ] Perfil ADI/CV², ETA estimadas y vencidas, `quantityonorder` frente a líneas abiertas, % de supuestos confirmados.

**DoD:** `salidas/reporte_calidad.txt` con resumen arriba y los 10 peores casos por chequeo.

## T7 · Motor (13 h)

- [ ] `fecha_corte` en lugar de `HOY`; etiquetas desde `meses`; sin mutar la entrada; `parametros`.
- [ ] Niveles de servicio A 98 % (A-Z 97 %), B 95 %, C 90 %, piso 97 % «sensible» (decisión 5).
- [ ] SS sobre LT + R; tope de vida útil efectivo con sus razones; proyección diaria con `en_transito` y crítico por t_q.
- [ ] Simulador por `pais`; sin OC con confianza baja; «sin venta» por ventas de 12 meses.
- [ ] Pagos al embarque; costo puesto según Incoterm; inventario a `costo_promedio`.
- [ ] Clientes con id y segmento; `procedencia` pintada; validación al cargar.
- [ ] IA apagada con datos reales (ADR-003) y `esc()` en todo campo, con pruebas.
- [ ] `node --test`, también con `TZ=Europe/Madrid`; golden actualizado y revisado.

**DoD:** pruebas en verde; el caso sintético RF-132 (10 días en almacén, 90 en tránsito) sale crítico.

## T8 · Build y publicación (2 h)

- [ ] `make dashboard` → `build/qortex.html` de un archivo con Chart.js vendorizado y SHA-256 comprobado.
- [ ] `make publicar` aborta si fallan el guard o la comprobación de `build/`; prueba en incógnito.

**DoD:** la URL protegida sirve el build nuevo, solo con datos demo.

## T9 · Corridas reales (4 h)

Requiere B4 y cobro.
- [ ] `make extraer` → snapshot y `salidas/supuestos.json`.
- [ ] Compras confirma los supuestos que pueda.
- [ ] `make datos` y `make calidad`; `git status` limpio.

## T10 · Sesión con Víctor (4 h)

- [ ] Dashboard con datos reales en local y reporte de calidad.
- [ ] Correo de cierre con su confirmación escrita y la lista de correcciones acordadas.

**DoD:** el de la Fase 0. Evidencia en `SEGUIMIENTO.md`: fecha, SKUs cargados, defectos por chequeo, % de supuestos confirmados. Sin datos del cliente en el repo.

## Al terminar

- Actualizar `docs/PROJECT_STATE.md`, la bitácora de `SEGUIMIENTO.md` y `docs/ARQUITECTURA.md` si cambió el contrato o el modelo.
- Brainstorming del Quick Win (OC real para el proveedor con más faltantes) → spec → plan.
