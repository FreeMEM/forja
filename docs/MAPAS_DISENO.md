# Editor de mapas de tiles: diseño

Estado: decidido (2026-11-03). Fase 1 hecha en Dash (rama `mapas`, sin fusionar); ver la sección 7.
Lo pedido: "alguna herramienta en forja para mapas de juegos". Es el bloque F de `docs/SPRITES_LOOP.md`, y el
nodo `Mapa` (TileMap) de Fragua (`docs/JUEGOS_DISENO.md`).

## 1. Las piezas

- **El tileset es un BOB del editor de sprites:** una tira de fotogramas cuadrados, uno por tile, de 8, 16 o 32
  píxeles. Se dibuja, se anima y se guarda con lo que ya hay. Con el FRJA de Forja, `bob_load` sabe el ancho de
  cada tile (tarea 15).
- **El mapa** es una rejilla de números de tile, en una o más capas (fondo, primer plano, choques, objetos).
- **El editor** es otra pestaña de Forja, como la de sprites, con el mismo panel en páginas.
- **En el juego:** el nodo `Mapa` de Fragua, sobre un builtin de Dash que pinta un trozo del mapa rápido.

## 2. El fichero del mapa

Propuesta: **IFF propio**, `FORM FMAP`. Es lo del Amiga (como el ILBM), se lee rápido en un 68000 y deja meter
trozos nuevos sin romper los viejos.

| Trozo | Qué lleva |
|---|---|
| `MHDR` | ancho y alto en tiles, lado del tile, número de capas, versión |
| `TSET` | el nombre del fichero del tileset (`.iff` de Forja), relativo al mapa |
| `LAYR` | una capa: nombre, tipo (tiles, choques u objetos), si se ve, y sus celdas: un word por celda, con el número de tile y dos bits de espejo (H y V) |
| `OBJS` | la capa de objetos: puntos con nombre y tipo ("jugador", "enemigo", "moneda") que Fragua convierte en nodos |

Un texto (CSV o JSON) sería más fácil de leer a mano, pero un mapa de 256x64 con dos capas son 32.768 números:
partirlos con `str_split` en Dash tarda segundos en un 68000. **Para usar mapas hechos en el PC:** importar y
exportar el JSON de Tiled (el editor de mapas libre más usado), como pestaña aparte más adelante.

## 3. El editor en Forja

Se parece al de sprites:
- **Zona central:** el mapa con su zoom (1x, 2x o 4x), con desplazamiento con las flechas, la rueda (y Mayúsculas
  + rueda en horizontal) o arrastrando con el botón del medio. Rejilla opcional (G).
- **Panel (en páginas):**
  - **Tiles:** el tileset para elegir con un clic, o un bloque de varios tiles arrastrando.
  - **Capas:** lista con ver u ocultar, cuál se edita, añadir, quitar y subir o bajar.
  - **Mapa:** ancho, alto, lado del tile y el tileset.
  - **Objetos:** tipo y nombre del objeto elegido.
- **Herramientas** (como en el editor de sprites, con las mismas teclas donde se puede):
  - lápiz, que pinta el tile o el bloque elegido;
  - caja rellena;
  - relleno;
  - cuentagotas, que coge el tile de la celda;
  - borrar (tile 0, o Alt + clic);
  - selección rectangular para copiar, cortar, pegar y voltear trozos de mapa;
  - espejo del tile (H y V).
- **Capa de choques:** cada celda lleva un tipo (vacío, sólido, plataforma que se cruza por debajo, escalera,
  daño), pintado encima en colores con transparencia por tramado. Es lo que lee `Cuerpo` en Fragua.
- **Capa de objetos:** se ponen con un clic, se arrastran y se ven como el primer fotograma de su sprite, si lo
  tiene.
- **Tiles animados:** si un tile del tileset es el primero de una animación (varios fotogramas seguidos con un
  nombre), el editor lo enseña animado con la vista animada que ya hay.
- **Deshacer y rehacer,** como en los sprites. Los pasos guardan solo las celdas tocadas.
- **"Código" (C):** las líneas para cargarlo, como en el editor de sprites.

## 4. Pintar el mapa en el juego

