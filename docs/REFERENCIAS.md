---
tipo: registro
id: REFERENCIAS
estado: VIGENTE
version: 1.0
fecha: 2026-10-05
---

# QORTEX — Referencias comprobadas

Proyectos comprobados uno a uno el 2026-10-05, en 8 ángulos. Licencia y actividad son las de la verificación; si contradicen al hallazgo previo, manda la verificación. **Sin verificar** = no comprobado en esta pasada. Veredicto: **usar** (entra en el sistema o en su desarrollo), **referencia** (se toma una idea, no código) o **descartar**. En la criba se descartaron otros 231 candidatos (22 + 14 + 45 + 16 + 41 + 23 + 23 + 47). Cómo se usa cada uno en el diseño: `docs/ARQUITECTURA.md` §12. De un proyecto sin licencia declarada solo se toman ideas, nunca código.

## 1. Optimización de inventario

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| stockpyl | https://github.com/LarrySnyder/stockpyl | EOQ (con descuentos), (r,Q), (s,S), multiescalón y simulación; LT determinista según el hallazgo previo (no reverificado) | MIT | 669 commits, 178★, mantenido; fecha no visible | referencia | Oráculo de EOQ y (r,Q) en desarrollo (F1): vectores generados en Python y comprobados por `node --test` |
| inventorize | https://pypi.org/project/inventorize/ | ~50 funciones (SS, ROP, (R,S), ABC); el uso de `^` en lugar de `**` en el SS es hallazgo previo no reverificado | No declarada en PyPI | 1.2.6 (2025-11-29) | referencia | Checklist de funciones y firmas; nunca dependencia |
| supplychainpy | https://github.com/KevinFasusi/supplychainpy | Análisis por SKU (SS, EOQ, ROL, ABC/XYZ), Monte Carlo y dashboard | BSD-3-Clause | 515 commits, 330★; abandono desde 2017 sin verificar | referencia | Forma de la salida por SKU (todas las métricas en un objeto) |
| SupplyNetPy | https://github.com/supplychainsimulation/SupplyNetPy | Simulación SimPy de (s,S), (R,Q) y (T,Q), con disrupciones | MIT | 253 commits, 7★; fecha no visible | referencia | Backtest de políticas con LT estocástico (F1) |
| Databricks safety-stock | https://github.com/databricks-industry-solutions/safety-stock | SS a partir del error del pronóstico (DBR 11+) | Databricks License (no OSI) | 23 commits | referencia | σ del SS = RMSE del backtest (solo la idea) |
| oalotaik | https://github.com/oalotaik/forecast-driven-inventory-control | Revisión periódica (R,S) con SS adaptativo | Ninguna | 5 commits, 2★ | referencia | Horizonte L + R (ARQUITECTURA §6.4) y σ con ventana móvil (F1) |
| 7vikram Safety_Stock_Tool | https://github.com/7vikram/Safety_Stock_Tool | Flask + Plotly: SS y ROP sin σ del lead time | Ninguna | 23 commits, 1★ | descartar | Nada |
| inventorylibx | https://pypi.org/project/inventorylibx/ | Micro EOQ/ROP/SS | MIT | 0.1.1 (2026-08-01) | descartar | Nada |

- Ninguna librería verificada calcula bien, con pruebas y en mantenimiento, el SS con variabilidad de demanda y de lead time: QORTEX escribe funciones propias (en `dashboard/motor.js`, ADR-002) y usa las librerías como oráculo.
- La σ del SS sale del error de backtest, no de la demanda cruda (Databricks, oalotaik y aakashc23 en §8): en F0 el RMSE dentro de muestra se declara supuesto; en F1, RMSE fuera de muestra a LT + R.
- En revisión periódica el horizonte de protección es L + R (oalotaik): el SS de F0 ya lo usa.
- Con importaciones de China, Brasil y Europa la variabilidad del lead time pesa: σLT por proveedor con `lt_n`, y valor por origen marcado supuesto cuando hay pocas recepciones.
- SupplyNetPy es el único candidato que conviene no reescribir, pero en F1 (versión 0.x, API en cambio).
- La investigación proponía vectores compartidos entre un motor JS y uno Python; con un solo motor (ADR-002), los vectores compartidos quedan para las reglas cruzadas del contrato.

