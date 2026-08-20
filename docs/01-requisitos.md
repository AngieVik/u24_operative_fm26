# 01 — Requisitos

Identificadores: `RF-n` funcional, `RNF-n` no funcional. Prioridad **M** (obligatorio) /
**D** (deseable, solo si no compromete la simplicidad).

## Requisitos funcionales

| ID | Prioridad | Requisito |
| --- | --- | --- |
| RF-1 | M | Pantalla única: campo de búsqueda arriba y lista de resultados debajo. Sin menús, sin navegación entre pantallas. |
| RF-2 | M | El campo de búsqueda recibe el foco al abrir la app. **El teclado no se abre solo:** ningún navegador móvil lo permite sin un gesto del usuario, ni Android ni iOS. Hace falta un toque sobre el campo. Comprobado en Android el 14/08/2026; en iOS el comportamiento es el mismo por diseño de la plataforma. Por eso el icono de lupa es permanente: es la señal de que ahí se escribe. |
| RF-3 | M | El filtrado es instantáneo a cada pulsación, sin botón de buscar y sin peticiones de red. |
| RF-4 | M | La búsqueda cubre **nombre**, **identificador** y **calle** en la misma caja. Escribir `97` encuentra la ubicación 97; `pimpi` encuentra El Pimpi; `peñista` encuentra la calle y sus ubicaciones. |
| RF-17 | M | **La puntuación no puede dejar la pantalla vacía.** `C/Peñ` sin espacio encuentra `C/ Peñista Rafael Fuentes`, y `66 67` encuentra `66-67-68`. Ver «Búsqueda sin espacios» en `docs/02-datos.md`. |
| RF-5 | M | La búsqueda es insensible a mayúsculas, tildes y diéresis: `malamia` encuentra `Malamía`, `alora` encuentra `Casa de Álora`. |
| RF-6 | M | La búsqueda por número acierta dentro de rangos: escribir `67` encuentra `66-67-68`. |
| RF-7 | M | Cada resultado muestra el identificador, el nombre y la calle. |
| RF-8 | M | Cada fila lleva a la derecha un **botón de ubicación**, y es el único elemento pulsable de la fila. Al pulsarlo se abre **la ficha de lugar de Google Maps** centrada en las coordenadas exactas de esa ubicación, según `docs/03-navegacion-maps.md`. No se lanza la navegación paso a paso: la inicia el usuario desde la propia ficha si la necesita. El resto de la fila no reacciona: evita que un desplazamiento con el dedo abra una ubicación equivocada. |
| RF-9 | M | Con el campo vacío se muestra el listado completo, recorrible por desplazamiento. |
| RF-10 | M | Si ningún resultado coincide, se indica con un mensaje claro y breve. |
| RF-11 | M | Existe una forma evidente de borrar la búsqueda de un toque y volver al listado completo. |
| RF-13 | M | **Tolerancia a erratas en el nombre.** Cuando la búsqueda literal no devuelve nada, la app ofrece las ubicaciones cuyo nombre más se parece a lo tecleado (`pinpi` → El Pimpi, `montecalro` → Monteclaro). Estas coincidencias van **separadas y rotuladas** como aproximadas, nunca mezcladas con las literales. |
| RF-14 | M | **La tolerancia a erratas no se aplica nunca a los números.** Una consulta de solo dígitos se resuelve exclusivamente con las reglas exactas de `docs/02-datos.md`. Un número que no existe devuelve lista vacía. |
| RF-12 | M | **Las coordenadas de cada ubicación están a la vista en su fila**, legibles y dictables por radio, y **se copian al portapapeles al tocar el texto**, con confirmación visible y sin icono. Es el plan B cuando Google Maps no carga. |
| RF-15 | M | Bajo el buscador se muestra el **operativo en curso** («Feria de Málaga 2026»). |
| RF-16 | M | **Trazar el recorrido de una calle** sobre el mapa, a partir de sus dos extremos. Aparece escribiendo el nombre de la calle, como primera fila. Datos en `calles.md` (`docs/02-datos.md`), enlace en `docs/03-navegacion-maps.md`. **Falta comprobar en un móvil real que Google dibuja la calle y no un rodeo por fuera del recinto.** |

## Requisitos no funcionales

