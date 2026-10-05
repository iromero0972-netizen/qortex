# QORTEX — reglas para Claude

Reabastecimiento con IA sobre NetSuite para Quamtex (distribuidor de WEG Paints, Houston).
Proveedor: KATIA.AI. Responsable: Ignacio Romero (CPA).

**Idioma:** español. Términos técnicos en inglés cuando aplique (SKU, lead time, EOQ, ROP).

## Antes de tocar nada, lee

1. `docs/PROJECT_STATE.md`: el estado vigente. Si el chat lo contradice, gana el archivo.
2. `docs/superpowers/specs/2026-10-05-qortex-design.md`: el diseño.
3. El plan activo en `docs/superpowers/plans/`, en su tabla «Estado de ejecución».

## Reglas que no se negocian

1. **QORTEX no escribe en NetSuite.** Solo lee: SuiteQL (`POST /services/rest/query/v1/suiteql`)
   y `GET` de REST. Cualquier otro verbo HTTP hacia NetSuite es un defecto, aunque un humano lo
   pida en el chat. Escribir exige un ADR nuevo y la firma de Víctor y Edgar (ADR-001).
2. **Ninguna credencial en el código, en los commits ni en el chat.** Solo referencias `op://`
   en `.env.example`. Se ejecuta con `op run --env-file=.env.example -- …`.
3. **Ningún dato del cliente en git.** `qortex_data.json`, `reporte_calidad.txt`,
   `supuestos_proveedores.json`, CSV y XLSX están en `.gitignore`. Si un test necesita datos,
   usa datos sintéticos en `tests/fixtures/`.
4. **Un supuesto nunca se presenta como dato.** Todo valor que no salga de NetSuite (arancel,
   flete, término de pago) lleva la marca `"origen": "supuesto"` hasta que Quamtex lo confirme.
5. **Una persona aprueba cada orden de compra.** QORTEX recomienda y explica (botón «¿Por qué?»);
   no decide.

## Cómo se trabaja (flujo Superpowers)

| Paso | Skill | Sale |
|---|---|---|
| Idea o cambio de alcance | `superpowers:brainstorming` | spec en `docs/superpowers/specs/AAAA-MM-DD-<tema>-design.md` |
| Spec aprobado | `superpowers:writing-plans` | plan en `docs/superpowers/plans/AAAA-MM-DD-<tema>.md` |
| Ejecutar el plan | `superpowers:subagent-driven-development` | commits por tarea, con revisión |
| Antes de decir «listo» | `superpowers:verification-before-completion` | evidencia (comando + salida) |

- Una decisión que un tercero no deduciría del código va a un ADR (`docs/adrs/`, ver su índice).
  Las menores, a `docs/DECISION_LOG.md`.
- Los ADR no se reescriben: si la decisión cambia, se escribe uno nuevo que supersede al anterior.
- Al cerrar la jornada se actualizan `docs/PROJECT_STATE.md` y `SEGUIMIENTO.md`.

## Prioridad comercial

El objetivo de las próximas 2 semanas es **cobrar la Fase 0**. Lo que acerque la demo con Víctor
va primero; el perfeccionismo técnico, después.
