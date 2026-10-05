---
tipo: adr
id: ADR-004
estado: aceptado
fecha: 2026-10-05
---

# ADR-004 · Candado de solo lectura con lista blanca, en código

**Fecha:** 5-oct-2026
**Estado:** aceptado (implementa ADR-001)

## Contexto

El plan preveía una lista negra: rechazar `PUT`, `PATCH`, `DELETE` y `POST` fuera de SuiteQL, más
un prefijo `SELECT`/`WITH`. No fijaba host ni desactivaba redirecciones, así que un cambio de URL
mandaría el token OAuth1 a cualquier dominio y un 302 podía cambiar el destino; tampoco imponía
timeouts ni límite de concurrencia, y la cuenta de NetSuite se comparte con el Tomador de Pedido
(`seguridad-2`, `-3`, `-4`).

## Decisión

`src/qortex/readonly.py` es la única puerta HTTP del proyecto:

1. Solo `https` y host exacto `{cuenta en minúsculas, _ → -}.suitetalk.api.netsuite.com`. Los
   RESTlets, en otro host, quedan fuera.
2. Solo `GET` bajo `/services/rest/record/v1/` (incluido `metadata-catalog`) y `POST` exacto a
   `/services/rest/query/v1/suiteql`. Todo lo demás lanza `ReadOnlyViolation`, que muestra verbo y
   ruta, nunca la consulta.
3. `allow_redirects=False`; `timeout=(5, 60)`; reintento solo ante 429, 502, 503 y 504, con backoff,
   jitter, 4 intentos y `Retry-After`; concurrencia 1.
4. El prefijo `SELECT`/`WITH` se conserva como chequeo barato.
5. Una prueba solo permite `import requests` en `readonly.py`.
6. Logs: método, ruta, estado, filas y duración; nunca `Authorization`, cuerpos ni filas.
7. Con 401/403 se detiene y nombra el permiso o la tabla que falta.

Permisos del rol: lista exacta en `docs/ARQUITECTURA.md` §10.1.

## Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| Lista negra de verbos | No protege el destino del token ni las redirecciones |
| Confiar solo en el rol | Un error de configuración del rol no debe ser la única barrera |

## Rollback

No aplica: aflojar el candado exige un ADR nuevo y la firma de ambos dueños (ADR-001).

## Evidencia

`docs/REVISION-2026-10-05.md`, hallazgos `seguridad-2` a `-5`.