Lo que cuesta, sin medir todavía (fase 1): una pantalla de 320x256 con tiles de 16 son 20x16 = 320 tiles. Con
`BltBitMap` del sistema, cada tile cuesta del orden de una décima de milisegundo (lo que mide `RectFill` en la tarea
4 de este loop). Pintarlos todos en cada fotograma no cabe en 20 ms. La salida está en lo que hacen los juegos del
Amiga:
- **Scroll por hardware:** la pantalla es algo más grande que lo visible y se mueve el comienzo del bitmap (o el
  registro de scroll fino). Cada fotograma solo se pintan las tiras nuevas: una columna o una fila de 16 a 21
  tiles. Pide el builtin de scroll de hardware (`docs/JUEGOS_DISENO.md`) y el doble búfer (tarea 25).
- **`tilemap_draw(mapa, capa, tx, ty, ancho, alto, x, y)`** en Dash: pinta un rectángulo de tiles en una llamada,
  en C, con el blitter (una tira de tiles de una vez cuando son seguidos en el tileset). Sirve para la pantalla
  entera al empezar y para las tiras del scroll.
- **En RTG** se pinta en un bitmap de memoria y se copia, como `gfx_pens_draw` (tarea 15b).
- **Tiles animados:** se cambia el tile en las celdas que se ven, solo las que tocan en ese fotograma.

## 5. Fases

1. **El fichero y los builtins:** leer y escribir `FMAP` en Dash; `tilemap_draw`. Medir en A500 y A1200 (tiles por
   milisegundo, pantalla entera y una tira). Ejemplo: un mapa que se pinta entero.
2. **El editor básico:** pestaña, tileset, lápiz, borrar, relleno, cuentagotas, capas, zoom, desplazamiento,
   deshacer y guardar. Pruebas como las de sprites.
3. **Choques y objetos:** las dos capas especiales y su vista.
4. **Selección:** copiar, cortar, pegar y voltear trozos; bloques de varios tiles.
5. **En Fragua:** el nodo `Mapa` con scroll por hardware y choques para `Cuerpo`. Ejemplo: un nivel de plataformas
   que se recorre.
6. **Tiled:** importar y exportar su JSON.

## 6. Decisiones para el usuario

**Decidido el 2026-11-03:** las cuatro propuestas (IFF propio, Tiled en la fase 6, tiles cuadrados de 8, 16 y 32, hasta 1.024x1.024 tiles por capa).

1. **Formato:** ¿IFF propio (`FORM FMAP`, propuesto), o texto/JSON aunque cargue más lento?
2. **Tiled:** ¿importa poder traer mapas hechos en el PC con Tiled? (Propuesta: sí, en la fase 6.)
3. **Tamaños de tile:** ¿8, 16 y 32 (propuesto), o también rectangulares (16x8, para juegos isométricos o de
   coches)?
4. **Mapas grandes:** propuesta, hasta 1.024x1.024 tiles por capa (2 MB por capa en words: en un A1200 con poca
   memoria, mejor menos). ¿Hace falta más, o por trozos?

## 7. Fase 1 (hecha, 2026-11-03)

En Dash, rama `mapas`. Los mapas viven en C, por número (8 a la vez), como los BOB:
- `tilemap_create(id, ancho, alto, tile, capas)`, `tilemap_load` y `tilemap_save` (`FORM FMAP`), `tilemap_free`.
- `tilemap_get` y `tilemap_set` (el word de la celda: el tile, 0 vacía, más 16384 con espejo H y 32768 con
  espejo V), `tilemap_width`, `_height`, `_tile_size` y `_layers`.
- `tilemap_tileset` y `tilemap_set_tileset`; `tilemap_layer_name`, `_type`, `_visible` y `tilemap_layer_set`;
  `tilemap_layer_add`, `_remove` y `_move`; `tilemap_resize`.
- `tilemap_draw(id, capa, bob, tx, ty, tw, th, x, y)`: el tile n es el fotograma n - 1 del BOB, con su espejo; las
  vacías, lápiz 0. `tilemap_draw_masked`: el color 0 y las vacías dejan ver lo de debajo. Se pinta en un bitmap
  aparte (entrelazado si la pantalla es de planos) y se copia a la ventana de una vez.
