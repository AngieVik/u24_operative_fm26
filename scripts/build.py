#!/usr/bin/env python3
"""Ensambla dist/, la carpeta que se publica, a partir de data.md y src/.

Uso:  python3 scripts/build.py

dist/ contiene EXACTAMENTE lo que la aplicacion necesita y nada mas. El resto
del repositorio -- datos de origen, documentacion, plantillas, scripts,
originales de marca -- no se publica. Netlify apunta a dist/.

Aplica las reglas de normalizacion documentadas en docs/02-datos.md y falla de
forma ruidosa ante cualquier dato invalido: nunca omite nada en silencio.
"""

import base64
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.md"
SRC = ROOT / "src"
TEMPLATE = SRC / "template.html"
FONTS = SRC / "fonts"
LOGO = SRC / "logo.svg"
CHARSET = FONTS / "charset.txt"
ICONS = ROOT / "icons"

DIST = ROOT / "dist"
OUTPUT = DIST / "index.html"

FONT_WEIGHTS = (400, 500, 700)

# Se copian tal cual a dist/. Cualquier archivo de src/ o icons/ que no este
# aqui NO se publica.
COPY_ROOT = ("manifest.webmanifest", "sw.js")
COPY_ICONS = (
    "icon-192.png",
    "icon-512.png",
    "icon-maskable-192.png",
    "icon-maskable-512.png",
    "apple-touch-icon.png",
    "favicon-32.png",
    "favicon-16.png",
)

EXPECTED_ROWS = 125

# Envolvente del Real de la Feria, con margen. Ver docs/02-datos.md.
LAT_RANGE = (36.699, 36.709)
LON_RANGE = (-4.467, -4.456)

COORDS_RE = re.compile(r"^(-?\d+\.\d+),(-?\d+\.\d+)$")
NUMERIC_LABEL_RE = re.compile(r"^\d+(-\d+)*$")

# Erratas del origen. data.md no se modifica: se corrigen aqui.
STREET_FIXES = {
    "C/ Peñista Rafael Fuentess": "C/ Peñista Rafael Fuentes",
}


def fail(msg):
    sys.exit(f"ERROR: {msg}")


def normalize(text):
    """Minusculas, sin tildes, comillas normalizadas, espacios colapsados."""
    text = text.lower().replace("‘", "'").replace("’", "'")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text).strip()


def compact_label(label, numbers):
    """Etiqueta abreviada para la columna de número, que es de ancho fijo.

    Uno o dos números se muestran tal cual. A partir de tres se abrevia como
    intervalo (180-181-182-183-184-185-186 -> 180–186), lo que solo es correcto
    porque todos los rangos de data.md son consecutivos. Se comprueba aquí: si
    algún año dejan de serlo, se muestra la etiqueta completa en lugar de
    mentir sobre los números que abarca.
    """
    if len(numbers) < 3:
        return label
    if numbers != list(range(numbers[0], numbers[0] + len(numbers))):
        return label
    return f"{numbers[0]}–{numbers[-1]}"


def check_charset(locations):
    """La tipografia va subconjuntada a los caracteres que hoy aparecen en
    data.md. Si un listado futuro trae uno nuevo, el navegador pintaria un
    cuadrado vacio sin avisar. Aqui se detiene el build en vez de publicarlo.
    """
    if not CHARSET.exists():
        fail(f"falta {CHARSET.relative_to(ROOT)}, necesario para validar la fuente")

    cubiertos = set(CHARSET.read_text(encoding="utf-8"))
    usados = set()
    for loc in locations:
        usados |= set(loc["display"]) | set(loc["name"])

    faltan = sorted(c for c in usados if c not in cubiertos and c.isprintable())
    if faltan:
        detalle = ", ".join(f"{c!r} (U+{ord(c):04X})" for c in faltan)
        fail(
            "la fuente no cubre estos caracteres de data.md: "
            + detalle
            + "\n       Regenera el subconjunto con scripts/subset-fonts.py "
            "y actualiza src/fonts/charset.txt."
        )
    return len(usados)


def read_logo():
    """Emblema oficial, empotrado en línea para que index.html siga siendo
    autocontenido y el logotipo no dependa de una petición de red."""
    if not LOGO.exists():
        fail(f"falta el logotipo {LOGO.relative_to(ROOT)}")
    svg = LOGO.read_text(encoding="utf-8").strip()
    if not svg.startswith("<svg"):
        fail(f"{LOGO.relative_to(ROOT)} no empieza por <svg")
    # Se marca como decorativo: el nombre lo da el texto contiguo.
    return svg.replace(
        "<svg", '<svg class="mark" role="img" aria-label="Emblema U24"', 1
    )


def read_fonts():
    fonts = {}
    for weight in FONT_WEIGHTS:
        path = FONTS / f"roboto-{weight}.woff2"
        if not path.exists():
            fail(f"falta la fuente {path.relative_to(ROOT)}")
        fonts[weight] = base64.b64encode(path.read_bytes()).decode("ascii")
    return fonts


def parse_rows(raw):
    rows = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0].startswith("---") or cells[0] == "ubication_number":
            continue
        if len(cells) != 4:
            fail(f"data.md linea {lineno}: se esperaban 4 columnas, hay {len(cells)}")
        rows.append((lineno, cells))
    return rows


