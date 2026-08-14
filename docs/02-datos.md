# 02 — Datos

## Fuente de verdad

`data.md`, en la raíz del proyecto. Tabla Markdown con **125 filas** de datos y cuatro
columnas: `ubication_number`, `name`, `adress`, `coords`.

**`data.md` no se edita.** Todas las correcciones y transformaciones descritas aquí se
aplican en el proceso de conversión a datos de aplicación, dejando el original intacto.
Si se detecta un error real en los datos de origen, se comunica al responsable del
proyecto para que decida; no se corrige por iniciativa propia.

## Análisis del origen

Comprobado sobre el archivo actual:

- 125 filas, sin nombres duplicados y sin coordenadas duplicadas.
- Todas las coordenadas tienen formato `lat,lon` con exactamente 6 decimales.
- Envolvente: latitud `36.701673`–`36.706490`, longitud `-4.464616`–`-4.458656`.
- 204 números de caseta individuales, todos únicos, en el rango 1–213.
- Huecos en la numeración: **39, 40, 41, 42, 81, 82, 83, 84, 212**. No son un error de
  transcripción; son números sin caseta asignada en el listado.
- Cuatro calles distintas, una de ellas por errata (ver más abajo).

## Modelo de datos de la aplicación

Cada ubicación se representa así:

| Campo | Tipo | Origen | Notas |
| --- | --- | --- | --- |
| `id` | texto | derivado | Identificador estable y único. Ver «Generación de `id`». |
| `label` | texto | `ubication_number` | Etiqueta tal cual aparece en el listado: `66-67-68`, `S/N`, `169BIS`. Es lo que se muestra al usuario. |
| `numbers` | lista de enteros | `ubication_number` | Números expandidos para la búsqueda: `66-67-68` → `[66, 67, 68]`. Vacía para `S/N` y `169BIS`. |
| `name` | texto | `name` | Nombre tal cual, con tildes y mayúsculas originales. Es lo que se muestra. |
| `street` | texto | `adress` | Calle normalizada. Ver «Normalización de calles». |
| `lat` | número | `coords` | Latitud decimal. |
| `lon` | número | `coords` | Longitud decimal. |
| `search` | texto | derivado | `name` + `label` normalizados. Filtrado de texto. Ver «Índice de búsqueda». |
| `nameSearch` | texto | derivado | Solo `name` normalizado. Permite encontrar cifras que forman parte del nombre sin contaminar la búsqueda por número. |

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

Una caseta puede ocupar varias parcelas: `1-2`, `32-33-34`, `180-181-182-183-184-185-186`.
El rango se expande a números individuales para que buscar cualquiera de ellos encuentre
la caseta, pero **se muestra siempre la etiqueta completa original**, que es la que
aparece rotulada en el recinto.

Los rangos son **enumeraciones, no intervalos**: `1-2` significa «casetas 1 y 2», no
«de la 1 a la 2». En la práctica coinciden porque todos los rangos son consecutivos, pero
la expansión debe hacerse partiendo por `-`, nunca generando el intervalo.

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

### Ubicación fuera del recinto

**Banquito de la feria** (`Palacio de Ferias`) está a unos 370 m del centro geométrico del
resto de ubicaciones, mientras que todas las demás quedan dentro de un radio de ~285 m.
No es un error: es un punto singular fuera de las calles de casetas. Se mantiene.

## Índice de búsqueda

Para cumplir RF-5 (insensible a mayúsculas y tildes) el filtrado no se hace sobre `name`
directamente, sino sobre un campo `search` precalculado:

1. Concatenar `name` y `label`.
2. Pasar a minúsculas.
3. Descomponer en Unicode NFD y eliminar los diacríticos combinantes.
4. Normalizar comillas tipográficas (`’` → `'`) y espacios múltiples.

Ejemplo: `Casa de Álora-Cosa Nuestra` + `58-59-60` → `casa de alora-cosa nuestra 58-59-60`.

El término tecleado por el usuario se normaliza igual antes de comparar.

### Reglas de coincidencia

El comportamiento depende de si el término tecleado es **solo dígitos** o no. Los dos
modos son excluyentes: nunca se mezclan.

**Término numérico** (`7`, `192`, `66`):

1. Número **exacto** presente en `numbers`.
2. Número de `numbers` que **empieza por** el término: `7` → `70`, `71`, `73`…
   Necesario para que la lista se estreche de forma natural mientras se teclea.
3. `nameSearch` que **contiene** el término, para nombres que llevan cifras
   (`Calle Larios 15`, `La Noria 211`, `Puerto 10 La Favela`).

Queda **prohibida la coincidencia por subcadena sobre el número**: escribir `39` no puede
devolver la caseta `139`, ni `7` la `17`. Enviar a la unidad a una caseta equivocada es el
único fallo grave que esta aplicación puede cometer, y una subcadena lo provoca en
silencio. Los huecos de numeración (39-42, 81-84, 212) deben devolver lista vacía, que es
información útil: esa caseta no existe.

**Término de texto** (`pimpi`, `alora`):

1. `search` que **empieza por** el término.
2. `search` que **contiene** el término.

### Orden de los resultados

Coincidencia exacta → prefijo → contiene. Dentro de cada grupo se conserva el orden
original de `data.md`.

## Formato de las coordenadas

- Se conservan los 6 decimales del origen (precisión de ~0,1 m, más que suficiente).
- Se pasan a Google Maps como `lat,lon` separados por coma, sin espacios y con punto
  decimal, en el orden latitud primero.
- Nunca se redondean ni se reformatean por localización: el separador decimal es siempre
  el punto, aunque la interfaz esté en español.

## Proceso de conversión

`data.md` → datos de aplicación mediante un script reproducible que:

1. Lee `data.md` y descarta cabecera y separador.
2. Valida que cada fila tiene exactamente 4 columnas.
3. Valida que `coords` cumple `^-?\d+\.\d+,-?\d+\.\d+$` y cae dentro de la envolvente
   documentada, con un margen razonable.
4. Aplica las normalizaciones descritas arriba.
5. Falla de forma ruidosa ante cualquier fila inválida. No omite filas en silencio.
6. Emite un recuento final que debe coincidir con 125.

La ejecución del script forma parte del proceso de compilación, para que un cambio en
`data.md` nunca quede sin reflejarse en la aplicación desplegada.

## Actualización anual

Las casetas cambian cada Feria. El procedimiento previsto es sustituir `data.md` por el
listado del año correspondiente y volver a compilar. Por eso la conversión debe ser un
script y no una transformación manual.
