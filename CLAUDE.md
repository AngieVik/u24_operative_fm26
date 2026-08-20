# U24 · Buscador de ubicaciones

Instrucciones permanentes del proyecto. Tienen prioridad sobre cualquier suposición por
defecto. Si algo aquí contradice a un documento de `docs/`, avisa antes de continuar.

## Qué es

Buscador de respuesta rápida para el operativo de emergencias sanitarias U24. El sanitario
recibe un aviso con el nombre o el número de una ubicación, lo teclea, pulsa la fila y el
móvil abre la ficha de lugar de Google Maps sobre las coordenadas exactas de ese punto.

Desde esa ficha, quien conoce la zona se ubica de un vistazo y sale; quien no la conoce
pulsa «Cómo llegar» dentro de Maps. Las dos salidas son legítimas y la aplicación no decide
por el usuario cuál necesita.

Elimina el tiempo perdido buscando ubicaciones a mano. No hace nada más.

## Principios

1. **Una sola función.** Buscar una ubicación y abrirla en el mapa. Cualquier propuesta de
   añadir menús, mapas propios, cuentas de usuario o pantallas intermedias dentro de la
   aplicación se rechaza salvo petición expresa del responsable. La ficha de Google Maps no
   es una pantalla de la aplicación: es el destino.
2. **Instantáneo.** El filtrado ocurre al teclear, sin botón de buscar, sin esperas de red
   y sin indicadores de carga.
3. **Se usa con prisa, de noche y con guantes.** Legibilidad y acierto al pulsar por encima
   de cualquier otra consideración estética.
4. **Precisión total.** Las coordenadas salen siempre del listado verificado. Nunca se
   resuelve una ubicación mediante búsqueda de texto en Google Maps.
5. **Nunca al sitio equivocado.** Ante la duda, se muestran menos resultados, no resultados
   aproximados disfrazados de exactos. La tolerancia a erratas no se aplica jamás a los
   números y siempre va rotulada como aproximada.
6. **Cero fricción de instalación.** Es una web: se abre por URL y se añade a la pantalla
   de inicio. No hay tiendas de aplicaciones.

## Libertad de diseño

La interfaz puede rediseñarse sin pedir permiso mientras respete los principios 2, 3 y 5.
No hay parámetros visuales protegidos: ni altura de fila, ni escala tipográfica, ni paleta,
ni densidad.

Con una excepción: **al mapa solo se llega por el botón de la derecha**. La fila no es un
enlace, y convertirla en uno exige acuerdo expreso del responsable. Las coordenadas sí son
pulsables —copian al portapapeles— porque copiar no navega ni tiene consecuencias.
Cualquier otro elemento pulsable se decide igual: se admite si no puede llevar a nadie a
otro sitio, y solo con acuerdo expreso.

## Documentación

| Documento | Contenido |
| --- | --- |
| `data.md` | **Fuente de verdad.** Ubicaciones y calles. No se edita sin autorización expresa. |
| `docs/01-producto.md` | Objetivo, usuarios, requisitos y fuera de alcance. |
| `docs/02-datos.md` | Modelo de datos, normalización y reglas de búsqueda. |
| `docs/03-navegacion-maps.md` | Construcción de los enlaces a Google Maps. |
| `docs/04-convenciones.md` | Estructura, proceso de compilación, código y pruebas. |
| `docs/05-mantenimiento.md` | Actualizar el listado y regenerar la tipografía. |

## Reglas de trabajo

- Trabaja en **español de España**. Identificadores de código en inglés; textos de interfaz
  y documentación en español.
- `data.md` es de solo lectura. Toda corrección sobre los datos de origen se implementa
  como regla de transformación en el proceso de compilación, no modificando el origen.
- No inventes coordenadas, nombres ni identificadores. Si un dato falta o es
  contradictorio, señálalo.
- **Propón antes de añadir.** Toda función, elemento o comportamiento nuevo se plantea
  primero y se implementa después de que el responsable lo apruebe. Esto no afecta a
  corregir defectos ni a terminar lo ya encargado.
- Verifica antes de dar una tarea por terminada. No afirmes que algo funciona si no lo has
  comprobado.
- El responsable se encarga personalmente de los commits y del despliegue.

## Estado

Aplicación en uso. Sitio estático generado por `scripts/build.py`: un único `index.html`
autocontenido con los datos, el motor de búsqueda, la tipografía y el emblema empotrados.
Sin framework, sin compilación de JavaScript y sin peticiones de red en el arranque. Única
dependencia de terceros: Fuse.js, en `src/vendor/`.

Pendiente de comprobación en dispositivo real: que la ficha de lugar caiga en el punto
correcto en Android e iOS, y que el trazado de una calle siga la calle y no un rodeo por
fuera del recinto.
