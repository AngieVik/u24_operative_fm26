# 04 — Convenciones

## Idioma

- **Documentación y textos de interfaz:** español de España.
- **Código:** identificadores, nombres de archivo, ramas y mensajes de commit en inglés.
- **Comentarios:** español, y solo cuando expliquen el *porqué*. Nada de comentarios que
  repitan lo que el código ya dice.

## Estructura de carpetas

```
u24_operative_fm26/
├── netlify.toml                 Despliegue. publish = "dist"
├── CLAUDE.md                    Instrucciones permanentes
├── data.md                      Fuente de verdad de ubicaciones. Solo lectura.
├── calles.md                    Fuente de verdad de calles. Solo lectura. Opcional.
├── descripcion.md               Brief original. Documento histórico.
│
├── dist/                        ← LO ÚNICO QUE SE PUBLICA. Generado.
│   ├── index.html
│   ├── manifest.webmanifest
│   ├── sw.js
│   └── icons/                   Los 7 iconos que se sirven
│
├── src/                         Fuentes de la aplicación
│   ├── template.html            Plantilla: HTML, CSS y JS
│   ├── manifest.webmanifest     Manifiesto PWA
│   ├── sw.js                    Service worker
│   ├── logo.svg                 Emblema optimizado que se empotra
│   ├── vendor/
│   │   └── fuse.basic.min.js    Fuse.js 7.5.0. Única dependencia externa.
│   └── fonts/
│       ├── roboto-*.woff2       Roboto subconjuntada. Derivado.
│       ├── charset.txt          Cobertura real, para validar el build
│       └── original/            Roboto 2.138 completa + licencia. No se sirve.
│           └── origen.md        Versión, URL y SHA-256 de cada archivo
│
├── icons/                       Biblioteca de iconos. build.py copia 7 a dist/.
├── logo/                        Originales de marca. No se sirven.
│
├── scripts/
│   ├── build.py                 data.md + src/ → dist/
│   └── subset-fonts.py          Regenera la fuente y charset.txt
└── docs/                        Documentación numerada
                                 05 = qué tocar al cambiar de operativo
```

### Solo se publica `dist/`

`netlify.toml` apunta a `dist/`, y `build.py` la reconstruye desde cero en cada
ejecución: borra la carpeta y copia únicamente los archivos declarados en `COPY_ROOT` y
`COPY_ICONS`. Un archivo retirado del proyecto deja de publicarse automáticamente, y uno
nuevo no aparece en internet salvo que se añada de forma explícita.

Esto mantiene fuera de la web `data.md`, la documentación, las plantillas, los scripts y
los originales de marca. No contienen secretos, pero son material interno de un
dispositivo de emergencias y no tienen por qué ser públicos.

`dist/` **se commitea**: Netlify no ejecuta build, así que el contenido publicado es el
que haya en el repositorio.

### Dependencias externas

Una sola: **Fuse.js 7.5.0** (`fuse.basic.min`), en `src/vendor/`.

- Se copia al repositorio con una versión fija. **El build no descarga nada.**
- `build.py` la empotra en `index.html` y comprueba que exporta como módulo CommonJS,
  porque la plantilla la envuelve esperando `module.exports`.
- Para actualizarla: `npm pack fuse.js@<version>` y copiar `dist/fuse.basic.min.cjs` sobre
  `src/vendor/fuse.basic.min.js`. Después hay que volver a pasar las pruebas de
  coincidencia: los parámetros de `docs/02-datos.md` están calibrados sobre esta versión.

### Validaciones que hace `build.py`

Aborta el build, no avisa y continúa:

- El recuento declarado en `EXPECTED_ROWS`, 4 columnas por fila y formato de coordenadas.
- Identificadores, coordenadas y números sin duplicar.
- **Coherencia geográfica del listado consigo mismo**, no contra un lugar declarado: aborta
  si un punto se aleja más de 25 km del centro del conjunto. Ver `docs/02-datos.md`.
- `calles.md`: nombres que existan en `data.md`, sin repetir, extremos distintos y dentro
  del alcance del listado.

Y avisa sin abortar de lo que hay que mirar pero no puede decidir: ubicaciones muy
excéntricas, calles con longitud rara entre extremos y correcciones de errata que ya no
corresponden a ninguna fila.

### Nada de valores atados a un lugar

