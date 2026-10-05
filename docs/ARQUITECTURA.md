---
tipo: registro
id: ARQUITECTURA
estado: PROPUESTO
version: 1.0
fecha: 2026-10-05
---

# QORTEX — Arquitectura

> **Propuesta pendiente de revisión de Ignacio.** Cambia una decisión registrada (spec D4, `docs/superpowers/specs/2026-10-05-qortex-design.md:27`; `docs/DECISION_LOG.md:18`, «Python para conector y motor») y el mecanismo de dos reglas que no se negocian (`CLAUDE.md:21-25`). No rige hasta que Ignacio acepte el ADR-002 y el texto nuevo de esas reglas (§16).

**Cómo leer las citas.** `fichero:línea` se refiere al commit `ba46970`. `spec` = `docs/superpowers/specs/2026-10-05-qortex-design.md`; `plan` = `docs/superpowers/plans/2026-10-05-fase0-diagnostico.md`. Los ids `formulas-N`, `contrato-datos-N`, `seguridad-N`, `ingenieria-N`, `plan-vs-dod-N` y `coherencia-docs-N` son hallazgos de la revisión técnica del 2026-10-05, con su evidencia en `docs/REVISION-2026-10-05.md`. «Verificado con node» = reproducido con el motor extraído de `index.html:247-558` y node v22.22.0, fuera del repo. «Verificado con uv» y «verificado con Ajv» = comprobado en un directorio temporal con uv 0.8.17 y Ajv 8.20.0. «Supuesto» o «sin verificar» = no comprobado. Las horas son estimaciones del arquitecto (supuesto). Las URL de proyectos externos van en el texto y en §12; la lista completa está en `docs/REFERENCIAS.md`.

## 1. Resumen en 10 líneas

1. QORTEX lee NetSuite sin escribir y recomienda qué, cuánto y cuándo comprar, con costo puesto en almacén y calendario de pagos; una persona aprueba cada OC (`README.md:14-15`, `:22-23`).
2. Python extrae con SuiteQL por una sola sesión que solo permite `GET …/record/v1/…` y `POST …/query/v1/suiteql` al host exacto de la cuenta, y guarda un snapshot crudo en `salidas/`, fuera de git.
3. Python prepara el snapshot (series, lead time, ETA de lo que viene en camino, conversión a USD, supuestos marcados) y escribe `qortex_data.json` solo si valida contra un JSON Schema único.
4. El motor de políticas (ABC/XYZ, SS, ROP, EOQ, estados, costo puesto, caja) vive una sola vez, en `dashboard/motor.js`, porque el simulador recalcula en el navegador (`index.html:862-865`).
5. Regla: una fórmula, un lenguaje. Python no reimplementa el motor y `motor.js` no infiere fechas ni convierte monedas; en la Fase 1 todo pronóstico (por SKU y agregado) pasa a Python y el Holt-Winters de JS se retira.
6. `qortex_data.json` es la entrada del motor, no su salida: trae fecha de corte, importes en USD, país e Incoterm de cada proveedor y un mapa `procedencia` que separa dato de supuesto (sustituye la marca `"origen"` de `CLAUDE.md:24-25`).
7. La Fase 0 entrega datos reales cargados y un reporte de calidad con las líneas base pendientes del acta (`README.md:43-47`); no construye servidor, base de datos, pronóstico nuevo ni escritura en NetSuite.
8. Antes de mostrar datos reales, `motor.js` cambia nueve reglas (§6): crítico con ETA, tope de vida útil efectivo, SS sobre LT+R, sin OC con confianza baja, «sin venta» por ventas de 12 meses, costo puesto según Incoterm, inventario a costo promedio, pagos al embarque y simulador por país.
9. La IA externa (`window.claude`) se apaga en código con datos reales; se publica solo un HTML de un archivo, sin scripts de terceros al ejecutarse, con datos demo, `noindex` y protección de Vercel.
10. Cada etapa corre con un `make` y CI prueba Python y JS sin credenciales.

## 2. Contexto

**Actores.** Víctor, sponsor, y Edgar, aprobador final; ambos firman la Fase 2 (`README.md:22`, `:31-32`). Compras de Quamtex confirma los supuestos y aprueba cada OC (`README.md:92`, `CLAUDE.md:26-27`). El admin de NetSuite crea el rol y el token (B4, `docs/PROJECT_STATE.md:48`) y responde si hay Landed Cost (B6, `:50`). Ignacio corre el conector en su computadora con `op run` (`spec:33-35`). El forwarder y el broker no tocan el sistema: sus facturas y el CBP 7501 calibran el costo puesto desde el Quick Win.

**Sistemas.** NetSuite: única fuente de hechos, de solo lectura con OAuth1 TBA y un rol exclusivo (`docs/adrs/ADR-001-expediente-separado-solo-lectura.md:30-32`, en adelante `ADR-001`). 1Password, bóveda `Quamtex-REA` (`.env.example:8-13`). GitHub privado y Actions (`docs/PROJECT_STATE.md:15`; `.github/workflows/ci.yml`). Vercel, solo para la demo (B7, `docs/PROJECT_STATE.md:51`). El runtime de artifacts de claude.ai, que da `window.claude` (`index.html:889`). El Tomador de Pedido Web es otro expediente (`README.md:17-18`), pero usa la misma cuenta NetSuite y, por tanto, el mismo límite de concurrencia (tier sin verificar).

**Límites.** (1) Solo SuiteQL y `GET`; escribir exige un ADR y la firma de ambos dueños (`CLAUDE.md:16-18`, `ADR-001:38-39`). (2) Ninguna credencial en código, commits ni chat (`CLAUDE.md:19-20`). (3) Ningún dato del cliente en git (`CLAUDE.md:21-23`, `.gitignore:1-12`). (4) Un supuesto nunca pasa por dato (`CLAUDE.md:24-25`): esta arquitectura conserva la regla y cambia su mecanismo (mapa `procedencia`, §5 y §16). (5) Una persona aprueba cada OC (`CLAUDE.md:26-27`). (6) Propuesta, ADR-003 y regla 6 de `CLAUDE.md`: ningún dato de NetSuite va a un LLM; está decidido (`docs/DECISION_LOG.md:20`) pero no implementado (`index.html:821`, `:867-876`).

## 3. Vista de componentes

| Componente | Hace | NO hace | Hoy |
|---|---|---|---|
| `src/qortex/readonly.py` (candado) | Única puerta HTTP: `https` y host exacto; `GET` bajo `/services/rest/record/v1/` (incluido `metadata-catalog`); `POST` exacto a `/services/rest/query/v1/suiteql`; sin redirecciones; timeout; backoff ante 429 y 5xx; concurrencia 1 | Otros verbos u hosts (RESTlets incluidos); registrar cabeceras, cuerpos o filas | No existe; el plan prevé una lista negra (`plan:62-74`) |
| `conector.py` + `queries/*.sql` | Descubrimiento de esquema y sondas de permisos; 6 consultas paginadas y troceadas por año; snapshot crudo; plantilla de supuestos | Calcular políticas; correr en CI; escribir fuera de `salidas/` | Fuera del repo (`docs/PROJECT_STATE.md:36-37`) |
| `preparar.py`, `proveedores.py`, `supuestos.py` | Series mensuales netas; lead time medio, σ y n por proveedor (`spec:64`); regla única de ETA (§5); conversión a USD; precio realizado y costo promedio; clientes sin nombre; escribe el JSON solo si valida | Pronosticar en F0; rellenar huecos con 0 (`spec:117`); calcular SS, EOQ o estados | No existe |
| `calidad.py` | Chequeos de `spec:100-112`; líneas base de `README.md:43-47`; perfil de demanda; ETA estimadas; % de supuestos confirmados | Corregir NetSuite; decidir | No existe |
| Contrato: `schema/`, `contrato.py`, `dashboard/validar_esquema.js`, `validarCruzadas()` | Frontera Python → motor: el mismo esquema en los dos lados (jsonschema y validador Ajv generado) más las reglas R1–R6; error con la ruta JSON | Transportar salidas del motor, nombres de clientes o secretos | `cargarJSON` solo exige `skus`, `proveedores` y 12 meses (`index.html:552-557`) |
| `dashboard/motor.js` | ABC/XYZ, z, SS, ROP, objetivo, proyección diaria y estados, EOQ y topes, costo puesto por Incoterm, caja, `explicar()`; en F0 también el HW, por SKU (`index.html:393`) y agregado (`:511`) | Leer archivos, red o reloj; mutar la entrada; inferir ETA; convertir monedas | `index.html:247-558`, con `HOY` fijo (`:248`) y mutación de la entrada (`:381-383`) |
| `pronostico.py` (F1) | Agente Demanda con StatsForecast y backtest, por SKU y para la serie agregada de ventas | — | No se construye en F0 |
| `dashboard/index.html` y simulador | 6 pestañas, «¿Por qué?», carga local (`index.html:867-876`), sliders y tabla editable (`:854-866`), `procedencia` pintada | Llamar a NetSuite; guardar datos (no hay storage ni `fetch`, verificado con grep); mandar datos reales a una IA; cargar scripts de terceros al ejecutarse | `index.html:121-245` y `:561-892`; Chart.js desde cdnjs sin `integrity` (`:10`) |

**Los cinco agentes del spec (`spec:59-67`).** Demanda: HW en `motor.js` en F0 y `pronostico.py` en F1. Proveedores: `proveedores.py`, la única que la F0 necesita en Python (`plan-vs-dod-1`). Riesgo, Comprador y Tesorería: `motor.js`.

## 4. Flujo de datos de extremo a extremo

