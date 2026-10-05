---
tipo: adr
id: ADR-001
estado: aceptado
fecha: 2026-10-05
---

# ADR-001 · QORTEX: expediente separado y de solo lectura sobre NetSuite

**Fecha:** 5-oct-2026
**Estado:** aceptado
**Modifica:** nada del Tomador de Pedido Web (`quamtex-ecosystem`). Abre un repositorio propio.

---

## Contexto

El 5-oct-2026 se abre **QORTEX** (PRJ-QTX-REA-01), el sistema de reabastecimiento de Quamtex:
pronóstico, stock de seguridad, ROP, EOQ y costo puesto en almacén, todo sobre NetSuite.
El acta (`README.md`) lo declara **independiente** del Tomador de Pedido Web.

Abre un camino nuevo hacia un sistema externo (criterio 2 del índice de ADR): un conector
que lee NetSuite con OAuth1 TBA. El repositorio del Tomador ya tiene credenciales, roles y despliegues propios;
mezclarlos con QORTEX acoplaría dos expedientes con aprobadores distintos.

## Decisión

1. **Repositorio propio.** QORTEX vive en este repositorio. No importa código de
   `quamtex-ecosystem` ni ese repositorio importa de este.
2. **Solo lectura.** El conector solo ejecuta SuiteQL y GET de REST. El rol de NetSuite es
   **exclusivo de QORTEX** y no tiene permisos de transacción. **No se reusa el rol ni el token
   del Tomador.**
3. **Credenciales separadas.** Seis variables (`NS_ACCOUNT`, `NS_CONSUMER_KEY`,
   `NS_CONSUMER_SECRET`, `NS_TOKEN_ID`, `NS_TOKEN_SECRET` y `NS_LOCATION_ID`) en la bóveda
   `Quamtex-REA`. Solo `.env.example` se versiona, y solo lleva referencias `op://`.
4. **Datos del cliente fuera de git.** `.gitignore` excluye `qortex_data.json`,
   `reporte_calidad.txt`, `supuestos_proveedores.json` y las salidas.
5. **Escribir en NetSuite** (la Fase 2) exige un ADR nuevo **y** la autorización escrita de
   Víctor y Edgar.

## Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| Carpeta `qortex/` dentro de `quamtex-ecosystem` | Se probó el 5-oct-2026 y se descartó el mismo día: comparte CI, historial y permisos con el Tomador |
| Reusar el adapter NetSuite del Motor (`quamtex-ecosystem/src/adapters/`) | Acopla dos expedientes con dueños y aprobadores distintos. Un cambio en uno podría romper al otro |
| Reusar el rol de NetSuite del Tomador | Mezcla auditoría y permisos. Si ese rol gana permisos de escritura, QORTEX los heredaría sin decisión |

## Consecuencias

- El dashboard y el conector que ya existen fuera del repo se suben aquí antes de la
  primera corrida contra NetSuite real.
- Cualquier cambio de esta decisión se registra en un ADR nuevo, no editando este.

## Variables de entorno / configuración

`.env.example`: las 6 variables arriba, todas `op://Quamtex-REA/qortex-netsuite/*`.

## Rollback

Archivar el repositorio. No toca el Motor, la base de datos, el VPS ni NetSuite.

## Evidencia

```bash
git check-ignore -v qortex_data.json reporte_calidad.txt .env
# → las tres las ignora .gitignore
git check-ignore .env.example || echo "se versiona"
# → se versiona
```
