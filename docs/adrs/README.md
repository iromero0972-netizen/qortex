---
tipo: indice-adr
id: ADR-INDEX
estado: vivo
fecha: 2026-10-05
---

# Índice de ADR · QORTEX

Un ADR documenta **una decisión que un tercero no podría deducir leyendo el código**, junto con lo
que se descartó y por qué. Se escribe uno cuando la respuesta a alguna de estas preguntas es «sí»:

1. ¿Cambia dónde vive la fuente de verdad?
2. ¿Abre o cierra un camino de escritura hacia un sistema externo (NetSuite)?
3. ¿Convierte una convención en una barrera de código que aborta?
4. ¿Deja obsoleto un componente que sigue en el árbol?

Si no, va a `docs/DECISION_LOG.md`.

**Formato:** `ADR-NNN-slug.md`, frontmatter `tipo/id/estado/fecha`, y las secciones Contexto ·
Decisión · Alternativas descartadas · Consecuencias · Configuración · Rollback · Evidencia.
**Ningún valor de secreto**: rutas `op://` sí, valores nunca.

**Los ADR no se reescriben.** Si la decisión cambia, se escribe uno nuevo que lo supersede, y en el
viejo solo cambia la línea de estado.

## Índice

| ADR | Título | Estado | Fecha |
|---|---|---|---|
| [ADR-001](ADR-001-expediente-separado-solo-lectura.md) | Expediente separado y de solo lectura sobre NetSuite | Aceptado | 2026-10-05 |

> ## **PRÓXIMO ADR LIBRE: ADR-002**
>
> Quien crea un ADR actualiza esta línea en el mismo commit.
