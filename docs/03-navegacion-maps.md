# 03 — Enlace a Google Maps

Cómo se construye el enlace que abre la ubicación en el móvil. Basado en **Maps URLs**, la
API de URLs públicas de Google Maps: no requiere clave de API, no tiene cuota y la misma
URL funciona en Android, iOS y navegador de escritorio.

Referencia oficial: <https://developers.google.com/maps/documentation/urls/get-started>

## URL de ficha de lugar

Formato único para todas las plataformas:

```
https://www.google.com/maps/search/?api=1&query={LAT},{LON}
```

Ejemplo real, El Sarao (66-67-68):

```
https://www.google.com/maps/search/?api=1&query=36.704300,-4.462917
```

### Parámetros

| Parámetro | Valor | Por qué |
| --- | --- | --- |
| `api` | `1` | Obligatorio. Identifica la versión de Maps URLs. Sin él la URL no es estable. |
| `query` | `{LAT},{LON}` | Coordenadas exactas de `data.md`. **Nunca el nombre de la ubicación:** el listado cerrado es la fuente de precisión (RNF-8, principio 4 de `CLAUDE.md`). |

No se añade nada más. En concreto **no se usa `query_place_id`**, que haría falta para que
la ficha mostrara un nombre propio: exigiría resolver cada ubicación contra la base de
datos de lugares de Google, que es precisamente lo que el principio 4 prohíbe.

### Codificación

- La coma entre latitud y longitud **no debe codificarse** como `%2C`: se envía literal.
- El signo menos de la longitud se envía literal.
- No se añaden espacios ni separadores de miles.

## Qué se ve al abrirlo

Un mapa centrado en el punto, con el marcador sobre las coordenadas exactas y la tarjeta
inferior de Google Maps, desde la que se accede a «Cómo llegar» e «Iniciar».

Dos avisos que conviene tener presentes y que **hay que confirmar en dispositivo real**:

1. **La tarjeta no muestra el nombre de la ubicación.** Al abrirse por coordenadas, Google
   rotula el punto con la dirección inversa o con las propias coordenadas, y puede
   asociarlo a un lugar cercano que no es el nuestro. El nombre lo aporta esta aplicación
   antes de salir; el mapa solo tiene que llevar al punto correcto.
2. **Se pierde el modo de transporte.** La URL ya no lleva `travelmode=driving`, así que
   al pulsar «Cómo llegar» Google Maps usará el último modo empleado en ese móvil, que
   puede no ser el coche. Es la contrapartida asumida de la decisión del 19/08/2026
   (ver `docs/01-requisitos.md`).

## Comportamiento por plataforma

| Plataforma | Resultado esperado |
| --- | --- |
| Android con Google Maps instalado | Se abre la app nativa con el marcador sobre el punto. |
| Android sin Google Maps | Se abre Maps en el navegador con el marcador sobre el punto. |
| iOS con Google Maps instalado | Se abre la app nativa de Google Maps sobre el punto. |
| iOS sin Google Maps | Se abre Maps en Safari. Google puede ofrecer instalar la app. |
| Escritorio | Se abre Google Maps web centrado en el punto. |

La misma URL cubre los cinco casos. **No se implementa detección de sistema operativo ni
esquemas propietarios** (`comgooglemaps://`, `maps://`, `geo:`): añaden complejidad,
degradan cuando la app no está instalada y contradicen el principio de simplicidad.

Se valoró y se descartó `geo:{LAT},{LON}?q={LAT},{LON}(Nombre)`, que sí mostraría el
nombre de la ubicación sobre el marcador: solo funciona en Android y obligaría a mantener
dos caminos distintos según el sistema.

## Trazado de una calle

Datos de entrada en `calles.md`, descrito en `docs/02-datos.md`.

Maps URLs **no permite dibujar nada**: no hay parámetro para líneas, trazados ni
polilíneas, y los únicos admitidos son `query` para buscar y
`origin` / `destination` / `waypoints` / `travelmode` / `avoid` para indicaciones.
Comprobado en la documentación oficial el 20/08/2026.

El recorrido de una calle se consigue, por tanto, pidiendo una ruta entre sus dos extremos:
el camino que Google dibuja **es** la calle.

