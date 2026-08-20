# 02 — Datos

## Fuente de verdad

`data.md`, en la raíz del proyecto. Tabla Markdown con **125 filas** de datos y cuatro
columnas: `ubication_number`, `name`, `adress`, `coords`.

**`data.md` no se edita.** Todas las correcciones y transformaciones descritas aquí se
aplican en el proceso de conversión a datos de aplicación, dejando el original intacto.
Si se detecta un error real en los datos de origen, se comunica al responsable del
proyecto para que decida; no se corrige por iniciativa propia.

## Análisis del origen

Comprobado sobre el archivo actual el 19/08/2026:

- 125 filas, sin nombres duplicados y sin coordenadas duplicadas.
- Todas las coordenadas tienen formato `lat,lon` con exactamente 6 decimales.
- Envolvente: latitud `36.701673`–`36.706490`, longitud `-4.464616`–`-4.458656`.
- 204 identificadores numéricos individuales, todos únicos, en el rango 1–213.
- Huecos en la numeración: **39, 40, 41, 42, 81, 82, 83, 84, 212**. No son un error de
  transcripción; son números sin punto asignado en el listado.
- Cuatro calles distintas, una de ellas por errata (ver más abajo).

## Modelo de datos de la aplicación

Cada ubicación se representa así:

| Campo | Tipo | Origen | Notas |
| --- | --- | --- | --- |
| `id` | texto | derivado | Identificador estable y único. Ver «Generación de `id`». |
| `label` | texto | `ubication_number` | Etiqueta tal cual aparece en el listado: `66-67-68`, `S/N`, `169BIS`. |
| `display` | texto | derivado | Etiqueta abreviada para la columna de ancho fijo: `180-181-…-186` → `180–186`. |
| `numbers` | lista de enteros | `ubication_number` | Números expandidos para la búsqueda: `66-67-68` → `[66, 67, 68]`. Vacía para `S/N` y `169BIS`. |
| `name` | texto | `name` | Nombre tal cual, con tildes y mayúsculas originales. Es lo que se muestra. |
| `street` | texto | `adress` | Calle normalizada. Ver «Normalización de calles». |
| `lat` | texto | `coords` | Latitud decimal, con sus 6 decimales literales. **Se muestra en pantalla.** |
| `lon` | texto | `coords` | Longitud decimal, con sus 6 decimales literales. **Se muestra en pantalla.** |
| `search` | texto | derivado | `name` + `label` + `street` normalizados. Filtrado literal de texto. |
| `flat` | texto | derivado | Lo mismo, dejando solo letras y dígitos. Ver «Búsqueda sin espacios». |
| `nameSearch` | texto | derivado | Solo `name` normalizado. Filtrado aproximado y búsqueda de cifras que forman parte del nombre sin contaminar la búsqueda por número. |

## Generación de `id`

`label` **no es único**: hay cuatro filas con `S/N`. El identificador se genera a partir
del índice de fila en `data.md` (base 0), con prefijo:

```
loc-000, loc-001, … loc-124
```

Es estable mientras no cambie el orden de `data.md`, que se conserva deliberadamente
porque refleja el recorrido físico de cada calle.

## Casos especiales

### Etiquetas no numéricas

| Etiqueta | Ocurrencias | Ubicaciones |
| --- | --- | --- |
| `S/N` | 4 | Caseta Municipal Ecuestre (Caballos), Fuente de la Biznaga, Rotonda de las Biznagas, Banquito de la feria |
| `169BIS` | 1 | «Sin nombre conocido» |

Estas cinco entradas tienen `numbers` vacío: solo se encuentran escribiendo texto. Se
mantienen en el listado porque son puntos de referencia útiles para dar acceso a la unidad.

### «Sin nombre conocido» (169BIS)

Es el nombre literal del origen, no un dato ausente. Se muestra tal cual; su valor
operativo está en la etiqueta `169BIS` y en las coordenadas.

### Rangos de números

Un punto puede ocupar varias parcelas: `1-2`, `32-33-34`, `180-181-182-183-184-185-186`.
El rango se expande a números individuales para que buscar cualquiera de ellos lo
encuentre, pero **se conserva siempre la etiqueta completa original** en `label`, que es
la que aparece rotulada sobre el terreno.

Los rangos son **enumeraciones, no intervalos**: `1-2` significa «1 y 2», no «de la 1 a la
2». En la práctica coinciden porque todos los rangos son consecutivos, pero la expansión
debe hacerse partiendo por `-`, nunca generando el intervalo.