| ID | Prioridad | Requisito |
| --- | --- | --- |
| RNF-1 | M | **Funciona sin cobertura.** Los datos y el motor de búsqueda viajan con la aplicación; buscar no requiere red. Google Maps sí la necesita, y por eso las coordenadas están a la vista (RF-12): sin red, la app sigue dando la información que permite llegar. |
| RNF-12 | M | **Abrir la app nunca depende de que la red conteste.** El escenario real no es «sin red» sino «red saturada», donde una petición no falla: se queda esperando. El service worker sirve la copia guardada si la red no responde en 1,5 s, y la actualiza en segundo plano. |
| RNF-2 | M | **Instalable** en la pantalla de inicio de Android e iOS como acceso directo, sin pasar por tiendas de aplicaciones. |
| RNF-3 | M | **Mobile-first.** Diseñada para móvil en vertical; debe seguir siendo usable en tablet y escritorio, sin optimizar para ellos. |
| RNF-4 | M | **Legible y acertable en condiciones adversas:** de noche, en marcha, con guantes y a una mano. Los medios concretos son decisión de diseño; el resultado se comprueba en dispositivo real. |
| RNF-5 | M | Arranque en frío inferior a 1 segundo en un móvil de gama media con la app instalada. |
| RNF-6 | M | El filtrado no produce retraso perceptible al teclear con el listado completo cargado, incluida la coincidencia aproximada. |
| RNF-7 | M | Sin cuentas de usuario, sin registro, sin seguimiento analítico, sin cookies. |
| RNF-8 | M | Sin claves de API de Google Maps: se usan exclusivamente Maps URLs públicas. |
| RNF-9 | M | Los enlaces funcionan igual en Android, iOS y navegador de escritorio con una sola URL. |
| RNF-10 | M | Dependencias mínimas y empotradas. Cada dependencia debe justificarse y quedar fijada a una versión concreta dentro del repositorio. |
| RNF-11 | M | Tema oscuro: el uso es mayoritariamente nocturno y prolongado. |

### Nota sobre RNF-10 — Fuse.js

La coincidencia aproximada de RF-13 se implementa con **Fuse.js 7.5.0**, variante
`fuse.basic.min`, copiada a `src/vendor/` y empotrada en `index.html` durante el build.

Justificación de la excepción a «dependencias mínimas»:

- Es la única dependencia de terceros del proyecto.
- Ocupa ~19 KB sin comprimir sobre un `index.html` de ~112 KB, dentro del presupuesto.
- No hace peticiones de red ni tiene dependencias propias, así que no compromete RNF-1.
- Está fijada a una versión en el repositorio: no se descarga en el build ni puede cambiar
  sola. Actualizarla es un acto deliberado que exige volver a pasar las pruebas.

Se descartó escribir un algoritmo propio de distancia de edición: era viable, pero Fuse
resuelve además el troceado por palabras y el orden por parecido, que es justo lo que hace
utilizable la lista de aproximadas.

### Nota sobre RF-8 — decisión del 19/08/2026

Hasta esa fecha el enlace abría la navegación paso a paso
(`dir_action=navigate`). Las pruebas de campo mostraron un problema no previsto: **buena
parte del equipo conoce la zona y solo necesita ver el punto**. Para esos usuarios la
navegación era un estorbo que había que cancelar para llegar a la ficha del sitio, con la
consecuencia de que algunos preferían abrir otras aplicaciones, más lentas e imprecisas.

El responsable del proyecto decidió que el destino del enlace pasa a ser la ficha de
lugar. Consecuencias asumidas:

- Quien sí necesita navegación da **dos toques más** dentro de Google Maps.
- Se pierde `travelmode=driving`: al pulsar «Cómo llegar», Maps usará el último modo de
  transporte empleado en ese móvil, que puede no ser el coche. **Verificar en campo** si
  esto llega a producirse en la práctica y, en tal caso, volver a plantear la decisión.
- La ficha no muestra el nombre de la ubicación, porque se abre por coordenadas y no por
  un lugar registrado en Google. El nombre lo aporta la app antes de salir. Nunca se
  resolverá la ubicación por texto para conseguir ese rótulo: ver principio 4 de
  `CLAUDE.md`.

### Nota sobre RF-12, RF-15 y RNF-12 — decisiones del 20/08/2026

Las tres salen del mismo análisis: la aplicación cumplía sus requisitos y aun así podía
dejar tirado al equipo, porque lo que fallaba estaba justo fuera de su frontera.

