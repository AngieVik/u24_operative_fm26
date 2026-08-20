# 00 — Contexto

## Problema

El operativo cubre un recinto denso de ubicaciones repartidas en varias calles paralelas.
Los avisos llegan identificando el punto por su **nombre** («El Pimpi», «Malamía») o por
su **número** («la 97», «la 145-146»), no por una dirección postal navegable.

Localizar ese punto a mano cuesta tiempo: los nombres no son direcciones, Google Maps no
los resuelve de forma fiable dentro del recinto, y hacerlo desde el móvil mientras se
conduce o se prepara la salida distrae al equipo.

## Objetivo

Reducir a segundos el paso «tengo el nombre de la ubicación» → «sé dónde está y salgo».

## Usuarios

- **Primario:** personal de la unidad U24 (conductor y sanitarios) usando su móvil dentro
  del vehículo, con prisa, frecuentemente de noche y en un entorno ruidoso.
- **Secundario:** coordinación del operativo, que puede necesitar consultar y dictar las
  coordenadas exactas de una ubicación.

Buena parte del equipo **conoce la zona**. Para esos usuarios, ver el punto sobre el mapa
un segundo es suficiente para salir; no necesitan navegación asistida y les estorba.

## Escenario de uso de referencia

1. Entra un aviso: *«asistencia en El Sarao»*.
2. El sanitario abre la app desde el acceso directo de la pantalla de inicio.
3. Escribe `sar`. La lista se filtra al instante y muestra **El Sarao (66-67-68)** con su
   calle.
4. Pulsa el botón de ubicación de esa fila. Se abre la ficha de lugar de Google Maps con
   el punto exacto sobre el mapa.
5. Quien conoce la zona se orienta y sale. Quien no, pulsa «Cómo llegar» e «Iniciar»
   dentro de Maps.

Variantes equivalentes: el aviso llega como *«la 66»* y el sanitario escribe `66`; o el
nombre se teclea con una errata (`saroa`) y la app ofrece la ubicación parecida.

### Por qué la ficha de lugar y no la navegación directa

Hasta el 19/08/2026 el enlace lanzaba la navegación paso a paso. Las pruebas de campo
mostraron que el equipo **cancelaba el navegador** para poder ver la ficha del sitio y
orientarse, lo que costaba más tiempo que no haberlo lanzado. Varios miembros preferían
abrir otras aplicaciones, más lentas y menos precisas, antes que pelearse con eso.

La ficha de lugar sirve a los dos perfiles sin penalizar a ninguno: es lo que la mayoría
necesita, y desde ella se llega a la navegación en un toque.

## Alcance

**Dentro:** buscador de texto con filtrado instantáneo y tolerante a erratas sobre el
listado cerrado de ubicaciones, y apertura de la ficha de lugar de Google Maps sobre las
coordenadas exactas.

**Fuera:** todo lo demás. Ver la lista explícita en `docs/01-requisitos.md`.

## Criterios de éxito

| Criterio | Umbral |
| --- | --- |
| Tiempo de apertura de la app hasta lista utilizable | < 1 s con la app ya instalada |
| Tiempo total de la tarea (abrir → punto visible en el mapa) | < 5 s |
| Aciertos al pulsar la fila correcta | sin fallos de pulsación en pruebas en vehículo |
| Precisión del destino | las coordenadas abiertas coinciden exactamente con `data.md` |
| Cobertura del listado | las 125 ubicaciones de `data.md` son localizables |
| Tolerancia a erratas | un nombre con una letra cambiada, omitida o intercambiada encuentra su ubicación |
| Utilidad con la red caída | la app abre y permite dictar la posición aunque Google Maps no cargue |
| Trazabilidad del listado | se puede saber, mirando el móvil, de qué fecha es la lista que lleva |

## Restricciones del entorno

- Red móvil **saturada** durante el operativo: la app no puede depender de la red para
  buscar. Google Maps sí requerirá datos, pero eso queda fuera de nuestro control.
- Uso a una mano, con el móvil en soporte o en marcha. Sin teclado físico.
- Pantallas de móvil de gama variada. No se puede presuponer un dispositivo concreto.

## Glosario

| Término | Significado |
| --- | --- |
| **Ubicación** | Cada uno de los puntos del listado. Unidad básica de búsqueda. |
| **Identificador** | Número o etiqueta oficial del punto. Puede ser un rango cuando ocupa varias parcelas (`66-67-68`). |
| **S/N** | Sin número. Puntos singulares del recinto sin parcela asignada. |
| **Ficha de lugar** | Pantalla de Google Maps que muestra un punto sobre el mapa con sus acciones («Cómo llegar», «Iniciar»). |
| **Coincidencia aproximada** | Resultado que se parece a lo tecleado sin coincidir literalmente. Siempre rotulado como tal. |
| **U24** | Unidad de emergencias sanitarias objeto de este operativo. |