```
 1Password ─ op run ─► [make extraer] conector.py ─ readonly.py ─► NetSuite (SuiteQL + GET, solo lectura)
                          ├─► salidas/crudo/AAAA-MM-DD/*.jsonl   snapshot crudo (fuera de git)
                          └─► salidas/supuestos.json              plantilla: valores por origen, todo «supuesto»
                                      │  Compras confirma campo por campo (lo demás sigue «supuesto»)
 [make datos]    preparar.py + proveedores.py + contrato.py   (sin red: lee el snapshot)
                          │   ETA (regla única) · USD · lead time · series · procedencia
                          ├─► salidas/qortex_data.json            solo si valida (esquema + R1–R6)
 [make calidad]  calidad.py
                          └─► salidas/reporte_calidad.txt   ◄── salidas/conteo_fisico.csv (conteo KATIA)
 [make dashboard] ─► build/qortex.html   un archivo: motor + validador + Chart.js + datos DEMO
 navegador (local): «Cargar datos de NetSuite» → validar() → planificar(fecha_corte) → vistas
                    IA apagada si fuente ≠ demo
 [make publicar] ─► Vercel: solo build/ (demo, noindex, protección)
```

- **Corrida 1** (`make extraer`) es la única que toca NetSuite: sondas de permisos y de esquema (§10.1), 6 consultas troceadas por año y la plantilla `salidas/supuestos.json`.
- **Corrida 2** (`make datos`, `make calidad`) lee el snapshot sin red, así que es reproducible; si el snapshot tiene más de 7 días (supuesto), avisa y sugiere `make extraer`.
- **Carga.** El JSON real se abre con el botón «Cargar datos de NetSuite» en `build/qortex.html` local, con `FileReader` y sin `fetch` (como hoy, `index.html:867-870`); nunca en la página publicada ni en el artifact de claude.ai.
- **Frente a `README.md:89-98` y `spec:39-53`:** `supuestos_proveedores.json` pasa a `salidas/supuestos.json`, con secciones de proveedor y de SKU (`contrato-datos-4`); todo sale a `salidas/`, que ya está ignorada (`.gitignore:8`); `qortex_data.json` es la entrada del motor, no su salida (`coherencia-docs-2`). Los documentos que describen el flujo viejo (`CLAUDE.md:21-23`, `README.md:84-98`, `.env.example:3`) cambian en el mismo commit que el ADR-002 (§16).

## 5. Contrato de datos (`qortex_data.json` v1)

Fuente: **NS** = columna SuiteQL (nombres de la investigación, hipótesis hasta el descubrimiento de esquema de la corrida 1); **calc** = derivado por Python de datos de NetSuite; **sup** = supuesto hasta que Compras lo confirme. Todo importe del archivo está en USD.

**Raíz**

| Campo | Tipo | Unidad | Fuente | Oblig. | Nota |
|---|---|---|---|---|---|
| `version_esquema` | `"1"` | — | calc | sí | |
| `fecha_corte` | AAAA-MM-DD | fecha | calc | sí | `motor.js` deriva «hoy» de aquí; hoy es fijo (`index.html:248`) |
| `fuente` | `netsuite` \| `demo` \| `mixto` | — | calc | sí | Lo trae el archivo; hoy se fija al cargar (`index.html:871`). La IA solo funciona con `demo` |
| `moneda_base` | `"USD"` | — | calc | sí | |
| `tipo_cambio` | {ISO 4217: {`valor`, `fecha`, `procedencia`}} | USD por unidad | calc (de `transaction.exchangerate`) o sup | si algún proveedor no es USD (R6) | Trazabilidad: la conversión ya la hizo `preparar.py` |
| `meses` | AAAA-MM[] | mes | calc | sí | Consecutivos; el último es el mes anterior a `fecha_corte` (R5) |
| `parametros` | objeto | varias | sup | no | Sobrescribe los valores por defecto de §6.9, todos supuestos |
| `agregados.ventas_mes.pronostico` | {`metodo`, `f`[6], `sigma_h`[6], `mase`} | USD/mes | calc | no (F1: sí) | Pronóstico de Σ `clientes[].compras[].m` por mes: la serie de `index.html:507` |

**Proveedor**

| Campo | Tipo | Unidad | Fuente | Oblig. | Nota |
|---|---|---|---|---|---|
| `id` | string | — | NS (`vendor.id`) | sí | internalid, nunca el país (`contrato-datos-3`); único (R2) |
| `nombre` | string | — | NS (`companyname`) | sí | |
| `pais` | `CN` \| `MX` \| `BR` \| `EU` \| `US` \| `OTRO` | — | calc (dirección del vendor) o sup | sí | Sustituye `origen` (`index.html:300-308`); el simulador filtra por aquí |
| `moneda` | ISO 4217 | — | NS (`vendor.currency`) | sí | Informativa: los importes ya llegan en USD |
| `terminos` | string | — | NS (`BUILTIN.DF(terms)`) | sí | Texto para la UI (`index.html:657`) |
| `pagos` | [{`pct`, `ref`: orden \| embarque \| llegada, `dias`}] | fracción; días | sup | sí | Σ `pct` = 1 (R3) |
| `transito_dias` | int ≥ 0 | días | sup | si algún `ref` = embarque (if/then del esquema) | Embarque = llegada − `transito_dias` |
| `incoterm` | EXW \| FCA \| FAS \| FOB \| CFR \| CPT \| CIF \| CIP \| DAP \| DPU \| DDP | — | NS (`vendor.incoterm`, sin verificar en la cuenta) o sup | sí | Decide qué componentes suma el costo puesto (§6.7) |
| `lt`, `ltSd` | > 0; ≥ 0 | días | calc (recepción − OC, consultas 3 y 4) | sí | |
| `lt_n` | int ≥ 0 | recepciones | calc | sí | Con `lt_n` < 5 (sup), `lt` y `ltSd` toman el valor por origen, marcado supuesto |
| `revision` | int 1..90 | días | sup | sí | |
| `maritimo` | bool | — | sup | sí | |
| `fleteM3`, `acarreoM3` | ≥ 0 | USD/m³ | sup | sí | |
| `brokerPO` | ≥ 0 | USD/OC | sup | sí | |
| `seguro` | 0..0,05 | fracción de (costo + flete) | sup | sí | |
| `arancel` | 0..1 | fracción del valor aduanero | sup | sí | Hoy `arancel: 25` pasa sin aviso: base $455,63/u y $473,98/u puesto sobre FOB $17,50 (verificado con node) |
| `procedencia` | {campo: `netsuite` \| `calculado` \| `supuesto` \| `confirmado`} | — | — | sí | Una entrada por campo de `supuestos.json` (`contrato-datos-1`) |

**SKU**

| Campo | Tipo | Unidad | Fuente | Oblig. | Nota |
|---|---|---|---|---|---|
| `sku`, `item_id` | string | — | NS (`item.itemid`, `item.id`) | sí | `sku` único (R2) |
| `nombre`, `linea` | string | — | NS (`displayname`; `linea`: campo por definir) | sí | |
| `prov` | → `proveedores[].id` | — | NS (`itemvendor` preferido) | sí | Sin proveedor: fuera del JSON y al reporte (R1) |
| `alterno` | → `proveedores[].id` \| null | — | NS (otro `itemvendor`) o sup | no | `explicar()` muestra su nombre y país, no el id (hoy `index.html:538`) |
| `costo` | > 0 | USD/u | NS (`itemvendor.purchaseprice` o última OC), en USD | sí | Precio de compra **en el Incoterm del proveedor** |
| `costo_promedio` | > 0 | USD/u | NS (`aggregateitemlocation.averagecostmli`, Houston) | sí | Valora el inventario (§6.7); si falta, = `costo` con procedencia supuesto |
| `precio` | > 0 | USD/u | calc (venta neta 12 m / unidades netas 12 m) | sí | Ninguna consulta lo trae hoy (`contrato-datos-5`); sin ventas: último precio realizado o `costo` marcado supuesto |
| `hist` | número[] ≥ 0 | u/mes | calc (consulta 2 a nivel línea; las notas de crédito restan) | sí | Largo = `meses` (R4); un mes negativo va al reporte |
| `onhand` | número | u | NS (`quantityonhand`, Houston) | sí | < 0 → confianza baja |
| `back` | ≥ 0 | u | NS (`quantitycommitted` + `quantitybackordered`) | sí | |
| `en_transito` | [{`oc`, `proveedor`, `cantidad`, `eta`, `eta_fuente`: netsuite \| estimada \| supuesto}] | u; fecha | NS (OC abiertas) y regla única de ETA | sí (`[]` si nada) | Sustituye a `onorder`: posición = onhand + Σ `cantidad` − back |
| `cbm` | > 0 | m³/u | sup | sí | |
| `moq` | int ≥ 1 | u | sup | sí | Múltiplo de compra |
| `vida` | int ≥ 1 | meses | sup (sin columna estándar; campo custom o lote, sin verificar) | sí | |
| `peso` | > 0 | kg/u | NS (`item.weight` + `weightunit`, a kg) o sup | no (F1: sí) | Tope de contenedor y acarreo por peso (F1, §6.7) |
| `peligroso` | {`imdg_clase`: string \| null} | — | sup (o campo custom) | no (F1: sí) | Recargo de mercancía peligrosa (F1) |
| `clientes` | int ≥ 0 | clientes en 12 m | calc | sí | Regla «sensible» (`index.html:399`) |
| `calidad` | {`confianza`, `metodo`, `clase_demanda`, `n_meses`, `motivos`[]} | — | calc | sí | `contrato-datos-8` |
| `pronostico` | {`metodo`, `f`[6], `sigma_h`[6], `mase`} | u/mes | calc | no (F1: sí) | |
| `procedencia` | mapa | — | — | sí | |

**Cliente** (bloque opcional)