## 2. Pronóstico

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| StatsForecast | https://github.com/Nixtla/statsforecast | AutoETS amortiguado, HoltWinters, Croston (Classic, Optimized, SBA), TSB, IMAPA, ADIDA e intervalos | Apache-2.0 | ~4,9k★, activa en 2026 | usar | Motor de pronóstico de F1, por SKU y agregado; que ya no requiere numba es supuesto |
| sktime | https://github.com/sktime/sktime | Framework de series; ADICVTransformer; backtesting | BSD-3-Clause | 1.2.0, ~10,1k★ | referencia | Clasificación ADI/CV² (umbrales 1,32/0,49 sin verificar en el código) y ExpandingWindowSplitter |
| Darts | https://github.com/unit8co/darts | Croston probabilístico, intervalos conformales | Apache-2.0 | ~9,5k★, 1.579 commits | referencia | Intervalos conformales sobre Croston/TSB (F1) |
| Prophet | https://github.com/facebook/prophet | Aditivo con Stan; en mantenimiento desde 1.4.0 | MIT | 1.5.0 (2026-10-05), ~20,4k★ | descartar | Nada (se cita como opción rechazada) |
| pmdarima | https://github.com/alkaline-ml/pmdarima | auto.arima; sin modelos intermitentes | MIT | ~1,7k★; fecha no visible | descartar | Nada |
| intermittent-forecast | https://github.com/pmrgn/intermittent-forecast | Croston, SBA, SBJ, TSB, ADIDA y suavizado con optimización; métrica PIS | MIT | 190 commits, 1★ | referencia | Lectura de referencia e idea de la métrica PIS; no se porta a JS (ADR-002) |
| Hyndman y Kostenko 2007 | https://robjhyndman.com/papers/shortseasonal.pdf | Mínimo m + 5 = 17 observaciones mensuales; «substantially more» en la práctica | Acceso libre | 2007 | referencia | HW estacional por defecto solo con n ≥ 36 |
| Hyndman 2006 | https://robjhyndman.com/papers/foresight.pdf | MASE para demanda intermitente (lubricante en envases grandes) | Acceso libre | 2006 | referencia | MASE por SKU y por clase |

- Un HW multiplicativo amortiguado con 24 meses no se defiende como modelo por defecto: dos datos por índice y falla con ceros. En F0 solo corre con n ≥ 24 y clase smooth o erratic (ARQUITECTURA §6.1).
- F0: clasificar (ADI/CV²) y medir. F1: modelo por clase que bata a Naive y SeasonalNaive(12) en MASE; RMSSE y pinball para intermitentes; nunca MAPE.
- Los modelos intermitentes de StatsForecast dan solo pronóstico puntual: para el SS harán falta intervalos (conformal o bootstrap) en F1.
- Pedir 36–60 meses de historia en la primera corrida: con SuiteQL no cuesta más.
- La investigación sugería portar Croston/SBA/TSB a JS para el Quick Win; se descarta, porque ninguna serie se pronostica en dos sitios (ARQUITECTURA §7).

## 3. ERPs open source

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| Odoo orderpoint | https://github.com/odoo/odoo/blob/17.0/addons/stock/models/stock_orderpoint.py | min/max, qty_multiple, trigger manual o auto, snoozed_until, visibility_days, qty_forecast | LGPL-3 | rama 17.0 mantenida en 2026 | referencia | On hand, en tránsito y pronóstico separados; múltiplo; posponer (F1); nunca trigger auto |
| Odoo landed costs | https://github.com/odoo/odoo/blob/17.0/addons/stock_landed_costs/models/stock_landed_cost.py | 5 métodos de reparto (equal, by_quantity, by_current_cost, by_weight, by_volume); redondeo a la última línea | LGPL-3 | rama 17.0 mantenida | referencia | Método de reparto por componente; flete por volumen o peso → campo `peso` (opcional en v1, usado en F1) |
| OCA stock_orderpoint_safety_stock | https://github.com/OCA/stock-logistics-orderpoint/tree/19.0/stock_orderpoint_safety_stock | SS = σ_L·z·g; min/max con cycle_days | AGPL-3 | rama 19.0; fecha no visible | referencia | Mostrar los insumos de cada cifra en «¿Por qué?» |
| OCA vendor_transport_lead_time | https://github.com/OCA/purchase-workflow/tree/18.0/vendor_transport_lead_time | LT del proveedor + LT de transporte | AGPL-3 | rama 18.0; módulo de 2020 | referencia | `lt` total y `transito_dias` separados |
| ERPNext reorder | https://github.com/frappe/erpnext/blob/develop/erpnext/stock/reorder_item.py | projected_qty contra reorder_level; Material Request | GPL-3 | develop activa | referencia | Cantidad proyectada con términos nombrados; respaldo simple para SKUs Z |
| ERPNext LCV | https://github.com/frappe/erpnext/blob/develop/erpnext/stock/doctype/landed_cost_voucher/landed_cost_voucher.py | Reparto por Qty o Amount sin desglose por componente | GPL-3 | develop activa | referencia | Contraejemplo: QORTEX guarda el desglose |
| OpenBoxes | https://github.com/openboxes/openboxes | WMS sanitario; informes de reorden y pronóstico (fórmulas sin verificar) | EPL-1.0 | 12,4k commits, 155 issues abiertos | referencia | Demanda que incluye lo no servido (consulta 6, línea base); restar lo que vence (F1, si hay lotes) |
| Dolibarr replenish | https://github.com/Dolibarr/dolibarr/blob/develop/htdocs/product/stock/replenish.php | max(max(deseado, alerta) − stock − pedido, 0); variante por almacén | GPL-3+ | develop activa | referencia | MOQ y múltiplo dichos en la fila (razones de `explicar()`) |

