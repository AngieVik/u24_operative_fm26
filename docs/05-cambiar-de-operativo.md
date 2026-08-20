# 05 — Cambiar de operativo

Qué hay que tocar para publicar esta misma aplicación con otro listado: otra feria, otro
año, otra ciudad. Escrito para hacerlo del tirón, en orden, sin tener que leer el resto de
la documentación.

**Regla de fondo:** el script no sabe dónde estás ni cuántas ubicaciones hay. Todo lo que
depende del operativo está en un solo bloque, al principio de `scripts/build.py`.

## 1. Sustituir `data.md`

El listado nuevo, con las mismas cuatro columnas: `ubication_number`, `name`, `adress`,
`coords`. Formato de coordenadas `lat,lon`, sin espacio y con punto decimal. Ver
`docs/02-datos.md`.

No hace falta que las coordenadas caigan en ningún sitio concreto: el build comprueba que
son coherentes **entre sí**, no contra una ciudad.

## 2. Abrir el bloque de configuración de `scripts/build.py`

Está en las primeras líneas del archivo, bajo el rótulo *Configuración del operativo*:

```python
OPERATIVO = "Feria de Málaga 2026"   # rótulo bajo el buscador
EXPECTED_ROWS = 125                  # filas que debe traer data.md, o None
```

- **`OPERATIVO`**: el texto que se ve bajo el buscador. En caja de título, tal cual se
  quiera leer.
- **`EXPECTED_ROWS`**: el número de filas del listado nuevo. Es la red contra un archivo
  truncado o pegado a medias, que es el único error de bulto que los datos no delatan por
  sí solos. Si no se quiere esa red, se pone `None` y el recuento solo se informa.

## 3. Rellenar o vaciar `calles.md`

Si el recinto nuevo no tiene calles que trazar, se deja solo la cabecera:

```markdown
| street | start | end | waypoints |
| --- | --- | --- | --- |
```

También se puede borrar el archivo entero: es opcional y sin él la aplicación funciona
igual, sin trazados.

Si sí las tiene, los nombres deben coincidir **exactamente** con los de la columna `adress`
de `data.md`. Formato en `docs/02-datos.md`.

## 4. Revisar `STREET_FIXES`

En `scripts/build.py`. Corrige erratas concretas del listado anterior. Si alguna ya no
aparece en el nuevo `data.md`, el build lo avisa y se puede borrar esa entrada.

## 5. Compilar

```
python3 scripts/build.py
```

Falla ruidosamente y dice qué pasa y en qué línea. Si se queja de que la tipografía no
cubre un carácter —un nombre con un símbolo que antes no se usaba—, hay que regenerar el
subconjunto:

```
pip install fonttools brotli
python3 scripts/subset-fonts.py
python3 scripts/build.py
```

Los originales están en `src/fonts/original/` y el script los toma solos.

## 6. Leer los avisos

El build no solo dice `OK`. También avisa, sin abortar, de lo que conviene mirar:

- Ubicaciones muy alejadas del grueso del listado. Puede ser correcto —un punto en otra
  parte de la ciudad— o una coordenada mal copiada. Lo decide quien conoce el operativo.
- Calles con una distancia rara entre extremos.
- Correcciones de errata que ya no corresponden a ninguna fila.

## 7. Comprobar antes de publicar

- Abrir `dist/index.html` y buscar tres o cuatro ubicaciones del listado nuevo.
- Comprobar en un **móvil real** que el enlace abre la ficha en el punto correcto,
  contrastando contra `data.md` y no de memoria.
- Si hay calles, comprobar que el trazado dibuja la calle y no un rodeo.

## Lo que **no** hay que tocar

- La envolvente geográfica: ya no existe. El build deduce el centro del propio listado.
- El motor de búsqueda, sus umbrales y la lista de resultados: no dependen del operativo.
- `netlify.toml`, el service worker y el manifiesto, salvo lo de la marca que se indica
  abajo.

## Si además cambia la unidad, no solo el operativo

`U24` está en seis sitios, y ninguno de ellos rompe el build: la aplicación se publicaría
con la marca antigua sin avisar. Hay que cambiarlos a mano.

| Dónde | Qué |
| --- | --- |
| `src/template.html` | `<title>`, `meta description`, `apple-mobile-web-app-title` |
| `src/manifest.webmanifest` | `name`, `short_name`, `description` |
| `scripts/build.py` | el `aria-label` del emblema, en `read_logo()` |
| `src/sw.js` | el nombre de la caché, `CACHE` |
| `src/logo.svg` | el emblema que se empotra |
| `icons/` | los siete iconos que se publican, y `logo/` como original |

Mientras solo cambie el operativo —misma unidad, otra feria—, nada de esto se toca.