| Campo | Tipo | Unidad | Fuente | Oblig. | Nota |
|---|---|---|---|---|---|
| `id` | string | — | NS (`customer.id`) | sí | Sin nombre (`contrato-datos-7`). La tabla de clientes en riesgo pinta hoy `f.c.nombre` (`index.html:742`): con datos reales mostraría el texto «undefined», porque `esc()` hace `String(s)` (`:571`). T7 pasa a id + segmento |
| `segmento` | string \| null | — | NS (`customer.category`) | sí | |
| `inicio` | AAAA-MM | mes | calc (primera venta) | sí | Censurado por la ventana de historia |
| `compras` | [{`f`: fecha, `m` > 0}] | USD | calc (una por factura o venta de contado) | sí | Notas de crédito fuera de `clientes` y contadas en calidad (supuesto) |

**Quién convierte a USD.** `preparar.py`, una sola vez, con `tipo_cambio[moneda]` a la `fecha_corte`; la tasa sale de `transaction.exchangerate` de la última OC en esa moneda (columna según la investigación, sin verificar en la cuenta) o es supuesto. Qué columnas de importe vienen en moneda base y cuáles en la de la transacción (`netamount`, `foreignamount`, `rate`) se fija en el descubrimiento de esquema. `motor.js` no convierte: hoy suma todo como USD (`index.html:412-416`, `:444-447`). El riesgo cambiario entre el corte y el pago queda para F1 (§6.8).

**Regla única de ETA.** La aplica solo `preparar.py`; `motor.js` lee `en_transito[].eta` y nunca la infiere.
1. Línea de OC abierta con `expectedreceiptdate` (consulta 3) → esa fecha; `eta_fuente: netsuite`.
2. Línea sin esa fecha → fecha de la OC + `lt` del proveedor de esa OC; `eta_fuente: estimada`.
3. Si la fecha de 1 o 2 es anterior a `fecha_corte` (OC vencida) → `fecha_corte` + 1 día; `eta_fuente: supuesto`; la OC va al reporte.
4. Si `quantityonorder` (consulta 1) supera la suma de las líneas abiertas de Houston (por ejemplo, órdenes de transferencia), la diferencia entra como una línea con `oc: null`, `eta` = `fecha_corte` + ⌈`lt`/2⌉ y `eta_fuente: supuesto`. Es la única herencia de la regla actual (`index.html:475`), ahora en un solo sitio. Si las líneas suman más, mandan las líneas y calidad anota la diferencia.

El simulador solo suma su retraso a las líneas de proveedores con `pais = CN` que aún no llegan (§6.6).

**Reglas cruzadas** (en `contrato.py` y en `validarCruzadas()` de `motor.js`, fijadas por los mismos vectores de `tests/contract/`):
- **R1** `prov`, `alterno` y `en_transito[].proveedor` existen en `proveedores[].id`.
- **R2** `skus[].sku` y `proveedores[].id` son únicos.
- **R3** Σ `pagos[].pct` = 1 (tolerancia 1e-9).
- **R4** `hist.length` = `meses.length`.
- **R5** `meses` son consecutivos y el último es el mes anterior a `fecha_corte` (`contrato-datos-6`). Hoy `datosDemo()` arma `meses` con `toISOString()` de fechas locales (`index.html:291`, `:372`): con `TZ=Europe/Madrid` sale 2024-09…2026-08 en lugar de 2024-10…2026-09 (verificado con node). `demo.js` lleva meses fijos y CI corre las pruebas de JS también con un huso UTC+.
- **R6** toda `moneda` de proveedor distinta de `moneda_base` tiene entrada en `tipo_cambio`.

Lo demás (tipos, rangos, enums, `transito_dias` condicionado a `ref: embarque`, entradas de `procedencia`) lo expresa el esquema, y el mismo archivo valida en los dos lados.

**Sin estas reglas, hoy** (verificado con node): un `prov` inexistente lanza `TypeError` («reading 'lt'») y un proveedor sin `pagos`, otro («reading 'map'»); sin `fleteM3` o sin `cbm` salen 0 órdenes y costo `NaN` en las 24 filas; sin `revision`, los 24 SKUs salen «sin venta» y 0 órdenes; con `lt: null`, 2 órdenes por $70.189 en lugar de 3 por $167.356 y ningún crítico.

**`salidas/supuestos.json`** (sustituye a `supuestos_proveedores.json`, `README.md:91`, `spec:91-93`): `{proveedores: {id: {pais, incoterm, pagos, transito_dias, fleteM3, seguro, arancel, brokerPO, acarreoM3, maritimo, revision, procedencia}}, skus: {sku: {cbm, moq, vida, alterno, peso, peligroso, procedencia}}, tipo_cambio: {…}}`. La corrida 1 lo llena así, todo marcado `supuesto`: por proveedor, los valores de su `pais` tomados de `index.html:300-309`, Incoterm FOB si es marítimo y FCA si es terrestre, y `transito_dias` 35 (CN), 30 (BR) y 45 (EU), que reproducen las fechas de pago del demo (`:301`, `:303`, `:305`); por SKU, `cbm` según la presentación deducida de la unidad de compra (galón 0,0045; cuarto 0,0012; litro 0,0011; cubeta 0,022; kit 0,024; caja 0,006 m³/u, del catálogo demo `:313-336`), `moq` 1 y `vida` 12 meses (el mínimo del catálogo demo). Compras confirma campo por campo (`procedencia: confirmado`). Un proveedor con `pais: OTRO` o un SKU sin presentación reconocible no recibe valores: sale del JSON y va al reporte, sin ceros (`spec:117`). Así B5 deja de bloquear la Fase 0 (`plan-vs-dod-3`, `README.md:114`) y la sesión con Víctor muestra cuántos supuestos están confirmados.

**Campos nuevos y tarea del plan que los implementa** (cambios_plan): `fecha_corte`, `fuente` y `meses` (T5 escribe; T7 lee); `moneda` y `tipo_cambio` (T5 convierte; T7 muestra la tasa en «¿Por qué?»); `pagos.ref = embarque` y `transito_dias` (T5 plantilla; T7 `planificar()`, `index.html:445`, `:463`); `incoterm` (T5 plantilla; T7 costo puesto, `:412-413`, `:464`); `costo_promedio` (T3, T5; T7 `:435`, `:601`, `:603`, `:698`); `en_transito` (T3, T5 regla de ETA; T7 proyección y posición, `:406`, `:474-478`); `calidad` (T5, T6; T7 sin OC con confianza baja); `procedencia` (T5; T7 la pinta); clientes sin `nombre` (T5; T7 `:742`); `peso` y `peligroso` (T3, T5; T6 mide cobertura; los usa F1).

## 6. Modelo matemático (tras los hallazgos)

Notación: d [u/día]; D = 365·d [u/año]; LT, σLT y R (revisión) [días]; σd = σ_mes/√30,4 [u/día], con demanda diaria independiente (supuesto; `index.html:398`). LT es el efectivo: `lt` + 7·semanas de retraso simulado si `pais = CN`.

