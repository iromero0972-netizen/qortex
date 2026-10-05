---
tipo: registro
id: PROJECT-STATE
estado: VIGENTE
version: 1.0
fecha: 2026-10-05
---

# PROJECT STATE — QORTEX

> **Si una conversación contradice este archivo, gana este archivo.**
> Se actualiza al cerrar cada jornada. Secciones fijas; lo cronológico va a `SEGUIMIENTO.md`.

**Última actualización:** 5 de octubre de 2026
**Remoto:** `https://github.com/iromero0972-netizen/qortex` (privado)
**Fase:** pre-venta. Prototipo listo; falta la reunión con Víctor y la firma de la Fase 0.

## 1. Qué es esto

Sistema de reabastecimiento sobre NetSuite que recomienda **qué, cuánto y cuándo comprar**, con
costo puesto en almacén y calendario de salida de dinero. Detalle en el spec
(`docs/superpowers/specs/2026-10-05-qortex-design.md`).

## 2. Reglas que no se negocian

Ver `CLAUDE.md` § «Reglas que no se negocian». La primera: **QORTEX no escribe en NetSuite.**

## 3. Qué existe

| Activo | Estado | Dónde |
|---|---|---|
| Acta del proyecto | Vigente | `README.md` |
| Spec de diseño | Propuesto, pendiente de revisión | `docs/superpowers/specs/` |
| Plan Fase 0 | Propuesto, bloqueado en la tarea 1 | `docs/superpowers/plans/` |
| Dashboard v0.1 (6 pestañas + simulador) | Probado con datos demo | **fuera del repo**, falta subirlo |
| Conector NetSuite (solo lectura, OAuth1 TBA) | Probado con respuestas simuladas | **fuera del repo**, falta subirlo |
| 5 queries SuiteQL | Escritas | **fuera del repo**, en un transcript |
| Deck general (12 láminas) y deck Víctor (13) | Listos; faltan precios y placeholders | Artifacts de claude.ai |
| Guion de 45 min + 5 objeciones + correo de seguimiento | Listo | Transcript |

## 4. Bloqueos

| # | Qué | De quién | Desbloquea |
|---|---|---|---|
| B1 | Subir dashboard, conector y queries al repo | Ignacio | Plan Fase 0, tarea 1 |
| B2 | Precios confirmados (Fase 0, Fase 1, retainer) | Ignacio | Decks y propuesta |
| B3 | Reunión a solas con Víctor | Víctor | Todo lo comercial |
| B4 | Rol NetSuite exclusivo de solo lectura + 6 credenciales en 1Password | Víctor / admin NetSuite | Primera corrida real |
| B5 | Origen, términos, arancel y flete por proveedor | Compras Quamtex | Costo puesto en almacén |
| B6 | ¿Hay Landed Cost en NetSuite? | Admin NetSuite | Saber si el costo sale real o con supuestos |
| B7 | Vercel: «No approval received» | Ignacio | Publicar el dashboard |

## 5. Siguiente paso

1. Cerrar B1 y B2 hoy.
2. WhatsApp a Víctor (script en `SEGUIMIENTO.md`).
3. Con B4: ejecutar el plan Fase 0 desde la tarea 2.
