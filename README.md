---
tipo: registro
id: QORTEX-ACTA
estado: VIGENTE
version: 1.0
fecha: 2026-10-05
---

# QORTEX — Reabastecimiento con IA para Quamtex

**Código:** PRJ-QTX-REA-01 · **Apertura:** 5-oct-2026 · **Responsable:** Ignacio Romero (KATIA.AI)
**Estado:** prototipo listo, pendiente de la reunión con Víctor.

Sistema de abastecimiento sobre NetSuite que dice **qué, cuánto y cuándo comprar**,
con el costo puesto en almacén y la fecha en que sale el dinero. Una persona aprueba cada orden.

> **Expediente independiente del Tomador de Pedido Web** (repo `quamtex-ecosystem`). No comparte
> código, credenciales, rol de NetSuite ni despliegue (ADR-001).

## Regla de oro

**QORTEX no escribe en NetSuite** hasta que ambos dueños aprueben la Fase 2 por escrito.
El rol de NetSuite es exclusivo y solo de lectura, sin permisos de transacción.

## Ficha

| Campo | Valor |
|---|---|
| Cliente | Quamtex, distribuidor de WEG Paints, Houston, TX |
| Proveedor | KATIA.AI (ventas@katia.solutions · +1-346-892-0577) |
| Sponsor del cliente | Víctor (dueño 1) |
| Aprobador final | Víctor + Edgar (dueño 2) |
| Sistema base | NetSuite (solo lectura en el prototipo) |

## Problema y metas

Quamtex pierde ventas por falta de stock: compra sin proyección y el inventario del sistema
no coincide con el físico (conteo de KATIA: **−961 u netas en 36 SKUs**). Compra a 5 orígenes
(China, México, Brasil, Europa y EE.UU.).

| Indicador | Línea base | Meta a 90 días tras la Fase 1 |
|---|---|---|
| Exactitud de inventario (36 SKUs) | −961 u netas | diferencia ≤ 2% |
| Nivel de servicio en SKUs A | se mide en la Fase 0 | ≥ 95% |
| Faltantes A/B por mes | se mide en la Fase 0 | −30% |
| OC con recomendación QORTEX | 0% | 100% |
| Tiempo para armar una OC | se mide | −50% |

## Alcance

| Incluye | No incluye |
|---|---|
| Lectura de NetSuite vía SuiteQL/REST (OAuth1 TBA) | Escribir OC, ajustes o registros en NetSuite |
| Inventario, 24 meses de ventas, OC y recepciones | Contabilidad, cuentas por cobrar y por pagar |
| Pronóstico, ABC/XYZ, stock de seguridad, ROP, EOQ | WMS y picking |
| Costo puesto en almacén por proveedor y origen | Negociación con proveedores |
| Dashboard HTML con simulador «¿y si…?» | App móvil nativa |
| Reporte de calidad de datos | Corrección masiva del maestro (se cotiza aparte) |
| Capacitación a compras (2 sesiones) | Soporte 24/7 |

Lo que no esté en la tabla entra como **solicitud de cambio, con precio y fecha**.

## Fases y precio (sugerido, por confirmar)

| Fase | Duración | Precio (USD) | Definition of Done |
|---|---|---|---|
| 0 — Diagnóstico | 2 sem | 1,500–2,500 (100% por adelantado) | `qortex_data.json` real cargado, reporte de calidad entregado y revisado con Víctor |
| Quick Win | 2–3 sem (dentro de la Fase 1) | incluido | Compras emite una OC real basada en QORTEX |
| 1 — Motor completo | 6–8 sem | 7,000–12,000 (50/50) | 100% de las OC con recomendación y costo puesto en almacén validado |
| 2 — Propone y aprueba | por definir | se cotiza al cerrar la Fase 1 | autorización escrita de ambos dueños |
| Retainer | mensual | 600–1,200/mes | reporte mensual de métricas |

## Estructura del repositorio

| Ruta | Qué es | Versionado |
|---|---|---|
| `README.md` | Esta acta | sí |
| `SEGUIMIENTO.md` | Tablero comercial y pendientes | sí |
| `.env.example` | 6 variables como referencias `op://` | sí |
| `index.html` | Dashboard v0.1 (6 pestañas + simulador) | **pendiente de subir** |
| `qortex_conector.py` | Conector NetSuite de solo lectura | **pendiente de subir** |
| `queries/*.sql` | 5 consultas SuiteQL | **pendiente de subir** |
| `qortex_data.json`, `reporte_calidad.txt`, `supuestos_proveedores.json` | Datos del cliente | **nunca** (`.gitignore`) |

## Secuencia de carga de datos

1. Primera corrida del conector: genera `supuestos_proveedores.json`.
2. Quamtex asigna origen, términos de pago, arancel y quién paga el flete de cada proveedor.
3. Segunda corrida: genera `qortex_data.json` y `reporte_calidad.txt`.
4. En el dashboard, botón «Cargar datos de NetSuite».

```bash
op run --env-file=.env.example -- python3 qortex_conector.py
```

## Seguridad

- Las credenciales salen solo de 1Password (bóveda `Quamtex-REA`). Nunca van en el código ni en el chat.
- El dashboard se publica con `noindex, nofollow`. Hay que comprobar en una ventana de incógnito si pide login.
- Ningún dato del cliente entra en git.

## Riesgos (alternativa recomendada)

| Riesgo | Recomendada |
|---|---|
| Inventario poco fiable (−961 u) | Recontar solo los SKUs clase A antes de proyectar |
| Edgar frena la decisión | Que Víctor presente la lámina «sin riesgo». Respaldo: piloto con 1 proveedor |
| Vercel bloqueado | Correr `npx vercel --prod` desde la computadora. Si la reunión es antes, mandar el HTML como archivo |
| Credenciales de NetSuite sin permisos | Crear con Víctor un rol nuevo de solo lectura (no reusar el del Tomador) |
| Sin datos de aranceles y flete | Usar supuestos por origen, marcados como tales, y pedir facturas en la Fase 1 |
| El alcance crece | Solicitud de cambio con precio |

## Preguntas abiertas

- ¿Fecha de la reunión con Víctor y de la firma de la Fase 0?
- ¿Quamtex registra Landed Cost en NetSuite? Si lo hace, el costo puesto en almacén sale 100% real.