`display` sí abrevia a partir de tres números, y solo si son consecutivos; si algún
listado futuro trae un rango no consecutivo, se muestra la etiqueta completa en vez de
mentir sobre los números que abarca.

### Normalización de calles

Se agrupan en cuatro valores. Se corrige una errata evidente del origen:

| Valor en `data.md` | Filas | Valor normalizado |
| --- | --- | --- |
| `C/ Antonio Rodríguez Sánchez` | 48 | `C/ Antonio Rodríguez Sánchez` |
| `C/ Peñista Rafael Fuentes` | 43 | `C/ Peñista Rafael Fuentes` |
| `C/ José Blánquez 'El Maño'` | 32 | `C/ José Blánquez 'El Maño'` |
| `C/ Peñista Rafael Fuentess` | 1 | `C/ Peñista Rafael Fuentes` — **errata corregida** (doble `s`) |
| `Palacio de Ferias` | 1 | `Palacio de Ferias` |

La fila afectada por la errata es la Caseta Municipal Ecuestre (`S/N`).

### Ubicación fuera del grupo principal

**Banquito de la feria** (`Palacio de Ferias`) está a unos 370 m del centro geométrico del
resto de ubicaciones, mientras que todas las demás quedan dentro de un radio de ~285 m.
No es un error: es un punto singular fuera de las calles principales. Se mantiene.

## Índice de búsqueda

Para cumplir RF-5 (insensible a mayúsculas y tildes) el filtrado no se hace sobre `name`
directamente, sino sobre campos precalculados:

1. Concatenar `name` y `label` (para `search`) o tomar solo `name` (para `nameSearch`).
2. Pasar a minúsculas.
3. Descomponer en Unicode NFD y eliminar los diacríticos combinantes.
4. Normalizar comillas tipográficas (`’` → `'`) y espacios múltiples.

Ejemplo: `Casa de Álora-Cosa Nuestra` + `58-59-60` + `C/ Peñista Rafael Fuentes` →
`casa de alora-cosa nuestra 58-59-60 c/ penista rafael fuentes`.

**La calle entra en el índice** desde el 20/08/2026: buscar por dirección es otra forma
legítima de llegar a una ubicación, y escribir el nombre de una calle devuelve la calle
primero y sus ubicaciones detrás.

El término tecleado por el usuario se normaliza igual antes de comparar, también antes de
entregárselo al motor aproximado: **Fuse.js no elimina tildes por su cuenta**.

### Búsqueda sin espacios

Además de `search` se precalcula `flat`: lo mismo dejando **solo letras y dígitos**, sin
espacios, barras, guiones ni apóstrofos. El término tecleado se aplana igual antes de
comparar.

Es lo que hace que `C/Peñ` encuentre `C/ Peñista Rafael Fuentes` aunque falte el espacio, y
que `66 67` encuentre `66-67-68`. Sin esto, un separador de más o de menos deja la pantalla
vacía, que es lo último que puede pasar tecleando con prisa.

No sustituye a la coincidencia aproximada: `flat` es exacto y determinista, y resuelve el
problema de la puntuación, no el de las erratas.

## Reglas de coincidencia

El comportamiento depende de si el término tecleado es **solo dígitos** o no. Los dos
modos son excluyentes: nunca se mezclan.

### Término numérico (`7`, `192`, `66`)

1. Número **exacto** presente en `numbers`.
2. Número de `numbers` que **empieza por** el término: `7` → `70`, `71`, `73`…
   Necesario para que la lista se estreche de forma natural mientras se teclea.
3. `nameSearch` que **contiene** el término, para nombres que llevan cifras
   (`Calle Larios 15`, `La Noria 211`, `Puerto 10 La Favela`).

Queda **prohibida la coincidencia por subcadena y la coincidencia aproximada sobre el
número**: escribir `39` no puede devolver la `139`, ni `7` la `17`. Enviar a la unidad a
la ubicación equivocada es el único fallo grave que esta aplicación puede cometer, y una
subcadena o una aproximación lo provocan en silencio. Los huecos de numeración (39-42,
81-84, 212) deben devolver **lista vacía**, que es información útil: ese punto no existe.

Una consulta numérica **nunca** cae al motor aproximado, ni siquiera cuando no devuelve
nada.

### Término de texto (`pimpi`, `alora`)

