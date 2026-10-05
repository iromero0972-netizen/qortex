---
tipo: spec
id: SPEC-QORTEX
estado: APROBADO
version: 2.0
fecha: 2026-10-05
---

# QORTEX — diseño

**Fecha:** 5-oct-2026 · **v2:** tras la revisión de arquitectura del mismo día
**Estado:** aprobado por Ignacio (acepta las 10 decisiones de `docs/REVISION-2026-10-05.md` §5)
**Autor:** sesión con Ignacio Romero, a partir del acta (PRJ-QTX-REA-01)
**Detalle técnico:** `docs/ARQUITECTURA.md` (contrato §5, fórmulas §6, seguridad §10)

---

## 1. Qué pide el cliente

1. Quamtex pierde ventas porque se queda sin stock: compra sin proyección.
2. El inventario en NetSuite no coincide con el físico. El conteo de KATIA dio **−961 u netas en 36 SKUs**.
3. Compra a 5 orígenes (China, México, Brasil, Europa y EE.UU.), cada uno con su lead time, sus términos y su costo.
4. Arma las OC sin punto de reorden, sin stock de seguridad y sin costo puesto en almacén.

**Objetivo:** que cada OC salga recomendada por datos, con el costo real y la fecha en que sale el
dinero, y que la apruebe una persona.

## 2. Decisiones

| # | Decisión | Fuente |
|---|---|---|
| D1 | Opción D, híbrido por fases: diagnóstico pagado, Quick Win, motor completo | Acta, «Fases y precio» |
| D2 | Solo lectura sobre NetSuite hasta la firma de la Fase 2 | Acta, «Regla de oro»; ADR-001 |
| D3 | Rol NetSuite exclusivo, no el del Tomador | Acta, «Riesgos»; ADR-001 |
| D4 | **Una fórmula, un lenguaje:** Python extrae, prepara, mide calidad y (en F1) pronostica; el motor de políticas vive solo en `dashboard/motor.js`; `qortex_data.json` es su entrada validada | ADR-002 (supersede la D4 de la v1) |
| D5 | Autonomía por fases: recomienda → propone y el humano aprueba → ejecuta dentro de límites firmados | Acta |
| D6 | La Fase 0 arregla el dato antes de prometer resultados | Acta, «Riesgos» |
| D7 | La IA del dashboard solo con datos de demostración | ADR-003 |
| D8 | Candado de solo lectura con lista blanca | ADR-004 |
| D9 | Se publica solo un HTML de demo, de un archivo y protegido | ADR-005 |

### Por qué D4

El simulador «¿y si…?» recalcula en el navegador, así que el motor tiene que estar ahí. Escribirlo
también en Python duplicaría lo que ya divergía antes de empezar. En la Fase 0 no hay servidor ni
base de datos: el conector corre en la computadora de Ignacio con `op run`, produce un snapshot y
Python prepara el JSON que el dashboard carga en local.

## 3. Arquitectura

```
NetSuite ◄── readonly.py (lista blanca) ◄── conector.py        [make extraer]
                                              ├─► salidas/crudo/…        snapshot
                                              └─► salidas/supuestos.json valores por origen, «supuesto»
Compras confirma supuestos ─────────────────────┘
preparar.py + contrato.py (sin red)                            [make datos]
   └─► salidas/qortex_data.json   solo si valida (esquema + R1–R6)
calidad.py                                                     [make calidad]
   └─► salidas/reporte_calidad.txt   ◄── salidas/conteo_fisico.csv
build/qortex.html (motor.js + demo + validador + Chart.js)     [make dashboard]
   └─ navegador local: «Cargar datos de NetSuite» → validar → planificar(fecha_corte) → vistas
```

**La separación que sostiene el diseño:** todo lo que toca NetSuite está en `conector.py` detrás de
`readonly.py`. ETA, conversión a USD y lead time se calculan solo en Python. Las políticas viven
solo en `motor.js`, como funciones puras que reciben `fecha_corte` y no mutan la entrada.

## 4. Los cinco agentes

