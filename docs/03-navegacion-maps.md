# 03 — Navegación con Google Maps

Cómo se construye el enlace que abre el GPS. Basado en **Maps URLs**, la API de URLs
públicas de Google Maps: no requiere clave de API, no tiene cuota y la misma URL funciona
en Android, iOS y navegador de escritorio.

Referencia oficial: <https://developers.google.com/maps/documentation/urls/get-started>

## URL de navegación

Formato único para todas las plataformas:

```
https://www.google.com/maps/dir/?api=1&destination={LAT},{LON}&travelmode=driving&dir_action=navigate
```

Ejemplo real, El Sarao (casetas 66-67-68):

```
https://www.google.com/maps/dir/?api=1&destination=36.704300,-4.462917&travelmode=driving&dir_action=navigate
```

### Parámetros

| Parámetro | Valor | Por qué |
| --- | --- | --- |
| `api` | `1` | Obligatorio. Identifica la versión de Maps URLs. Sin él la URL no es estable. |
| `destination` | `{lat},{lon}` | Coordenadas exactas de `data.md`. **Nunca el nombre de la caseta:** el listado cerrado es la fuente de precisión (RNF-8, principio 4 de `CLAUDE.md`). |
| `travelmode` | `driving` | La unidad se desplaza en vehículo. Sin este parámetro Google elige el modo por su cuenta. |
| `dir_action` | `navigate` | Lanza la navegación paso a paso directamente si el dispositivo tiene ubicación disponible. Si no la tiene, muestra la vista previa de la ruta. |

`origin` se omite deliberadamente: al no indicarlo, Google Maps usa la ubicación actual
del dispositivo, que es exactamente el comportamiento que se busca.

### Codificación

- La coma entre latitud y longitud **no debe codificarse** como `%2C`: se envía literal.
- El signo menos de la longitud se envía literal.
- No se añaden espacios ni separadores de miles.

## Comportamiento por plataforma

| Plataforma | Resultado esperado |
| --- | --- |
| Android con Google Maps instalado | Se abre la app nativa en navegación por voz. |
| Android sin Google Maps | Se abre Maps en el navegador con la ruta calculada. |
| iOS con Google Maps instalado | Se abre la app nativa de Google Maps en navegación. |
| iOS sin Google Maps | Se abre Maps en Safari con la ruta. Google puede ofrecer instalar la app. |
| Escritorio | Se abre Google Maps web con la ruta. Sin ubicación de origen, pedirá permiso o mostrará vista previa. |

La misma URL cubre los cinco casos. **No se implementa detección de sistema operativo ni
esquemas propietarios** (`comgooglemaps://`, `maps://`, `geo:`): añaden complejidad,
degradan cuando la app no está instalada y contradicen el principio de simplicidad.

## Apertura desde la aplicación

- Enlace HTML real (`<a href="…">`), no un manejador de clic con `window.open()`. Un
  enlace nativo se comporta mejor en las capas de aplicación web instalada de iOS y
  Android, y permite pulsación larga para copiar o abrir en otra app.
- `target="_blank"` con `rel="noopener noreferrer"`: la app queda abierta detrás, lista
  para el siguiente aviso, sin volver a cargar.
- **Solo el botón de la derecha es el enlace. La fila no lo es** (RF-8). Con filas de
  42 px y una lista de 125 elementos, una fila-enlace se activa sola al desplazar con el
  dedo y lanza el GPS hacia una caseta equivocada. El botón mide 64 px de ancho por toda
  la altura de la fila, bastante más que la píldora visible.

## Enlace de ubicación (opcional)

Si en algún momento se necesita **ver** el punto sin iniciar ruta —por ejemplo para
valorar el acceso— el formato es:

```
https://www.google.com/maps/search/?api=1&query={LAT},{LON}
```

No forma parte de la v1. Queda documentado para no tener que volver a investigarlo.

## Verificación antes de desplegar

Comprobaciones obligatorias, sobre dispositivo real, no solo en emulador:

1. Abrir tres ubicaciones distintas en un Android con Google Maps instalado y confirmar
   que arranca la navegación por voz en modo coche.
2. Repetir en un iPhone, con y sin la app de Google Maps instalada.
3. Comprobar que el destino cae sobre la caseta correcta contrastando con `data.md`,
   no de memoria.
4. Comprobar el caso de longitud negativa: todas las del proyecto lo son, así que un
   fallo de codificación se manifestaría en todas a la vez.

Estas comprobaciones no se dan por superadas si no se han ejecutado.

---

Fuentes: [Get Started | Maps URLs | Google for Developers](https://developers.google.com/maps/documentation/urls/get-started)
