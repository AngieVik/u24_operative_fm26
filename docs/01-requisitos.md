# 01 — Requisitos

Identificadores: `RF-n` funcional, `RNF-n` no funcional. Prioridad **M** (obligatorio para
la v1) / **D** (deseable, solo si no compromete la simplicidad).

## Requisitos funcionales

| ID | Prioridad | Requisito |
| --- | --- | --- |
| RF-1 | M | Pantalla única: campo de búsqueda arriba y lista de resultados debajo. Sin menús, sin navegación entre pantallas. |
| RF-2 | M | El foco entra en el campo de búsqueda al abrir la app, listo para teclear. |
| RF-3 | M | El filtrado es instantáneo a cada pulsación, sin botón de buscar y sin peticiones de red. |
| RF-4 | M | La búsqueda cubre **nombre** y **número** de ubicación en la misma caja. Escribir `97` encuentra la caseta 97; escribir `pimpi` encuentra El Pimpi. |
| RF-5 | M | La búsqueda es insensible a mayúsculas, tildes y diéresis: `malamia` encuentra `Malamía`, `alora` encuentra `Casa de Álora`. |
| RF-6 | M | La búsqueda por número acierta dentro de rangos: escribir `67` encuentra la caseta `66-67-68`. |
| RF-7 | M | Cada resultado se muestra como una tarjeta con el nombre destacado, el número y la calle. |
| RF-8 | M | Pulsar cualquier punto de la tarjeta abre Google Maps con la ruta en coche hacia las coordenadas de esa ubicación, según `docs/03-navegacion-maps.md`. |
| RF-9 | M | Con el campo vacío se muestra el listado completo, recorrible por desplazamiento. |
| RF-10 | M | Si ningún resultado coincide, se indica con un mensaje claro y breve. |
| RF-11 | M | Existe una forma evidente de borrar la búsqueda de un toque y volver al listado completo. |
| RF-12 | D | Copiar las coordenadas de una ubicación al portapapeles, para dictarlas por radio. Acción secundaria, nunca compitiendo visualmente con el botón principal. |

## Requisitos no funcionales

| ID | Prioridad | Requisito |
| --- | --- | --- |
| RNF-1 | M | **Funciona sin cobertura.** Los datos de ubicaciones viajan con la aplicación; buscar no requiere red. Solo Google Maps la necesita. |
| RNF-2 | M | **Instalable** en la pantalla de inicio de Android e iOS como acceso directo, sin pasar por tiendas de aplicaciones. |
| RNF-3 | M | **Mobile-first.** Diseñada para móvil en vertical; debe seguir siendo usable en tablet y escritorio, sin optimizar para ellos. |
| RNF-4 | M | **Alto contraste y tipografía grande.** Contraste mínimo 7:1 en texto principal (WCAG 2.1 AAA). Altura de fila **42 px** — ver nota. |
| RNF-5 | M | Arranque en frío inferior a 1 segundo en un móvil de gama media con la app instalada. |
| RNF-6 | M | El filtrado no produce retraso perceptible al teclear con el listado completo cargado. |
| RNF-7 | M | Sin cuentas de usuario, sin registro, sin seguimiento analítico, sin cookies. |
| RNF-8 | M | Sin claves de API de Google Maps: se usan exclusivamente Maps URLs públicas. |
| RNF-9 | M | Los enlaces de navegación funcionan igual en Android, iOS y navegador de escritorio con una sola URL. |
| RNF-10 | M | Dependencias mínimas. Cada dependencia debe justificarse; el proyecto debe poder mantenerse dentro de un año sin sorpresas. |
| RNF-11 | D | Tema oscuro por defecto o adaptado al sistema, por uso nocturno prolongado. |

### Nota sobre RNF-4 — altura de fila

El requisito original fijaba 48 px, el mínimo recomendado por WCAG 2.1 (criterio 2.5.5,
*Target Size*) para pulsación fiable.

El responsable del proyecto decidió **42 px** el 14/08/2026, priorizando la densidad: 16
ubicaciones visibles por pantalla frente a 11, lo que reduce el desplazamiento necesario
para encontrar una caseta cuando se busca por nombre parcial.

Queda registrado el riesgo asociado: con el vehículo en marcha y guantes puestos, una
fila de 42 px (~0,9 cm) aumenta la probabilidad de pulsar la fila contigua. La mitigación
es que las filas son contiguas y ocupan todo el ancho, de modo que no existen zonas
muertas entre objetivos, y que el destino se confirma visualmente en Google Maps antes
de arrancar.

**Verificar en pruebas de campo.** Si se detectan pulsaciones erróneas con guantes, la
decisión debe revisarse: es el único parámetro de diseño que puede provocar que la unidad
salga hacia una caseta equivocada.

## Fuera de alcance (v1)

Registrado explícitamente para que no reaparezca como propuesta durante la implementación:

- Mapa interactivo dentro de la aplicación.
- Registro de avisos, incidencias, tiempos de respuesta o partes de asistencia.
- Cuadrantes, turnos o gestión de personal.
- Cuentas, autenticación o roles.
- Edición de ubicaciones desde la interfaz.
- Backend, base de datos o sincronización entre dispositivos.
- Geolocalización propia de la unidad dentro de la app (la aporta Google Maps).
- Datos de otros años o de otros recintos feriales.
- Notificaciones push.
- Analítica de uso.

## Restricciones técnicas de partida

Condicionan la elección de stack, que se decide y justifica en el plan de implementación:

- Debe poder servirse como sitio estático, sin servidor de aplicación.
- Los datos de ubicaciones se empaquetan con la aplicación, no se piden en tiempo de ejecución.
- Sin claves de API ni secretos de ningún tipo en el cliente.
- Debe admitir instalación como aplicación web progresiva (manifiesto + service worker).
- Superficie de código pequeña y legible: este proyecto se revisa una vez al año, antes de cada Feria.