- Todos razonan sobre una cantidad proyectada con términos explícitos: QORTEX separa onhand, `en_transito` con ETA y `back`, y la ETA se resuelve una sola vez, en Python.
- Un lead time de un solo número no sirve con 5 orígenes: `lt`, `ltSd`, `lt_n` y `transito_dias` por proveedor.
- La sugerencia debe aplicar MOQ y múltiplo y decirlo (Dolibarr; el issue #9561 es hallazgo previo no verificado).
- Costo de importación en dos niveles, con método de reparto por componente (Odoo); por eso el contrato prevé `peso` aunque la F0 solo reparta por m³ y por valor.
- La demanda debe incluir lo pedido y no servido (OpenBoxes, fórmulas no verificadas): la consulta 6 de pedidos de venta mide los faltantes de la línea base.
- Nada de rutas multialmacén, trigger automático ni contabilidad en F0–F1.

## 4. SaaS comerciales

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| Netstock | https://www.netstock.com/integrations/netsuite/ | SS dinámico, desempeño de proveedor, completar contenedor, panel priorizado | Propietario | sitio activo 2026 | referencia | Panel por excepción y completar contenedor (F1); su sync con NetSuite se declara unidireccional |
| EazyStock | https://www.eazystock.com/ | Conectar → pronosticar → optimizar → orden propuesta que se aprueba | Propietario | sitio activo 2026 | referencia | Flujo con aprobación humana; matriz 9×9 y SuiteApp no verificadas |
| Inventory Planner (Sage) | https://www.inventory-planner.com/ | Pronóstico y OC para retail y e-commerce; Sage Copilot | Propietario | sitio activo 2026 | referencia | Open-to-buy como contraste con el calendario de pagos (precios no verificados) |
| StockIQ | https://stockiqtech.com/integrations/netsuite/ | Bundles NetSuite; POs con un clic; OTIF | Propietario | sitio activo | referencia | Patrón de escritura de F2 y scorecard OTIF |
| Slimstock Slim4 | https://www.slimstock.com/about-us/news/slimstock-celebrates-7-consecutive-years-of-netsuite-certification/ | APS mid-market; 7 años Built for NetSuite | Propietario | nota del 2024-12-17 | referencia | Nada (mercado; la transparencia como diferenciador) |
| GMDH Streamline | https://gmdhsoftware.com/netsuite-demand-planning-software/ | Sync bidireccional; EOQ grupal; aprobación de pronósticos | Propietario | sitio activo | referencia | Estados de aprobación por SKU y EOQ grupal (F1) |
| Lokad sync NetSuite | https://docs.lokad.com/platform/integrations/sync-netsuite/ | Solo lectura; Saved Searches; páginas de 500; 35+ TSV; seudonimización | Propietario | docs activos | referencia | Columnas explícitas y minimización: clientes sin nombre |
| NetSuite Inventory Optimization | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_1155215810.html | ABC × 123, nivel de servicio por segmento, SS, ROP y Preferred Stock Level | Oracle | documentación vigente | referencia | Línea base a superar (F1: comparar con sus SS y ROP) |

- Checklist de demo que todos cumplen: pronóstico por SKU, SS dinámico, ABC/XYZ, ROP, OC por proveedor con MOQ y contenedor, panel por excepción, desempeño de proveedor, simulador, sync diaria y explicación de cada recomendación.
- Diferenciador que ninguno de los 8 publica: costo puesto por línea y componente, por origen, más el calendario de pagos.
- Todos escriben OC de vuelta: eso es la F2 de QORTEX.
- Las anclas de precio (StockIQ $750/mes, Netstock ~$900/mes, $15k–$50k/año) son de terceros y no se verificaron en las páginas.
- NetSuite 2026.2 cubre SS, ROP y segmentación nativos: QORTEX se diferencia por costo puesto, caja y fórmulas visibles.

## 5. Lectura de NetSuite

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| netsuite (jacobsvante) | https://github.com/jacobsvante/netsuite | Cliente async para SOAP, REST y Restlets con CLI opcional; SuiteQL y TBA no confirmados en el README | MIT | 180 commits, 120★ | referencia | CLI para explorar en F0 (opcional); nunca dependencia de producción |
| Gist michoelchaikin | https://gist.github.com/michoelchaikin/100a569343a013c7181800f5325c5501 | SuiteQL con OAuth1 HMAC-SHA256, `Prefer: transient` y paginación por `next` | Ninguna | creado 2021-06-22, 18★ | usar | El patrón del cliente, reescrito (sin licencia) |
| Oracle: SuiteQL por REST | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157909186990.html | Endpoint, `{"q", "params"}`, limit/offset, tope de 100.000 resultados | Oracle | vigente | referencia | Contrato del conector y troceo por año |
| Oracle: prerrequisitos REST | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_5085602973.html | REST Web Services y Access Tokens en Full; Workbook en Edit; no usar Administrator | Oracle | vigente | referencia | Los 3 permisos base del rol |
| SuiteQL Query Library (Tim Dietrich) | https://timdietrich.me/suiteql-query-library/ | 106 consultas (inventario, recepciones de OC, ítem-proveedor) | No indicada | no indicada | referencia | Tablas y columnas de las consultas (hipótesis hasta la corrida 1) |
| truto.one | https://truto.one/blog/the-final-boss-of-erps-architecting-a-reliable-netsuite-api-integration/ | Realm frente a host del sandbox; OneWorld y multimoneda; SOAP retirado en 2028.2 | Artículo | fecha no visible | referencia | Realm en mayúsculas con guion bajo; detectar OneWorld antes de consultar |
| dlt (NetSuite REST) | https://dlthub.com/workspace/source/netsuite-rest-api | Plantilla generada: TBA, suiteql, metadata-catalog; destino DuckDB | Apache-2.0 según dlt (la página no lo indica) | no indicada | referencia | Ruta `GET /record/v1/metadata-catalog` para el descubrimiento de esquema; DuckDB como opción futura |
| Airbyte source-netsuite | https://docs.airbyte.com/integrations/sources/netsuite | Conector TBA con rol dedicado; éxito de sync «Low» | No indicada | no indicada | referencia | Checklist de setup para B4 |

- Contrato del endpoint (Oracle): `Prefer: transient`, parámetros con `?`, `limit` de hasta 1000 y tope de 100.000 filas por consulta, que obliga a trocear `transactionline` por año.
- La concurrencia por tier (Standard 5, Premium 15, Enterprise 20) viene de la investigación sin URL primaria registrada; ante 429, backoff con jitter y un solo hilo.
- Las columnas de las consultas (`aggregateitemlocation`, `transactionline`, `previoustransactionlinelink`, `itemvendor`, `term`), los signos y las monedas de cada importe son hipótesis hasta el descubrimiento de esquema (metadata-catalog y sondas).
- Descartados: clientes SOAP (retiro en 2028.2 según truto) y el esquema inventado de peliqan.io. El archivo de NetSuite Professionals devolvió 429 y no se cita.

## 6. Costo puesto y caja

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| FreightSight | https://github.com/Pchambet/freightsight-landed-cost | Prorrateo por línea (flete, THC, seguro, acarreo, demoras, aranceles); conector Odoo 17 | FSL-1.1-MIT | 16 commits | referencia | THC y demoras como componentes (F1); estimado frente a real |
| HyVoid | https://github.com/HyVoid/landed-cost-calculator-excel | Plantilla de reconciliación en 7 hojas; driver por componente | Apache-2.0 | 26 commits | referencia | Driver por componente (acarreo por peso, F1) y hoja de varianza para calibrar (Quick Win) |
| landed-cost-engine | https://github.com/wave03F/landed-cost-engine | Capas MFN + 301 + 232 + IEEPA; 105 pruebas; el README no menciona MPF/HMF | MIT | 58 commits | referencia | Arancel = MFN + max(301, IEEPA) + 232 por HTS × origen × fecha (F1) |
| tariff-resolver | https://github.com/opsloft/tariff-resolver | MCP en TypeScript; MPF y HMF como líneas aparte; datos de USITC | MIT | 43 commits | referencia | MPF y HMF como componentes (F1) |
| Tryton account_stock_landed_cost | https://github.com/tryton/account_stock_landed_cost | Factura repartida entre embarques recibidos, por valor | GPL-3.0 | mirror archivado el 2023-01-07 | referencia | Reparto posterior de una factura de forwarder entre recepciones |
| NetSuite Landed Cost | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N2418831.html | Categorías; peso, cantidad o valor; fuentes This Transaction, Other Transaction y Other Transaction (exclude tax) | Oracle | vigente | referencia | Descubrir en F0 si existe y con qué método (B6) |
| Odoo Landed Costs 18 | https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/landed_costs.html | Compute → Validate; By Volume y By Weight; requiere AVCO o FIFO | Doc Odoo (módulo LGPL) | v18 vigente | referencia | Flujo calcular → revisar → validar para la aprobación (F1) |
| ERPNext LCV (doc) | https://docs.frappe.io/erpnext/stock-transactions-landed-cost-voucher | Reparto por Qty o Amount; revaluación del costo de venta | Doc Frappe (ERPNext GPL-3.0) | vigente (v16) | referencia | Estimado provisional hasta la factura real |

- El motor actual ya cubre FOB, flete y acarreo por m³, seguro y arancel por valor, aduana por OC, anticipos y mantener (`index.html:410-455`).
- Faltan MPF, HMF, ISF, THC, tope por peso y recargo de peligrosos; China ≈ 25 % + MFN (28,2–28,7 %). Son cifras de la investigación sin fuente primaria registrada.
- El Incoterm decide qué paga Quamtex: con CIF o DDP, sumar flete y arancel sobre el precio los cuenta dos veces (ARQUITECTURA §6.7).
- Riesgo de doble conteo financiero: un 9 % de costo de capital sobre anticipos y un 22 % de mantener que ya lo incluye (investigación).
- Calibrar contra una importación real (±5 % total, ±10 % por componente); ningún dato de esas facturas entra en git.

## 7. GitHub: pronóstico y NetSuite

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| harshakavali81-collab | https://github.com/harshakavali81-collab/Demand-Forecasting-Inventory-Optimization-Project | Portafolio: pronóstico, SS, ROP, FastAPI, Streamlit, pytest; «decision support, not purchase orders» | MIT | 3 commits, 0★ | referencia | Estructura del repo y el aviso de humano en el bucle |
| Mohammed-Zain-py | https://github.com/Mohammed-Zain-py/demand-forecasting-inventory | LightGBM/LSTM sobre Favorita; ROP/ROQ con case-pack; copilot anclado a herramientas | MIT | 4 commits, 0★ | referencia | Pruebas de redondeo al múltiplo y de lead time; LLM que solo cita funciones |
| kalaiselvan-10 | https://github.com/kalaiselvan-10/inventory-forecasting-reorder-assistant | Reorden priorizada; backtest rolling-origin | Ninguna | 3 commits | referencia | Banderas SLOW-MOVING y STOCKOUT-PRONE; backtest del Quick Win |
| netsuite (jacobsvante) | https://github.com/jacobsvante/netsuite | Ver §5 | MIT | ver §5 | referencia | Nada como dependencia |
| Gist michoelchaikin | https://gist.github.com/michoelchaikin/100a569343a013c7181800f5325c5501 | Ver §5 | Ninguna | ver §5 | usar | Ver §5 |
| Lokad: priorización económica | https://docs.lokad.com/how-to/economic-purchase-prioritization/ | Ranking por recompensa/costo con corte por presupuesto | Propietaria | página activa | referencia | Score = recompensa / max(1, costo puesto·Q), adaptación nuestra (F1) |
| Odoo 17 Replenishment report | https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/report.html | To Order editable, Order Once, snooze, agrupar por proveedor | Doc Odoo | v17 vigente | referencia | Fila de la pantalla de aprobación (F1) |
| Netstock (blog) | https://www.netstock.com/blog/use-netstock-for-inventory-planning/ | Modelo por SKU, ABC/XYZ, SS diario, escritura de OC aprobadas | Propietario | blog activo | referencia | Funciones de F1: fiabilidad del LT por proveedor en el SS; restricción por contenedor |

- Ningún proyecto abierto hace el 80 %: los repos son portafolios sobre datos sintéticos o M5/Favorita, sin ERP real, costo puesto ni caja. GarrettsMeta devuelve 404; Slooze y stockflow-sim existen, sin valor de base.
- Estructura limpia común: paquete puro sin I/O + interfaz + SQL versionado + pruebas + docs.
- La investigación recomendaba Python como única fuente de verdad del motor; el ADR-002 adopta el principio (una sola fuente) pero no la ubicación, porque el simulador recalcula en el navegador.
- Pruebas que conviene copiar: múltiplo de compra, lead time, no fuga en el backtest y anclaje del LLM.

## 8. Dashboard y operación

| Nombre | URL | Qué hace | Licencia | Actividad | Veredicto | Qué tomamos |
|---|---|---|---|---|---|---|
| Ajv | https://github.com/ajv-validator/ajv | Validador JSON Schema (draft-07, 2019-09, 2020-12, JTD) con generación de código | MIT | 2.721 commits, 14,9k★ | usar | Validador standalone generado en desarrollo e incrustado en el build, sin CDN ni `new Function` (verificado con Ajv 8.20.0) |
| Chart.js | https://github.com/chartjs/Chart.js | Gráficas sobre canvas, v4 | MIT | 4.597 commits, 67,7k★ | usar | 4.4.1 (la de `index.html:10`) vendorizada, con su SHA-256 comprobado en CI |
| Observable Framework | https://github.com/observablehq/framework | Sitio estático con data loaders en cualquier lenguaje | ISC | 3,7k★ | referencia | Si F1 pide varias páginas: loader Python que emite el JSON |
| Evidence | https://github.com/evidence-dev/evidence | BI como código (SQL + Markdown); soporta DuckDB | MIT | 7k+★ | referencia | Reporte mensual narrativo (F1, opcional) |
| 1Password `op run` | https://www.1password.dev/cli/reference/commands/run/ | Resuelve `op://` de un dotenv y enmascara la salida | Propietario | vigente | usar | Ya adoptado (`.env.example`) |
| Vercel Deployment Protection | https://vercel.com/docs/deployment-protection/usage-and-pricing | Authentication en todos los planes; Password Protection a $20/mes por proyecto en Pro | Doc | last_updated 2026-09-15 | referencia | Protección más `X-Robots-Tag` en `vercel.json` |
| pydevtools handbook | https://pydevtools.com/handbook/explanation/modern-python-project-setup-guide-for-ai-assistants/ | uv, PEP 621, dependency-groups, ruff, pytest, `uv.lock` | No indicada | fecha no confirmada | referencia | Estructura del paquete con uv |
| aakashc23 | https://github.com/aakashc23/demand-forecasting-inventory-reorder-engine | SS = Z·RMSE(backtest)·√L; 38 pruebas (fuga, matemática de inventario, SQL) | Ninguna | 1 commit, 0★ | referencia | σ del SS por backtest (F1) y pruebas de no fuga |

- Sin servidores en F0; el JSON real solo se carga en local. Se descarta incrustar el JSON real en el HTML, que proponía la investigación: el archivo viajaría con datos del cliente.
- Ajv standalone (verificado con 8.20.0): sin `require()` ni `new Function` si el esquema evita `minLength`, `maxLength` y `uniqueItems`; con ellos importa `ucs2length` o `equal` de su runtime. En modo estricto exige `type` explícito dentro de `if`.
- Vercel: Password Protection no existe en Hobby; Authentication es gratis y, desde 2026-09-09, cubre también producción (changelog). Que producción no lleve `noindex` y que Hobby no admita uso comercial no se verificó en la página de precios.
- «No approval received» se atribuye al harness de la sesión, sin verificar: publicar desde la terminal del dueño con `VERCEL_TOKEN` en el entorno.
- Observable o Evidence solo cuando haya varias páginas o reportes; Streamlit y Dash exigen un servidor.
