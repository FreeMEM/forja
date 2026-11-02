# Herramientas de Forja por tipo de proyecto: diseño

Estado: propuesta para revisar (2026-11-02). Aún no hay código. Las decisiones que son del usuario están al final.

Lo pedido: herramientas de Forja específicas para hacer videojuegos, otras para demos y otras para aplicaciones de
escritorio.

## 1. Un proyecto con tipo

Hoy Forja abre ficheros sueltos y su panel enseña un cajón. La propuesta es un fichero de proyecto, `.forja` (ya en
el plan), en JSON como `.dashui`:

```
{ "forja": 1, "nombre": "Cueva", "tipo": "juego", "principal": "main.dash",
  "ejecutable": "Cueva", "opciones": "--cpu 68020", "version": "0.1", "icono": "Cueva.info" }
```

- **El tipo** es juego, demo o aplicación. Cambia tres cosas:
  - el menú Herramientas, con las de ese tipo;
  - la plantilla con que empieza el proyecto (Proyecto > Nuevo proyecto...);
  - cómo se agrupan los ficheros en el panel.
- **Lo demás:** el `.dash` principal, el ejecutable y las opciones de compilar. Así compilar ya no depende de qué
  pestaña está delante (hoy, desde un sprite, Forja busca `main.dash` a ciegas).
- **Sin `.forja`,** Forja funciona como ahora.

El panel del proyecto agrupa por clase: código (`.dash`), ventanas (`.dashui`), imágenes (`.iff`), mapas, escenas,
música (`.mod`) y textos (`.cd`/`.ct`).

## 2. Lo común a los tres tipos

| Herramienta | Hay | Nuevo |
|---|---|---|
| Editor, compilar, ejecutar, depurar | Sí | — |
| Perfil (`--profile`): qué funciones gastan el tiempo | En Dash, sin vista en Forja | Una tabla en la salida, con clic a la función |
| Fallos de memoria (`--memcheck`) | En Dash, sin vista en Forja | Los avisos como errores, con su línea |
| Memoria chip y fast mientras corre | `mem_chip_free` y los demás | Una línea en la barra mientras el programa corre |
| Editor de sprites | Este loop | — |
| Paquete `.lha` | `tools/paquete.py` (en el PC) | Hacerlo desde el Amiga (ver aplicaciones) |

## 3. Juegos

Lo grande ya está en otros diseños: sprites (este loop), mapas (bloque F) y escenas (`docs/JUEGOS_DISENO.md`).
Las herramientas de juego aparte de esas:

| Herramienta | Qué hace | Pide |
|---|---|---|
| Vista de depuración | Con el juego corriendo, dibuja encima las formas de choque, las velocidades y los nodos; F-tecla para encenderla | La biblioteca de juegos la dibuja ella misma si Forja se lo pide (una variable de entorno o un puerto) |
| Efectos de sonido | Grabar o cargar un 8SVX, recortarlo, cambiar volumen y tono, oírlo; para los efectos del juego | Leer y escribir 8SVX en Dash (hay `sound_load`; escribir, no) |
| Medidor de fotograma | Cuánto del fotograma de 20 ms gasta cada parte (lógica, físicas, dibujo) | La biblioteca mide con `time_ms`; Forja lo enseña |
| Plantilla | Un juego mínimo que se mueve, con su escena, su sprite y su mapa | Nada |

## 4. Demos

Lo que hace única a Forja para demos es **sincronizar con la música mientras la demo corre**.

| Herramienta | Qué hace | Pide |
|---|---|---|
| Pistas de sincronía | Valores que cambian a lo largo de la música ("zoom", "fundido", "escena"), con claves por fila del MOD e interpolación escalón, lineal o suave. Se editan en Forja con la demo corriendo, y el cambio se ve al momento. Al acabar se meten en el ejecutable como tabla. | `lib/sync.dash` (Dash puro); hablar con Forja: un puerto que reciba órdenes en un programa sin MUI (`rexx_port_open`, `rexx_port_get`, `rexx_port_reply`), que hoy no hay (solo `rexx_send` y `mui_app_rexx`) |
| Vista de la música | Los patrones del MOD, la fila que suena, las marcas E8x, y saltar a una posición | `music_pos`, `music_row` (hay); `music_sync()` para E8x y `music_seek(pos, fila)`: faltan |
| Línea de tiempo | Las partes de la demo (de la posición 0 a la 8, la 1; de la 8 a la 20, la 2), encima de la música | Nada más que las pistas |
| Editor de copper | Degradados y cambios de color por línea, con el resultado a la vista, que generan las llamadas a `copper_*` | `copper_*` (hay); listas a doble búfer: falta |
| Medidor de coste | Barras de color en el borde (raster bars) y las líneas de pantalla que gasta cada efecto | `frame_lines()` (leer VHPOSR): falta |
| Tamaño | Lo que ocupa el ejecutable, con el tope de 4K o 64K a la vista, y comprimirlo con Shrinkler | Shrinkler es un programa del PC; si tiene versión de Amiga (sin comprobar), llamarlo con `run_start`, como a `dash` |
| Plantilla | Una demo con música, una pista de sincronía y dos partes | Nada |