def build_locations(rows):
    locations = []
    for index, (lineno, (label, name, street, coords)) in enumerate(rows):
        if not label or not name:
            fail(f"data.md linea {lineno}: numero o nombre vacio")

        match = COORDS_RE.match(coords)
        if not match:
            fail(f"data.md linea {lineno}: coordenadas invalidas {coords!r}")
        lat, lon = match.group(1), match.group(2)

        if not LAT_RANGE[0] <= float(lat) <= LAT_RANGE[1]:
            fail(f"data.md linea {lineno}: latitud {lat} fuera del recinto")
        if not LON_RANGE[0] <= float(lon) <= LON_RANGE[1]:
            fail(f"data.md linea {lineno}: longitud {lon} fuera del recinto")

        # Los rangos son enumeraciones, no intervalos: se parten por "-".
        numbers = (
            [int(n) for n in label.split("-")] if NUMERIC_LABEL_RE.match(label) else []
        )

        locations.append(
            {
                "id": f"loc-{index:03d}",
                "label": label,
                "display": compact_label(label, numbers),
                "numbers": numbers,
                "name": name,
                "street": STREET_FIXES.get(street, street),
                "lat": lat,
                "lon": lon,
                "search": normalize(f"{name} {label}"),
                "nameSearch": normalize(name),
            }
        )
    return locations


def check(locations):
    ids = {loc["id"] for loc in locations}
    if len(ids) != len(locations):
        fail("identificadores duplicados")

    coords = {(loc["lat"], loc["lon"]) for loc in locations}
    if len(coords) != len(locations):
        fail("coordenadas duplicadas")

    seen = {}
    for loc in locations:
        for n in loc["numbers"]:
            if n in seen:
                fail(f"numero {n} repetido en {seen[n]!r} y {loc['label']!r}")
            seen[n] = loc["label"]

    if len(locations) != EXPECTED_ROWS:
        fail(f"se esperaban {EXPECTED_ROWS} ubicaciones, hay {len(locations)}")

    return seen


def assemble_dist(html):
    """Reconstruye dist/ desde cero. Se borra antes para que un archivo
    retirado del proyecto no siga publicandose por inercia."""
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "icons").mkdir(parents=True)

    OUTPUT.write_text(html, encoding="utf-8", newline="\n")

    for name in COPY_ROOT:
        origen = SRC / name
        if not origen.exists():
            fail(f"falta {origen.relative_to(ROOT)}")
        shutil.copy2(origen, DIST / name)

    for name in COPY_ICONS:
        origen = ICONS / name
        if not origen.exists():
            fail(f"falta {origen.relative_to(ROOT)}")
        shutil.copy2(origen, DIST / "icons" / name)


def check_dist_references():
    """Todo lo que index.html, el manifiesto y el service worker referencian
    debe existir dentro de dist/. Un 404 en produccion se detecta aqui."""
    textos = {
        p: (DIST / p).read_text(encoding="utf-8")
        for p in ("index.html", "manifest.webmanifest", "sw.js")
    }
    referencias = set()
    for contenido in textos.values():
        referencias |= set(re.findall(r'["\'](\./)?(icons/[\w.-]+)["\']', contenido))
    faltan = [ref for _, ref in referencias if not (DIST / ref).exists()]
    if faltan:
        fail("dist/ referencia archivos que no contiene: " + ", ".join(sorted(faltan)))
    return len(referencias)


def main():
    for path in (DATA, TEMPLATE):
        if not path.exists():
            fail(f"no se encuentra {path}")

    rows = parse_rows(DATA.read_text(encoding="utf-8"))
    locations = build_locations(rows)
    numbers = check(locations)
    n_chars = check_charset(locations)

    template = TEMPLATE.read_text(encoding="utf-8")
    markers = ["__LOCATIONS__", "__LOGO__"] + [f"__FONT_{w}__" for w in FONT_WEIGHTS]
    for marker in markers:
        if marker not in template:
            fail(f"la plantilla no contiene el marcador {marker}")

    fonts = read_fonts()
    payload = json.dumps(locations, ensure_ascii=False, separators=(",", ":"))

    html = template.replace("__LOCATIONS__", payload)
    html = html.replace("__LOGO__", read_logo())
    for weight, b64 in fonts.items():
        html = html.replace(f"__FONT_{weight}__", b64)

    restantes = [m for m in markers if m in html]
    if restantes:
        fail("marcadores sin sustituir: " + ", ".join(restantes))

    assemble_dist(html)
    n_refs = check_dist_references()

    size = OUTPUT.stat().st_size
    unnamed = [loc["label"] for loc in locations if not loc["numbers"]]
    streets = sorted({loc["street"] for loc in locations})

    abbreviated = [
        f"{loc['label']} -> {loc['display']}"
        for loc in locations
        if loc["display"] != loc["label"]
    ]

    total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    n_files = sum(1 for f in DIST.rglob("*") if f.is_file())

    print(f"OK  {len(locations)} ubicaciones -> {OUTPUT.relative_to(ROOT)}")
    print(f"    {len(numbers)} numeros de caseta, {len(streets)} calles")
    print(f"    sin numero: {', '.join(unnamed)}")
    print(f"    etiquetas abreviadas: {len(abbreviated)}")
    print(f"    fuente: {n_chars} caracteres usados, todos cubiertos")
    print(f"    emblema empotrado: {LOGO.stat().st_size / 1024:.1f} KB")
    print(f"    index.html: {size / 1024:.1f} KB")
    print(f"    dist/: {n_files} archivos, {total / 1024:.1f} KB, {n_refs} referencias OK")


if __name__ == "__main__":
    main()
