---
tipo: plantilla
id: T0B-CORREO-ARRANQUE
estado: VIGENTE
version: 1.0
fecha: 2026-10-05
---

# T0b · Correo de arranque al admin de NetSuite y a Compras

**Cuándo:** después del «sí» de Víctor, con él en copia. Permisos según `docs/ARQUITECTURA.md` §10.1.

---

**Asunto:** QORTEX · acceso de solo lectura a NetSuite y datos de proveedores

Hola [admin], con la autorización de Víctor arrancamos el diagnóstico de abastecimiento. QORTEX
solo **lee** NetSuite: no crea ni modifica ningún registro. Necesitamos:

**1. Un rol nuevo «QORTEX solo lectura»** (no reutilizar otro):
- Setup: *Log in using Access Tokens* y *REST Web Services* (Full); *Records Catalog* (View).
- Reports: *SuiteAnalytics Workbook*.
- Transactions (**solo View**): Find Transaction, Purchase Order, Item Receipt, Invoice, Cash Sale,
  Credit Memo, Sales Order, Item Fulfillment.
- Lists (**solo View**): Items, Vendors, Customers, Locations, Currency, Units of Measure.
- Ningún permiso Create, Edit o Full sobre transacciones o listas.

**2. Un usuario dedicado con ese rol, una integración TBA y su token.** Las credenciales van
directo a nuestra bóveda de 1Password; nunca por correo.

**3. Cinco preguntas rápidas:**
1. ¿Usan Landed Cost o Inbound Shipments?
2. ¿Desde qué año hay ventas registradas?
3. ¿La vida útil, el país de origen o el peso de los productos están en algún campo personalizado?
4. ¿Hay stock vendible fuera de Houston?
5. ¿La cuenta maneja varias monedas?

A Compras le pido aparte 15 minutos para ver cómo arman hoy una orden de compra, y la plantilla
de proveedores (Incoterm, términos de pago, flete y arancel).

¿Podemos tenerlo para el [fecha]? Gracias.

Ignacio Romero · KATIA.AI
