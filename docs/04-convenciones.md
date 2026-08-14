# 04 — Convenciones

Aplicables con independencia del stack que se elija en el plan de implementación. Las
secciones marcadas *(a concretar)* se completarán cuando la decisión esté tomada.

## Idioma

- **Documentación y textos de interfaz:** español de España.
- **Código:** identificadores, nombres de archivo, ramas y mensajes de commit en inglés.
- **Comentarios:** español, y solo cuando expliquen el *porqué*. Nada de comentarios que
  repitan lo que el código ya dice.

## Estructura de carpetas

```
u24_operative_fm26/
├── CLAUDE.md              Instrucciones permanentes
├── data.md                Fuente de verdad. Solo lectura.
├── docs/                  Documentación del proyecto
│   ├── 00-contexto.md
│   ├── 01-requisitos.md
│   ├── 02-datos.md
│   ├── 03-navegacion-maps.md
│   └── 04-convenciones.md
├── scripts/               Conversión de data.md a datos de aplicación
└── src/                   Código de la aplicación (a concretar)
```

Nombres de archivo y carpeta en `kebab-case`. Los documentos de `docs/` llevan prefijo
numérico de dos dígitos para fijar el orden de lectura.

## Nomenclatura en código

| Elemento | Convención | Ejemplo |
| --- | --- | --- |
| Variables y funciones | `camelCase` | `normalizeSearchTerm` |
| Constantes de módulo | `SCREAMING_SNAKE_CASE` | `MAPS_DIR_BASE_URL` |
| Componentes / clases | `PascalCase` | `LocationCard` |
| Archivos de código | `kebab-case` | `location-card` |
| Campos de datos | `snake_case` no; usar `camelCase` | `lat`, `lon`, `numbers` |

Vocabulario del dominio, de uso obligatorio para evitar sinónimos dispersos:

| Concepto | Término en código |
| --- | --- |
| Ubicación del listado | `location` |
| Etiqueta visible del número | `label` |
| Números expandidos | `numbers` |
| Cadena normalizada de búsqueda | `search` |
| Término tecleado por el usuario | `query` |

## Estilo de código

- Formateo automático. Nadie discute sobre comas ni sangrías en revisión.
- Sangría de 2 espacios, comillas simples, punto y coma al final de sentencia.
- Módulos pequeños, con una responsabilidad clara. Si un archivo pasa de ~200 líneas,
  probablemente esté haciendo dos cosas.
- Sin abstracciones anticipadas. Este proyecto es pequeño a propósito: se escribe la
  solución directa y se refactoriza solo cuando el código lo pida por duplicado real.
- Nada de dependencias para lo que la plataforma ya resuelve (normalización Unicode,
  filtrado de arrays, enlaces).

## Interfaz

- **Mobile-first en vertical.** Se diseña para 360 px de ancho y se deja crecer.
- **Contraste mínimo 7:1** en el texto principal (RNF-4). Se verifica con una herramienta,
  no a ojo.
- **Altura de fila 42 px**, contigua y a todo el ancho, sin zonas muertas entre objetivos.
  Es una excepción consciente al mínimo de 48 px: ver la nota sobre RNF-4 en
  `docs/01-requisitos.md`.
- **Tipografía grande.** El nombre de la caseta es el elemento más prominente de la
  tarjeta; el número, secundario pero legible de un vistazo; la calle, terciario.
- **Sin animaciones de transición** que retrasen la respuesta. El filtrado es instantáneo
  y debe *parecerlo*.
- **Sin iconografía ambigua.** Si algo necesita un icono explicativo, es que sobra.
- El campo de búsqueda usa `inputmode` adecuado y no activa autocorrección ni
  autocapitalización, que estorban al teclear nombres propios y números.

## Accesibilidad

- HTML semántico: el listado es una lista, las tarjetas son enlaces.
- Cada enlace tiene un nombre accesible que identifica la ubicación completa, no un
  genérico «navegar».
- El resultado del filtrado se anuncia a lectores de pantalla mediante una región activa.
- Navegable por teclado de principio a fin, aunque el uso previsto sea táctil.
- Respetar `prefers-reduced-motion`.

## Rendimiento

- Sin peticiones de red en el arranque más allá de los propios archivos de la aplicación.
- Los datos de ubicaciones se empaquetan en el bundle (125 registros: irrelevante en peso).
- Presupuesto orientativo: menos de 150 KB transferidos en la carga inicial, sin comprimir
  las imágenes de icono.
- Sin fuentes web externas. Se usa la pila tipográfica del sistema.

## Control de versiones

- Rama principal: `main`. Se trabaja con ramas cortas y se integra rápido.
- Mensajes de commit en inglés, imperativo, con prefijo de tipo:
  `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`.
- Un commit, un cambio con sentido propio. No se mezclan formateo y lógica.
- `data.md` solo cambia en commits `chore(data):` dedicados, nunca junto a código.

## Pruebas

Cobertura deliberadamente selectiva: se prueba lo que puede fallar en silencio y hacer
que la unidad vaya a la dirección equivocada.

Obligatorio:

- Conversión de `data.md`: recuento de 125, validación de coordenadas, expansión de
  rangos, corrección de la errata de calle.
- Normalización de búsqueda: tildes, mayúsculas, comillas tipográficas.
- Reglas de coincidencia: `7` no devuelve la 74 por delante de la 7; `67` encuentra
  `66-67-68`.
- Construcción de la URL de Maps: coordenadas con signo negativo y coma sin codificar.

No obligatorio: pruebas de interfaz automatizadas. La validación de interfaz es manual,
sobre dispositivo real, siguiendo la lista de `docs/03-navegacion-maps.md`.

## Definición de terminado

Una tarea no está terminada hasta que:

1. Cumple los requisitos `M` que le corresponden de `docs/01-requisitos.md`.
2. Pasa las pruebas obligatorias.
3. Se ha comprobado en un móvil real, no solo en el navegador de escritorio.
4. No ha ampliado el alcance ni ha añadido dependencias sin justificar.