Lo que dependa del operativo va en el bloque de configuración del principio de `build.py`
—hoy `OPERATIVO` y `EXPECTED_ROWS`— y en ningún otro sitio. Una validación que obligue a
declarar dónde está el recinto es una traba: hay que escribirla en relación a los propios
datos. Ver `docs/05-cambiar-de-operativo.md`.
- **Cobertura tipográfica:** todo carácter que la aplicación vaya a pintar debe existir en
  `src/fonts/charset.txt`. Cubre tanto `data.md` (identificador, nombre y calle) como los
  rótulos de la interfaz: el bloque `TEXT` de la plantilla y el texto del HTML fuera de
  `<script>` y `<style>`. Sin esto, un carácter nuevo se publicaría como un cuadrado vacío
  sin que nadie se enterase.
- Ningún marcador `__…__` sin sustituir en la salida.
- Toda referencia a `icons/…` desde `index.html`, el manifiesto o el service worker existe
  dentro de `dist/`.

Los atributos HTML quedan fuera de la validación tipográfica a propósito: un `aria-label`
lo lee un lector de pantalla, no lo dibuja la fuente.

Nombres de archivo y carpeta en `kebab-case`. Los documentos de `docs/` llevan prefijo
numérico de dos dígitos para fijar el orden de lectura.

### Regla de originales frente a derivados

`logo/` guarda los originales de marca tal como los entregó el responsable y **no se
modifican**. Lo que consume la aplicación son derivados generados a partir de ellos:
`src/logo.svg` (optimizado, empotrado en el HTML) y los iconos de `icons/`. Si cambia la
marca, se sustituye el original y se regeneran los derivados; nunca al revés.

La misma regla se aplica a la tipografía: los `.woff2` de `src/fonts/` son derivados de
los originales de `src/fonts/original/`, que **sí viven en el repositorio** —Roboto es
Apache 2.0 y se puede redistribuir— precisamente para que regenerarlos no dependa de lo
que cada uno se descargue. La versión es la **2.138 (2017)**, la clásica estática; Google
Fonts sirve hoy la 3.x variable, con métricas distintas. `subset-fonts.py` comprueba la
versión y aborta si no es la esperada. Detalle completo en `src/fonts/original/origen.md`.

### Iconos servidos

| Archivo | Uso |
| --- | --- |
| `icon-192.png`, `icon-512.png` | Manifiesto, `purpose: any`. Emblema a sangre sobre el fondo de la app. |
| `icon-maskable-192.png`, `-512.png` | Manifiesto, `purpose: maskable`. Con zona de seguridad para que Android los recorte sin comerse el emblema. |
| `apple-touch-icon.png` | iOS, 180×180 y opaco: iOS no respeta la transparencia. |
| `favicon-32.png`, `-16.png` | Pestaña del navegador. |

Son los siete que `build.py` copia a `dist/icons/`. Los `icons/maskable_icon_x*.png` y
`icons/Icons.js` son la entrega original del generador: se conservan como referencia y
**no se publican**. En particular `maskable_icon.png` pesa 7 MB.

## Nomenclatura en código

| Elemento | Convención | Ejemplo |
| --- | --- | --- |
| Variables y funciones | `camelCase` | `normalizeSearchTerm` |
| Constantes de módulo | `SCREAMING_SNAKE_CASE` | `FUZZY_MAX_SCORE` |
| Archivos de código | `kebab-case` | `subset-fonts.py` |
| Campos de datos | `camelCase` | `lat`, `lon`, `numbers`, `nameSearch` |

Vocabulario del dominio, de uso obligatorio para evitar sinónimos dispersos:

| Concepto | Término en código |
| --- | --- |
| Punto del listado | `location` |
| Etiqueta visible del identificador | `label` / `display` |
| Números expandidos | `numbers` |
| Cadena normalizada de búsqueda | `search` / `nameSearch` |
| Término tecleado por el usuario | `query` |
| Coincidencia literal | `exact` |
| Coincidencia aproximada | `approx` |

## Estilo de código

- Sangría de 2 espacios, comillas simples, punto y coma al final de sentencia.
- Sin abstracciones anticipadas. Este proyecto es pequeño a propósito: se escribe la
  solución directa y se refactoriza solo cuando el código lo pida por duplicado real.
- Nada de dependencias para lo que la plataforma ya resuelve (normalización Unicode,
  filtrado de arrays, enlaces).
- Los textos visibles se declaran en el objeto `TEXT` de la plantilla, no dispersos por el
  código: es lo que permite validar la cobertura tipográfica.

