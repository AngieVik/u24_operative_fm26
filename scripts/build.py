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
import hashlib
import json
import math
import re
import shutil
import statistics
import sys
import unicodedata
from datetime import date
from pathlib import Path

# ── Configuracion del operativo ───────────────────────────────────────────────
# Lo unico que hay que tocar al cambiar de listado o de operativo. Todo lo demas
# se deduce de los datos. Ver docs/05-cambiar-de-operativo.md.

# Rotulo que aparece bajo el buscador.
OPERATIVO = "Feria de Málaga 2026"

# Filas que debe traer data.md. Es la red contra un listado truncado o pegado a
# medias, el unico error de bulto que los datos no delatan por si solos.
# Poner None para que el recuento solo se informe y nunca aborte.
EXPECTED_ROWS = 125

# ──────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data.md"
STREETS = ROOT / "calles.md"
SRC = ROOT / "src"
TEMPLATE = SRC / "template.html"
FONTS = SRC / "fonts"
LOGO = SRC / "logo.svg"
CHARSET = FONTS / "charset.txt"
VENDOR = SRC / "vendor" / "fuse.basic.min.js"
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

# Coherencia geografica. Se comprueba que las coordenadas son consistentes ENTRE
# SI, no contra un lugar concreto: este script no tiene por que saber en que
# ciudad se trabaja. Calibrado sobre el listado actual, donde la mediana al
# centro es de 143 m y el punto mas excentrico esta a 370 m. Ver docs/02-datos.md.
FAR_AWAY_KM = 25    # aborta: a esa distancia ya no es el mismo operativo
OUTLIER_FACTOR = 4  # avisa: se sale del grueso...
OUTLIER_MIN_M = 500  # ...y ademas esta a mas de esto del centro

# Longitud de calle que se considera normal, en metros. Solo para avisar: una
# calle puede medir lo que quiera y el build no es quien para decidirlo.
STREET_LENGTH_USUAL = (20, 5000)

COORDS_RE = re.compile(r"^(-?\d+\.\d+),(-?\d+\.\d+)$")
NUMERIC_LABEL_RE = re.compile(r"^\d+(-\d+)*$")

# Bloque de textos visibles de la plantilla y cadenas que contiene.
UI_TEXT_RE = re.compile(r"const TEXT = \{(.*?)\n\};", re.S)
UI_STRING_RE = re.compile(r"'((?:[^'\\]|\\.)*)'")

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


def flatten(text):
    """Solo letras y digitos: fuera espacios, barras, guiones y apostrofos.

    Es lo que permite que 'C/Peñ' encuentre 'C/ Peñista Rafael Fuentes' y que
    '66 67' encuentre '66-67-68'. Sin esto, un espacio de mas o de menos hace
    que no aparezca nada, que es justo lo que no puede pasar tecleando con
    prisa.
    """
    return re.sub(r"[^a-z0-9]", "", normalize(text))


def compact_label(label, numbers):
    """Etiqueta abreviada para la columna de identificador, de ancho fijo.

    Uno o dos numeros se muestran tal cual. A partir de tres se abrevia como
    intervalo (180-181-182-183-184-185-186 -> 180–186), lo que solo es correcto
    porque todos los rangos de data.md son consecutivos. Se comprueba aqui: si
    algun listado futuro deja de serlo, se muestra la etiqueta completa en
    lugar de mentir sobre los numeros que abarca.
    """
    if len(numbers) < 3:
        return label
    if numbers != list(range(numbers[0], numbers[0] + len(numbers))):
        return label
    return f"{numbers[0]}–{numbers[-1]}"


def ui_texts(template):
    """Texto que la aplicacion pinta en pantalla: el de la plantilla fuera de
    <script> y <style>, mas las cadenas del objeto TEXT del script. Los
    atributos quedan fuera a proposito: un aria-label lo lee un lector de
    pantalla, no lo dibuja la tipografia."""
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", template, flags=re.S)
    html = re.sub(r"<[^>]*>", " ", html)

    bloque = UI_TEXT_RE.search(template)
    if not bloque:
        fail("la plantilla no declara el objeto TEXT con los textos visibles")

    return " ".join([html] + UI_STRING_RE.findall(bloque.group(1)))


