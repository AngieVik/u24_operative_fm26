# U24 · Buscador de ubicaciones

Instrucciones permanentes del proyecto. Este archivo tiene prioridad sobre cualquier
suposición por defecto. Si algo aquí contradice a un documento de `docs/`, avisa antes
de continuar.

## Qué es esto

Buscador de respuesta rápida para el **operativo de emergencias sanitarias U24**. Un
sanitario recibe un aviso con el nombre o el número de una ubicación, lo teclea, pulsa la
fila correspondiente y el móvil abre la **ficha de lugar de Google Maps** centrada en las
coordenadas exactas de ese punto.

Desde esa ficha, quien conoce la zona se ubica de un vistazo y sale; quien no la conoce
pulsa «Cómo llegar» e «Iniciar» dentro de Maps. Las dos salidas son legítimas y la app no
decide por el usuario cuál necesita.

Elimina el tiempo perdido buscando ubicaciones a mano. No hace nada más.

## Principios de diseño — no negociables

1. **Una sola función.** Buscar una ubicación y abrirla en el mapa. Cualquier propuesta de
   añadir menús, mapas propios, cuentas de usuario o pantallas intermedias **dentro de la
   app** se rechaza salvo petición expresa del responsable del proyecto. La ficha de
   Google Maps no es una pantalla de la app: es el destino.
2. **Instantáneo.** El filtrado ocurre al teclear, sin botón de buscar, sin esperas de red
   y sin spinners. Objetivo: de abrir la app a ver la ubicación en el mapa en menos de
   5 segundos.
3. **Se usa con prisa, de noche y con guantes.** Legibilidad y acierto al pulsar por
   encima de cualquier otra consideración estética. Cómo se consigue eso es una decisión
   de diseño abierta: este documento no congela tamaños, colores ni densidades.
4. **Precisión total.** Las coordenadas se toman siempre del listado cerrado y verificado.
   Nunca se resuelve una ubicación mediante búsqueda de texto en Google Maps.
5. **Nunca al sitio equivocado.** Ante la duda, la app muestra menos resultados, no
   resultados aproximados disfrazados de exactos. La búsqueda tolerante a erratas nunca
   se aplica a números y siempre va rotulada como aproximada.
6. **Cero fricción de instalación.** Es una web. Se abre por URL y se puede añadir a la
   pantalla de inicio del móvil. No hay tiendas de aplicaciones.

## Libertad de diseño

La interfaz puede rediseñarse sin pedir permiso mientras respete los principios 2, 3 y 5.
No hay parámetros visuales protegidos: ni altura de fila, ni escala tipográfica, ni paleta,
ni densidad.

Con una excepción: **al mapa solo se llega por el botón de la derecha**. La fila no es un
enlace, y convertirla en uno exige acuerdo expreso del responsable. Con 125 elementos en
lista, una fila-enlace se activa sola al desplazar con el dedo.

Las coordenadas sí son pulsables —copian al portapapeles— porque copiar no navega ni tiene
consecuencias. Cualquier otro elemento pulsable se decide igual: se admite si no puede
llevar a nadie a otro sitio, y solo con acuerdo expreso. Y si obliga a un relleno táctil,
se compensa con márgenes negativos: el ritmo vertical de la fila no se toca.

Se mantiene además la obligación de justificar en `docs/04-convenciones.md` cualquier
decisión que afecte a la probabilidad de abrir la ubicación equivocada, y de comprobarla en
dispositivo real.

## Documentos canónicos

Léelos antes de tocar nada relacionado con su ámbito.

| Documento | Contenido |
| --- | --- |
| `data.md` | **Fuente de verdad de las ubicaciones.** No se edita sin autorización expresa. |
| `calles.md` | **Fuente de verdad de las calles** (extremos, para trazar su recorrido). Mismas reglas que `data.md`. Opcional: sin él la app funciona sin trazados. |
| `docs/00-contexto.md` | Objetivo, usuarios, escenario de uso, criterios de éxito. |
| `docs/01-requisitos.md` | Requisitos funcionales, no funcionales y fuera de alcance. |
| `docs/02-datos.md` | Modelo de datos, normalización de `data.md` y reglas de coincidencia. |
| `docs/03-navegacion-maps.md` | Construcción de los enlaces a Google Maps. |
| `docs/04-convenciones.md` | Convenciones de código, estructura, interfaz y pruebas. |
| `docs/05-cambiar-de-operativo.md` | Qué tocar para publicar la app con otro listado. |
| `descripcion.md` | Brief original del responsable. **Documento histórico.** |

Sobre `descripcion.md`: describe la aplicación tal como se concibió, cuando el enlace
lanzaba la navegación paso a paso. Sigue siendo útil para entender la intención, pero
donde contradiga a `docs/` prevalece la decisión fechada más reciente. No se reescribe:
es el registro de lo que se pidió, no de lo que hoy hace la aplicación.

## Reglas de trabajo

- Trabaja en **español de España**. Los identificadores de código en inglés; los textos
  de interfaz y la documentación en español.
- `data.md` es de solo lectura. Cualquier corrección sobre los datos originales se
  documenta como regla de transformación en `docs/02-datos.md`, no modificando el origen.
- No inventes coordenadas, nombres ni identificadores. Si un dato falta o es
  contradictorio, señálalo; no lo rellenes.
- No amplíes el alcance por iniciativa propia. Las ideas fuera de alcance van a la
  sección correspondiente de `docs/01-requisitos.md`, no al código.
- **Propón antes de añadir.** Toda función, elemento o comportamiento nuevo se plantea
  primero y se implementa después de que el responsable lo apruebe. Las propuestas son
  bienvenidas —cuantas más y mejor razonadas, mejor—, pero se proponen, no se dan por
  hechas. Esto no afecta a corregir lo que está mal ni a terminar lo ya encargado.
- Antes de dar por terminada una tarea, verifica el resultado. No afirmes que algo
  funciona si no lo has comprobado.

## Estado

- **Fase actual:** en uso. Ficha de lugar y búsqueda tolerante a erratas implementadas el
  19/08/2026 tras las primeras pruebas de campo. El 20/08/2026 se añadieron las
  coordenadas a la vista, el rótulo del operativo y el límite de espera del service
  worker, la lista perdió las líneas de separación y se añadió el trazado de calles.
- **Pendiente de campo:** comprobar en un móvil real que el trazado de una calle dibuja la
  calle y no un rodeo por fuera del recinto, y en qué modo de transporte queda «Cómo
  llegar» al pulsarlo desde una ficha de lugar.
- **Stack:** sitio estático generado por `scripts/build.py`. Un único `index.html`
  autocontenido: datos, motor de búsqueda, tipografía y emblema empotrados. Sin
  framework, sin paso de compilación de JavaScript, sin peticiones de red en el arranque.
- **Única dependencia de terceros:** Fuse.js, empotrada desde `src/vendor/`.
