---
tipo: registro
id: QORTEX-SEGUIMIENTO
estado: VIGENTE
version: 1.0
fecha: 2026-10-05
---

# QORTEX — Seguimiento

## Tablero comercial (actualizar cada día)

| Fecha | Contactos Víctor/Edgar | Reuniones agendadas | Demos | Propuestas Fase 0 | Cierres (Fase 0 pagada) |
|---|---|---|---|---|---|
| Meta | 2 | 1 | 1 | 1 | 1 |
| 2026-10-05 | 0 | 0 | 0 | 0 | 0 |

## Pendientes

- [ ] Publicar el dashboard en Vercel (`qortex-quamtex`) y validarlo en incógnito
- [x] Precio de la Fase 0: $2,500 (5-oct)
- [ ] Confirmar los precios de la Fase 1 y el retainer
- [ ] Llenar los placeholders `[$__]` y `[__]` de ambos decks
- [ ] Agendar la reunión a solas con Víctor (45 min)
- [ ] Conseguir una línea escrita de Víctor que autorice el frente de compras
- [x] Subir el dashboard (`e623751`)
- [ ] Subir el conector y las 5 queries SuiteQL (B1)
- [ ] Guardar las 6 credenciales de NetSuite en 1Password (`Quamtex-REA`)
- [ ] Correr el conector contra NetSuite real (2 corridas)
- [ ] Confirmar si existe Landed Cost en NetSuite
- [ ] Recibir términos, aranceles y flete por proveedor
- [ ] Preparar con Víctor la presentación a Edgar

## Script WhatsApp para Víctor

> Víctor, buenas. Terminé algo que quiero mostrarte antes que a nadie: un sistema que le dice a
> Quamtex qué comprar, cuánto y cuándo, con el costo real puesto en Houston. Son 45 minutos, tú y
> yo. ¿Te queda bien el [día] a las [hora] o el [día] a las [hora]?

## Bitácora

| Fecha | Qué pasó | Evidencia |
|---|---|---|
| 2026-10-05 | Se abre el expediente en repositorio propio: acta, `.gitignore`, `.env.example` y ADR-001 | commit inicial |
| 2026-10-05 | Kit de proyecto: CLAUDE.md, PROJECT_STATE, DECISION_LOG, índice de ADR, spec, plan Fase 0 y CI | segundo commit |
| 2026-10-05 | Dashboard importado del artifact; decisión: IA solo con datos demo | `e623751`, `ba46970` |
| 2026-10-05 | Revisión multiagente: 64 proyectos comprobados, 48 hallazgos; arquitectura propuesta | `docs/ARQUITECTURA.md`, `docs/REVISION-2026-10-05.md` |
| 2026-10-05 | Ignacio acepta las 10 decisiones; ADR-002 a ADR-005, spec v2 y plan v2 | este commit |
