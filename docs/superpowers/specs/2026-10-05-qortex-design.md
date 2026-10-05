# QORTEX — diseño

**Fecha:** 5-oct-2026
**Estado:** propuesto, pendiente de revisión de Ignacio
**Autor:** sesión con Ignacio Romero, a partir del Acta de creación (PRJ-QTX-REA-01)
**Repositorio:** `iromero0972-netizen/qortex`

---

## 1. Qué pide el cliente

1. Quamtex pierde ventas porque se queda sin stock: compra sin proyección.
2. El inventario en NetSuite no coincide con el físico. El conteo de KATIA dio **−961 u netas en 36 SKUs**.
3. Compra a 5 orígenes (China, México, Brasil, Europa y EE.UU.), cada uno con su lead time, sus términos y su costo.
4. Arma las OC sin punto de reorden, sin stock de seguridad y sin costo puesto en almacén.

**Objetivo:** que cada OC salga recomendada por datos, con el costo real y la fecha en que sale el
dinero, y que la apruebe una persona.

## 2. Decisiones tomadas

| # | Decisión | Fuente |
|---|---|---|
| D1 | Opción D, híbrido por fases: diagnóstico pagado, después Quick Win, después motor completo | Acta §5 |
| D2 | Solo lectura sobre NetSuite hasta la firma de la Fase 2 | Acta §3, ADR-001 |
| D3 | Rol NetSuite exclusivo, no el del Tomador | Acta §9 |
| D4 | Python para conector y motor; dashboard HTML estático que carga un JSON | Activos existentes |
| D5 | Autonomía por fases: recomienda → propone y el humano aprueba → ejecuta dentro de límites firmados | Acta §5 |
| D6 | Fase 0 arregla el dato antes de prometer resultados | Acta §9 |

### Por qué D4

En la Fase 0 no hay servidor que operar ni base de datos que respaldar. El conector corre en la
computadora de Ignacio con `op run`, produce un JSON y el dashboard lo carga en el navegador. Si
la Fase 1 necesita correr cada noche, se decide entonces (ADR nuevo), no ahora.

## 3. Arquitectura

```
NetSuite (solo lectura, OAuth1 TBA)
   │  SuiteQL: inventario, ventas 24 m, OC, recepciones, proveedores
   ▼
qortex_conector.py ──► supuestos_proveedores.json ──► Quamtex completa origen/términos/arancel/flete
   │                                                         │
   ▼ (2.ª corrida)                                           │
motor (5 agentes, funciones puras) ◄─────────────────────────┘
   │
   ├─► qortex_data.json        (fuera de git)
   └─► reporte_calidad.txt     (fuera de git)
          │
          ▼
index.html (dashboard, 6 pestañas + simulador «¿y si…?»)  ── botón «Cargar datos de NetSuite»
```

**La separación que sostiene el diseño:** todo lo que toca NetSuite está en un solo módulo
(el conector). Los cinco agentes son **funciones puras**: entra una tabla y sale otra, sin I/O.
Así se prueban con datos sintéticos y el conector se puede auditar en una lectura.

## 4. Los cinco agentes

| Agente | Entrada | Cálculo | Salida |
|---|---|---|---|
| **Demanda** | Ventas mensuales por SKU (24 m) | Holt-Winters multiplicativo con tendencia amortiguada. Si hay menos de 24 meses o demanda intermitente, cae a promedio móvil o Croston y lo marca. Clasificación ABC (valor) × XYZ (coeficiente de variación) | Pronóstico por SKU y mes, con su error (MAPE) |
| **Proveedores** | OC y recepciones | Lead time real = fecha de recepción − fecha de OC, por proveedor y origen. Media y desviación | Lead time y riesgo por proveedor |
| **Riesgo** | Pronóstico, lead time, inventario | SS = z · √(LT · σd² + d² · σLT²); ROP = d · LT + SS; cobertura = disponible / d | Semáforo: **ordenar ya** / en nivel / exceso |
| **Comprador** | ROP, costos, restricciones | EOQ = √(2 · D · S / H), con tope por vida útil y redondeo al múltiplo de compra | OC sugerida por proveedor, con «¿Por qué?» por línea |
| **Tesorería** (diferenciador CPA) | OC sugeridas, términos, costos de importación | Costo puesto en almacén = FOB + flete + seguro + arancel + broker + acarreo. Calendario de pagos según los términos (anticipo, saldo contra BL, neto 30…) | Flujo de caja de compras por semana |

z sale del nivel de servicio objetivo por clase: A = 95%, B = 90%, C = 85% (valores iniciales, se
ajustan con Quamtex).

