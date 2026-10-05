---
tipo: adr
id: ADR-003
estado: aceptado
fecha: 2026-10-05
---

# ADR-003 · La IA del dashboard solo funciona con datos de demostración

**Fecha:** 5-oct-2026
**Estado:** aceptado por Ignacio (decisión del 5-oct en `docs/DECISION_LOG.md`; decisión 8 de `docs/REVISION-2026-10-05.md` §5)
**Implementa:** la decisión del registro; añade la regla 6 de `CLAUDE.md`

## Contexto

La tarjeta «Pregúntele a QORTEX» y el botón «Explicar con IA» usan `window.claude`, que solo
existe dentro de un artifact de claude.ai. Al cargar un JSON real, el manejador solo cambia la
fuente y `preguntarIA` solo comprueba que haya runtime: enviaría a un modelo externo hasta 30 SKUs
con costos, las OC con sus pagos y métricas de clientes (`seguridad-1`, `index.html:808-821`,
`:867-876`).

## Decisión

1. `iaPermitida()` = `fuente === 'demo'` y runtime presente. Si es falsa, `preguntarIA` sale sin
   llamar a nada.
2. Al cargar un JSON cuyo `fuente` no es `demo`, se anula la referencia al runtime y se ocultan la
   tarjeta y el botón.
3. Una prueba en node fija el comportamiento.
4. El JSON real se carga en `build/qortex.html` local, nunca en el artifact de claude.ai.
5. **Nunca con datos reales**, ni en la Fase 0 ni en la Fase 1. Se revisa, si acaso, con la Fase 2.

## Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| Quitar la IA del todo | Resta en la demo con Víctor, y con datos demo no expone nada de Quamtex |
| IA con datos reales anonimizados y consentimiento | Exige contrato de tratamiento y revisión que no caben en la Fase 0 ni la 1 |

## Consecuencias

Regla 6 de `CLAUDE.md`: «Ningún dato de NetSuite va a un LLM».

## Rollback

Un ADR nuevo, con consentimiento escrito de Quamtex.

## Evidencia

`docs/REVISION-2026-10-05.md`, hallazgos `seguridad-1` y `coherencia-docs-4`.
