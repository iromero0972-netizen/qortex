---
tipo: adr
id: ADR-005
estado: aceptado
fecha: 2026-10-05
---

# ADR-005 · Se publica solo un HTML de demo, de un archivo y protegido

**Fecha:** 5-oct-2026
**Estado:** aceptado por Ignacio (decisión 6 de `docs/REVISION-2026-10-05.md` §5)

## Contexto

Desplegar desde la raíz del repo publicaría el acta con precios, `SEGUIMIENTO.md` y `docs/`. El
dashboard no tiene `noindex`, carga Chart.js de cdnjs sin `integrity` y mete campos del JSON en
`innerHTML` sin escapar (`seguridad-2`, `-7`; `ingenieria-3`). Vercel rechazó dos intentos con
«No approval received».

## Decisión

1. `make dashboard` genera `build/qortex.html`: **un solo archivo** con motor, datos demo,
   validador generado y Chart.js 4.4.1 vendorizado (SHA-256 comprobado en `make ci`). Ningún script
   de terceros se descarga al ejecutarse.
2. Solo se publica `build/`, **solo con datos de demostración**, con
   `<meta name="robots" content="noindex, nofollow">` y `X-Robots-Tag` en `vercel.json`.
3. **Vercel Pro con Password Protection** mientras dure la venta: Víctor y Edgar entran con una
   contraseña, sin cuenta de Vercel. Se comprueba en una ventana de incógnito.
4. `make publicar` aborta si fallan el guard de datos o la comprobación de `build/`. `VERCEL_TOKEN`
   va en el entorno, nunca en la línea de comandos. Se publica desde la terminal de Ignacio.
5. `esc()` en todo campo del JSON que entra en el HTML, con una prueba de JSON malicioso.
6. Los datos reales se cargan solo en `build/qortex.html` abierto en local.

## Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| Vercel Authentication (gratis) | Víctor y Edgar necesitarían cuenta de Vercel: fricción en plena venta |
| Mandar el HTML por correo | Sin control de acceso ni de versión; queda como respaldo si Vercel falla |
| CDN con SRI | Sigue dependiendo de la red al abrir la demo |

## Consecuencias

Costo: el plan Pro de Vercel más Password Protection (precio por confirmar en la cuenta). Se
cancela al cerrar la venta o se traslada a Quamtex.

## Rollback

Despublicar el proyecto de Vercel. El build local no cambia.

## Evidencia

`docs/REVISION-2026-10-05.md`, hallazgos `seguridad-2`, `seguridad-7` e `ingenieria-3`.