| Agente | Dónde | Cálculo | Salida |
|---|---|---|---|
| **Demanda** | F0: HW en `motor.js`. F1: `pronostico.py` | F0: Holt-Winters solo con n ≥ 24 y clase smooth o erratic, parámetros como supuesto; si no, confianza baja y sin OC. F1: StatsForecast por clase ADI/CV², evaluado con MASE, RMSSE y pinball contra Naive y SeasonalNaive; también para la serie agregada; el HW se retira | Pronóstico por SKU y mes |
| **Proveedores** | `proveedores.py` | Lead time = recepción − OC; media, σ y número de recepciones `lt_n`; con `lt_n` < 5, valor por origen marcado supuesto; `transito_dias` aparte | Lead time y riesgo por proveedor |
| **Riesgo** | `motor.js` | SS = z·√((LT+R)·σd² + d²·σLT²); ROP = d·LT + SS; posición = onhand + Σ en tránsito − comprometido; **crítico** si la proyección diaria con las ETA reales deja demanda sin servir antes de LT; «sin venta» por ventas reales de 12 meses | Semáforo: crítico / ordenar / en nivel / exceso / sin venta |
| **Comprador** | `motor.js` | EOQ = √(2·D·S/H); tope de vida útil efectivo (vida al llegar menos stock al llegar); redondeo al múltiplo, hacia abajo si manda el tope; razones visibles. F1: reabastecimiento conjunto | OC sugerida por proveedor, con «¿Por qué?» |
| **Tesorería** (diferenciador CPA) | `motor.js` | Costo puesto según el **Incoterm** de cada proveedor (ARQUITECTURA §6.7); inventario valorado a costo promedio; pagos al ordenar, al embarque o a la llegada; importes en USD. F1: MPF, HMF, broker por valor, THC, ISF, peso, peligrosos, LCL | Flujo de caja de compras: mensual en F0, semanal en F1 |

**Niveles de servicio** (supuesto, en `parametros`): A 98 % (A-Z 97 %), B 95 %, C 90 %, con piso de
97 % para SKUs «sensibles» (clase A o ≥ 15 clientes).

**Regla para «¿Por qué?»:** cada línea sugerida muestra demanda, lead time, SS, ROP, posición,
cantidad y sus razones, y la **procedencia** de cada valor (`netsuite`, `calculado`, `supuesto` o
`confirmado`), el Incoterm, el tipo de cambio usado y la ETA de lo que viene en camino con su
fuente. Si compras no entiende la línea, no la aprueba.

**Parámetros** (todos supuestos, en `parametros`): cortes ABC/XYZ, umbrales de estados, factor de
vida útil 0,75, 240 días, 28 m³ por contenedor, tasa 9 %, mantener 22 %, costo de pedir 150 y
constantes de clientes (lista completa en ARQUITECTURA §6.9).

## 5. Datos

### 5.1 Lo que se lee de NetSuite

Antes de consultar: descubrimiento de esquema (`GET metadata-catalog`) y una sonda por tabla.

| # | Consulta | Para qué |
|---|---|---|
| 1 | Inventario por Location: on hand, comprometido, backorder, en pedido, costo promedio, peso | Riesgo, Tesorería |
| 2 | Ventas a nivel línea con notas de crédito, **toda la historia hasta 60 meses**, troceada por año | Demanda, clientes |
| 3 | OC con fecha esperada de recepción, tipo de cambio e Incoterm | Proveedores, ETA |
| 4 | Recepciones enlazadas a su línea de OC | Proveedores |
| 5 | Proveedores con moneda, términos, Incoterm y `itemvendor` | Tesorería, Comprador |
| 6 | Pedidos de venta | Demanda no servida |

### 5.2 Lo que pone Quamtex (supuestos)

`salidas/supuestos.json`, con dos secciones. Proveedores: país, Incoterm, pagos, días de tránsito,
flete por m³, seguro, arancel, broker, acarreo, marítimo, revisión. SKUs: m³, múltiplo, vida útil,
alterno, peso, peligroso. La primera corrida lo llena con valores por origen o presentación, todos
marcados `supuesto` en el mapa `procedencia`; Compras confirma campo por campo. Arancel de China por
defecto: 28,5 % (25 % + MFN). Así B5 deja de bloquear la Fase 0.

### 5.3 Contrato de `qortex_data.json`

Lo fija `schema/qortex_data.schema.json`, que valida en Python y en el navegador (validador Ajv
generado del mismo archivo), más las reglas cruzadas R1–R6. Obligatorios: versión, `fecha_corte`,
`fuente`, `moneda_base`, `tipo_cambio` si hay otra moneda y `meses`; por proveedor, id interno,
país, moneda, Incoterm y pagos; por SKU, costo, costo promedio, lo que viene en camino con su ETA y
`calidad`. Clientes sin nombre. Detalle campo por campo: ARQUITECTURA §5.

## 6. Reporte de calidad de datos (entregable de la Fase 0)

| Chequeo | Por qué importa |
|---|---|
| SKUs con disponible negativo | No se puede proyectar sobre un negativo |
| Diferencia sistema vs conteo físico (`salidas/conteo_fisico.csv`) | Línea base del indicador de exactitud |
| SKUs sin ventas en 12 m con stock | Exceso / obsoleto |
| SKUs vendidos sin proveedor preferido | El Comprador no puede sugerir OC |
| OC sin recepción o con recepción anterior a la OC | Lead time imposible |
| Unidades de medida inconsistentes entre compra y venta | Un factor mal puesto multiplica el error |
| Proveedores sin términos de pago | Tesorería no puede calendarizar |