## Interfaz

**El diseño visual es libre.** No hay tamaños, colores ni densidades protegidos: si una
propuesta mejora la legibilidad o el acierto al pulsar, se aplica. Lo que sigue no son
restricciones, sino las decisiones vigentes y el motivo por el que se tomaron, para que
quien las cambie sepa qué estaba resolviendo.

- **Mobile-first en vertical.** Se diseña para 360 px de ancho y se deja crecer. A partir
  de 600 px el contenido se centra en una columna.
- **Tema oscuro.** El uso es nocturno y prolongado.
- **Jerarquía de la fila:** identificador (acento, ancho fijo, cifras tabulares), nombre
  (elemento principal), calle (secundaria) y coordenadas (terciarias, cifras tabulares).
  El ancho fijo del identificador es lo que mantiene los nombres alineados en columna con
  etiquetas tan dispares como `3`, `180–186` o `S/N`.
- **Las coordenadas se pintan siempre**, no bajo demanda: son el plan B cuando Google Maps
  no carga y hay que dictar la posición por radio (RF-12). Cuestan una tercera línea y
  unas tres filas menos por pantalla; se asume, porque el mecanismo principal para llegar
  a una ubicación es el buscador, no el desplazamiento.
- **Bajo el buscador, el operativo en curso** (RF-15), en caja de título. Sin fecha de
  publicación: se probó y el responsable la retiró el 20/08/2026.
- **Sin líneas de separación.** Ni entre filas ni entre la fila y su botón. Lo que agrupa
  las tres líneas de una ubicación es la proximidad, y por eso las dos distancias están
  calculadas, no elegidas a ojo:

  | Distancia | Valor |
  | --- | --- |
  | Hueco óptico entre las líneas de una misma ubicación | **6,5 px**, idéntico en los dos |
  | Hueco entre bloques de ubicaciones distintas | **13,75 px** |
  | Aire sobre y bajo el bloque, dentro de la fila | 6,875 px, simétrico |

  Cambiar una obliga a recalcular la otra: la proporción entre ambas (2,1 a 1) es la que
  hace de separador ahora que no hay líneas. Por debajo de ahí las tres líneas de una
  ubicación empiezan a leerse pegadas a las de la siguiente.
- **Altura de línea en píxeles, no proporcional.** El espacio que se ve entre dos líneas es
  el margen más el aire interno de cada caja, `(altura de línea − tamaño) / 2`. Con
  `line-height` proporcional ese aire cambia con cada tamaño de letra y los huecos dejan de
  cuadrar. Con valores fijos —21 px para el nombre, 16 px para calle y coordenadas— los
  márgenes de 2,5 y 2,75 px dan exactamente 6,5 px en los dos huecos.
- **Contrastes medidos** sobre el fondo actual, no estimados a ojo: texto principal
  17,1:1; calle 7,1:1; rótulos secundarios 6,2:1; identificador 12,2:1.
- **Al mapa solo se llega por el botón de la derecha.** Filas de 72 px,
  botón de 64 px de ancho por toda la altura de la fila. Con 125 elementos en lista, todo
  lo que se pueda pulsar se acaba pulsando sin querer al desplazar. Esta regla no está
  sujeta a la libertad de diseño del párrafo anterior: añadir otro elemento pulsable, o
  convertir la fila en enlace, exige acuerdo expreso del responsable.
- **Tocar las coordenadas las copia**, sin icono: la confirmación cambia el texto entero a
  «Copiado» durante 1,4 s, que es lo único que anuncia la acción. El relleno que le da 32 px
  de objetivo táctil se compensa con márgenes negativos, de modo que la caja ocupa en el
  flujo lo mismo que una línea de texto y el ritmo vertical no se mueve ni un píxel.
- **La fila de calle se ve igual que las demás.** La distinguen su segunda línea y el icono
  de recorrido del botón, no el color: teñirla de amarillo desentonaba con el resto.
- **Las coincidencias aproximadas van rotuladas y al final.** Nunca se mezclan con las
  literales ni se presentan como exactas.
- **Sin animaciones de transición** que retrasen la respuesta. El filtrado es instantáneo
  y debe *parecerlo*.
- El campo de búsqueda usa `inputmode` adecuado y no activa autocorrección ni
  autocapitalización, que estorban al teclear nombres propios y números.

### Pendiente conocido