1. `search` que **empieza por** el término.
2. `search` que **contiene** el término.
3. `flat` que **contiene** el término aplanado, para los que no hayan entrado por 1 ni 2.
4. Si nada de lo anterior devuelve nada: **coincidencia aproximada** sobre `nameSearch` y
   sobre los nombres de calle.

Las calles se buscan siempre por `flat`, con un mínimo de 3 caracteres, y van delante.

### Coincidencia aproximada

Motor: Fuse.js. Parámetros actuales, en `src/template.html`:

| Parámetro | Valor | Por qué |
| --- | --- | --- |
| `keys` | `['nameSearch']` | Solo el nombre. El identificador tiene su propia rama exacta y no debe entrar aquí jamás. |
| `threshold` | `0.4` | Tolera la errata típica de una o dos letras sin abrir la mano a cualquier cosa. |
| `ignoreLocation` | `true` | La errata puede estar al principio, en medio o al final del nombre. |
| `minMatchCharLength` | `2` | **No subir a 3.** Comprobado el 19/08/2026: con 3, `pinpi` deja de encontrar «El Pimpi», porque la coincidencia se parte en fragmentos de dos caracteres. |
| `includeScore` | `true` | Necesario para ordenar por parecido y para el corte de abajo. |

Y tres límites propios, fuera de Fuse:

| Límite | Valor | Por qué |
| --- | --- | --- |
| Longitud mínima del término | 3 caracteres | Con una o dos letras cualquier nombre se parece a la consulta y el resultado es ruido. |
| Corte de puntuación | `score <= 0.6` | Por encima ya no es una errata, es otra palabra. Medido sobre el listado actual: los aciertos reales quedan entre 0,14 y 0,59. |
| Máximo de resultados | 8 | La lista aproximada se lee entera de un vistazo o no sirve. |

**Solo actúa como respaldo.** Mientras la búsqueda literal devuelva algo, la lista es
exactamente la de siempre: nada de ruido añadido a una consulta que ya funciona.

Casos comprobados el 19/08/2026 sobre los 125 nombres reales: `pinpi` → El Pimpi,
`malamja` → Malamía, `alorra` → Casa de Álora, `revelo` → El Revuelo, `montecalro` →
Peña Caballista Monteclaro, `bisnaga` → Fuente de la Biznaga, `saroa` → El Sarao,
`favella` → Puerto 10 La Favela. En todos ellos el acierto sale **el primero** de la
lista aproximada.

### Orden y presentación de los resultados

Exacto → prefijo → contiene. Dentro de cada grupo se conserva el orden original de
`data.md`. Las aproximadas van **siempre al final**, detrás de un rótulo que las
identifica como tales, y ordenadas por parecido. La interfaz nunca presenta una
coincidencia aproximada como si fuera literal.

## Formato de las coordenadas

- Se conservan los 6 decimales del origen (precisión de ~0,1 m, más que suficiente).
- Se pasan a Google Maps como `lat,lon` separados por coma, sin espacios y con punto
  decimal, en el orden latitud primero.
- Nunca se redondean ni se reformatean por localización: el separador decimal es siempre
  el punto, aunque la interfaz esté en español. Por eso se guardan como texto y no como
  número.

### Coordenadas a la vista

Desde el 20/08/2026 cada fila muestra sus coordenadas, en la forma `36.701673, -4.462155`
—con espacio tras la coma, que es como se dictan— y con cifras de ancho fijo para que se
lean sin trastabillar.

No es un dato técnico de relleno. La aplicación funciona sin cobertura, pero su destino
—Google Maps— no: si la red no da, pulsar el botón lleva a un mapa en blanco y el equipo
se queda sin nada. Las coordenadas a la vista son la única salida que queda entonces, y se
pueden dictar por radio. Ver RF-12 en `docs/01-requisitos.md`.

**Al tocarlas se copian al portapapeles.** El texto copiado es exactamente el que se ve,
`lat, lon`, sin adornos ni etiquetas: es lo que se pega en un mensaje o en otra aplicación
de mapas. Durante 1,4 s el texto cambia a «Copiado» y vuelve solo.

**Sin icono.** La confirmación es lo único que anuncia la acción, y por eso cambia el texto
entero y no un detalle de 12 px. El relleno que le da un objetivo táctil de 32 px se
compensa con márgenes negativos, de modo que la caja sigue ocupando en el flujo lo mismo
que ocupaba siendo una línea de texto: el ritmo vertical de la fila no se mueve.

Se copia con `navigator.clipboard` cuando el contexto es seguro —el caso normal, por
https— y con el método antiguo de `execCommand` cuando no lo es, para que también funcione
abriendo el archivo directamente en una prueba.

