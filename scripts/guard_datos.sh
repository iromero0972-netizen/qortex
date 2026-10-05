#!/usr/bin/env bash
# Falla si algún archivo con datos del cliente está versionado (CLAUDE.md, regla 3).
set -euo pipefail
prohibidos=$(git ls-files | grep -E '(^|/)(qortex_data\.json|reporte_calidad\.txt|supuestos_proveedores\.json)$|\.(csv|xlsx)$' | grep -v '^tests/fixtures/' || true)
if [ -n "$prohibidos" ]; then
  echo "ERROR: datos del cliente versionados:"; echo "$prohibidos"; exit 1
fi
echo "ok: ningún archivo de datos del cliente en git"
