# 00 — Contexto

## Problema

Durante la Feria de Málaga el Real es un recinto denso de casetas numeradas repartidas en
varias calles paralelas. Los avisos sanitarios llegan identificando la caseta por su
**nombre comercial** ("El Pimpi", "Malamía") o por su **número** ("la 97", "la 145-146"),
no por una dirección postal navegable.

Localizar esa caseta a mano cuesta tiempo: los nombres no son direcciones, Google Maps no
los resuelve de forma fiable dentro del recinto, y hacerlo desde el móvil mientras se
conduce o se prepara la salida distrae al equipo.

## Objetivo

Reducir a segundos el paso «tengo el nombre de la caseta» → «el GPS me está guiando».

## Usuarios

- **Primario:** personal de la unidad U24 (conductor y sanitarios) usando su móvil dentro
  del vehículo, con prisa, frecuentemente de noche y en un entorno ruidoso.
- **Secundario:** coordinación del operativo, que puede necesitar consultar y dictar las
  coordenadas exactas de una ubicación.

## Escenario de uso de referencia

1. Entra un aviso: *"asistencia en la caseta El Sarao"*.
2. El sanitario abre la app desde el acceso directo de la pantalla de inicio.
3. Escribe `sar`. La lista se filtra al instante y muestra la tarjeta de **El Sarao
   (66-67-68)**.
4. Pulsa la tarjeta. Se abre Google Maps con la ruta en coche calculada desde la posición
   actual hasta las coordenadas exactas de la caseta.
5. La unidad sale.

Variante equivalente: el aviso llega como *"la 66"* y el sanitario escribe `66`.

## Alcance

**Dentro:** buscador de texto con filtrado instantáneo sobre el listado cerrado de
ubicaciones y apertura de Google Maps en modo navegación en coche.

**Fuera:** todo lo demás. Ver la lista explícita en `docs/01-requisitos.md`.

## Criterios de éxito

| Criterio | Umbral |
| --- | --- |
| Tiempo de apertura de la app hasta lista utilizable | < 1 s con la app ya instalada |
| Tiempo total de la tarea (abrir → GPS navegando) | < 5 s |
| Aciertos al pulsar la tarjeta correcta | sin fallos de pulsación en pruebas en vehículo |
| Precisión del destino | las coordenadas abiertas coinciden exactamente con `data.md` |
| Cobertura del listado | las 125 ubicaciones de `data.md` son localizables |

## Restricciones del entorno

- Red móvil **saturada** durante la Feria: la app no puede depender de la red para buscar.
  Google Maps sí requerirá datos, pero eso queda fuera de nuestro control.
- Uso a una mano, con el móvil en soporte o en marcha. Sin teclado físico.
- Pantallas de móvil de gama variada. No se puede presuponer un dispositivo concreto.

## Glosario

| Término | Significado |
| --- | --- |
| **Real de la Feria** | Recinto ferial de Cortijo de Torres donde se ubican las casetas. |
| **Caseta** | Local temporal de una peña, asociación o empresa. Unidad básica de ubicación. |
| **Número de caseta** | Identificador oficial. Puede ser un rango si la caseta ocupa varias parcelas (`66-67-68`). |
| **S/N** | Sin número. Puntos singulares del recinto sin parcela asignada. |
| **U24** | Unidad de emergencias sanitarias objeto de este operativo. |
| **FM26** | Feria de Málaga 2026. |
