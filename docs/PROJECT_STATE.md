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
| Spec de diseño | **Aprobado, v2** | `docs/superpowers/specs/` |
| Plan Fase 0 | **Aprobado, v2**: T0–T10, ~70,5 h (supuesto). T1c hecha; T1 parcial | `docs/superpowers/plans/` |
| Arquitectura e ingeniería | **Aprobada** (ADR-002 a ADR-005) | `docs/ARQUITECTURA.md` |
| Referencias comprobadas (64 proyectos, 8 ángulos) | Vigente | `docs/REFERENCIAS.md` |
| Revisión del 5-oct (48 hallazgos, cambios propuestos al spec y al plan) | Vigente | `docs/REVISION-2026-10-05.md` |
| Dashboard v0.1 (6 pestañas + simulador) | Probado con datos demo. Necesita los 9 arreglos de la T7 antes de mostrar datos reales | `index.html`, importado del artifact el 5-oct |
| Conector NetSuite (solo lectura, OAuth1 TBA) | Probado con respuestas simuladas | **fuera del repo**, falta subirlo |
| 5 queries SuiteQL | Escritas; el plan las amplía a 6 (T3) | **fuera del repo**, en un transcript |
| Deck general (12 láminas) y deck Víctor (13) | Listos; faltan precios y placeholders | Artifacts de claude.ai |
| Guion de 45 min + 5 objeciones + correo de seguimiento | Listo | Transcript |

## 4. Bloqueos

| # | Qué | De quién | Desbloquea |
|---|---|---|---|
| B1 | Subir conector y queries al repo (el dashboard ya está) | Ignacio | Plan Fase 0, tarea 1 |
| B2 | Precios confirmados (Fase 0, Fase 1, retainer) | Ignacio | Decks y propuesta |
| B3 | Reunión a solas con Víctor | Víctor | Todo lo comercial |
| B4 | Rol NetSuite exclusivo de solo lectura + 6 credenciales en 1Password | Víctor / admin NetSuite | Primera corrida real |
| B5 | Confirmar origen, Incoterm, términos, arancel y flete por proveedor (ya no bloquea: hay supuestos por origen) | Compras Quamtex | Costo puesto confirmado |
| B6 | ¿Hay Landed Cost en NetSuite? | Admin NetSuite | Saber si el costo sale real o con supuestos |
| B7 | Vercel: «No approval received»; contratar Pro con contraseña (ADR-005) | Ignacio | Publicar la demo (T0c) |

## 5. Siguiente paso

Antes del cobro, solo esto (decisión 3):
1. **T0c:** demo publicada con contraseña para la reunión (cierra B7).
2. **T0b:** correo de arranque al admin de NetSuite y a Compras (permisos exactos, plantilla de supuestos, preguntas).
3. **T0:** WhatsApp a Víctor (script en `SEGUIMIENTO.md`), reunión, propuesta a $2,500 con la cláusula de propiedad, cobro.

Tras el cobro: T1 (con B1), T1b, T4, T7 y T8 en paralelo a la espera de B4.
