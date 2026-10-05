#!/usr/bin/env bash
# T0c · Publica la demo de QORTEX en Vercel (ADR-005).
# Solo se publica demo/: un index.html con datos de demostración y su vercel.json.
# Se corre desde la terminal de Ignacio, con la sesión de Vercel ya iniciada (vercel login).
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/guard_datos.sh

# 1. demo/ solo puede tener estos dos archivos
extra=$(ls -A demo | grep -vxE 'index\.html|vercel\.json|\.vercel' || true)
if [ -n "$extra" ]; then echo "ERROR: demo/ tiene archivos de más: $extra"; exit 1; fi

# 2. noindex en el HTML y en las cabeceras
grep -q '<meta name="robots" content="noindex, nofollow">' demo/index.html || { echo "ERROR: falta meta robots"; exit 1; }
grep -q 'X-Robots-Tag' demo/vercel.json || { echo "ERROR: falta X-Robots-Tag"; exit 1; }

# 3. solo datos de demostración: el HTML no puede traer un JSON de NetSuite incrustado
if grep -q '"fuente"[[:space:]]*:[[:space:]]*"netsuite"' demo/index.html; then echo "ERROR: datos reales en la demo"; exit 1; fi

echo "ok: demo/ lista. Publicando en producción…"
vercel deploy demo --prod
echo
echo "Ahora, en el panel de Vercel: Settings › Deployment Protection › Password Protection (Pro)."
echo "Después abre la URL en incógnito: debe pedir contraseña."