El texto no es seleccionable con el dedo, igual que el resto de la fila: al desplazar una
lista de 125 elementos, el arrastre iniciaba selecciones y llenaba la pantalla de resaltes.
Copiar con un toque sustituye a esa vía.

## Proceso de conversión

`data.md` → datos de aplicación mediante `scripts/build.py`, que:

1. Lee `data.md` y descarta cabecera y separador.
2. Valida que cada fila tiene exactamente 4 columnas.
3. Valida que `coords` cumple `^-?\d+\.\d+,-?\d+\.\d+$` y que el punto es coherente con el
   resto del listado. Ver «Coherencia geográfica».
4. Aplica las normalizaciones descritas arriba.
5. Comprueba que no hay identificadores, coordenadas ni números repetidos.
6. Comprueba que la tipografía subconjuntada cubre todos los caracteres que se van a
   pintar, tanto los de `data.md` como los rótulos de la propia interfaz.
7. Falla de forma ruidosa ante cualquier fila inválida. No omite filas en silencio.
8. Emite un recuento final que debe coincidir con 125.

La ejecución del script forma parte del proceso de compilación, para que un cambio en
`data.md` nunca quede sin reflejarse en la aplicación desplegada.

## Calles — `calles.md`

Segunda fuente de verdad, en la raíz junto a `data.md` y con las mismas reglas: se lee, no
se edita desde el código, y cualquier corrección se aplica en la conversión.

**El archivo es opcional.** Si no existe, la aplicación se compila y funciona igual, solo
que sin trazado de calles, y el build lo dice en su salida. Las filas sin coordenadas se
omiten y también se informan, para poder rellenar el listado por partes.

Sirve para trazar el recorrido de una calle sobre el mapa a partir de sus dos extremos.
Google Maps no permite dibujar ni resaltar nada, así que el trazado se consigue pidiendo
una ruta **a pie** entre los dos puntos: el camino que dibuja sigue la calle. Ver
`docs/03-navegacion-maps.md`.

### Formato

```markdown
| street                       | start               | end                 | waypoints |
| ---------------------------- | ------------------- | ------------------- | --------- |
| C/ Antonio Rodríguez Sánchez | 36.701673,-4.462155 | 36.705559,-4.464616 |           |
```

| Columna | Obligatoria | Contenido |
| --- | --- | --- |
| `street` | Sí | Nombre de la calle **idéntico al de la columna `adress` de `data.md`**, ya corregido de erratas. Es lo que permite relacionar cada calle con sus ubicaciones. |
| `start` | Sí | Coordenadas de un extremo, `lat,lon`. |
| `end` | Sí | Coordenadas del otro extremo, `lat,lon`. |
| `waypoints` | No | Puntos intermedios, `lat,lon` separados por `;`. Solo hacen falta si Google traza el camino por otro sitio. Se puede dejar vacía. |

Reglas de escritura, iguales a las de `data.md`:

- Coordenadas **sin espacio tras la coma**, punto decimal y 6 decimales: `36.701673,-4.462155`.
  Es el mismo formato que `data.md`, para que lo valide el mismo código y no convivan dos
  maneras de escribir lo mismo.
- Una fila por calle, sin repetir.
- La fila de cabecera se ignora al leer, así que da igual en qué idioma esté puesta.

### Validaciones

Las mismas que para `data.md`: abortan el build, nunca continúan en silencio.

- Tres o cuatro columnas por fila.
- Coordenadas con formato válido y dentro de la envolvente documentada.
- `street` existe en `data.md`. Un nombre que no case es un error, no una calle nueva.
- Sin calles repetidas, y `start` distinto de `end`.
- Distancia entre extremos dentro de lo plausible. Las tres calles del recinto miden hoy
  entre 485 y 538 m, medidas sobre las ubicaciones de `data.md`; una distancia de pocos
  metros o de varios kilómetros indica una coordenada mal copiada.

### Origen de las coordenadas actuales

Las tres filas están rellenas con las **dos ubicaciones más alejadas entre sí de cada
calle**, tomadas de `data.md`. No son coordenadas medidas sobre el terreno ni inventadas:
salen del propio listado.