def check_charset(locations, template, streets=()):
    """La tipografia va subconjuntada a los caracteres que hoy necesita la
    aplicacion: los de data.md y los de sus propios rotulos. Si aparece uno
    nuevo, el navegador pintaria un cuadrado vacio sin avisar. Aqui se detiene
    el build en vez de publicarlo.
    """
    if not CHARSET.exists():
        fail(f"falta {CHARSET.relative_to(ROOT)}, necesario para validar la fuente")

    cubiertos = set(CHARSET.read_text(encoding="utf-8"))

    usados = set()
    for loc in locations:
        # Las cuatro se pintan en la fila: identificador, nombre, calle y
        # coordenadas.
        usados |= set(loc["display"]) | set(loc["name"]) | set(loc["street"])
        usados |= set(loc["lat"]) | set(loc["lon"])
    for street in streets:
        usados |= set(street["name"])
    # El rotulo ya no esta en la plantilla, sino en la configuracion de arriba.
    usados |= set(OPERATIVO)
    usados |= set(ui_texts(template))

    faltan = sorted(
        c for c in usados if c not in cubiertos and c.isprintable() and not c.isspace()
    )
    if faltan:
        detalle = ", ".join(f"{c!r} (U+{ord(c):04X})" for c in faltan)
        fail(
            "la fuente no cubre estos caracteres: "
            + detalle
            + "\n       Regenera el subconjunto con scripts/subset-fonts.py "
            "y actualiza src/fonts/charset.txt."
        )
    return len(usados)


def read_logo():
    """Emblema oficial, empotrado en linea para que index.html siga siendo
    autocontenido y el logotipo no dependa de una peticion de red."""
    if not LOGO.exists():
        fail(f"falta el logotipo {LOGO.relative_to(ROOT)}")
    svg = LOGO.read_text(encoding="utf-8").strip()
    if not svg.startswith("<svg"):
        fail(f"{LOGO.relative_to(ROOT)} no empieza por <svg")
    # Se marca como decorativo: el nombre lo da el texto contiguo.
    return svg.replace(
        "<svg", '<svg class="mark" role="img" aria-label="Emblema U24"', 1
    )


def read_vendor():
    """Fuse.js, empotrado como el resto: sin CDN y sin peticiones de red, la
    busqueda tiene que funcionar sin cobertura (RNF-1)."""
    if not VENDOR.exists():
        fail(
            f"falta {VENDOR.relative_to(ROOT)}\n"
            "       Descargalo con: npm pack fuse.js@7.5.0\n"
            "       y copia dist/fuse.basic.min.cjs a esa ruta."
        )
    code = VENDOR.read_text(encoding="utf-8").strip()
    if "module.exports" not in code:
        fail(
            f"{VENDOR.relative_to(ROOT)} no exporta como modulo CommonJS: "
            "la plantilla lo envuelve esperando module.exports"
        )
    return code


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
            fail(f"data.md linea {lineno}: identificador o nombre vacio")

        match = COORDS_RE.match(coords)
        if not match:
            fail(f"data.md linea {lineno}: coordenadas invalidas {coords!r}")
        lat, lon = match.group(1), match.group(2)

        # No se comprueba aqui donde cae la coordenada: eso se hace despues,
        # sobre el conjunto entero, en check_coherence().

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
                # La calle entra en el indice: buscar por direccion es otra
                # forma legitima de llegar a una ubicacion.
                "search": normalize(f"{name} {label} {STREET_FIXES.get(street, street)}"),
                "flat": flatten(f"{name} {label} {STREET_FIXES.get(street, street)}"),
                "nameSearch": normalize(name),
            }
        )
    return locations


def haversine(a, b):
    """Metros entre dos puntos. Solo para validar que unas coordenadas no son
    un error de copiado, no para calcular nada que se muestre."""
    radio = 6371000
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radio * math.asin(math.sqrt(h))


def centro_de(locations):
    """Punto central del conjunto, por mediana y no por media: asi una
    coordenada disparatada no arrastra el centro y sigue destacando."""
    return (
        statistics.median(float(loc["lat"]) for loc in locations),
        statistics.median(float(loc["lon"]) for loc in locations),
    )