No hay forma de saber, desde un móvil, qué listado lleva instalado. La fecha y la huella de
`data.md` solo aparecen en la salida de `scripts/build.py`. Ver `docs/02-datos.md`.

## Accesibilidad

- HTML semántico: el listado es una lista, cada resultado es un enlace.
- Cada enlace tiene un nombre accesible que identifica la ubicación completa —nombre,
  identificador y calle—, no un genérico «navegar».
- El resultado del filtrado se anuncia mediante una región activa, indicando además si lo
  que se ofrece son coincidencias aproximadas.
- Navegable por teclado de principio a fin, aunque el uso previsto sea táctil.
- Respetar `prefers-reduced-motion`.

## Rendimiento

- Sin peticiones de red en el arranque más allá del propio `index.html`.
- Todo va empotrado: datos, motor de búsqueda, tipografía y emblema.
- Presupuesto orientativo: menos de 150 KB en la carga inicial, sin comprimir. Estado
  actual: ~112 KB.

## Control de versiones

- Rama principal: `main`. Se trabaja con ramas cortas y se integra rápido.
- Mensajes de commit en inglés, imperativo, con prefijo de tipo:
  `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`.
- Un commit, un cambio con sentido propio. No se mezclan formateo y lógica.
- `data.md` solo cambia en commits `chore(data):` dedicados, nunca junto a código.

## Pruebas

Cobertura deliberadamente selectiva: se prueba lo que puede fallar en silencio y hacer
que la unidad vaya a la ubicación equivocada.

Obligatorio:

- Conversión de `data.md`: recuento de 125, validación de coordenadas, expansión de
  rangos, abreviatura de etiquetas, corrección de la errata de calle.
- Normalización de búsqueda: tildes, mayúsculas, comillas tipográficas.
- Reglas de coincidencia exacta: `7` no devuelve la 74 por delante de la 7; `67` encuentra
  `66-67-68`; `39` devuelve lista vacía y **no** ofrece aproximadas.
- Reglas de coincidencia aproximada: `pinpi` encuentra El Pimpi y aparece bajo el rótulo
  de aproximadas; una consulta literal con resultados no muestra ese rótulo; un término de
  menos de 3 caracteres no dispara el motor aproximado.
- Construcción de la URL de Maps: coordenadas con signo negativo, coma sin codificar, y
  las 125 URLs contrastadas una a una contra `data.md`.
- Coordenadas mostradas: las 125 contrastadas una a una contra `data.md`.
- Rótulo del operativo, literal y sin fecha.
- Calles: escribir el nombre de una calle la devuelve como primera fila, sin identificador
  y con su recuento de ubicaciones; las tres URLs de trazado contrastadas contra
  `calles.md`; un término de dos letras y una consulta numérica no traen calles; la fila de
  calle no va en un color distinto al de las demás.
- Búsqueda por dirección y sin espacios: `C/Peñ` encuentra la calle y sus 44 ubicaciones,
  `rodriguez` devuelve las 48 de su calle, `66 67` encuentra `66-67-68` y `peñsta` llega a
  la calle por aproximación.
- Copiado: el texto copiado es exactamente `lat, lon`, aparece la confirmación, vuelve sola,
  no navega, y las coordenadas no llevan icono.
- Que la fila no sea un enlace, que no contenga ningún botón y que no haya líneas de
  rejilla. Es la forma de que estas reglas no se pierdan en un rediseño futuro.
- **Service worker**, contra un servidor que se puede volver lento a voluntad: con la red
  saturada la app abre desde la caché en ~1,5 s y no espera a la red; sin cobertura sigue
  abriendo; con red normal responde la red en milisegundos, no el límite.

Estas pruebas se ejecutan sobre `dist/index.html` ya construido, en un navegador real sin
interfaz. Es la única forma de comprobar a la vez el motor, el DOM y los enlaces. Las del
service worker necesitan además servirlo por HTTP: desde `file://` no se registra.

No obligatorio: pruebas de interfaz automatizadas más allá de lo anterior. La validación
visual es manual, sobre dispositivo real, siguiendo la lista de
`docs/03-navegacion-maps.md`.

## Definición de terminado

Una tarea no está terminada hasta que:

1. Cumple los requisitos `M` que le corresponden de `docs/01-requisitos.md`.
2. Pasa las pruebas obligatorias.
3. Se ha comprobado en un móvil real, no solo en el navegador de escritorio.
4. No ha ampliado el alcance ni ha añadido dependencias sin justificar.