**6.1 Pronóstico** [u/mes]. Hoy, Holt-Winters multiplicativo con tendencia amortiguada (`index.html:263-288`): α 0,35, β 0,1 y φ 0,9 fijos (`:277`); índices estacionales promediados por año, encogidos un 30 % y acotados a [0,35; 2,5] (`:270-273`), sin γ; tendencia 0 si n < 24 (`:276`); σ como RMSE dentro de la muestra desde t = 6 (`:280`, `:286`). Con la serie sin ruido 100 + 2t pronostica 105,6 frente a 124 con n = 12, 129,4 frente a 148 con n = 24 y 198,1 frente a 220 con n = 60 (verificado con node). La causa principal es la normalización anual de los índices, que convierte la tendencia de cada año en «estacionalidad» (`formulas-1`, corregido). Tiene dos usos: por SKU (`:393`) y sobre la serie mensual de ventas de los clientes, que alimenta la pestaña Clientes y el gráfico de ventas totales (`:507`, `:511`, `:516`, `:695`).
- **F0:** el HW solo corre si `calidad.metodo = hw`, que Python fija con n ≥ 24 y clase smooth o erratic; si no, confianza baja y sin OC (`spec:116`). Sus parámetros se declaran supuestos. El plan B de `spec:63` (promedio móvil o Croston) no se construye en JS (`formulas-7`; §7).
- **F1, en Python con StatsForecast** (https://github.com/Nixtla/statsforecast), para las dos series: clase por ADI/CV² con cortes 1,32/0,49 (Syntetos-Boylan; umbrales sin verificar en el código de sktime, https://github.com/sktime/sktime). smooth → AutoETS {ANN, AAdN}, estacional solo si n ≥ 36 (Hyndman y Kostenko, https://robjhyndman.com/papers/shortseasonal.pdf: mínimo m + 5 = 17 y «substantially more» en la práctica); erratic → AutoETS o Theta; intermittent → CrostonSBA (TSB si hay ceros finales); lumpy → mediana de SBA, TSB e IMAPA. El modelo debe batir a Naive y SeasonalNaive(12) en MASE (Hyndman 2006, https://robjhyndman.com/papers/foresight.pdf) con backtest de origen rodante; para intermitentes, RMSSE y pinball; nunca MAPE. La σ del SS es el RMSE fuera de muestra a LT + R. CI exige sesgo < 3 % sobre series sintéticas.

**6.2 ABC/XYZ.** ABC por ingreso acumulado de 12 m (Σ hist·precio), cortes 0,80/0,95 (`index.html:379-381`). XYZ por CV bruto de 12 m, cortes 0,25/0,50 (`:382-383`). F0: cortes declarados en `parametros`. F1: CV sobre los residuos del pronóstico, porque hoy la estacionalidad cuenta como variabilidad y GR-401 sale AY (`formulas-6`; clase AY verificada con node).

**6.3 Servicio y z.** Hoy A 0,98 (A-Z 0,97), B 0,95, C 0,90, con piso 0,97 para «sensibles» (clase A o ≥ 15 clientes) (`index.html:399-402`; verificado con node). El spec dice 95/90/85 (`spec:69`) y el indicador del panel, «Meta 97 %» (`:607`). z = Φ⁻¹(ns) por Acklam (`:256-260`); z(0,95) = 1,6449 (verificado con node). Queda una sola tabla en `parametros`, marcada supuesto (`spec:147`); cuál, lo decide Ignacio (§16).

**6.4 SS, ROP y objetivo.** d = media del pronóstico de los nM meses siguientes / 30,4, con nM = ⌈(LT + R)/30,4⌉ acotado a 1–6 (`index.html:396-397`). **SS [u] = z·√((LT + R)·σd² + d²·σLT²)**: hoy usa LT (`:404`) aunque el objetivo cubre LT + R (`:408`) (`formulas-5`); GR-401 pasa de 224 a 264 u, QL-501 de 98 a 115 y WM-301 de 180 a 192 (verificado con node). σLT × 1,3 con retraso simulado (`:392`, supuesto). ROP [u] = d·LT + SS; objetivo S [u] = d·(LT + R) + SS; posición [u] = onhand + Σ `en_transito.cantidad` − back; necesidad [u] = max(0, S − posición) (`:405-409`). **Simulador por país (F0):** hoy filtra por `pv.id === 'CN'` (`:391-392`, `:411`); con ids reales de NetSuite, el escenario +4 semanas y +25 % de arancel a China deja el total en $167.356, sin efecto, y con ids demo lo sube a $224.126 (verificado con node; `contrato-datos-3`). Pasa a filtrar por `pais`.

**6.5 Cantidad.** Hoy EOQ [u] = √(2·D·S/H), con S = costoPedido + brokerPO [USD] cargado a cada SKU y H = base·0,22 [USD/u·año] (`index.html:414-415`); tope = d·vida·30,4·0,75 (`:416`); qty = ⌈max(necesidad, min(EOQ, tope))/moq⌉·moq (`:419-420`). FP-241 con vida de 1 mes y sin stock: tope 51 u, qty 252 u, 113 días de demanda (`formulas-3`); RF-101: EOQ 1.014 u frente a 507 con S = 150, y DF-601, 2.354 frente a 1.177 (`formulas-4`); todo verificado con node. **Queda (F0):** vida al llegar [días] = 0,75·vida·30,4 − LT; stock al llegar [u] = max(SS, posición − d·LT); tope_ef [u] = max(0, d·vida al llegar − stock al llegar); q* = min(max(necesidad, EOQ), tope_ef). Se redondea hacia arriba al múltiplo si el resultado no pasa de tope_ef; si pasa, hacia abajo. Si necesidad > tope_ef, la línea lleva la razón `necesidad_excede_vida_util`; si tope_ef < moq, q = 0 con `tope_menor_que_multiplo`; en ambos casos decide la persona. `parametros` declara si costoPedido es por OC o por línea. **F1:** reabastecimiento conjunto, T* = √(2·S_OC/Σ Dᵢ·Hᵢ) y qᵢ = Dᵢ·T*.

**6.6 Estados y proyección diaria.** Las llegadas son `en_transito[].eta` (regla única de §5); hoy todo el tránsito llega a la mitad del lead time del proveedor base (`index.html:475`), sin el retraso simulado. Proyección para t = 0…180 días (`:473`): s(0) = onhand − back; cada día entra lo que llega (más 7·semanas de retraso si el proveedor de la línea es de China) y sale d_t = pronóstico del mes/30,4 (como `:477`); lo que no se sirve se pierde (supuesto). t_q [días] = primer día con demanda no servida.
- **Crítico:** t_q < LT. Hoy, cobertura = posición/d < LT (`:407`, `:424`), que cuenta el tránsito como si ya estuviera en almacén: RF-132, con 10 días en almacén y 90 en tránsito, sale «ordenar» con faltante 0, pero la proyección pasa 29 días en cero, del día 10 al 38 (verificado con node; `formulas-2`). **Faltante** [días] = días con demanda no servida antes de LT; **venta en riesgo** [USD] = Σ demanda no servida·precio (hoy `:433-434`).
- **Ordenar** (posición ≤ ROP, o la cruzará antes de la próxima revisión, `:425`, `:428-430`) y **exceso** (posición/d > LT + R + 150, `:426`) no cambian.
- **Sin venta (F0):** onhand > 0, unidades netas de 12 m ≤ U_min y ventas de 12 m ≤ V_min (supuestos; por defecto 0 y 0, es decir, «sin ventas en 12 meses», como dice el texto de `:543`). Hoy decide el pronóstico, d < 0,2 u/día (`:423`).
- **Confianza baja** (`calidad.confianza`) → qty 0 con el motivo visible (`spec:116`).
- Las vistas que comparan la «cobertura» con la llegada pasan a t_q (`index.html:168`, `:598`, `:616`, `:641`, `:779`); exceso sigue con posición/d.

**6.7 Costo puesto en almacén [USD/u]** (`index.html:410-455`). Hoy suma siempre flete, seguro, arancel, broker y acarreo sobre `costo` (`:412-413`) y paga esa logística a la llegada (`:464`): con un proveedor CIF o DDP, el flete y el arancel se cuentan dos veces. **Queda (F0):** qué se suma depende del `incoterm` (supuesto hasta calibrar con un CBP 7501):

| Incoterm | Flete = fleteM3·cbm | Seguro | Arancel | Broker | Acarreo = acarreoM3·cbm |
|---|---|---|---|---|---|
| EXW, FCA, FAS, FOB | sí | s·(costo + flete) | a·costo | sí | sí |
| CFR, CPT | no (va en el precio) | s·costo | a·costo (aproximación conservadora) | sí | sí |
| CIF, CIP | no | no | a·costo (aproximación conservadora) | sí | sí |
| DAP, DPU | no | no | a·costo | sí | no si el lugar convenido es el almacén (supuesto) |
| DDP | no | no | no | no | no |

El valor aduanero de EE.UU. es el de transacción sin flete ni seguro internacionales (según la investigación, sin fuente primaria registrada); con términos C, a·costo lo sobrestima en a·(flete + seguro incluidos), y se marca supuesto. Con EXW, los gastos de origen deben ir dentro de `fleteM3` (supuesto declarado). El resto no cambia: aduana y pedido = (brokerPO, si aplica, + costoPedido)/unidades de la OC (`:448`); anticipo = costo·tasa·días de adelanto/365 (`:449`, días según §6.8); mantener = base·0,22·min(240, q/2d + SS/d)/365 (`:450-451`); margen = (precio − unitario)/precio (`:455`).

**Valor del inventario:** onhand·`costo_promedio`. Hoy usa `costo`, el precio de compra en el Incoterm (`:435`), y también así valora la rotación (`:601`), el capital inmovilizado (`:603`) y el inventario proyectado (`:698`).

**F1:** arancel por capas MFN + max(301, IEEPA) + 232 por HTS × origen × fecha (https://github.com/wave03F/landed-cost-engine); China ≈ 25 % + MFN 3,2–3,7 % según la investigación. MPF 0,3464 % (entre $33,58 y $651,50 por entrada) y HMF 0,125 % marítimo, cifras FY2026 de la investigación sin fuente primaria (como componentes, https://github.com/opsloft/tariff-resolver). Broker por valor; THC e ISF. Contenedores = max(⌈m³/28⌉, ⌈kg/tope_kg⌉) con `peso` (28 m³ hoy, `:461`; tope_kg supuesto); recargo de mercancía peligrosa con `peligroso`; acarreo por peso, el driver de HyVoid (https://github.com/HyVoid/landed-cost-calculator-excel) y el reparto `by_weight` de Odoo (https://github.com/odoo/odoo/blob/17.0/addons/stock_landed_costs/models/stock_landed_cost.py). LCL cuando conviene: la OC de Europa del demo va con 0,73 m³ en un 20′ al 2,6 % (verificado con node; `:461`). Calibración: ±5 % total y ±10 % por componente contra una importación real. Propuesta del arquitecto, no hallazgo: mantener = tasa + i_físico, para que el 22 % se mueva con la tasa del simulador y no cobre dos veces el costo de capital.

**6.8 Caja [USD]** (`index.html:459-466`, `:652-654`).
- llegada_OC = `fecha_corte` + LT; embarque_OC = llegada_OC − `transito_dias`.
- fecha(p) = base(p.ref) + p.dias, con base(orden) = `fecha_corte`, base(embarque) = embarque_OC y base(llegada) = llegada_OC; monto(p) = p.pct·Σ q·costo. Hoy solo existen orden y llegada (`:445`, `:463`): «70 % al embarcar» se escribe como llegada − 35 y «Neto 60 desde embarque» como llegada + 15 (`:301`, `:305`), supuestos implícitos.
- Logística = Σ q·(componentes que suma el Incoterm) + brokerPO si aplica, a la llegada (como `:464-465`).
- Días de adelanto (costo financiero, §6.7) = Σ p.pct·max(0, llegada_OC − fecha(p)).
- Con `transito_dias` 35, 30 y 45 y pagos al embarque, las fechas de CN, BR y EU del demo no cambian (`:301`, `:303`, `:305`): el golden de caja debe salir idéntico.
- **Fases.** F0: `ref: embarque` en `planificar()` (T7) e importes en USD convertidos por `preparar.py` (T5); vista mensual desde `fecha_corte` (hoy desde `HOY`, `:293`, `:652`). F1: vista semanal (`spec:67`), MPF/HMF y escenario de tipo de cambio en el simulador.

**6.9 Pasan a `parametros` (supuestos).** Niveles de servicio, piso «sensible» y 15 clientes (`index.html:399-401`). Tasa 0,09, mantener 0,22 y costoPedido 150 (`:376`), con su base (OC o línea). Factor 0,75 (`:416`). +150 días de exceso (`:426`); U_min y V_min de «sin venta». 240 días (`:450`). 28 m³ (`:461`). Cortes ABC/XYZ (`:381-383`). Encogimiento 0,7, límites 0,35–2,5, α, β y φ del HW (`:272`, `:277`). σLT × 1,3 (`:392`). Horizonte de 180 días y banda del 80 % con z = 1,28 (`:473`, `:674`). Constantes de clientes: 1,4 × ciclo y 200 días (`:502`), ticket 600 y frecuencia 1,2 (`:513-514`), factor 0,5 (`:516`, `:739`), ventas12/4 (`:518`). De `preparar.py`: `lt_n` mínimo 5, ETA vencida + 1 día, snapshot de más de 7 días, `vida` 12 meses y `moq` 1 por defecto.

## 7. Un solo motor: cómo evitar que el JS y el Python diverjan

**Problema.** El spec y el plan ponen el motor en Python (`spec:27`, `:43-57`; `plan:89-100`), pero el motor completo ya vive en JS (`index.html:247-558`) y el simulador lo necesita en el navegador. Divergen antes de que exista el segundo motor: niveles de servicio (`spec:69` frente a `index.html:400-401`), plan B y MAPE (`spec:63`) (`ingenieria-1`, `coherencia-docs-2`).

**Decisión (ADR-002): una fórmula, un lenguaje.** Python: extracción, preparación (series, lead time, regla única de ETA, conversión a USD, precio y costo promedio), calidad, validación al escribir y, en F1, todo pronóstico con backtest. `dashboard/motor.js`: ABC/XYZ, z, SS, ROP, proyección diaria y estados, EOQ y topes, costo puesto por Incoterm, caja, `explicar()` y validación al cargar.

1. Python nunca reimplementa el motor. Si F1 necesita el plan fuera del navegador, `qortex plan` ejecuta el mismo `motor.js` con node.
2. `motor.js` no infiere fechas ni convierte monedas: lee `en_transito[].eta` e importes en USD.
3. **Ninguna serie se pronostica en dos sitios.** En F0, el HW de JS pronostica por SKU (`index.html:393`) y la serie agregada de ventas de las pestañas Clientes y Proyección (`:511`, `:516`, `:695`). En F1, `pronostico.py` escribe `skus[].pronostico` y `agregados.ventas_mes.pronostico`, y el HW se borra cuando ambos son obligatorios (contrato v2), no antes: sin el segundo, la pestaña Clientes y el gráfico de ventas totales quedarían sin pronóstico. La proyección lineal de clientes nuevos (`:508-510`) solo existe en JS y se queda ahí, declarada supuesto. El demo pasa a ser una fixture sintética con ambos campos.
4. `motor.js` es un script clásico con guardia `module.exports` (como `index.html:558`), no un módulo ES, porque Chrome bloquea módulos ES abiertos desde `file://` (comprobarlo en T7). Recibe `fecha_corte` y no muta la entrada: hoy `clasificar` escribe `_abc`, `_xyz` e `_ing12` en cada SKU (`index.html:381-383`; verificado con node).
5. Lo único escrito dos veces son las reglas cruzadas R1–R6 (`contrato.py` y `validarCruzadas()`), fijadas por los mismos vectores en pytest y en node. El resto de la validación sale del mismo `schema/qortex_data.schema.json`: jsonschema en Python y el validador Ajv generado en el navegador (§9).
6. `node scripts/golden.mjs` congela la salida de `planificar()` con la fixture; todo cambio numérico es un diff revisable.

**Descartadas.** Todo en Python, como recomendaba la investigación (`docs/REFERENCIAS.md` §7–§8): el simulador pierde la recalculación o exige servidor, que la F0 descarta (`spec:31-35`). Dos motores con paridad: duplica lo que ya diverge. Pyodide: pesado y sin verificar con StatsForecast. HW en JS solo para el agregado en F1: dos métodos de pronóstico, uno de ellos sin backtest.

## 8. Estructura del repositorio

```
qortex/
├── README.md, CLAUDE.md, SEGUIMIENTO.md     acta, reglas, tablero comercial
├── Makefile                   un comando por etapa
├── pyproject.toml, uv.lock, .python-version (3.12)
├── package.json, package-lock.json   solo desarrollo: Ajv (versión exacta) para generar el validador
├── .env.example               6 referencias op://
├── .gitignore, .gitleaks.toml, .pre-commit-config.yaml   candados locales
├── .github/workflows/ci.yml   make ci, sin credenciales
├── src/qortex/
│   ├── cli.py                 qortex extraer | preparar | calidad | validar
│   ├── readonly.py            candado: host exacto, GET record/v1, POST suiteql, sin redirecciones
│   ├── conector.py            único módulo que habla con NetSuite (antes qortex_conector.py)
│   ├── queries/01..06_*.sql   inventario, ventas, OC, recepciones, proveedores, pedidos de venta
│   ├── preparar.py            snapshot + supuestos → qortex_data.json (ETA, USD, series, procedencia)
│   ├── proveedores.py         lead time medio, σ y n por proveedor
│   ├── supuestos.py           plantilla con valores por origen y presentación, marcados «supuesto»
│   ├── calidad.py             chequeos, líneas base, perfil de demanda
│   ├── contrato.py            jsonschema + reglas cruzadas R1–R6
│   └── pronostico.py          (F1) StatsForecast y backtest, por SKU y agregado
├── schema/qortex_data.schema.json   contrato único
├── dashboard/
│   ├── index.html             interfaz, sin fórmulas
│   ├── motor.js               motor de políticas ÚNICO + validarCruzadas()
│   ├── demo.js                datos de demostración con meses fijos (sale de index.html:296-373)
│   ├── validar_esquema.js     generado con Ajv standalone desde schema/; CI comprueba que está al día
│   ├── vendor/chart.umd.min.js, vendor/SHA256SUMS   Chart.js 4.4.1, sin CDN
│   └── vercel.json            X-Robots-Tag: noindex, nofollow
├── scripts/guard_datos.sh, compilar_validador.mjs, construir_dashboard.py, golden.mjs
├── tests/
│   ├── test_*.py              readonly, conector, proveedores, preparar, calidad, contrato
│   ├── js/*.test.mjs          motor, contrato, ia, xss
│   ├── fixtures/              solo sintéticos («sintetico» en el nombre)
│   ├── golden/                entrada y salida esperada del motor
│   └── contract/              vectores válidos e inválidos, compartidos por pytest y node
├── docs/                      PROJECT_STATE, DECISION_LOG, ARQUITECTURA, REFERENCIAS, RUNBOOK, adrs/, superpowers/
├── salidas/  (ignorado)       crudo/, supuestos.json, qortex_data.json, reporte_calidad.txt, conteo_fisico.csv
└── build/    (ignorado)       qortex.html (un archivo, solo demo) + vercel.json
```

`index.html` pasa a `dashboard/` y se separan `motor.js` y `demo.js` sin cambiar la lógica (golden «antes»). `qortex_conector.py` pasa a `src/qortex/conector.py` después de importarlo tal cual (`plan:55-58`). `README.md:73-87` cambia en consecuencia (§16).

## 9. Ingeniería

- **Python 3.12** (CI ya lo usa, `ci.yml:30`; el plan dice 3.11+, `plan:9`) con uv y `uv.lock`. `uv init --package` da src layout con backend `uv_build` (verificado con uv; pone `requires-python` según el Python local, así que se fija `>=3.12` a mano). Guía: https://pydevtools.com/handbook/explanation/modern-python-project-setup-guide-for-ai-assistants/. Dependencias: `requests`, `requests-oauthlib`, `jsonschema`; dev: `pytest`, `ruff` (E, F, I, B, UP, S) y `pre-commit`; extra `pronostico = ["statsforecast"]` en F1. Script `qortex = "qortex.cli:main"`. El snapshot es JSONL de la biblioteca estándar: sin pandas en F0.
- **Node ≥ 20** (verificado con v22.22.0) para `node --test`, el golden y generar el validador. npm solo en desarrollo, para `ajv` con versión exacta en `package-lock.json`; el navegador no descarga nada.
- **Validador del navegador.** `scripts/compilar_validador.mjs` genera `dashboard/validar_esquema.js` con el modo standalone de Ajv (https://github.com/ajv-validator/ajv). Verificado con Ajv sobre un esquema de prueba con `if/then`, `contains`, `pattern` y `enum`: el código generado no contiene `require()` ni `new Function`, y el error trae la ruta (`/proveedores/0 must have required property 'transito_dias'`). Con `minLength`/`maxLength` importa `ajv/dist/runtime/ucs2length` y con `uniqueItems`, `ajv/dist/runtime/equal`; el esquema no los usa (cadena no vacía con `pattern`, unicidad en R2) y CI falla si el generado contiene `require(`. Ajv en modo estricto exige `type` explícito en los subesquemas de `if` (también verificado).
- **Pruebas.** Motor (`node --test`): casos a mano (EOQ con 1.200/50/2 = 244,9 y 252 con múltiplo 12, `spec:129`, `plan:93`; SS de `plan:94`); propiedades (SS crece con CSL, σd y σLT; SS = 0 con CSL 0,5; qty múltiplo; qty ≤ tope cuando manda; sin `NaN`; entrada intacta); golden; un caso por grupo de Incoterm; equivalencia de pagos al embarque; RF-132 sintético (crítico con 10 días en almacén y 90 en tránsito); «sin venta»; y la batería completa también con `TZ=Europe/Madrid`. Contrato: vectores R1–R6 compartidos. Preparación: regla de ETA (4 casos), conversión a USD, lead time con `lt_n`. Candado: verbos, host, rutas, redirecciones y timeout. Conector: paginación, troceo y 401/403/429 con respuestas grabadas sintéticas. Calidad: un test por chequeo y por línea base. IA: `iaPermitida()` falsa si `fuente` ≠ demo. XSS: JSON malicioso. F1: sesgo < 3 %.
- **CI.** Falla si no hay pruebas (hoy pasa en verde sin ellas, `ci.yml:33-38`), deja de instalar un `requirements.txt` inexistente (`ci.yml:34`) y corre `make ci`: lint, test, guard, dashboard, validador al día y hash de Chart.js. Pre-commit con gitleaks y guard actúa antes del push (`ingenieria-6`).
- **Makefile (un comando por etapa).** `setup` (uv sync, npm ci, pre-commit install); `lint`; `test` (pytest y node); `guard`; `validador`; `ci`; `extraer` (`op run --env-file=.env.example -- uv run qortex extraer`); `datos` (preparar y validar, sin red); `calidad`; `fase0` (extraer, datos y calidad); `dashboard` (→ `build/qortex.html`); `demo` (abre el build); `publicar` (guard, dashboard, comprobación de `build/` y `vercel deploy build --prod` con `VERCEL_TOKEN` en el entorno).

## 10. Seguridad

**10.1 Rol y permisos (lista para pedir en B4).**
- **Setup:** *Log in using Access Tokens* y *REST Web Services*, Full (verificado en https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_5085602973.html). *Records Catalog*, View: para el descubrimiento de esquema de la corrida 1 (§5, §13); lo pide la investigación, sin fuente primaria. *Custom Item/Entity/Body/Column Fields*, View: solo si vida útil, país o peso viven en campos custom (pregunta 7; investigación, sin fuente primaria).
- **Reports:** *SuiteAnalytics Workbook*, Edit según Oracle; que baste View es un supuesto a probar.
- **Transactions, View:** Find Transaction, Purchase Order, Item Receipt, Invoice, Cash Sale, Credit Memo, Sales Order (consulta 6) e Item Fulfillment. Condicionales: Vendor Bill, solo si B6 dice que el costo de importación está en facturas; *Inbound Shipment*, solo si B6 confirma que Quamtex usa Inbound Shipments (tablas `inboundshipment*`; nombre exacto del permiso por confirmar con el admin); Transfer Order, solo si hay más de una Location con stock (pregunta 3).
- **Lists, View:** Items, Vendors, Customers, Locations, Currency y Units of Measure; Subsidiaries solo si la cuenta es OneWorld. La investigación no identificó qué permiso pide la tabla `term`: la sonda lo detecta.
- **Nunca:** Create, Edit o Full en transacciones o listas; SuiteScript; despliegues de RESTlet (confirmarlo con el admin); Administrator.
- **Integración:** solo TBA, usuario dedicado y concurrencia reservada de 1 a 2 en Integration Governance. Los límites por tier vienen de la investigación (Standard 5, Premium 15, Enterprise 20; sin URL primaria registrada); el de Quamtex no se conoce.
- **Evidencia de B4:** la exportación de permisos del rol, anotada en `SEGUIMIENTO.md` (`seguridad-3`). La corrida 1 empieza con una sonda: un `SELECT … WHERE ROWNUM <= 1` por tabla (item, vendor, customer, transaction, transactionline, aggregateitemlocation, itemvendor, term, previoustransactionlinelink) y `GET /services/rest/record/v1/metadata-catalog`; un 403 la detiene y nombra la tabla. Nunca se «prueba» una escritura.

**10.2 Candado** (`readonly.py`; hoy el plan prevé una lista negra, `plan:64-71`). (1) `https` y host exacto `{cuenta en minúsculas, _ → -}.suitetalk.api.netsuite.com`; el realm OAuth va en mayúsculas con guion bajo, y los RESTlets, en otro host, quedan fuera. (2) Solo `GET` bajo `/services/rest/record/v1/` (el `metadata-catalog` cabe ahí) y `POST` exacto a `/services/rest/query/v1/suiteql`; lo demás lanza `ReadOnlyViolation`, que muestra verbo y ruta, nunca la consulta. (3) `allow_redirects=False`; `timeout=(5, 60)`; reintento solo en 429/502/503/504 con backoff, jitter, 4 intentos y `Retry-After`; concurrencia 1 (`seguridad-4`). (4) El prefijo `SELECT`/`WITH` se queda como chequeo barato. (5) Un test solo permite `import requests` en `readonly.py`, porque el grep de `plan:71` se esquiva. (6) Con 401/403 se detiene y dice qué permiso falta (`spec:118`).

**10.3 Secretos.** Seis `op://Quamtex-REA/qortex-netsuite/*` (`.env.example:8-13`) resueltos con `op run`, que enmascara la salida (https://www.1password.dev/cli/reference/commands/run/). CI nunca recibe credenciales de NetSuite. `VERCEL_TOKEN` va en el entorno, nunca en la línea de comandos. Rotación y revocación: `docs/RUNBOOK.md` (§17).

**10.4 Datos fuera de git.** Hoy: `.gitignore:2-4` lista tres nombres exactos, `.gitignore:6-8` cubre `*.xlsx`, `*.csv` y `salidas/`, y `.gitignore:10-12`, los `.env`; `scripts/guard_datos.sh:4` combina esos tres nombres con la extensión `\.(csv|xlsx)$` y exime `tests/fixtures/`; el guard y gitleaks solo corren en CI (`ci.yml:11-22`), es decir, después del push. Huecos: `*.json` con otro nombre, `*.jsonl`, `*.parquet`, `*.xls`, `*.xlsm`, `*.log`, `build/`, `.vercel/` y fixtures sin marca de sintético. Queda: todas las salidas en `salidas/` (`ingenieria-7`); `.gitignore` con `build/`, `.vercel/`, `node_modules/`, `*.jsonl`, `*.parquet`, `*.xls`, `*.xlsm` y `*.log`; guard que además rechaza `*.json` fuera de `schema/`, `tests/` y `package*.json`, y fixtures sin «sintetico» en el nombre; pre-commit. El conteo físico entra como `salidas/conteo_fisico.csv`.

**10.5 Publicación privada.** Hoy no hay `noindex` (`index.html:4-6`) ni `vercel.json`, y desplegar desde la raíz (`README.md:112`) expondría el acta con precios (`README.md:63-71`), `SEGUIMIENTO.md` y `docs/` (`seguridad-2`, `ingenieria-3`). Queda: se publica solo `build/`; meta robots y `X-Robots-Tag`; protección de Vercel también en producción (https://vercel.com/docs/deployment-protection/usage-and-pricing), comprobada en incógnito, que cierra B7; nunca datos reales; `.vercel/`, que el CLI crea al enlazar el proyecto, en `.gitignore` sin barra inicial porque su ubicación depende de la versión. La única cifra real de la página es el agregado del conteo (−961 u, `index.html:154`), que ya está en el acta (`README.md:38`). Para «No approval received» (`docs/PROJECT_STATE.md:51`), la investigación sospecha del harness, sin verificar: publicar desde la terminal del dueño.

**10.6 «Pregúntele a QORTEX» y `window.claude`.** `sample` solo existe en el runtime de artifacts de claude.ai (`index.html:889`); en Vercel o en un archivo local es `null` y la tarjeta se oculta (`:887-891`, `:793`). Al cargar un JSON real dentro del artifact, el manejador solo cambia la fuente (`:867-876`) y `preguntarIA` solo comprueba `sample` (`:821`); así, `promptGeneral` enviaría hasta 30 SKUs con costos, las OC con sus pagos y métricas de clientes (`:808-818`), contra lo decidido en `docs/DECISION_LOG.md:20` (`seguridad-1`, `coherencia-docs-4`). Queda: `iaPermitida()` = `fuente === 'demo'` y `sample` presente; al cargar, `sample = null` y se ocultan `#askCard` y `#aiRow`; `preguntarIA` sale si `iaPermitida()` es falsa; `window.claude` solo se consulta con datos demo; prueba en node. La barrera se registra en el ADR-003 y en una regla 6 nueva de `CLAUDE.md` (texto en §16), junto con las reglas 3 y 4, que cambian por el contrato. El JSON real se carga en `build/qortex.html` local, nunca en el artifact.

**10.7 XSS y dependencias de terceros.**
- `esc()` en todo campo del JSON que hoy entra sin escapar en `innerHTML` o en atributos (`index.html:614`, `:616`, `:639-641`, `:657`, `:667`, `:688`, `:762-766` en `data-p`, `:776`, `:780`), con una prueba de JSON malicioso (`seguridad-7`).
- **Ningún script de terceros al ejecutarse en `build/qortex.html`.** Chart.js 4.4.1, que hoy llega de cdnjs sin `integrity` (`:10`), se vendoriza con su SHA-256 comprobado en `make ci`. El validador se genera con Ajv standalone (§9): sin CDN ni `new Function`. Descartadas: Ajv desde cdnjs con SRI (sigue dependiendo de la red y de `new Function`) y vendorizar `ajv7.min.js` (sin red, pero con `new Function`), que queda como plan B si el código generado necesitara helpers de Ajv.
- Google Fonts (`:7-9`) solo afecta a la tipografía y expone IP y referrer: deuda (§17).
- CSP: no en F0. Ya no choca con Ajv ni con CDNs y en `build/` no hay `window.claude`, pero `connect-src 'none'` exige hashes de los scripts en línea: F1.

**10.8 Logs.** Método, ruta, estado, filas y duración; nunca `Authorization`, cuerpos ni filas; `*.log` en `.gitignore` (`seguridad-5`).

## 11. Evolución por fases

| Fase | Qué cambia en la arquitectura | Qué NO se construye |
|---|---|---|
| **0 · Diagnóstico** (`README.md:67`) | Candado y conector; preparación (regla única de ETA, USD, lead time), calidad con líneas base y contrato en Python; `motor.js` con las nueve reglas de §6, validación al cargar e IA apagada con datos reales; build de un archivo sin scripts de terceros, publicado y protegido | Pronóstico en Python y los otros 4 agentes en Python; servidor, base de datos, corrida programada; escritura; reabastecimiento conjunto; arancel por capas, MPF/HMF, THC, LCL, tope por peso y recargo de peligrosos (el contrato ya prevé `peso` y `peligroso`); caja semanal y riesgo cambiario; exportar OC; IA con datos reales; CSP; SupplyNetPy |
| **Quick Win** (`README.md:68`) | Backtest de los SKUs del proveedor con más faltantes (`spec:146`); costo de pedido repartido por OC; costo puesto calibrado con una importación real (hoja de varianza de HyVoid); OC aprobada exportada a CSV o PDF para captura manual | Escritura en NetSuite |
| **1 · Motor completo** (`README.md:69`) | `pronostico.py` para SKUs y agregado; contrato v2 con ambos pronósticos, `peso` y `peligroso` obligatorios; retiro del HW de JS; XYZ por residuos; σ de backtest; costo puesto completo (capas, MPF/HMF, broker por valor, THC, ISF, contenedor por m³ y peso, recargo de peligrosos, LCL); caja semanal y escenario cambiario; reabastecimiento conjunto; presupuesto (score de Lokad); pantalla de aprobación (patrón Odoo); desempeño de proveedor; comparación con Inventory Optimization nativo; CSP. Corrida programada o servidor solo con ADR (`spec:34-35`) | Escritura en NetSuite |
| **2 · Propone y aprueba** (`README.md:70`) | ADR y firma de ambos dueños (`ADR-001:38-39`); rol aparte que solo crea OC pendientes de aprobación; sesión de escritura con su propia lista blanca; idempotencia, bitácora, límites e interruptor | Escritura sin aprobación humana |

## 12. Qué tomamos de los proyectos comparables

Ningún proyecto abierto hace el 80 % de QORTEX. Lista completa, con descartados, licencias y actividad: `docs/REFERENCIAS.md`.

| Proyecto | URL | Qué tomamos |
|---|---|---|
| Gist SuiteQL (michoelchaikin) | https://gist.github.com/michoelchaikin/100a569343a013c7181800f5325c5501 | OAuth1 HMAC-SHA256, `Prefer: transient`, paginación por `next`; reescrito porque no tiene licencia |
| Oracle: SuiteQL por REST | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_157909186990.html | `{"q", "params"}`, `limit`/`offset` y tope de 100.000 filas, que obliga a trocear |
| Oracle: prerrequisitos REST | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_5085602973.html | Los 3 permisos base del rol (§10.1) |
| SuiteQL Query Library | https://timdietrich.me/suiteql-query-library/ | Tablas y columnas de las consultas (hipótesis hasta la corrida 1) |
| truto.one | https://truto.one/blog/the-final-boss-of-erps-architecting-a-reliable-netsuite-api-integration/ | Realm frente a host; detectar OneWorld y multimoneda antes de consultar |
| dlt NetSuite REST | https://dlthub.com/workspace/source/netsuite-rest-api | Ruta `GET /record/v1/metadata-catalog` para el descubrimiento de esquema |
| Airbyte source-netsuite | https://docs.airbyte.com/integrations/sources/netsuite | Checklist de setup para B4 (Integration record, rol dedicado, token) |
| Lokad sync NetSuite | https://docs.lokad.com/platform/integrations/sync-netsuite/ | Columnas explícitas y minimización: clientes sin nombre |
| StatsForecast | https://github.com/Nixtla/statsforecast | Pronóstico de F1, por SKU y agregado |
| sktime | https://github.com/sktime/sktime | Clasificación ADI/CV² y backtest con ventana creciente |
| Hyndman y Kostenko 2007 | https://robjhyndman.com/papers/shortseasonal.pdf | HW estacional por defecto solo con n ≥ 36 |
| Hyndman 2006 | https://robjhyndman.com/papers/foresight.pdf | MASE como métrica |
| Databricks safety-stock | https://github.com/databricks-industry-solutions/safety-stock | σ del SS = RMSE del backtest (solo la idea; licencia no OSI) |
| aakashc23 | https://github.com/aakashc23/demand-forecasting-inventory-reorder-engine | Pruebas de no fuga en el backtest (F1) |
| oalotaik | https://github.com/oalotaik/forecast-driven-inventory-control | Horizonte L + R en revisión periódica (§6.4) |
| stockpyl | https://github.com/LarrySnyder/stockpyl | Oráculo de EOQ y (r,Q) en desarrollo (F1) |
| OCA stock_orderpoint_safety_stock | https://github.com/OCA/stock-logistics-orderpoint/tree/19.0/stock_orderpoint_safety_stock | Mostrar los insumos de cada cifra en «¿Por qué?» |
| OCA vendor_transport_lead_time | https://github.com/OCA/purchase-workflow/tree/18.0/vendor_transport_lead_time | `lt` y `transito_dias` separados |
| Odoo orderpoint | https://github.com/odoo/odoo/blob/17.0/addons/stock/models/stock_orderpoint.py | On hand, en tránsito y pronóstico separados; múltiplo; posponer (F1) |
| Odoo landed costs | https://github.com/odoo/odoo/blob/17.0/addons/stock_landed_costs/models/stock_landed_cost.py | Método de reparto por componente; `by_weight` → campo `peso` |
| Odoo Replenishment report | https://www.odoo.com/documentation/17.0/applications/inventory_and_mrp/inventory/warehouses_storage/replenishment/report.html | Fila de aprobación editable, agrupada por proveedor (F1) |
| OpenBoxes | https://github.com/openboxes/openboxes | Demanda que incluye lo no servido (consulta 6, línea base) |
| Dolibarr replenish | https://github.com/Dolibarr/dolibarr/blob/develop/htdocs/product/stock/replenish.php | MOQ y múltiplo dichos en la fila |
| Mohammed-Zain-py | https://github.com/Mohammed-Zain-py/demand-forecasting-inventory | Pruebas de redondeo al múltiplo y de lead time |
| HyVoid | https://github.com/HyVoid/landed-cost-calculator-excel | Driver por componente (acarreo por peso, F1) y hoja de varianza para calibrar (Quick Win) |
| landed-cost-engine | https://github.com/wave03F/landed-cost-engine | Arancel por capas por HTS × origen × fecha (F1) |
| tariff-resolver | https://github.com/opsloft/tariff-resolver | MPF y HMF como componentes (F1) |
| NetSuite Landed Cost | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N2418831.html | En F0, descubrir si existe y con qué método (B6) |
| Lokad: priorización económica | https://docs.lokad.com/how-to/economic-purchase-prioritization/ | Score con costo puesto y corte por presupuesto (F1, adaptación nuestra) |
| Netstock | https://www.netstock.com/integrations/netsuite/ | Panel por excepción; completar contenedor (F1) |
| NetSuite Inventory Optimization | https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/article_1155215810.html | Línea base a superar en F1 |
| Ajv | https://github.com/ajv-validator/ajv | Validador standalone generado desde el esquema (verificado con Ajv) |
| Chart.js | https://github.com/chartjs/Chart.js | 4.4.1 vendorizada con hash |
| 1Password `op run` | https://www.1password.dev/cli/reference/commands/run/ | Secretos por referencia `op://`, salida enmascarada |
| Vercel Deployment Protection | https://vercel.com/docs/deployment-protection/usage-and-pricing | Protección y `X-Robots-Tag` |
| pydevtools handbook | https://pydevtools.com/handbook/explanation/modern-python-project-setup-guide-for-ai-assistants/ | uv, PEP 621, ruff y `uv.lock` |

## 13. Riesgos técnicos

| Riesgo | Mitigación |
|---|---|
| Los motores JS y Python divergen | ADR-002: una fórmula, un lenguaje; golden y vectores compartidos (§7) |
| Columnas, signos, monedas o unidades de NetSuite distintos de los supuestos | Descubrimiento de esquema y sondas en la corrida 1; respuestas grabadas; tabla campo → columna en `queries/README` |
| 403 por un permiso faltante | Lista completa en B4 (§10.1, con Records Catalog y los condicionales de B6); la sonda nombra la tabla |
| Tope de 100.000 filas, latencia o 429 compartido con el Tomador | Troceo por año, `limit` 1000, concurrencia 1, backoff, horario de poca carga |
| ETA vacías o vencidas en NetSuite | Regla única (§5); calidad cuenta las ETA estimadas y supuestas |
| Incoterm mal declarado: flete o arancel contados dos veces | `incoterm` obligatorio con `procedencia`; tabla de componentes (§6.7); calibración en el Quick Win |
| Importes en otra moneda o tipo de cambio viejo | Conversión única en `preparar.py` con fecha; «¿Por qué?» muestra la tasa; escenario cambiario en F1 |
| Historia corta o demanda intermitente | Hasta 60 meses; sin OC con confianza baja; StatsForecast por clase en F1 |
| Inventario poco fiable (−961 u, `README.md:38`) | Línea base y reconteo de los SKUs A (`README.md:110`) |
| Pocas recepciones por proveedor | `lt_n`; valor por origen marcado supuesto |
| Supuestos por SKU sin confirmar (cbm, múltiplo, vida útil) | Valores por presentación marcados supuesto; calidad mide el % confirmado; Víctor lo ve en la sesión |
| Datos reales hacia un LLM; exposición en Vercel; XSS | §10.6, §10.5 y §10.7 |
| Meses o fechas corridos por zona horaria | `fecha_corte` y `meses` como texto; R5; pruebas también con `TZ=Europe/Madrid` |
| El validador generado necesita helpers de Ajv | Esquema sin `minLength`, `maxLength` ni `uniqueItems`; CI falla si contiene `require(`; plan B en §10.7 |
| Arancel, flete o peso irreales (China al 25 % plano; tope por m³ sin peso) | Supuestos marcados; `peso` opcional desde v1; calibración con un CBP 7501 |
| NetSuite Inventory Optimization cubre SS y ROP | Diferenciarse en costo puesto, caja y fórmulas visibles |
| La F0 cuesta más horas que su precio (unas 69,5 h, supuesto) | Decisiones de alcance y de qué se construye antes del cobro (§16) |

## 14. Preguntas abiertas

1. ¿Cuándo son la reunión con Víctor y la firma de la Fase 0 (`README.md:119`)?
2. ¿Hay Landed Cost en NetSuite? ¿Con qué categorías y método? ¿Usan Inbound Shipments (`README.md:120`, B6)?
3. ¿Solo Houston tiene stock vendible (`spec:145`)?
4. ¿Qué proveedor tiene más faltantes (`spec:146`)?
5. ¿Qué niveles de servicio acepta Quamtex (`spec:147`)?
6. ¿Cuántos meses de ventas hay en NetSuite?
7. ¿Dónde están la vida útil, el país de origen y el peso (campo custom o lote)?
8. ¿La cuenta es OneWorld o multimoneda? ¿Qué tier tiene? ¿De dónde sale el tipo de cambio?
9. ¿Se conservan los backorders y las líneas cerradas por quiebre?
10. ¿El costo de pedir es por OC o por línea?
11. ¿Qué Incoterm, lugar convenido, HTS y pagador del flete tiene cada proveedor?
12. ¿Qué productos son mercancía peligrosa (base solvente)?
13. ¿Qué umbrales U_min y V_min definen «sin venta»?
14. ¿Qué columnas de importe vienen en moneda base (`netamount` frente a `foreignamount`)?
15. ¿Quién es dueño del código?

## 15. Trazabilidad

- `formulas-1` a `formulas-8` → §6.1–§6.9 (F0: declarar, LT + R, tope, ETA, «sin venta», confianza; F1: StatsForecast, XYZ por residuos, reabastecimiento conjunto, capas, LCL).
- `contrato-datos-1` a `contrato-datos-8` → §5 (y §6.7 para `costo_promedio`, §6.8 para moneda y fecha de corte).
- `seguridad-1`, `-2`, `-3`, `-4`, `-5` y `-7` → §10.6, §10.5, §10.1–§10.2, §10.2, §10.8 y §10.7.
- `ingenieria-1`, `-2`, `-3`, `-6` y `-7` → §7, §9, §10.5, §9 y §10.4.
- `plan-vs-dod-1` a `plan-vs-dod-7` → plan revisado (cambios_plan) y §11.
- `coherencia-docs-1` a `coherencia-docs-4` → §6.3, §7, §16 (`README.md:84`, `SEGUIMIENTO.md:25`, `plan:19`, `:27`) y §10.6.
- Revisión crítica de la síntesis anterior → `CLAUDE.md` y documentos (§16), regla única de ETA (§5, §6.6), monedas y pagos al embarque (§5, §6.8), Incoterm y valor del inventario (§6.7), retiro del HW (§7.3), `peso` y `peligroso` (§5, §6.7), clientes sin nombre (§5), R5 (§5), `.gitignore` y cita de SEGUIMIENTO (§10.4, esta lista), ADR-005 y `.vercel/` (§10.5, §16), permisos (§10.1), líneas base y «sin venta» (§1.8, §6.6), horas y validador (§9, §10.7, §16).

## 16. Decisiones que requiere y documentos que cambian

**ADR** (criterios de `docs/adrs/README.md:13-16`):
- **ADR-002** · Motor y contrato (criterio 1, `:13`): supersede spec D4 y `docs/DECISION_LOG.md:18`; incluye la regla única de ETA, la conversión a USD en Python, `procedencia` y el texto nuevo de las reglas 3 y 4 de `CLAUDE.md`.
- **ADR-003** · IA solo con datos demo (criterio 3, `:15`): implementa `docs/DECISION_LOG.md:20` y añade la regla 6.
- **ADR-004** · Candado con lista blanca (criterio 3): implementa `ADR-001`.
- **ADR-005** · Publicación y build (criterio 3): solo `build/qortex.html`, un archivo sin scripts de terceros al ejecutarse, con datos demo, `noindex` y protección; `make publicar` aborta si el guard o la comprobación de `build/` fallan.
- F1: pronóstico en Python y retiro del HW (criterios 1 y 4); corrida programada o servidor, si hace falta. F2: escritura controlada (criterio 2; `ADR-001:38-39`).

**Decisiones de Ignacio:** dónde vive el motor; reglas 3, 4 y 6 de `CLAUDE.md`; qué se construye antes del cobro; alcance y precio de la F0; niveles de servicio; publicación; meses de historia; IA en F1; arancel de China por defecto; propiedad del código (alternativas y recomendación en decisiones_para_ignacio).

**Documentos que cambian además del spec y el plan**, en el mismo commit que acepta el ADR-002 (plan, T1c):

| Fichero:línea | Hoy | Queda |
|---|---|---|
| `CLAUDE.md:8-12` | Lista de lectura sin arquitectura | Añade `docs/ARQUITECTURA.md`: componentes, contrato y fórmulas |
| `CLAUDE.md:21-23` (regla 3) | Nombra `qortex_data.json`, `reporte_calidad.txt` y `supuestos_proveedores.json` | «**Ningún dato del cliente en git.** Todo lo que sale del conector va a `salidas/` (snapshot, `supuestos.json`, `qortex_data.json`, `reporte_calidad.txt`), ignorada por git junto con CSV, XLSX, JSONL y Parquet. Si un test necesita datos, usa datos sintéticos en `tests/fixtures/`, con «sintetico» en el nombre.» |
| `CLAUDE.md:24-25` (regla 4) | Marca `"origen": "supuesto"` en cada campo | «**Un supuesto nunca se presenta como dato.** Todo valor que no salga de NetSuite (arancel, flete, Incoterm, término de pago, volumen, vida útil…) se marca en el mapa `procedencia` de su proveedor o SKU como `supuesto` hasta que Quamtex lo confirme (`confirmado`). El esquema rechaza un supuesto sin su entrada en `procedencia`, y el dashboard lo pinta aparte.» |
| `CLAUDE.md`, tras `:27` | — | Regla 6: «**Ningún dato de NetSuite va a un LLM.** La IA del dashboard (`window.claude`) solo funciona con `fuente: demo`; con datos reales se apaga en código (ADR-003).» |
| `README.md:84-87` | `index.html`, `qortex_conector.py` y `queries/*.sql` «pendiente de subir»; datos en la raíz | `dashboard/` (sí, `e623751`); `src/qortex/conector.py` y `src/qortex/queries/*.sql` (pendientes, B1); `salidas/` (nunca) |
| `README.md:89-98` (incl. `:97`) | Dos corridas del conector; `python3 qortex_conector.py` | `make extraer` (snapshot y plantilla), Compras confirma, `make datos` y `make calidad` sin red, carga en `build/qortex.html` local; el bloque de código pasa a `make fase0` |
| `README.md:103`, `:112` | «comprobar en incógnito si pide login»; `npx vercel --prod` | `make publicar`: solo `build/`, demo, `noindex` y protección comprobada en incógnito |
| `README.md:54` | 24 meses de ventas | Solo si Ignacio elige la historia larga: «hasta 60 meses» |
| `.env.example:3` | `python3 qortex_conector.py` | `make extraer` (= `op run --env-file=.env.example -- uv run qortex extraer`) |
| `docs/DECISION_LOG.md:18` | «Python para conector y motor», vigente | Se anota «supersedida por ADR-002» y se añade una fila con la decisión nueva |
| `docs/DECISION_LOG.md:20` | Se lee como implementada | Se anota «pendiente de implementar (ADR-003, plan T7)» hasta que T7 cierre |
| `SEGUIMIENTO.md:20`, `:25`, `:40-43` | Publicar sin decir qué; una sola casilla de «subir»; bitácora sin `e623751` ni `ba46970` | `make publicar` (B7); `:25` se divide (dashboard hecho en `e623751`; conector y queries pendientes); bitácora completa |
| `docs/PROJECT_STATE.md:34-35`, `:57` | Plan bloqueado en la tarea 1; «Con B4: … desde la tarea 2» | Orden nuevo: T1b, T1c, T4, T7 y T8 no esperan a B1; T9 espera B4 y el cobro |
| `docs/adrs/README.md:29-35` | Solo ADR-001; próximo libre ADR-002 | Filas ADR-002 a ADR-005; próximo libre ADR-006 |
| `.gitignore`, `scripts/guard_datos.sh:4` | §10.4 | Patrones ampliados de §10.4 |
| `ADR-001:36-37` | Nombra `supuestos_proveedores.json` | No se toca (`docs/adrs/README.md:24-25`): `salidas/` sigue fuera de git; el ADR-002 registra el cambio de nombre |

## 17. Deuda menor (hallazgos no materiales)

`seguridad-6` (runbook de rotación y revocación del token). `seguridad-8` (acciones por SHA, `ci.yml:14`, `:27-28`; imagen de gitleaks por digest, `ci.yml:21`; regex con espacio en `.gitleaks.toml:8`; regla para claves TBA). `ingenieria-4`, `-5` y `-8` (resueltos por §8 y §9). `plan-vs-dod-8` (confirmación escrita de Víctor en T10; capacitación en F1, `README.md:59`). `coherencia-docs-5` («Acta §N»: fallan `spec:25`, `plan:13` y `docs/DECISION_LOG.md:19`; aciertan `.env.example:6` y `.gitignore:1`). `coherencia-docs-6` (una sola lista de bloqueos). `coherencia-docs-7` (frontmatter único; el spec y el plan no lo tienen). `coherencia-docs-8` (RUNBOOK, licencia, CONTRIBUTING). «Responsable: Ignacio Romero (KATIA.AI)» (`README.md:11`) frente a «(CPA)» (`CLAUDE.md:4`). Google Fonts (`index.html:7-9`). `toISOString()` también corre un día las fechas de compra del demo en husos UTC+ (`index.html:367`). CSP en F1.