## 5. Aplicaciones de escritorio

Hoy, de esto, en el Amiga solo está el editor de ventanas. Iconos, traducciones y paquetes se hacen en el PC con
Python (`tools/iconos_wb.py`, `tools/catalogo.py` de Dash, `tools/paquete.py`). Para que Forja sea un IDE completo
en el Amiga, eso tiene que pasar a Forja.

| Herramienta | Qué hace | Pide |
|---|---|---|
| Ventanas `.dashui` | Árbol, propiedades y vista con MUI de verdad | Ya está |
| Traducciones | Tabla con cada texto (`tr`) y su traducción en cada idioma; genera `.cd`, `.ct` y el `.catalog` | Dash puro: es lo que hace `tools/catalogo.py`, escrito en Dash |
| Iconos `.info` | Dibujar el icono (con el editor de sprites: 4 colores del Workbench, dos imágenes, normal y elegido) y sus datos (herramienta por defecto, tipos de herramienta) | Escribir `.info` en Dash, como `tools/iconos_wb.py`; para los de 3.5+ (ColorIcons) más adelante |
| Ayuda AmigaGuide | Editor de nodos y enlaces con vista; enlaza desde el menú Ayuda | Dash puro (es texto); abrirla con MultiView, que ya se puede |
| Puerto ARexx | Tabla de órdenes (nombre, argumentos, qué función de Dash) que genera el código de `mui_app_rexx` y su documentación | Nada nuevo |
| Instalador | El script de Installer de la aplicación (cajón, Libs que pide, iconos, catálogos), como el de Trasfondo | Dash puro |
| Paquete para Aminet | El `.lha` y su `.readme` con el formato de Aminet (Short, Author, Type, Version, Requires) | Llamar a `lha` del Amiga con `run_start` |
| Plantilla | Una aplicación MUI con su ventana, su menú, su catálogo y su icono | Nada |

## 6. Orden propuesto (cada fase deja algo que se usa)

1. **El `.forja`, las plantillas y el menú por tipo.** Compilar va con el proyecto.
2. **Lo común:** perfil, memcheck y la memoria mientras corre.
3. **Escritorio:** traducciones, iconos e instalador. Son Dash puro, ya tienen su versión de Python que sirve de
   modelo, y Forja e Inferencia los usan ya.
4. **Demos:** pistas de sincronía y vista de la música (piden `rexx_port_*`, `music_sync` y `music_seek`), luego
   el editor de copper y el medidor.
5. **Juegos:** cuando esté la biblioteca de juegos (`docs/JUEGOS_DISENO.md`): vista de depuración, medidor y
   efectos de sonido.
6. **El resto:** AmigaGuide, paquete para Aminet, Shrinkler.

**Builtins nuevos que salen de aquí** (además de los de los otros diseños):
- `rexx_port_open`, `rexx_port_get` y `rexx_port_reply`: un puerto ARexx en un programa sin MUI;
- `music_sync()` y `music_seek(pos, fila)`, y el reproductor de MOD con los efectos que le faltan (E6, E8, E9,
  ED, EE y 7);
- `frame_lines()`;
- listas de copper a doble búfer;
- escribir 8SVX.

## 7. Decisiones para el usuario

1. **¿Fichero de proyecto `.forja`** como se propone, o el tipo en otro sitio (por ejemplo, en el cajón)?
2. **El orden:** ¿escritorio antes que demos (propuesta: es lo que Forja e Inferencia ya necesitan), o demos
   antes, porque es lo que más distingue a Forja?
3. **Iconos:** ¿solo los clásicos de 4 colores, o también los de 3.5+ (ColorIcons) desde el principio?
4. **Shrinkler:** es de otro autor; ¿se llama si está instalado (propuesta), o se busca un compresor propio?