def check_coherence(locations):
    """Coherencia geografica del listado consigo mismo.

    Sustituye a la envolvente fija que habia antes, que obligaba a declarar en
    que ciudad estaba el operativo y aun asi solo detectaba errores de bulto.
    Esto detecta los mismos sin pedir nada a cambio: un digito cambiado en la
    latitud manda el punto a decenas de kilometros, y una coordenada pegada de
    otra provincia, a cientos.

    Aborta con lo imposible. Con lo raro pero posible -- una ubicacion en otra
    parte de la ciudad -- solo avisa: el que decide si eso es correcto es quien
    conoce el operativo, no este script.
    """
    centro = centro_de(locations)
    medidas = [
        (haversine((float(loc["lat"]), float(loc["lon"])), centro), loc)
        for loc in locations
    ]

    lejos = [(d, loc) for d, loc in medidas if d > FAR_AWAY_KM * 1000]
    if lejos:
        d, loc = max(lejos, key=lambda x: x[0])
        fail(
            f"{loc['name']!r} ({loc['lat']},{loc['lon']}) esta a {d / 1000:.0f} km "
            f"del resto del listado.\n"
            f"       Con {len(lejos)} punto(s) asi, casi seguro hay una coordenada "
            "mal copiada o de otro operativo."
        )

    mediana = statistics.median(d for d, _ in medidas) or 1.0
    raros = [
        (d, loc)
        for d, loc in medidas
        if d > OUTLIER_MIN_M and d > mediana * OUTLIER_FACTOR
    ]
    return centro, mediana, sorted(raros, key=lambda x: -x[0])


def parse_point(value, donde, centro):
    match = COORDS_RE.match(value)
    if not match:
        fail(f"calles.md {donde}: coordenadas invalidas {value!r}")
    d = haversine((float(match.group(1)), float(match.group(2))), centro)
    if d > FAR_AWAY_KM * 1000:
        fail(f"calles.md {donde}: {value} esta a {d / 1000:.0f} km de las ubicaciones")
    return match.group(1), match.group(2)