```
https://www.google.com/maps/dir/?api=1&origin={LAT1},{LON1}&destination={LAT2},{LON2}&travelmode=walking
```

Con puntos intermedios, cuando hagan falta:

```
&waypoints={LAT},{LON}|{LAT},{LON}
```

| Parámetro | Valor | Por qué |
| --- | --- | --- |
| `travelmode` | `walking` | **A pie, no en coche.** El Real es peatonal: en coche Google daría un rodeo por el exterior del recinto, o no encontraría ruta. A pie el trazado sigue la calle y no respeta sentidos únicos. |
| `waypoints` | Opcional | Fuerza el trazado por donde debe ir si Google elige otro camino entre los extremos. Se separan con `|`. |
| `dir_action` | **No se usa** | Lanzaría la navegación paso a paso. Aquí solo se quiere ver el trazado. |

Diferencias con el enlace de una ubicación, que conviene tener presentes:

- Abre la **pantalla de indicaciones**, no la ficha de lugar. Es otro sitio de Google Maps y
  se ve distinto.
- Es un recorrido entre dos puntos, no un resaltado de la calle: si la calle continúa más
  allá de los extremos que se den, esa parte no se dibuja.
- Depende de que Google conozca el vial. Ver el aviso en `docs/02-datos.md`.

En la aplicación, una calle aparece **escribiendo su nombre** en el buscador —`peñista`,
`maño`, `rodríguez`—, como primera fila y con el nombre en color de acento. No aparece con
el campo vacío ni en las consultas numéricas. Hacen falta 3 caracteres, igual que para la
coincidencia aproximada.

Esto aprovecha algo que antes no devolvía nada: el índice de las ubicaciones **no** incluye
su calle, a propósito, porque buscar `peñista` habría devuelto 44 resultados inútiles.

## Variante anterior — navegación directa

Hasta el 19/08/2026 el enlace era:

```
https://www.google.com/maps/dir/?api=1&destination={LAT},{LON}&travelmode=driving&dir_action=navigate
```

Lanzaba la navegación paso a paso en cuanto se pulsaba. Se retiró porque el equipo, que
conoce la zona, tenía que **cancelar el navegador** para ver la ficha del sitio, lo que
costaba más tiempo del que ahorraba. El motivo completo está en `docs/00-contexto.md` y la
decisión, con sus consecuencias, en `docs/01-requisitos.md`.

Queda documentada aquí para no tener que volver a investigarla si algún día se decide
recuperarla o hacerla configurable.

## Apertura desde la aplicación

- Enlace HTML real (`<a href="…">`), no un manejador de clic con `window.open()`. Un
  enlace nativo se comporta mejor en las capas de aplicación web instalada de iOS y
  Android, y permite pulsación larga para copiar o abrir en otra app.
- `target="_blank"` con `rel="noopener noreferrer"`: la app queda abierta detrás, lista
  para el siguiente aviso, sin volver a cargar.
- **Solo el botón de la derecha es el enlace. La fila no lo es** (RF-8). Con una lista de
  125 elementos, una fila-enlace se activa sola al desplazar con el dedo y abre una
  ubicación equivocada. El botón mide 64 px de ancho por toda la altura de la fila,
  bastante más que la pastilla visible.

## Verificación antes de desplegar

Comprobaciones obligatorias, sobre dispositivo real, no solo en emulador:

1. Abrir tres ubicaciones distintas en un Android con Google Maps instalado y confirmar
   que aparece la ficha de lugar con el marcador sobre el punto correcto.
2. Repetir en un iPhone, con y sin la app de Google Maps instalada.
3. Comprobar que el marcador cae sobre la ubicación correcta contrastando con `data.md`,
   no de memoria.
4. Comprobar el caso de longitud negativa: todas las del proyecto lo son, así que un
   fallo de codificación se manifestaría en todas a la vez.
5. Desde la ficha, pulsar «Cómo llegar» y comprobar en qué modo de transporte queda la
   ruta. Si aparece a pie de forma habitual, reabrir la decisión de RF-8.

Estas comprobaciones no se dan por superadas si no se han ejecutado.

---

Fuentes: [Get Started | Maps URLs | Google for Developers](https://developers.google.com/maps/documentation/urls/get-started)
