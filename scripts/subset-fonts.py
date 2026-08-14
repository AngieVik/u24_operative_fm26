#!/usr/bin/env python3
"""Regenera src/fonts/ : Roboto subconjuntada a los caracteres que la app usa.

Uso:  pip install fonttools brotli
      python3 scripts/subset-fonts.py /ruta/a/RobotoTTF

Solo hace falta ejecutarlo cuando `scripts/build.py` avisa de que data.md trae
un caracter que la fuente no cubre -- tipicamente al actualizar el listado para
una Feria nueva.

Produce:
  src/fonts/roboto-{400,500,700}.woff2
  src/fonts/charset.txt   <- lo que build.py usa para validar

La alternativa a subconjuntar seria empotrar Roboto completa (~170 KB por peso)
o servirla desde Google Fonts. Lo primero triplica el arranque; lo segundo rompe
el funcionamiento sin cobertura, que es requisito (RNF-1).
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.md"
OUT = ROOT / "src" / "fonts"

WEIGHTS = {400: "Regular", 500: "Medium", 700: "Bold"}

# Todo lo que la interfaz puede pintar y no sale de data.md: rotulos, mensajes,
# y el repertorio latino basico por seguridad ante nombres futuros.
UI_TEXT = (
    "U24 SERVICIOS SANITARIOS FM26 "
    "UBICACIONES ubicacion ubicaciones resultados "
    "Sin coincidencias Comprueba el numero o escribe menos letras del nombre "
    "Buscar caseta por nombre Navegar a Borrar busqueda "
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "áéíóúüñçÁÉÍÓÚÜÑÇàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛ"
    "¡!¿?.,;:·-–—_/()[]{}'\"“”‘’&+*%#@=<>|~^ "
)


def main():
    if len(sys.argv) < 2:
        sys.exit(f"Uso: {sys.argv[0]} /ruta/a/RobotoTTF")
    src = Path(sys.argv[1])

    chars = set(UI_TEXT)
    for line in DATA.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0].startswith("---"):
            continue
        chars |= set(cells[0]) | set(cells[1])

    chars = {c for c in chars if c.isprintable()}
    text = "".join(sorted(chars))

    OUT.mkdir(parents=True, exist_ok=True)
    for weight, name in WEIGHTS.items():
        origen = src / f"Roboto-{name}.ttf"
        if not origen.exists():
            sys.exit(f"ERROR: no se encuentra {origen}")
        destino = OUT / f"roboto-{weight}.woff2"
        subprocess.run(
            [
                sys.executable, "-m", "fontTools.subset", str(origen),
                f"--text={text}", "--flavor=woff2",
                "--layout-features=kern,liga", "--no-hinting", "--desubroutinize",
                f"--output-file={destino}",
            ],
            check=True,
        )
        print(f"  {destino.relative_to(ROOT)}  {destino.stat().st_size / 1024:.1f} KB")

    # charset.txt = interseccion real de los tres pesos, leida de los woff2.
    from fontTools.ttLib import TTFont

    cobertura = None
    for weight in WEIGHTS:
        font = TTFont(OUT / f"roboto-{weight}.woff2")
        puntos = set()
        for table in font["cmap"].tables:
            puntos |= set(table.cmap.keys())
        cobertura = puntos if cobertura is None else (cobertura & puntos)

    charset = "".join(sorted(chr(c) for c in cobertura if chr(c).isprintable()))
    (OUT / "charset.txt").write_text(charset, encoding="utf-8")
    print(f"  src/fonts/charset.txt  {len(charset)} caracteres")
    print("\nAhora ejecuta: python3 scripts/build.py")


if __name__ == "__main__":
    main()