**Regla para «¿Por qué?»:** cada línea sugerida muestra demanda usada, lead time usado, SS, ROP,
disponible, cantidad y qué valores son supuestos. Si compras no entiende la línea, no la aprueba.

## 5. Datos

### 5.1 Lo que se lee de NetSuite

| Consulta | Para qué agente |
|---|---|
| Artículos activos con disponible por Location (Houston) | Riesgo, Comprador |
| Ventas por SKU y cliente, 24 meses | Demanda |
| OC abiertas y cerradas, con fechas | Proveedores, Riesgo (lo que ya viene en camino) |
| Recepciones de artículo | Proveedores |
| Proveedores con moneda y términos | Tesorería |

Las 5 queries SuiteQL ya están escritas (falta subirlas, B1 en `PROJECT_STATE.md`).

### 5.2 Lo que pone Quamtex (supuestos)

`supuestos_proveedores.json`, uno por proveedor: origen, Incoterm, términos de pago, % de arancel,
quién paga el flete, costo de flete por unidad o contenedor, múltiplo de compra y vida útil.
**Cada campo lleva `"origen": "supuesto" | "confirmado"`.** El dashboard pinta distinto lo supuesto.

### 5.3 Contrato de `qortex_data.json`

Lo fija un JSON Schema (`schema/qortex_data.schema.json`, plan Fase 0, tarea 4). El dashboard se
niega a cargar un archivo que no lo cumple y dice qué campo falla.

## 6. Reporte de calidad de datos (entregable de la Fase 0)

| Chequeo | Por qué importa |
|---|---|
| SKUs con disponible negativo | No se puede proyectar sobre un negativo |
| Diferencia sistema vs conteo físico (36 SKUs) | La línea base del indicador de exactitud |
| SKUs sin ventas en 24 m con stock | Exceso / obsoleto |
| SKUs vendidos sin proveedor preferido | El Comprador no puede sugerir OC |
| OC recibidas sin fecha de recepción o con recepción anterior a la OC | Lead time imposible |
| Unidades de medida inconsistentes entre compra y venta | Un factor mal puesto multiplica el error |
| Proveedores sin términos de pago | Tesorería no puede calendarizar |

Salida: un TXT legible para Víctor, con conteos, porcentajes y los 10 peores casos de cada chequeo.

## 7. Manejo de errores

- Un SKU con datos insuficientes **no se cae**: sale con confianza «baja» y sin OC sugerida.
- Un campo obligatorio ausente en NetSuite se reporta en calidad de datos; no se rellena con 0.
- Si el conector recibe 401/403, se detiene y dice qué permiso falta. No reintenta en bucle.

## 8. Seguridad

- El rol NetSuite no tiene permisos de transacción. El conector solo usa SuiteQL y GET.
- Credenciales: 6 variables en `op://Quamtex-REA/qortex-netsuite/*`.
- Datos del cliente fuera de git. CI con gitleaks y un chequeo que falla si se versiona un archivo de datos.
- Dashboard publicado con `noindex, nofollow`, detrás de login.

## 9. Pruebas

- Agentes: pytest con datos sintéticos y resultados calculados a mano (por ejemplo, EOQ con D=1200, S=50 y H=2 da 244,9).
- Conector: respuestas grabadas de NetSuite (sin datos reales) y una prueba de que no existe ningún camino de escritura.
- Dashboard: carga del JSON de ejemplo y rechazo de un JSON inválido.

## 10. Dependencias externas

| Bloquea | Qué falta | De quién |
|---|---|---|
| Primera corrida real | Rol de solo lectura + 6 credenciales | Víctor / admin NetSuite |
| Costo puesto en almacén real | Origen, términos, arancel y flete | Compras Quamtex |
| Costo 100% sin supuestos | ¿Landed Cost en NetSuite? | Admin NetSuite |

## 11. Preguntas abiertas

1. Fecha de la reunión con Víctor y de la firma de la Fase 0.
2. ¿Quamtex registra Landed Cost en NetSuite?
3. ¿Hay más de una Location con stock vendible, o solo Houston?
4. ¿Cuál es el proveedor con más faltantes? (Es el del Quick Win.)
5. Niveles de servicio objetivo por clase: ¿los acepta Quamtex?

## 12. Alternativas descartadas

| Opción | Por qué se descarta |
|---|---|
| A · NetSuite nativo (Demand Planning) | Módulo adicional con licencia, sin costo puesto en almacén ni tesorería, y no se diferencia |
| B · Motor propio desde cero sin fases | Se construye antes de cobrar y antes de saber si el dato sirve |
| C · SaaS tipo Netstock | Nivel 2 de 4; Quamtex paga suscripción y KATIA no queda en el medio |
| Servidor + base de datos en la Fase 0 | Operar sin necesitarlo; se decide en la Fase 1 |
