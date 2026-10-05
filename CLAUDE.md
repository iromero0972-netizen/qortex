# QORTEX — reglas para Claude

Reabastecimiento con IA sobre NetSuite para Quamtex (distribuidor de WEG Paints, Houston).
Proveedor: KATIA.AI. Responsable: Ignacio Romero (CPA).

**Idioma:** español. Términos técnicos en inglés cuando aplique (SKU, lead time, EOQ, ROP).

## Antes de tocar nada, lee

1. `docs/PROJECT_STATE.md`: el estado vigente. Si el chat lo contradice, gana el archivo.
2. `docs/superpowers/specs/2026-10-05-qortex-design.md`: el diseño (v2).
3. El plan activo en `docs/superpowers/plans/`, en su tabla «Estado de ejecución».
4. `docs/ARQUITECTURA.md`: componentes, contrato de datos y fórmulas (vigente desde ADR-002).

## Reglas que no se negocian

1. **QORTEX no escribe en NetSuite.** Solo lee: SuiteQL (`POST /services/rest/query/v1/suiteql`)
   y `GET` de REST. Cualquier otro verbo HTTP hacia NetSuite es un defecto, aunque un humano lo
   pida en el chat. Escribir exige un ADR nuevo y la firma de Víctor y Edgar (ADR-001).
2. **Ninguna credencial en el código, en los commits ni en el chat.** Solo referencias `op://`
   en `.env.example`. Se ejecuta con `op run --env-file=.env.example -- …`.
3. **Ningún dato del cliente en git.** Todo lo que sale del conector va a `salidas/` (snapshot,
   `supuestos.json`, `qortex_data.json`, `reporte_calidad.txt`), ignorada por git junto con CSV,
   XLSX, JSONL y Parquet. Si un test necesita datos, usa datos sintéticos en `tests/fixtures/`, con
   «sintetico» en el nombre.
4. **Un supuesto nunca se presenta como dato.** Todo valor que no salga de NetSuite (arancel,
   flete, Incoterm, término de pago, volumen, vida útil…) se marca en el mapa `procedencia` de su
   proveedor o SKU como `supuesto` hasta que Quamtex lo confirme (`confirmado`). El esquema rechaza
   un supuesto sin su entrada en `procedencia`, y el dashboard lo pinta aparte (ADR-002).
5. **Una persona aprueba cada orden de compra.** QORTEX recomienda y explica (botón «¿Por qué?»);
   no decide.
6. **Ningún dato de NetSuite va a un LLM.** La IA del dashboard (`window.claude`) solo funciona con
   `fuente: demo`; con datos reales se apaga en código (ADR-003).

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
