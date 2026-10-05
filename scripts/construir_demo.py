#!/usr/bin/env python3
"""T0c · Genera demo/index.html a partir de index.html (ADR-005).

- Añade <meta name="robots" content="noindex, nofollow">.
- Sustituye Chart.js de cdnjs por la copia de vendor/, incrustada en el mismo archivo,
  después de comprobar su SHA-256: la demo no descarga scripts de terceros.
No cambia nada más: sigue siendo el dashboard con datos de demostración.
"""
import hashlib
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CDN = '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>'
ROBOTS = '<meta name="robots" content="noindex, nofollow">'


def main() -> int:
    html = (RAIZ / "index.html").read_text(encoding="utf-8")
    chart = (RAIZ / "vendor" / "chart.umd.js").read_bytes()
    esperado = (RAIZ / "vendor" / "SHA256SUMS").read_text().split()[0]
    real = hashlib.sha256(chart).hexdigest()
    if real != esperado:
        print(f"ERROR: chart.umd.js no coincide con SHA256SUMS ({real})", file=sys.stderr)
        return 1
    texto = chart.decode("utf-8")
    if "</script" in texto.lower():
        print("ERROR: chart.umd.js contiene </script>", file=sys.stderr)
        return 1
    if CDN not in html:
        print("ERROR: index.html ya no carga Chart.js desde cdnjs; revisar el script", file=sys.stderr)
        return 1
    html = html.replace(CDN, f"<script>/* Chart.js 4.4.1 · sha256 {esperado} */\n{texto}\n</script>", 1)
    if ROBOTS not in html:
        html = html.replace('<meta name="viewport"', ROBOTS + '\n<meta name="viewport"', 1)
    (RAIZ / "demo").mkdir(exist_ok=True)
    (RAIZ / "demo" / "index.html").write_text(html, encoding="utf-8")
    print("ok: demo/index.html generado (Chart.js incrustado, noindex)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