| Calle | Ubicaciones | Extremo a extremo |
| --- | --- | --- |
| `C/ Antonio Rodríguez Sánchez` | 48 | `36.701673,-4.462155` → `36.705559,-4.464616` (485 m) |
| `C/ Peñista Rafael Fuentes` | 44 | `36.701843,-4.461482` → `36.706232,-4.464010` (538 m) |
| `C/ José Blánquez 'El Maño'` | 32 | `36.702188,-4.460701` → `36.706490,-4.463178` (527 m) |
| `Palacio de Ferias` | 1 | No es una calle: una sola ubicación. Queda fuera a propósito. |

**Consecuencia:** el trazado cubre de la primera a la última caseta, que es el tramo con
ubicaciones. Si el vial arranca antes o sigue más allá, esa parte no se dibuja. Afinarlo es
cambiar dos números en `calles.md` y recompilar.

### Riesgo abierto — verificar en campo

Las calles del Real son viales de feria. **Si Google Maps no las tiene como camino
transitable, la ruta a pie no las seguirá**: la trazará por fuera del recinto o no
devolverá nada. Esto **no se ha podido comprobar**: hace falta abrir una de las tres en un
móvil real y mirar qué dibuja.

Si el trazado se va por otro sitio, la columna `waypoints` lo corrige. Si no existe camino
alguno, esta vía no sirve y hay que replantear la función entera.

## Coherencia geográfica

El build comprueba que las coordenadas son consistentes **entre sí**, no contra un lugar
concreto: no sabe ni tiene por qué saber en qué ciudad se trabaja.

Toma como centro la **mediana** de latitudes y longitudes —no la media, para que una
coordenada disparatada no arrastre el centro y siga destacando— y mide la distancia de
cada punto a ese centro.

| Situación | Qué hace |
| --- | --- |
| Un punto a más de **25 km** del centro | **Aborta.** A esa distancia ya no es el mismo operativo. |
| Un punto a más de **500 m** y a más de **4 veces** la mediana | **Avisa** y sigue. Puede ser correcto. |
| Todo lo demás | Nada. |

Calibrado sobre el listado actual: la mediana al centro es de 144 m y el punto más
excéntrico —el Banquito de la feria— está a 370 m, 2,6 veces la mediana. No genera ningún
aviso.

Comprobado el 20/08/2026 sobre copias del listado real:

| Caso | Resultado |
| --- | --- |
| Un dígito cambiado en la latitud (`36.701673` → `36.071673`) | Aborta: 70 km |
| Una coordenada pegada de otra provincia | Aborta: 182 km |
| Una ubicación añadida en Calle Larios, a 4 km | Compila y avisa |

### Por qué no una envolvente fija

Hasta el 20/08/2026 el build exigía que cada coordenada cayera dentro de un rectángulo
declarado a mano, el del Real de la Feria de Málaga. Se retiró por dos motivos:

1. **Obligaba a declarar la ciudad.** Añadir una ubicación del centro de Málaga, o cambiar
   de feria, exigía editar el script antes de que compilara nada.
2. **No detectaba los errores pequeños.** Se comprobó moviendo un punto 33 m —el tipo de
   errata que se comete copiando— y el build lo publicó sin rechistar.

Es decir, cobraba un peaje permanente por una protección que solo cubría los errores de
bulto. La comprobación relativa cubre exactamente esos mismos errores sin pedir nada.

## Actualización del listado

Procedimiento completo, paso a paso, en **`docs/05-cambiar-de-operativo.md`**.

En resumen: se sustituye `data.md`, se ajusta el bloque de configuración del principio de
`scripts/build.py` —`OPERATIVO` y `EXPECTED_ROWS`— y se rellena o se vacía `calles.md`. No
hay nada más que dependa del operativo.

Si el listado nuevo trae caracteres que la fuente no cubre, el build se detiene: hay que
regenerar el subconjunto con `python3 scripts/subset-fonts.py`, que toma los originales de
`src/fonts/original/`. Ver `src/fonts/original/origen.md`.

### Cómo saber qué listado hay publicado

`build.py` imprime la fecha de publicación y las 8 primeras cifras del SHA-256 de
`data.md`:

```
OK  125 ubicaciones -> dist/index.html
    publicado 20.08.26, data.md 36637fe8
```

Ninguno de los dos se pinta en la aplicación: sirven para anotar qué se publicó y para
comparar dos compilaciones sin abrir los archivos. Conviene apuntar la fecha y la huella
en el mensaje del commit que actualiza `data.md`, porque es el único rastro que queda.

**Limitación conocida:** desde un móvil no se puede saber qué listado lleva. Si un
dispositivo se queda con una versión anterior en la caché, es indetectable sin comparar
resultados a mano contra otro móvil.
