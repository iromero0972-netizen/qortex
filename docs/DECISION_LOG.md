---
tipo: registro
id: DECISION-LOG
estado: VIGENTE
version: 1.0
fecha: 2026-10-05
---

# DECISION LOG — QORTEX

Decisiones operativas y menores: las que no merecen un ADR (ver `docs/adrs/README.md`).

| Fecha | Decisión | Quién | Por qué |
|---|---|---|---|
| 2026-10-05 | Opción D (híbrido por fases) en lugar de NetSuite nativo, motor propio desde cero o SaaS tipo Netstock | Ignacio | Cobra un diagnóstico antes de construir y deja un Quick Win visible en 2–3 semanas |
| 2026-10-05 | Repositorio propio en vez de carpeta en `quamtex-ecosystem` | Ignacio | Expediente con aprobadores distintos; ver ADR-001 |
| 2026-10-05 | Flujo Superpowers (brainstorming → spec → plan → subagentes) | Ignacio | El mismo que se usó en el Gestor de Cobranza |
| 2026-10-05 | Python para conector y motor; HTML estático para el dashboard | Ignacio | Es lo que ya existe y funciona; sin servidor que mantener en la Fase 0 |
| 2026-10-05 | Rol NetSuite nuevo, no el del Tomador | Ignacio | Separa auditoría y permisos (Acta §9, alternativa B) |
| 2026-10-05 | «Pregúntele a QORTEX» (y «Explicar con IA») solo funcionan con datos de demostración; se desactivan en cuanto se carga un JSON real de NetSuite | Ignacio | La tarjeta manda costos, órdenes y pagos a un modelo externo: con datos de Quamtex eso saldría del cliente |