- Test `test_tilemap` (celdas, capas, tamaño, guardar y cargar, pintar con espejos y con máscara).

Medido a velocidad real, pantalla de 320x256 con 5 planos y tiles de 16 (320 tiles):

| | A1200 | A500 |
|---|---|---|
| Pantalla entera | 130 ms | 311 ms |
| Una columna (16 tiles) | 7 ms | 21 ms |
| Una fila (20 tiles) | 9 ms | 23 ms |
| Pantalla entera con máscara | 485 ms | 975 ms |

Conclusiones:
- Una tira del scroll cabe en un fotograma (20 ms) en A1200; en A500 va justa.
- Pintar la pantalla entera cada fotograma no cabe: hace falta el scroll por hardware (fase 5).
- La máscara cuesta casi cuatro veces más: las capas de delante, con pocos tiles llenos.
- Probado y descartado: copiar los tiles con la CPU (tiles de bytes enteros, sin desplazar) fue más lento que el
  blitter en un A1200 sin memoria Fast (300 ms frente a 170). Los bitmaps entrelazados bajaron de 170 a 130.
- Para ir más rápido haría falta programar el blitter directamente; queda para la fase 5 si hace falta.

## 8. Fase 2 (hecha, 2026-11-03)

El editor en Forja (`src/mapas.dash`). Lo de la fase 1 cambió un poco para él: en `tilemap_draw` cada celda mide lo
que un fotograma del BOB (el editor tiene zoom haciendo un BOB mayor) y las celdas vacías dejan ver lo de debajo.
- Abre y guarda `.fmap`; Amiga-B crea un mapa (y pide el tileset: un mapa nuevo toma el lado de sus tiles).
- Vista con zoom 1, 2 o 4 (el primero, 2 si caben 8 filas; si no, 1), rejilla, flechas y rueda. Hasta 4 mapas
  abiertos a la vez: cada uno usa dos BOB de Dash para verse (con los lápices de la pantalla: uno con el color 0
  del tema para la primera capa, otro con el color 0 transparente para las demás).
- Panel: Tiles (herramientas, espejos, el tileset), Capas y Mapa (ancho, alto, zoom, rejilla, tileset, código).
- Deshacer: las celdas tocadas; los cambios de tamaño o de capas guardan el mapa entero en `RAM:`.
- Pruebas: `mapas_base` y `mapas_forja` (con `tests/fmap.py`, que también escribe mapas para las pruebas).

Pendiente: la selección y los bloques de tiles, los tiles animados, y elegir el zoom de la vista sin depender del
alto de la pantalla.

## 9. Fase 3 (hecha, 2026-11-03)

- **Choques:** una capa de tipo 1 (`tilemap_layer_type`). Sus celdas: 1 sólido, 2 plataforma (se cruza desde
  abajo), 3 escalera, 4 daño. En el editor, la página Capas cambia el tipo de la capa elegida; en una capa de
  choques, la página Tiles ofrece los cuatro tipos. Se pintan encima con `tilemap_draw_masked` y un BOB de tramas
  (el borde y un píxel de cada cuatro del color del tipo). No se guardan aparte: es una capa más del FMAP.
- **Objetos:** del mapa entero, no de una capa. En Dash (rama `mapas-objetos`): el trozo `OBJS` y
  `tilemap_object_add`, `_remove`, `_move`, `_set`, `_find`, `_x`, `_y`, `_kind`, `_name` y `_sprite` (hasta 256,
  en píxeles). En el editor, la página Objetos: la clase (jugador, enemigo, moneda, puerta, otro), un clic pone o
  elige, arrastrar mueve (de celda en celda), Supr quita, y "Sprite..." le da un sprite, que se ve con su primer
  fotograma; sin sprite, un marco con la inicial de la clase.
- Deshacer de los objetos y del tipo de capa: el mapa entero, como los cambios de tamaño.
- "Código" añade cómo leer los choques y un bucle por cada clase de objeto con `tilemap_object_find`.
- Pruebas: `mapas_base` y `mapas_forja` ampliadas; `tests/fmap.py` lee y escribe objetos y capas de choques.

