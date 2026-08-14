# U24 Operative FM26

Instrucciones permanentes del proyecto. Este archivo tiene prioridad sobre cualquier
suposición por defecto. Si algo aquí contradice a un documento de `docs/`, avisa antes
de continuar.

## Qué es esto

Buscador de respuesta rápida para el **operativo de emergencias sanitarias U24** durante
la **Feria de Málaga 2026**. Un sanitario recibe un aviso con el nombre o el número de una
caseta del Real, lo teclea, pulsa la tarjeta correspondiente y el móvil abre Google Maps
con la ruta en coche ya calculada hasta las coordenadas exactas.

Elimina el tiempo perdido buscando ubicaciones a mano. No hace nada más.

## Principios de diseño — no negociables

1. **Una sola función.** Buscar y navegar. Cualquier propuesta de añadir menús, mapas
   embebidos, cuentas de usuario o pantallas intermedias se rechaza salvo petición
   expresa del responsable del proyecto.
2. **Instantáneo.** El filtrado ocurre al teclear, sin botón de buscar, sin esperas de
   red y sin spinners. Objetivo: de abrir la app a tener el GPS en marcha en menos de
   5 segundos.
3. **Se usa con prisa, de noche y con guantes.** Alto contraste, tipografía grande,
   áreas de pulsación amplias. Si hay que elegir entre estética y acierto al pulsar,
   gana el acierto.
4. **Precisión total.** Las coordenadas se toman siempre del listado cerrado y
   verificado. Nunca se resuelve una ubicación mediante búsqueda de texto en Google Maps.
5. **Cero fricción de instalación.** Es una web. Se abre por URL y se puede añadir a la
   pantalla de inicio del móvil. No hay tiendas de aplicaciones.

## Documentos canónicos

Léelos antes de tocar nada relacionado con su ámbito.

| Documento | Contenido |
| --- | --- |
| `data.md` | **Fuente de verdad de las ubicaciones.** No se edita sin autorización expresa. |
| `descripcion.md` | Brief original del responsable del proyecto. Prevalece sobre cualquier interpretación posterior. |
| `docs/00-contexto.md` | Objetivo, usuarios, escenario de uso, criterios de éxito. |
| `docs/01-requisitos.md` | Requisitos funcionales, no funcionales y fuera de alcance. |
| `docs/02-datos.md` | Modelo de datos, normalización de `data.md` y casos especiales. |
| `docs/03-navegacion-maps.md` | Construcción de los enlaces a Google Maps (Android/iOS/web). |
| `docs/04-convenciones.md` | Convenciones de código, estructura y accesibilidad. |

## Reglas de trabajo

- Trabaja en **español de España**. Los identificadores de código en inglés; los textos
  de interfaz y la documentación en español.
- `data.md` es de solo lectura. Cualquier corrección sobre los datos originales se
  documenta como regla de transformación en `docs/02-datos.md`, no modificando el origen.
- No inventes coordenadas, nombres ni números de caseta. Si un dato falta o es
  contradictorio, señálalo; no lo rellenes.
- No amplíes el alcance por iniciativa propia. Las ideas fuera de alcance van a la
  sección correspondiente de `docs/01-requisitos.md`, no al código.
- Antes de dar por terminada una tarea, verifica el resultado. No afirmes que algo
  funciona si no lo has comprobado.

## Estado

- **Fase actual:** instrucciones cerradas. Siguiente paso: plan de implementación.
- **Stack técnico:** pendiente de decisión. Se propone y justifica en el plan de
  implementación, dentro de las restricciones de `docs/01-requisitos.md`.