def build_streets(locations, centro):
    """Lee calles.md, la segunda fuente de verdad. Ver docs/02-datos.md.

    El archivo es opcional: sin el, la aplicacion funciona igual y solo pierde
    el trazado de calles. Las filas sin coordenadas se omiten y se informa de
    ellas, para poder rellenar el listado por partes.
    """
    if not STREETS.exists():
        return [], [], []

    conocidas = {}
    for loc in locations:
        conocidas.setdefault(loc["street"], 0)
        conocidas[loc["street"]] += 1

    streets, incompletas, avisos = [], [], []
    vistas = set()

    for lineno, line in enumerate(STREETS.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) not in (3, 4):
            fail(f"calles.md linea {lineno}: se esperaban 3 o 4 columnas, hay {len(cells)}")
        if cells[0].startswith("---"):
            continue
        # Cabecera: la unica fila cuyo nombre no es una calle conocida y cuyas
        # celdas de coordenadas no lo son tampoco. Asi da igual su idioma.
        if cells[0] not in conocidas and not COORDS_RE.match(cells[1]):
            continue

        name, start, end = cells[0], cells[1], cells[2]
        waypoints = cells[3] if len(cells) == 4 else ""

        if name not in conocidas:
            fail(
                f"calles.md linea {lineno}: la calle {name!r} no existe en data.md.\n"
                "       El nombre debe coincidir exactamente, ya corregido de erratas."
            )
        if name in vistas:
            fail(f"calles.md linea {lineno}: la calle {name!r} esta repetida")
        vistas.add(name)

        if not start or not end:
            incompletas.append(name)
            continue

        lat1, lon1 = parse_point(start, f"linea {lineno}, inicio", centro)
        lat2, lon2 = parse_point(end, f"linea {lineno}, fin", centro)
        if (lat1, lon1) == (lat2, lon2):
            fail(f"calles.md linea {lineno}: inicio y fin son el mismo punto")

        largo = haversine((float(lat1), float(lon1)), (float(lat2), float(lon2)))
        if not STREET_LENGTH_USUAL[0] <= largo <= STREET_LENGTH_USUAL[1]:
            avisos.append(f"{name}: {largo:.0f} m entre extremos, comprueba las coordenadas")

        puntos = []
        for i, punto in enumerate(p.strip() for p in waypoints.split(";") if p.strip()):
            plat, plon = parse_point(
                punto, f"linea {lineno}, punto intermedio {i + 1}", centro
            )
            puntos.append(f"{plat},{plon}")

        streets.append(
            {
                "name": name,
                "search": normalize(name),
                "flat": flatten(name),
                "start": f"{lat1},{lon1}",
                "end": f"{lat2},{lon2}",
                "waypoints": puntos,
                "count": conocidas[name],
                "length": round(largo),
            }
        )

    return streets, incompletas, avisos


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

    if EXPECTED_ROWS is not None and len(locations) != EXPECTED_ROWS:
        fail(
            f"se esperaban {EXPECTED_ROWS} ubicaciones, hay {len(locations)}.\n"
            "       Si el listado nuevo es correcto, ajusta EXPECTED_ROWS en el bloque\n"
            "       de configuracion del principio de este script, o ponlo a None."
        )

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

    template = TEMPLATE.read_text(encoding="utf-8")

    rows = parse_rows(DATA.read_text(encoding="utf-8"))
    locations = build_locations(rows)
    numbers = check(locations)
    centro, mediana, raros = check_coherence(locations)
    streets, sin_coords, avisos = build_streets(locations, centro)
    n_chars = check_charset(locations, template, streets)

    markers = ["__LOCATIONS__", "__STREETS__", "__OPERATIVO__", "__LOGO__", "__FUSE__"]
    markers += [f"__FONT_{w}__" for w in FONT_WEIGHTS]
    for marker in markers:
        if marker not in template:
            fail(f"la plantilla no contiene el marcador {marker}")

    fonts = read_fonts()
    vendor = read_vendor()
    payload = json.dumps(locations, ensure_ascii=False, separators=(",", ":"))

    # Fecha y huella del listado. No se pintan en la aplicacion: se emiten aqui
    # para poder anotar que se publico y comparar dos compilaciones sin abrir
    # los archivos.
    build_date = date.today().strftime("%d.%m.%y")

    html = template.replace("__LOCATIONS__", payload)
    html = html.replace(
        "__STREETS__", json.dumps(streets, ensure_ascii=False, separators=(",", ":"))
    )
    html = html.replace("__OPERATIVO__", OPERATIVO)
    html = html.replace("__LOGO__", read_logo())
    html = html.replace("__FUSE__", vendor)
    for weight, b64 in fonts.items():
        html = html.replace(f"__FONT_{weight}__", b64)

    restantes = [m for m in markers if m in html]
    if restantes:
        fail("marcadores sin sustituir: " + ", ".join(restantes))

    assemble_dist(html)
    n_refs = check_dist_references()

    size = OUTPUT.stat().st_size
    unnamed = [loc["label"] for loc in locations if not loc["numbers"]]
    nombres_calle = sorted({loc["street"] for loc in locations})

    abbreviated = [
        f"{loc['label']} -> {loc['display']}"
        for loc in locations
        if loc["display"] != loc["label"]
    ]

    total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    n_files = sum(1 for f in DIST.rglob("*") if f.is_file())

    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()[:8]

    print(f"OK  {len(locations)} ubicaciones -> {OUTPUT.relative_to(ROOT)}")
    print(f"    operativo: {OPERATIVO}")
    print(f"    publicado {build_date}, data.md {digest}")
    print(f"    {len(numbers)} numeros, {len(nombres_calle)} calles en data.md")
    print(
        f"    centro {centro[0]:.6f},{centro[1]:.6f}"
        f" · mediana al centro {mediana:.0f} m"
    )

    # Una correccion de errata que ya no corresponde a ninguna fila es
    # configuracion muerta: no rompe nada, pero engana al que la lea.
    calles_crudas = {cells[2] for _, cells in rows}
    for errata in STREET_FIXES:
        if errata not in calles_crudas:
            print(f"    AVISO  STREET_FIXES corrige {errata!r}, que ya no esta en data.md")

    for aviso in avisos:
        print(f"    AVISO  {aviso}")
    for d, loc in raros:
        print(
            f"    AVISO  {loc['name']} esta a {d:.0f} m del centro,"
            f" {d / mediana:.0f} veces la mediana. Comprueba que es correcto."
        )

    if streets:
        detalle = ", ".join(f"{s['name']} ({s['length']} m)" for s in streets)
        print(f"    trazado disponible en {len(streets)}: {detalle}")
    if sin_coords:
        print(f"    SIN COORDENADAS, no se publican: {', '.join(sin_coords)}")
    if not STREETS.exists():
        print("    calles.md no existe: la app se publica sin trazado de calles")
    print(f"    sin numero: {', '.join(unnamed)}")
    print(f"    etiquetas abreviadas: {len(abbreviated)}")
    print(f"    fuente: {n_chars} caracteres usados, todos cubiertos")
    print(f"    emblema empotrado: {LOGO.stat().st_size / 1024:.1f} KB")
    print(f"    Fuse.js empotrado: {len(vendor) / 1024:.1f} KB")
    print(f"    index.html: {size / 1024:.1f} KB")
    print(f"    dist/: {n_files} archivos, {total / 1024:.1f} KB, {n_refs} referencias OK")


if __name__ == "__main__":
    main()
