---
tipo: adr
id: ADR-002
estado: aceptado
fecha: 2026-10-05
---

# ADR-002 · Un solo motor de políticas, y `qortex_data.json` como su entrada validada

**Fecha:** 5-oct-2026
**Estado:** aceptado por Ignacio (decisiones 1 y 2 de `docs/REVISION-2026-10-05.md` §5)
**Supersede:** spec D4 y `docs/DECISION_LOG.md` («Python para conector y motor»)

## Contexto

El spec ponía el motor en Python, pero el motor completo ya existe en JavaScript dentro de
`index.html` y el simulador «¿y si…?» lo necesita en el navegador para recalcular. Antes de
escribir una línea de Python, las dos versiones ya divergían: niveles de servicio, plan B del
pronóstico y métrica de error (`ingenieria-1`, `coherencia-docs-1`). Además, el contrato del JSON
era implícito: `cargarJSON` solo exige `skus`, `proveedores` y 12 meses, y un campo ausente
produce un plan falso en silencio (`contrato-datos-1`, verificado con node).

## Decisión

**Una fórmula, un lenguaje.**

1. **Python** extrae (conector detrás del candado, ADR-004), prepara (series netas, lead time con
   `lt_n`, regla única de ETA, conversión a USD, precio realizado, costo promedio), mide la calidad,
   valida al escribir y, en la Fase 1, pronostica. Nunca reimplementa el motor.
2. **`dashboard/motor.js`** calcula ABC/XYZ, z, SS, ROP, proyección diaria y estados, EOQ y topes,
   costo puesto por Incoterm, caja y «¿Por qué?». No lee archivos, red ni reloj: recibe
   `fecha_corte` y no muta la entrada. No infiere ETA ni convierte monedas.
3. **`qortex_data.json` es la entrada del motor**, no su salida. Lo define
   `schema/qortex_data.schema.json`, que valida en Python (jsonschema) y en el navegador (validador
   Ajv generado). Las reglas cruzadas R1–R6 se escriben dos veces (`contrato.py` y
   `validarCruzadas()`) y las fijan los mismos vectores de prueba.
4. **Supuestos:** el mapa `procedencia` por proveedor y por SKU (`netsuite`, `calculado`,
   `supuesto`, `confirmado`) sustituye a la marca `"origen": "supuesto"` campo por campo, porque
   `origen` ya significa país y envolver cada valor rompe el motor. El esquema rechaza un supuesto
   sin su entrada. `supuestos_proveedores.json` pasa a `salidas/supuestos.json`, con secciones de
   proveedor y de SKU y valores por origen o presentación, todos marcados `supuesto`.
5. **Pronóstico:** en la Fase 0, el Holt-Winters de JS sigue, solo para series con n ≥ 24 y clase
   smooth o erratic; si no, confianza baja y sin OC. En la Fase 1 lo sustituye StatsForecast en
   Python, para los SKUs y para la serie agregada, y el HW se borra (ADR propio).

Detalle del contrato, la regla de ETA y las fórmulas: `docs/ARQUITECTURA.md` §5–§7.

## Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| Todo el motor en Python | El simulador pierde la recalculación o exige un servidor, que la Fase 0 descarta |
| Dos motores con pruebas de paridad | Duplica lo que ya diverge, con el doble de mantenimiento |
| Pyodide (Python en el navegador) | Pesado y sin verificar con StatsForecast |
| Mantener la marca `origen` por campo | Choca con `origen` = país y deja costo `NaN` y 0 órdenes (verificado con node) |

## Consecuencias

- Las reglas 3 y 4 de `CLAUDE.md` cambian en el mismo commit que este ADR.
- La tarea 5 del plan (5 agentes en Python) sale de la Fase 0; entra «Preparación en Python».
- Todo cambio numérico del motor es un diff del golden (`node scripts/golden.mjs`).

## Configuración

`parametros` en el JSON sobrescribe los valores por defecto del motor (lista en ARQUITECTURA §6.9),
todos marcados supuesto. Niveles de servicio por defecto: A 98 % (A-Z 97 %), B 95 %, C 90 %, con
piso de 97 % para SKUs «sensibles».

## Rollback

Volver al spec D4 con un ADR nuevo que supersede a este. El contrato y el esquema se conservan.

## Evidencia

`docs/REVISION-2026-10-05.md` (hallazgos `ingenieria-1`, `coherencia-docs-1`, `contrato-datos-1`
a `-8`) y las cifras repetidas a mano en su §1.