- **Coordenadas a la vista.** `RNF-1` garantizaba buscar sin cobertura, pero el resultado
  útil lo servía Google Maps. Sin red, el botón llevaba a un mapa en blanco y no quedaba
  nada. Con las coordenadas en pantalla siempre se puede dictar la posición por radio. Por
  eso RF-12 pasa de deseable a obligatorio.

  Copiarlas al tocarlas entró, salió y volvió a entrar el mismo día. Lo que sobraba era el
  **icono** de copiar, no la función: descuadraba el ritmo vertical de la fila y añadía
  ruido. La versión que queda copia al tocar el texto, sin icono, y compensa el relleno
  táctil con márgenes negativos para que la caja ocupe en el flujo exactamente lo mismo que
  una línea de texto normal.

  Las coordenadas son, por tanto, el **segundo elemento pulsable de la fila**. Se admite
  porque copiar **no tiene consecuencias**: no navega, no abre nada y no puede mandar a
  nadie a otro sitio. Lo que sigue prohibido es que se llegue al mapa desde cualquier punto
  de la fila que no sea su botón.
- **Límite de espera en el service worker.** La estrategia era «red primero» sin plazo:
  con la red caída funcionaba, pero con la red *saturada* la petición no fallaba, se
  quedaba esperando el tiempo que decidiera el navegador. La app que debía abrirse en
  menos de un segundo tardaba justo en las condiciones para las que se diseñó. Ahora la
  red tiene 1,5 s para contestar; pasado ese plazo se sirve la copia guardada y la
  descarga continúa en segundo plano. La red sigue teniendo preferencia mientras responda
  a tiempo, para que una corrección de coordenadas llegue en la misma apertura.
  Comprobado el 20/08/2026 contra un servidor que tarda 6 s: la app abre en ~1,5 s en vez
  de en 6, y con red normal responde en milisegundos.
- **Operativo bajo el buscador.** Sustituye al rótulo genérico anterior («Servicios
  Sanitarios»), que no decía nada que el emblema no dijera ya. Va en caja de título, tal
  cual: «Feria de Málaga 2026».

  Se probó a acompañarlo de la fecha de publicación, para poder comprobar en campo si un
  móvil se había quedado con un listado anterior. El responsable la retiró el 20/08/2026
  por no cargar el rótulo. **Queda pendiente**, por tanto, una forma de saber desde el
  dispositivo qué listado lleva: hoy la fecha y la huella de `data.md` solo aparecen en la
  salida de `scripts/build.py`, que no ve nadie en la calle.

### Nota sobre RNF-4 — objetivos táctiles

El requisito original fijaba 48 px de alto de fila, mínimo recomendado por WCAG 2.1
(criterio 2.5.5). Entre el 14/08/2026 y el 19/08/2026 estuvo en 42 px por densidad.

Desde el 19/08/2026 la altura concreta deja de estar congelada y pasa a ser una decisión
de diseño: la implementación actual usa 60 px, que caben en pantalla sin apretar y dan un
objetivo cómodo con guantes.

Lo que **no** cambia es la regla que lo acompañaba desde el principio: **la fila no es
pulsable, solo lo es el botón de la derecha**. Con una lista de 125 elementos, una
fila-enlace se activa sola al desplazar con el dedo. El botón mide 64 px de ancho por toda
la altura de la fila, bastante más que la pastilla visible.

Tampoco se levanta la obligación de comprobarlo en vehículo y con guantes antes de darlo
por bueno, ni la de dejar registrada cualquier decisión que afecte a la probabilidad de
abrir la ubicación equivocada.

## Fuera de alcance

Registrado explícitamente para que no reaparezca como propuesta durante la implementación:

- Mapa interactivo dentro de la aplicación.
- Registro de avisos, incidencias, tiempos de respuesta o partes de asistencia.
- Cuadrantes, turnos o gestión de personal.
- Cuentas, autenticación o roles.
- Edición de ubicaciones desde la interfaz.
- Backend, base de datos o sincronización entre dispositivos.
- Geolocalización propia de la unidad dentro de la app (la aporta Google Maps).
- Notificaciones push.
- Analítica de uso.

## Restricciones técnicas

- Se sirve como sitio estático, sin servidor de aplicación.
- Los datos de ubicaciones se empaquetan con la aplicación, no se piden en tiempo de
  ejecución.
- Sin claves de API ni secretos de ningún tipo en el cliente.
- Instalable como aplicación web progresiva (manifiesto + service worker).
- Superficie de código pequeña y legible: este proyecto se revisa una vez al año.