**Líneas base del acta:** exactitud contra el conteo, lista de SKUs A para recontar, nivel de
servicio en A, faltantes A/B por mes y tiempo para armar una OC (entrevista con Compras, dato
declarado). **Además:** perfil de demanda ADI/CV², OC con ETA estimada o vencida, diferencia entre
`quantityonorder` y las líneas abiertas, notas de crédito y % de supuestos confirmados.

Salida: un TXT legible para Víctor, con conteos, porcentajes y los 10 peores casos de cada chequeo.

## 7. Manejo de errores

- Un SKU con datos insuficientes **no se cae**: sale con confianza baja y sin OC sugerida.
- Un campo ausente en NetSuite se reporta; no se rellena con 0. Un SKU sin proveedor o sin supuestos sale del JSON y va al reporte.
- Una OC con ETA vencida se proyecta al día siguiente del corte y se reporta.
- Con 401/403 el conector se detiene y nombra el permiso o la tabla. Con 429 y 5xx, backoff con concurrencia 1.
- Los logs nunca llevan `Authorization`, cuerpos ni filas.

## 8. Seguridad

- Rol sin permisos de transacción; lista exacta en ARQUITECTURA §10.1.
- Candado de lista blanca: host exacto, dos rutas, sin redirecciones (ADR-004).
- Credenciales: 6 variables en `op://Quamtex-REA/qortex-netsuite/*`.
- Datos del cliente solo en `salidas/`, fuera de git; guard en CI y en pre-commit.
- IA apagada con datos reales (ADR-003).
- Se publica solo `build/`: demo, un archivo, sin scripts de terceros al ejecutarse, `noindex` y contraseña (ADR-005). `esc()` en todo campo del JSON.

## 9. Pruebas

- Motor (`node --test`): casos a mano (EOQ con D=1200, S=50 y H=2 da 244,9; con múltiplo 12, 252), propiedades, golden, tabla de Incoterm, pagos al embarque, crítico con ETA; también con `TZ=Europe/Madrid`.
- Contrato: vectores R1–R6 compartidos por pytest y node.
- Preparación: regla de ETA, conversión a USD, lead time con `lt_n`.
- Candado y conector: verbos, host, rutas, redirecciones, timeout; paginación y 401/403/429 con respuestas grabadas sintéticas.
- IA apagada y XSS con JSON malicioso.

## 10. Dependencias externas

| Bloquea | Qué falta | De quién |
|---|---|---|
| Primera corrida real | Rol de solo lectura + 6 credenciales | Víctor / admin NetSuite |
| Costo puesto confirmado | Incoterm, términos, arancel y flete por proveedor (con supuestos ya no bloquea) | Compras Quamtex |
| Costo puesto sin supuestos | ¿Landed Cost en NetSuite? ¿Inbound Shipments? | Admin NetSuite |

## 11. Preguntas abiertas

1. Fecha de la reunión con Víctor y de la firma de la Fase 0.
2. ¿Landed Cost en NetSuite? ¿Con qué método? ¿Inbound Shipments?
3. ¿Solo Houston tiene stock vendible?
4. ¿Qué proveedor tiene más faltantes? (Es el del Quick Win.)
5. ¿Cuántos meses de ventas hay en NetSuite?
6. ¿Dónde están vida útil, país de origen y peso (campo custom o lote)?
7. ¿La cuenta es OneWorld o multimoneda? ¿Qué tier? ¿De dónde sale el tipo de cambio?
8. ¿Qué Incoterm, lugar convenido y HTS tiene cada proveedor?
9. ¿Qué productos son mercancía peligrosa?
10. ¿Qué umbrales definen «sin venta»? ¿El costo de pedir es por OC o por línea?

## 12. Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| A · NetSuite nativo (Demand Planning, Inventory Optimization) | Módulo con licencia, sin costo puesto en almacén ni tesorería; queda como línea base a superar en F1 |
| B · Motor propio desde cero sin fases | Se construye antes de cobrar y antes de saber si el dato sirve |
| C · SaaS tipo Netstock | Nivel 2 de 4; Quamtex paga suscripción y KATIA no queda en el medio |
| Todo el motor en Python | El simulador perdería la recalculación o exigiría servidor (ADR-002) |
| Dos motores con paridad | Duplica lo que ya diverge (ADR-002) |
| Servidor + base de datos en la Fase 0 | Operar sin necesitarlo; se decide en la Fase 1 con ADR |
