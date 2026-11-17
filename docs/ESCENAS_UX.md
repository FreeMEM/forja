# Fragua en Forja: diseño de la experiencia de uso

Estado: propuesta para revisar (2026-11-17). Es un documento de diseño. No hay código hecho a partir de él.

Qué cubre: el editor de escenas de Forja, los comportamientos, los eventos con acciones sin código, los recorridos
de uso por tipo de juego, los casos difíciles, el isométrico, lo que hay que dejar abierto para el 3D, el plan por
fases y cómo se prueba.

De dónde sale:
- `docs/JUEGOS_DISENO.md`, `docs/MAPAS_DISENO.md`, `docs/3D_DISENO.md`, `docs/EXTENSIONES.md` y `docs/FORJA_LOOP.md`
  de Forja.
- `docs/FRAGUA_LOOP.md` y `src/*.dash` de la rama `nodos` de Fragua (en marcha: lo que digo de ella puede cambiar).
- Los editores de Sprites y de Mapas, que ya son extensiones con ventana propia.

Cómo leer las marcas:
- **(de memoria)**: lo que cuento de Godot, GameMaker, Construct, Unity, RPG Maker, Tiled, AMOS o Blitz sale de mi
  recuerdo de esas herramientas. No lo he comprobado para este documento.
- **(propuesto)**: no está en el plan de Fragua ni de Forja de hoy. Lo añade este diseño.
- **(por medir)**: una cifra que es objetivo, no medida.

Nombres: en la interfaz, en castellano e inglés por catálogo, como Forja. En el código que se genera, la API de
Fragua, en inglés.

---

## 0. Las doce decisiones que sostienen lo demás

1. **Una extensión, "Escenas", con ventana propia**, como Sprites y Mapas. Abre los `.escena`. Los paneles de Forja
   son de texto y no sirven para dibujar.
2. **Tres zonas fijas y siempre las mismas: árbol, vista e inspector.** En pantallas pequeñas no se encogen: se
   turnan. Nunca hay ventanas flotantes que perder.
3. **El inspector tiene cuatro páginas por nodo: Propiedades, Comportamientos, Eventos y Script.** Son los cuatro
   escalones de "sin código" a "código". Se sube de uno en uno y no se pierde nada al subir.
4. **Todo lo que no es código se convierte en código Dash legible**, en un fichero aparte que el usuario puede
   leer siempre y no edita nunca. Su código va en otro fichero, que Forja no toca nunca.
5. **La hoja de eventos es por nodo, no por escena.** Una fila es "Cuando pasa esto, y si se cumple esto, haz
   esto". Como los eventos de un objeto de GameMaker, con filas como las de Construct (de memoria).
6. **La vista del editor no corre el juego.** Enseña la escena colocada. Para verla "de verdad" hay una tecla que
   compila y la abre parada. Para jugar, otra.
7. **Tres calidades de vista: Cajas, Aproximada y Fiel.** La de Cajas funciona con 4 colores y en un 68020 a
   14 MHz. Nadie se queda sin editor por su máquina.
8. **La definición de nodos, propiedades, comportamientos, eventos y acciones sale de `api/fragua.json`.** El
   editor no lleva ninguna lista escrita a mano. Añadir un nodo a Fragua no pide tocar el editor.
9. **Plantillas por género.** Nadie empieza con una escena vacía si no quiere.
10. **Cada error lleva al nodo, no a una línea de código generado.**
11. **La proyección (plana, isométrica y, un día, 3D) es una propiedad de la escena y una pieza cambiable de la
    vista.** El árbol, el inspector y los eventos no saben de proyecciones.
12. **Cada fase se mide:** clics y segundos por tarea, en el emulador, con las pruebas de Forja.

---

## 1. Principios de UX para un editor de juegos en un Amiga

### 1.1 Lo que manda la máquina

| Límite | Lo que obliga a hacer |
|---|---|
| Pantalla de 640x256 con píxeles altos (el doble de altos que de anchos) | Un píxel del juego (320x256) se pinta de 2x1 en la vista. La vista útil es de unos 200x150 píxeles de juego. Hay que ver poco y moverse bien. |
| 4 u 8 colores en el Workbench | El significado nunca va solo en el color. Va en la forma, la letra o el tramado, como las marcas del margen de Forja. |
| 68020 a 14 MHz | Una imagen de 16x16 con máscara cuesta 1,6 ms (medido en Fragua). Repintar 100 sprites son 160 ms. No se repinta la vista entera al arrastrar. |
| 2 MB de chip y 4 de fast como mínimo de Forja | El editor carga las imágenes una vez y las comparte. Dice cuánta memoria usa la escena. |
| Ratón de dos botones, sin rueda en muchos | Todo lo de la rueda tiene tecla. Todo lo del botón derecho tiene otra vía, porque el botón derecho es el de los menús. |
| MUI 3.8 | Sin clases de fuera (ni NList ni Listtree). El árbol se pinta en un lienzo propio, como el panel del proyecto de Forja. |
| Disco lento, disquetes | Guardar es rápido y pequeño. No se escribe en disco sin que el usuario lo sepa, salvo en `T:` y `RAM:`. |

### 1.2 Diez principios

1. **Lo que se ve es lo que hay en el juego, y lo que no, se dice.** Si la vista va en modo Cajas o con colores
   aproximados, la barra de estado lo dice con una palabra: "Cajas", "Aprox." o "Fiel".
2. **Un sitio para cada cosa, y siempre el mismo.** Árbol a la izquierda, vista en el centro, inspector a la
   derecha, estado abajo. En pantalla pequeña cambia cuántas se ven, no dónde están.
3. **Primero lo corriente.** Cada lista (nodos, propiedades, eventos, acciones) enseña primero las 6 a 8 cosas más
   usadas. El resto está tras "Más...". Lo usado hace poco sube solo.
4. **Tres caminos para cada orden: ratón, tecla y menú.** El menú enseña la tecla. La ayuda corta (la burbuja de
   MUI, `mui_help`) también. Así quien empieza con el ratón aprende las teclas sin buscarlas.
5. **Teclas de una letra en la vista y en el árbol**, como en Sprites y Mapas, y las mismas donde significan lo
   mismo: G rejilla, C código, + y - zoom, Supr quitar, D duplicar. Con Amiga, las de siempre: S, Z, R, C, X, V, E.
6. **Nada se pierde.** Todo cambio se deshace. Quitar un nodo con hijos no pregunta: se deshace. Solo pregunta lo
   que no se puede deshacer (borrar un fichero del disco).
7. **Respuesta en menos de una décima, o aviso de que tarda.** Arrastrar mueve un marco, no la imagen. Al soltar,
   se pinta. Lo que tarda más de medio segundo enseña un medidor (`mui_gauge`) y se puede parar con Esc.
8. **Los números, siempre a la vista y editables.** Colocar con el ratón es rápido; afinar pide escribir "128".
   Cada cosa que se arrastra tiene su campo en el inspector, y cambia mientras se arrastra.
9. **Los errores hablan del juego, no del editor ni del compilador.** "El nodo Jugador no tiene forma de choque:
   no chocará con nada. [Añadir una caja]". Con el botón que lo arregla al lado.
10. **El código no es un castigo ni un secreto.** Se enseña desde el primer día, en una tecla (C). Quien no quiere
    verlo no lo ve. Quien quiere aprender tiene el mejor libro: su propio juego escrito en Dash.

### 1.3 Descubrible y rápido a la vez

| Para quien empieza | Para quien sabe |
|---|---|
| Plantillas con un juego que ya se mueve | Escena vacía con Amiga-N |
| Botones con icono y texto en la barra | Teclas de una letra |
| "Añadir nodo" con 8 nodos grandes y su frase | Escribir en el buscador: "ar" + Return = Area |
| Avisos con botón que arregla | Lista de avisos en la barra de estado, F8 va al siguiente |
| "¿Qué quieres que haga?" al añadir un nodo de cuerpo (pregunta por un comportamiento) | Se apaga en Preferencias |
| Ayuda corta al pasar el puntero | F1 abre la ficha de Fragua del nodo o la propiedad |
| Hoja de eventos | Script, con completado de la API de Fragua |

Regla: ninguna ayuda para principiantes añade un clic a quien sabe. Si lo añade, se puede apagar.

### 1.4 El lenguaje de la interfaz

- Verbos llanos: Añadir, Quitar, Duplicar, Mover, Probar, Jugar.
- Los nodos y las propiedades se enseñan con su nombre de la API (`Body`, `speed`) y, al lado y en tenue, su nombre
  en el idioma del usuario ("Cuerpo", "velocidad"). Motivo: lo que se ve en el inspector es lo que luego se escribe
  en el código. Quien solo quiere el castellano lo cambia en Preferencias ("Nombres: API / idioma / los dos").
- Una palabra para cada cosa, siempre la misma: "escena", "nodo", "comportamiento", "evento", "acción", "script",
  "recurso". Nunca "objeto" para un nodo en un sitio y "actor" en otro.

---

## 2. El editor de escenas

### 2.1 Qué es y cómo se abre

- La extensión `extensiones/Escenas`, con `tipos = .escena` y `nuevo = _Escena | escena | ...`.
- Un doble clic en un `.escena` del panel del proyecto la abre. Amiga-B en Forja ofrece "Escena".
- Una ventana MUI suya, con una pestaña por escena abierta (hasta 4, como Mapas).
- Se puede pedir "a pantalla entera" (`mui_window_fullscreen`) con F11 (propuesto). En 640x256 es lo normal.

### 2.2 Las zonas

```
+--------------------------------------------------------------------------------+
| Menús: Escena  Editar  Nodo  Ver  Juego  Ventana                               |
+--------------------------------------------------------------------------------+
| Barra: [Elegir][Mover][Girar][Escalar] | [Rejilla][Ajustar] | [Probar][Jugar]  |
+---------------+--------------------------------------------+-------------------+
| ARBOL         | VISTA                                      | INSPECTOR         |
|               |                                            |  Prop Comp Ev Scr |
|               |                                            |                   |
+---------------+                                            |                   |
| RECURSOS      |                                            |                   |
|               |                                            |                   |
+---------------+--------------------------------------------+-------------------+
| Estado: nodo elegido, x y, zoom, calidad, memoria, avisos                      |
+--------------------------------------------------------------------------------+
```

Las separaciones se arrastran (`mui_balance`) y su sitio se recuerda por tamaño de pantalla.

### 2.3 En 1280x1024 (RTG)

Todo a la vista. Fuente de 8 o de 11 puntos. La vista del juego cabe a 2x (640x512) con sitio de sobra.

```
+----------------------------------------------------------------------------------------------------------------+
| Escena  Editar  Nodo  Ver  Juego  Ventana                                                   nivel1.escena *    |
+----------------------------------------------------------------------------------------------------------------+
| [^Elegir Q][+Mover W][oGirar E][#Escalar R] | [Rejilla G 16][Iman S] | Capa:[Todas v] | Zoom 2x | [>Probar F6][>>Jugar F5] |
+-------------------------+----------------------------------------------------------+---------------------------+
| nivel1 | jugador | hud  |    0        64        128       192       256            | Jugador           (Body)  |
+-------------------------+  0 +---------------------------------------------+       | [Prop.][Comp.][Event.][Script] |
| Buscar: [           ]   |    | .   .   .   .   .   .   .   .   .   .   .   |       +---------------------------+
| v Nivel1        Node2D  |    |                                             |       | Nombre   [Jugador       ] |
|   > Mapa        TileMap | 64 | .   .   .  +----+   .   .   .   .   .   .   |       | Posición x[ 96] y[ 128]   |
|   v Jugador     Body  S |    |            |    |<- marco de la pantalla    |       | Capa     [ 2 ] [-][+]     |
|       Dibujo    AnimSpr |    | .   .   .  | o< |   .   .   .   .   .   .   |       | Visible  [x]              |
|       Caja      Shape   |128 |            +-##-+                           |       | Grupos   [jugador      +] |
|     Camara      Camera  |    | ############################   .   .   .   .|       |-- Body -------------------|
|   v Enemigos    Node2D  |    | ############################                |       | Sólido   [x]              |
|     > Bicho1  (escena)  |192 | .   .   .   .   .   .  #####################|       | Capa de choque [1][ ][ ][ ]|
|     > Bicho2  (escena)  |    |                        #####################|       | Choca con      [1][2][ ][ ]|
|   > Monedas     Node2D  |    +---------------------------------------------+       | Rebote   [==|-----]  0    |
|   > Marcador  (escena)  |                                                          |                           |
| [+ Nodo][Escena][Quitar]|    (reglas arriba y a la izquierda; el fondo fuera       | Avisos de este nodo: 0    |
+-------------------------+     de la escena, tramado)                               |                           |
| Recursos                |                                                          |                           |
| [Imag.][Mapas][Son.][Esc.]                                                         |                           |
| jugador.iff   32x32 x6  |                                                          |                           |
| bicho.iff     16x16 x4  |                                                          |                           |
| tiles.iff     16x16 x64 |                                                          |                           |
| [Nuevo][Editar][Traer]  |                                                          |                           |
+-------------------------+----------------------------------------------------------+---------------------------+
| Jugador  x 96 y 128 | puntero 140, 88 | 2x | Fiel | chip 212K fast 96K | 1 aviso (F8)                          |
+----------------------------------------------------------------------------------------------------------------+
```

La "S" tras `Body` dice que el nodo tiene script. Otras letras de la misma columna: "C" comportamientos, "E"
eventos, "!" aviso, "o" oculto, "#" bloqueado. Son letras, no colores: se leen con 4 colores.

### 2.4 En 640x256 (PAL, sin RTG)

Caben unas 28 líneas de texto de 8 píxeles. Quitando título, menús, barra y estado quedan unas 200 líneas de alto.
No caben tres columnas. Solución: **vista siempre, y un solo panel lateral que se turna**.

```
+------------------------------------------------------------------------------+
| nivel1.escena *                                           [Arbol][Insp][Rec] |
+------------------------------------------------------------------------------+
|[Q][W][E][R]|[G][S]|Capa:Todas|1x|[Probar][Jugar]                             |
+----------------------------------------------------+-------------------------+
|                                                    | Buscar:[              ] |
|   .   .   .   .   .   .   .   .   .   .   .   .    | v Nivel1         Node2D |
|                                                    |   > Mapa        TileMap |
|   .   .  +----+   .   .   .   .   .   .   .   .    |   v Jugador      Body S |
|          | o< |                                    |       Dibujo    AnimSpr |
|   .   .  +-##-+   .   .   .   .   .   .   .   .    |       Caja        Shape |
|   ##########################                       |     Camara       Camera |
|   ##########################  .   .   .   .   .    |   > Enemigos     Node2D |
|                                                    |   > Monedas      Node2D |
|   .   .   .   .   .   .   .   .   .   .   .   .    |                         |
|                                                    | [+Nodo][Escena][Quitar] |
+----------------------------------------------------+-------------------------+
| Jugador 96,128 | 140,88 | 1x Cajas | chip 212K | 1 aviso                     |
+------------------------------------------------------------------------------+
```

Reglas para la pantalla pequeña:
- **Tab** pasa el panel lateral de Árbol a Inspector y a Recursos. Mayúsculas+Tab, al revés. También los tres
  botones de arriba a la derecha.
- **Elegir un nodo en la vista no cambia el panel.** Un doble clic en un nodo (en la vista o en el árbol) pasa al
  Inspector. Así el panel no baila mientras se coloca.
- **Espacio** esconde y enseña el panel lateral: vista a todo el ancho (unos 300x190 píxeles de juego a 1x).
- La barra de botones lleva solo iconos de 12x12, como la zona de las extensiones. El texto sale en la burbuja.
- Las páginas del inspector son un `mui_cycle` de una línea, no cuatro pestañas: gastan menos alto.
- Una pantalla entrelazada (640x512) usa la disposición de 2.3 con menos ancho: árbol y recursos a la izquierda, y
  el inspector se turna con ellos solo si el ancho baja de 800.

Cuándo se usa cada disposición (propuesto): ancho de ventana menor de 800, o alto menor de 400: la pequeña. Si no,
la grande. El usuario puede forzar una en el menú Ver.

### 2.5 El árbol de nodos

Se pinta en un lienzo (`mui_canvas`), una línea por nodo: sangrado, triángulo de abrir o cerrar, icono de 8x8 del
tipo, nombre, tipo en tenue y letras de estado.

| Tarea | Ratón | Tecla | Notas |
|---|---|---|---|
| Añadir un nodo hijo del elegido | botón "+ Nodo" | A (o Amiga-A) | Abre "Añadir nodo" (2.5.1) |
| Añadir un nodo hermano | Mayúsculas + "+ Nodo" | Mayúsculas+A | |
| Instanciar una escena | botón "Escena", o arrastrarla desde Recursos al árbol o a la vista | I | Pide el `.escena`. |
| Elegir | clic | flechas arriba y abajo | Izquierda cierra, derecha abre, como en Forja |
| Elegir varios | Mayúsculas + clic (un tramo), Ctrl + clic (sueltos) | Mayúsculas + flechas | |
| Renombrar | doble clic lento, o clic en el nombre del elegido | F2 | F2 es renombrar también en Forja |
| Mover a otro padre | arrastrar sobre otro nodo | Amiga-X y Amiga-V sobre el nuevo padre | Mientras se arrastra, una raya dice dónde cae: entre dos (hermano) o un marco (hijo) |
| Reordenar entre hermanos | arrastrar entre dos | Alt + arriba / abajo | Alt + flechas ya mueve fotogramas en Sprites |
| Sacar un nivel / meter en el de encima | | Alt + izquierda / derecha | |
| Duplicar | | D (o Amiga-D) | El duplicado se llama "Bicho2", "Bicho3"... |
| Quitar | botón "Quitar" | Supr | Sin preguntar. Se deshace. |
| Copiar, cortar, pegar | menú Editar | Amiga-C, X, V | Entre escenas abiertas también |
| Ocultar en el editor / bloquear | clic en la columna de letras | H / L | Bloqueado: no se elige en la vista |
| Buscar | campo "Buscar" | / (barra) o Amiga-F | Filtra por nombre, por tipo ("t:area") o por grupo ("g:enemigos") |
| Abrir la escena de una instancia | doble clic en su icono | Return | Se abre en otra pestaña |
| Convertir una rama en escena | menú Nodo | | "Guardar rama como escena...": la rama pasa a ser una instancia |
| Hacer local una instancia | menú Nodo | | Copia sus nodos aquí. Avisa de que deja de seguir a la escena. |
| Cambiar el tipo de un nodo | menú Nodo | | Solo entre tipos parecidos (Sprite a AnimatedSprite, Area a Body). Lo que no cabe se enseña antes de aceptar. |
| Menú del nodo | botón derecho sobre el nodo (`mui_context_menu_begin`) | M | Las mismas órdenes del menú Nodo |

Sobre el botón derecho: en el Amiga abre los menús de la ventana. MUI deja poner un menú de contexto sobre un
objeto. Se usa, pero nada depende de él: todo está también en el menú Nodo y con tecla.

Sobre arrastrar: `input_drag` da problemas en un lienzo con búfer (bitácora de Forja). El árbol va en un lienzo sin
búfer, y todo arrastre tiene su tecla. Si el arrastre falla en una versión de MUI, el editor sigue siendo usable.

#### 2.5.1 "Añadir nodo"

Una ventanita, no un menú: tiene que caber una frase por nodo.

```
+- Añadir nodo a "Nivel1" ------------------------------------+
| Buscar: [bo            ]                                    |
| Corrientes                                                  |
|  [o] Sprite          Una imagen.                            |
|  [O] AnimatedSprite  Una imagen con animaciones.            |
|  [#] Body            Algo que se mueve y choca.             |
|  [~] Area            Una zona que nota quién entra.         |
|  [=] TileMap         Un mapa de tiles.                      |
|  [T] Label           Un texto: marcador, vidas.             |
|  [>] Camera          Sigue a un nodo.                       |
|  [.] Node2D          Un punto. Sirve de carpeta.            |
| Más... (Shape, Timer, AudioPlayer, Particles, Button...)    |
| ----------------------------------------------------------- |
| Body: se mueve con move_and_slide y choca con el mapa y     |
| con otros cuerpos. Necesita un hijo Shape.                  |
|                        [ Añadir (Return) ]   [ Cancelar ]   |
+-------------------------------------------------------------+
```

- Se abre con el cursor en "Buscar". Escribir filtra. Return añade el primero. Flechas eligen.
- La frase de abajo sale de `api/fragua.json`.
- **Nodos con lo que necesitan (propuesto):** al añadir un `Body` o un `Area`, el editor añade ya un hijo `Shape`
  con una caja del tamaño del primer `Sprite` hermano o hijo. Motivo: el error más corriente en Godot es el cuerpo
  sin forma (de memoria). Se deshace en un solo paso con el nodo.
- **"¿Qué quieres que haga?" (propuesto, se apaga):** tras añadir un `Body`, una fila de botones: "Jugador de
  plataformas", "Se mueve en 8 direcciones", "Bala", "Patrulla", "Nada todavía". Pone el comportamiento.

### 2.6 La vista de la escena

#### 2.6.1 Qué se ve

- El **marco de la pantalla** del juego (por defecto 320x256): un rectángulo. Fuera de él, fondo tramado.
- El **marco de la cámara** si hay `Camera` con límites: otro rectángulo, a rayas.
- Los nodos visuales, en el orden en que los pintará Fragua: por capa (`z`) y, dentro, por orden en el árbol.
- El nodo elegido: marco con ocho asas y un punto en su origen. Sus hijos `Shape`, a trazos.
- Las formas de choque de todos, si "Ver > Formas" está puesto (tecla F).
- Reglas arriba y a la izquierda, en píxeles de juego (se quitan en 640x256 para ganar sitio).
- Los nodos sin dibujo (`Timer`, `AudioPlayer`, `Node2D`) no se ven salvo con "Ver > Nodos sin dibujo": un icono de
  8x8 en su posición.

#### 2.6.2 Las tres calidades

| Calidad | Qué pinta | Cuándo |
|---|---|---|
| **Cajas** | Un marco por nodo con su nombre dentro, el mapa como rejilla con las celdas llenas tramadas | Siempre posible. Por defecto con menos de 16 colores, o si pintar tarda más de 300 ms (por medir). |
| **Aproximada** | Las imágenes con los lápices que la pantalla da (`ObtainBestPen`), como hace Sprites | Por defecto en pantallas de 16 a 256 colores |
| **Fiel** | Las imágenes con sus colores de verdad | RTG con color de 15 bits o más |

Tecla: K recorre las tres. La barra de estado dice cuál está puesta.

La vista no usa sprites de hardware, scroll de hardware ni copper: es una ventana de MUI. Lo que eso no enseña
(luces, colores exactos, scroll) se ve con **Probar parada** (2.10).

#### 2.6.3 Herramientas

Cuatro, como en Godot (de memoria: Q, W, E, R son las suyas):

| Herramienta | Tecla | Qué hace arrastrando |
|---|---|---|
| Elegir | Q | Clic elige. Arrastrar en vacío elige con caja. Arrastrar un nodo elegido lo mueve. |
| Mover | W | Mueve aunque se pinche fuera del nodo. Mayúsculas: solo en un eje. |
| Girar | E | Solo en los nodos que giran (ver abajo). |
| Escalar | R | Asas. Mayúsculas: mantiene la proporción. |

Además, sin cambiar de herramienta:

| Tarea | Ratón | Tecla |
|---|---|---|
| Mover 1 píxel | | flechas |
| Mover una celda de la rejilla | | Mayúsculas + flechas |
| Desplazar la vista | arrastrar con el botón del medio, o Alt + arrastrar; rueda (vertical), Mayúsculas + rueda (horizontal) | Ctrl + flechas |
| Zoom | Ctrl + rueda | + y -; 1, 2, 4 ponen 1x, 2x, 4x; 0 encaja la escena entera |
| Centrar en el elegido | doble clic en el árbol | Z (de "zona") |
| Elegir el de debajo | Alt + clic repetido | Tab no (es del panel): coma y punto, nodo anterior y siguiente |
| Colocar un recurso | arrastrarlo desde Recursos | Return en Recursos: lo pone en el centro de la vista |
| Sellar copias | con un nodo elegido, Ctrl + clic pone un duplicado ahí | |
| Cancelar lo que se arrastra | | Esc |

- **Girar y escalar con honradez.** Fragua mueve en píxeles enteros y la escala es entera. Un BOB no gira en un
  Amiga sin precalcular. Por eso:
  - Escalar: en `Shape`, `Area`, `Label` y marcos, libre. En sprites, solo 1x, 2x y voltear (H y V).
  - Girar: solo en pasos de 90 grados en sprites (propuesto, si Fragua lo da), y libre en nodos que lo admitan
    (un punto de aparición con dirección, un emisor de partículas). En los demás, la herramienta sale apagada, y la
    burbuja dice por qué: "Un sprite del Amiga no gira. Dibuja los fotogramas girados en el editor de sprites."
  - En el 3D futuro, girar y escalar son libres: por eso las herramientas existen ya.
- **Zoom:** enteros (1x, 2x, 4x, 8x) y "encajar". En pantallas con píxel alto (640x256), "1x" es 2x1. La mitad
  (para ver la escena entera) solo en modo Cajas: reducir imágenes cuesta CPU y se ve mal.

#### 2.6.4 Rejilla y ajuste

- **Rejilla** (G): se ve o no. Tamaño en la barra (8, 16, 32 o el que se escriba). Si la escena tiene un `TileMap`,
  la rejilla toma el lado de sus tiles al crearla.
- **Imán** (S, de "snap"): al mover, el origen del nodo cae en la rejilla. Con Ctrl pulsado se invierte mientras
  dura el arrastre: si el imán está puesto, lo quita; si no, lo pone.
- **Ajuste a otros nodos (fase posterior):** bordes y centros de los hermanos, con una raya guía.
- **Ajuste al suelo (propuesto):** tecla Fin baja el nodo hasta el primer tile sólido de debajo. Para plataformas.
- Los valores de rejilla e imán se guardan en la escena (parte "editor" del fichero, que el conversor no mira).

#### 2.6.5 Capas

"Capa" es el `z` de Fragua: el orden de pintado.

- El desplegable "Capa" de la barra filtra la vista: "Todas", o una. Las demás se ven tramadas y no se eligen.
- Av Pág y Re Pág suben y bajan de capa el nodo elegido.
- Las capas pueden llevar nombre en la escena ("fondo", "juego", "delante", "interfaz"): es más claro que un
  número. En el código, constantes: `Z_JUEGO = 2`.
- Los nodos de interfaz (`ui`, los que no se mueven con la cámara) van en una capa llamada "interfaz" y se editan
  contra el marco de la pantalla, no contra el mundo. Con "Capa: interfaz", la vista enseña solo el marco de la
  pantalla y esos nodos. Evita el lío de un marcador "perdido" en la coordenada 0,0 de un nivel enorme.

#### 2.6.6 El mapa dentro de la escena

- Un `TileMap` se ve en la vista, pero **no se pinta aquí**. Un doble clic abre el editor de Mapas con ese `.fmap`.
  Al guardar allí, la vista se refresca (suceso `GUARDADO` de Forja).
- Motivo: un solo editor de mapas, con todas sus herramientas, mejor que dos a medias.
- Los objetos de la capa de objetos del mapa (`OBJS`: jugador, enemigo, moneda) se ven en la vista como nodos
  "del mapa", con un icono propio. En el inspector de la escena se dice qué escena se instancia por cada clase:
  "enemigo → bicho.escena". Es la forma rápida de poblar un nivel de tiles, como en Tiled y RPG Maker (de memoria).

### 2.7 El inspector

Cuatro páginas por nodo: **Propiedades**, **Comportamientos**, **Eventos**, **Script**. Esta sección trata la
primera; las otras, la sección 3.

#### 2.7.1 Estructura

- Arriba, lo común: nombre, posición, capa, visible, grupos.
- Debajo, un bloque por lo que el nodo es. Un `Body` enseña "Node2D" y "Body". Los bloques se pliegan y recuerdan
  su estado por tipo.
- Cada fila: etiqueta, control y, si el valor no es el de fábrica, una marca "*" a la izquierda. Un clic en la
  marca lo devuelve al de fábrica.
- En una **instancia** de escena, las propiedades cambiadas respecto a la escena original llevan ">" en vez de
  "*". Un clic en ">" vuelve al valor de la escena. Así se ve qué tiene de especial este enemigo.
- Con **varios nodos elegidos**, se enseñan las propiedades comunes. Donde difieren, el campo dice "varios".
  Escribir cambia todos.
- F1 sobre una fila abre su ficha en la ayuda de Fragua.

#### 2.7.2 Un control por tipo de propiedad

Los tipos salen de `api/fragua.json`. El editor tiene un control para cada uno:

| Tipo | Control | Detalle |
|---|---|---|
| Entero con rango | Campo + deslizador (`mui_slider`) | Flechas arriba y abajo en el campo: de 1 en 1; con Mayúsculas, de 10 en 10. Fuera de rango: el campo vuelve al límite y la barra de estado lo dice. |
| Entero sin rango | Campo con [-][+] | Admite cuentas: "128+16" (propuesto) |
| `Fixed` (velocidades) | Campo con decimales: "2.5" | Se enseña en "píxeles por fotograma", con la unidad escrita |
| Sí o no | Casilla | |
| Uno de varios | `mui_cycle` | |
| Texto | Campo | |
| Posición, tamaño | Dos campos en una fila: x, y | El formato del fichero admite tres (sección 7) |
| Color | Un cuadro con el color; clic abre la **paleta de la escena** | Es un lápiz de la paleta, no un RGB: en un Amiga los colores son de la paleta. Abajo, "Editar la paleta...". |
| Imagen | Miniatura + nombre + [...] + [Editar] | [...] abre el selector de recursos (2.8). [Editar] abre Sprites. |
| Animación | `mui_cycle` con las animaciones de la imagen | Con un botón de reproducir en la miniatura |
| Sonido | Nombre + [...] + [> Oír] | Oír lo toca en el momento |
| Mapa | Nombre + [...] + [Editar] | |
| Escena | Nombre + [...] + [Abrir] | |
| Nodo de esta escena | Nombre + [Elegir] | [Elegir]: el siguiente clic en el árbol o en la vista lo toma. Esc cancela. Se guarda como ruta (`"../Jugador"`). |
| Grupo | Campo con lista de los grupos que ya hay en el proyecto | Evita "enemigos" y "enemigo" |
| Bits (capas de choque) | 8 casillas en fila, con nombre en la burbuja | Los nombres de las capas de choque, en los ajustes del proyecto |
| Tecla o acción de entrada | `mui_cycle` con las acciones del proyecto + "Nueva..." | Ver 2.11 |
| Variable del juego | `mui_cycle` con las variables + "Nueva..." | `game_get("score")` |
| Lista | Filas con [+] y [-] | Animaciones, puntos de un camino |

#### 2.7.3 Avisos del nodo

Abajo del inspector, los avisos del nodo elegido, con su arreglo:

| Aviso | Botón |
|---|---|
| "Body sin Shape: no chocará." | [Añadir una caja] |
| "Sprite sin imagen." | [Elegir imagen] |
| "Falta el fichero bicho.iff." | [Buscar...] |
| "Platformer y EightWay mueven los dos: manda el de arriba." | [Quitar EightWay] |
| "Camera sin nodo que seguir." | [Elegir nodo] |
| "Dos nodos se llaman Moneda bajo el mismo padre." | [Renombrar] |

La barra de estado cuenta los de toda la escena. F8 va al siguiente (como los errores en Forja).

### 2.8 Recursos

Una página por clase: **Imágenes**, **Mapas**, **Sonidos**, **Escenas**. Más adelante, **Modelos** (3D).

- Lista lo que hay en el cajón del proyecto y los de dentro, por su extensión. No hay "importar": un fichero del
  cajón es un recurso. Como en Godot (de memoria), y al revés que en GameMaker.
- Cada fila: miniatura (en Fiel y Aproximada; en Cajas, solo el nombre), nombre y un dato: "32x32 x6", "40x16
  tiles", "0,8 s", "12 nodos".
- Un clic lo elige y enseña su vista previa abajo. Espacio en un sonido lo toca.
- Botones: [Nuevo] (abre Sprites, Mapas o una escena nueva, según la página), [Editar] (lo abre en su editor),
  [Traer...] (copia un fichero de fuera al cajón del proyecto).
- **Arrastrar a la vista** crea el nodo que toca: una imagen crea un `Sprite` (o `AnimatedSprite` si tiene varias
  animaciones), un mapa un `TileMap`, un sonido un `AudioPlayer`, una escena una instancia.
- **Arrastrar a un campo del inspector** lo pone ahí.
- Sin arrastrar: Return lo coloca; en el selector del inspector ([...]) sale esta misma lista en una ventanita con
  buscador.
- "Dónde se usa" (tecla U): los nodos de las escenas del proyecto que usan el recurso. Antes de borrar o renombrar.
- Las miniaturas se guardan en `T:` y se rehacen solo si el fichero cambió (por fecha). En un 68020 no se generan
  cien miniaturas de golpe: se hacen las que se ven.

### 2.9 Ajustes del juego

Una ventana ("Juego > Ajustes del juego..."), que se guarda en `juego.fragua` (propuesto), junto al `.forja`:

- Pantalla: ancho, alto, colores (planos), PAL o NTSC, proyección por defecto.
- Escena inicial.
- Paleta del juego (de un IFF o editada aquí).
- **Acciones de entrada:** "izquierda", "derecha", "saltar", "disparar"... con sus teclas y el joystick. Vienen
  puestas las de `fragua_default_actions()`.
- **Variables del juego:** nombre y valor inicial ("puntos" 0, "vidas" 3). Son las de `game_get`/`game_set`.
- Nombres de las capas de choque (8) y de las capas de dibujo.
- Escenas siempre cargadas (autoload), si las hay.
- Máquina objetivo: A1200 (por defecto), A500, RTG. Solo cambia los avisos de presupuesto (5.2).

### 2.10 Ejecutar y volver

| Orden | Tecla | Qué hace |
|---|---|---|
| **Jugar** | F5, Amiga-E | Compila y ejecuta el juego desde la escena inicial |
| **Probar esta escena** | F6 | Compila y ejecuta esta escena sola |
| **Probar parada** | F7 | Compila y abre esta escena en la pantalla de verdad, sin lógica (`set_paused`): se ven los sprites de hardware, la paleta y las luces. Las flechas mueven la cámara. Es "la vista fiel" para quien no tiene RTG. |
| **Probar con formas** | Mayúsculas + F6 | Como F6, con el dibujo de depuración encendido (4.9) |
| Parar | Esc en el juego (lo trae la plantilla), o Amiga-. en el editor | |

F5 y F6 son las de Godot (de memoria). Amiga-E es la de Forja, Sprites y Mapas.

Qué pasa, paso a paso:
1. El editor genera el `.dash` de las escenas cambiadas (3.6). Si hay avisos graves (falta un fichero), pregunta:
   "Hay 1 aviso. [Verlo] [Jugar igual]".
2. **Guarda la escena.** Como Godot al ejecutar (de memoria). Se puede cambiar en Preferencias a "preguntar". La
   pila de deshacer no se toca.
3. Pide a Forja `EJECUTAR` del programa. La barra de estado dice "Compilando..." con medidor, y luego "Jugando".
4. El juego abre su pantalla, delante.
5. Al salir del juego, la ventana del editor vuelve delante, **tal como estaba**: mismo nodo elegido, mismo zoom,
   misma página. La barra dice: "Jugaste 42 s. Sin errores." o el error (5.4).

Tiempos objetivo (por medir): de F6 a ver el juego, menos de 15 s en un A1200 con disco duro para una escena de 20
nodos; menos de 3 s en un 68040.

Para que el paso 1 sea rápido: solo se regenera el `.dash` de las escenas que cambiaron, y la compilación de Dash
es del programa entero (hoy no hay otra). Si resulta lenta, es un encargo para Dash, no un parche del editor.

**Lo cambiado mientras se juega no vuelve al editor** en las primeras fases. Más adelante (fase 6), el árbol en
vivo deja ver valores, no cambiarlos.

### 2.11 Deshacer y rehacer

- Amiga-Z y Amiga-R, como en todo Forja. Sin límite hasta cerrar la escena (con tope de memoria: 5.3).
- Cada escena abierta tiene su pila.
- Un paso es **una intención del usuario**, no un cambio interno:
  - un arrastre entero (no cada píxel);
  - una ráfaga de flechas seguidas sobre el mismo nodo, hasta medio segundo de pausa;
  - escribir en un campo, al salir de él o con Return;
  - añadir un `Body` con su `Shape` automática;
  - pegar diez nodos.
- El menú Editar dice qué se va a deshacer: "Deshacer: mover Jugador", "Rehacer: añadir Area".
- Deshacer **lleva la vista a lo que cambia**: elige el nodo y, si hace falta, cambia de página. Sin eso, en
  640x256 se deshace algo que no se ve.
- Cubre todo lo de la escena: árbol, propiedades, comportamientos, eventos. No cubre lo de otros editores (el
  mapa, el sprite, el script): cada uno tiene su deshacer.
- La marca de "cambiado" (el `*` del título) sabe volver: si se deshace hasta el punto guardado, se quita.
- **Historial** (fase posterior): una lista de los pasos, con clic para volver a uno. Como el de Photoshop o el de
  Godot 4 (de memoria).

---

## 3. Comportamientos, eventos y acciones: programar sin programar

### 3.1 La escalera

```
  4. Script        código Dash tuyo, en tu fichero            (como Godot)
  3. Eventos       "cuando pasa X, haz Y", en filas           (como GameMaker y Construct)
  2. Comportamientos   piezas listas con propiedades          (como Construct)
  1. Propiedades   lo que el nodo es
```

- Cada escalón es una página del inspector, en ese orden.
- Los cuatro conviven en el mismo nodo. Un jugador puede tener `Platformer` (2), dos eventos para las monedas (3)
  y un script para el doble salto (4).
- En Fragua ya encaja: un nodo tiene una lista de comportamientos (`n.behaviors`) y un script (`n.script`), y los
  dos cumplen la interfaz `Script`. La hoja de eventos se convierte en un comportamiento más.
- Orden en cada fotograma, fijo y dicho en la ayuda: comportamientos de arriba abajo, luego la hoja de eventos,
  luego el script. El script manda: es el último en tocar.

### 3.2 Comportamientos

#### 3.2.1 Cómo se ve

```
+ Jugador (Body) ------------------------------+
| [Prop.][Comp.][Event.][Script]               |
+----------------------------------------------+
| v Platformer                     [x] [^][v][-]|
|     Velocidad     [==|----] 2.0  px/fotograma |
|     Aceleración   [=|-----] 0.25              |
|     Salto         [===|---] 5.0               |
|     Gravedad      [=|-----] 0.3               |
|     Salto doble   [ ]                         |
|     Izquierda     [izquierda v]               |
|     Derecha       [derecha   v]               |
|     Saltar        [saltar    v]               |
| > Health   vida 3                [x] [^][v][-]|
| > Blink    apagado               [ ] [^][v][-]|
|                                               |
| [+ Comportamiento]              [Ver código C]|
+----------------------------------------------+
```

- Cada comportamiento es un bloque plegable. Plegado, enseña un resumen de una línea.
- La casilla lo enciende y lo apaga sin quitarlo. Útil para probar.
- [^][v] cambian el orden. [-] lo quita.
- "+ Comportamiento" abre una ventanita como "Añadir nodo": buscador, lista con una frase y, abajo, lo que necesita
  ("Platformer necesita un Body"). **Solo se ofrecen los que valen para este tipo de nodo.** Los demás salen en
  tenue, con el motivo.
- Los deslizadores tienen el rango de `api/fragua.json`. Se puede escribir un valor fuera del rango del deslizador
  si el rango es "aconsejado" y no "obligado".
- **Probar al momento (propuesto, fase 5):** con F6 en marcha, cambiar un deslizador de un comportamiento manda el
  valor al juego por su puerto de depuración. Es lo que más ayuda a afinar un salto. Pide el puerto de 4.9.

#### 3.2.2 Tabla mínima de comportamientos

Los doce primeros están en el plan de Fragua (fase E). Los marcados (propuesto) los pide este diseño para cubrir
todos los géneros de la sección 4.

| Comportamiento | Vale en | Qué hace | Propiedades principales | Género |
|---|---|---|---|---|
| `Platformer` | Body | Anda, salta y cae con gravedad | velocidad, aceleración, salto, gravedad, acciones | Plataformas |
| `EightWay` | Body | Se mueve en 4 u 8 direcciones | velocidad, direcciones (4/8), acciones | Cenital, matamarcianos |
| `GridMove` (propuesto) | Body, Node2D | Se mueve de casilla en casilla | lado de la casilla, fotogramas por paso, choca con el mapa | RPG, puzle, isométrico |
| `Vehicle` (propuesto) | Body | Acelera, frena, inercia, marchas | aceleración, frenada, velocidades máximas, rozamiento | Carreras de lado |
| `Bullet` | Body, Area | Va recto a una velocidad | velocidad, ángulo o dirección, vida | Disparos |
| `Shooter` (propuesto) | Node2D | Crea una escena cada cierto tiempo o al pulsar | escena, cadencia, acción, desvío | Disparos |
| `Spawner` (propuesto) | Node2D | Crea escenas en oleadas | escena, cada cuánto, cuántas, zona | Matamarcianos |
| `Follow` | Body, Node2D | Sigue a un nodo | a quién, velocidad, distancia mínima | Enemigos, rival |
| `Patrol` | Body | Va y vuelve; gira en pared o borde | velocidad, gira en borde | Enemigos |
| `Path` (propuesto) | Node2D | Recorre una lista de puntos | puntos, velocidad, bucle | Enemigos, plataformas móviles |
| `BounceEdges` | Body | Rebota en los bordes | bordes de pantalla o del mapa | Pong, rompeladrillos |
| `Wrap` | Node2D | Sale por un lado y entra por el otro | | Asteroides |
| `DestroyOffscreen` | Node2D | Se quita al salir de la pantalla | margen | Balas |
| `Scroller` (propuesto) | Camera | Avanza sola | velocidad x, y | Matamarcianos |
| `Health` | cualquiera | Vida, daño, invencible un rato | vida, fotogramas invencible | Todos |
| `Pickup` | Area | Al tocarlo quien toca: suma y se quita | variable, cuánto, sonido, grupo | Monedas |
| `Draggable` | Area | Se arrastra con el ratón | ajusta a rejilla | Puzle |
| `Blink` | Sprite | Parpadea | cada cuánto, cuánto dura | Daño |
| `Sine` (propuesto) | Node2D | Sube y baja o va y viene | eje, amplitud, periodo | Plataformas, enemigos |
| `IsoMove` (propuesto) | Body | Como EightWay, por los ejes del rombo | velocidad | Isométrico |
| `Button` (propuesto) | Label, Sprite | Se elige con flechas y fuego o con clic | siguiente, anterior | Menús |

Señales que dan (para la hoja de eventos): `Health` da "hurt" y "died"; `Pickup` da "picked"; `Platformer` da
"jumped" y "landed"; `Vehicle` da "landed" con la velocidad de caída; `Path` da "arrived"; `Button` da "pressed".

#### 3.2.3 Comportamientos del usuario

Un script del usuario que cumple `Script` y declara propiedades exportadas se puede **guardar como
comportamiento** del proyecto. Sale en la lista con los de fábrica. Así el que sabe programar hace piezas para el
que no. La forma de declarar las propiedades (un comentario con formato o un fichero al lado) la decide Fragua;
al editor le basta el mismo esquema que `api/fragua.json`.

### 3.3 Eventos y acciones

#### 3.3.1 El modelo

- Una **hoja** por nodo. Es una lista de **filas**.
- Una fila: **un evento**, **cero o más condiciones** y **una o más acciones**.
- Se lee en voz alta: "Cuando el Jugador choca con uno de 'enemigos', y vidas es mayor que 0: resta 1 a vidas,
  toca 'ay.8svx' y parpadea."
- A medio camino:
  - De GameMaker (de memoria): los eventos son del objeto y están nombrados ("Crear", "Paso", "Choque con").
  - De Construct (de memoria): filas con condiciones a un lado y acciones al otro, que se leen como frases.
  - De Godot: los eventos entre nodos son señales. Una fila "Cuando Moneda emite picked" es un `connect`. Y la
    acción puede ser "llamar a una función de mi script".
- **No hay**: expresiones largas, bucles ni variables locales. Quien los necesita está pidiendo el escalón 4, y
  el editor se lo pone a un clic (3.7).

#### 3.3.2 Cómo se ve

En pantalla grande, la página Eventos se queda estrecha. Por eso tiene dos formas:

**En el inspector** (resumen, una línea por fila):

```
| [Prop.][Comp.][Event.][Script]               |
+----------------------------------------------+
| 1 Choca con enemigos  > vidas-1, sonar, +1   |
| 2 Entra Area Meta     > cambiar escena       |
| 3 vidas llega a 0     > cambiar escena       |
| 4 Al empezar          > música               |
|                                              |
| [+ Evento]   [Abrir la hoja (Return)]  [C]   |
```

**La hoja abierta**: ocupa el sitio de la vista (no es otra ventana). Esc vuelve a la vista.

```
+- Eventos de Jugador ------------------------------------------- [Esc: volver a la vista] -+
| 1  CUANDO  choca con un nodo del grupo [enemigos]                              [x][^][v][-]|
|    Y SI    variable [vidas] [>] [0]                                                  [+ Y] |
|    HAZ     restar [1] a la variable [vidas]                                                |
|            tocar el sonido [ay.8svx]                                                       |
|            encender [Blink] durante [50] fotogramas                              [+ Acción]|
|--------------------------------------------------------------------------------------------|
| 2  CUANDO  entra en el área [Meta]                                             [x][^][v][-]|
|    HAZ     cambiar a la escena [nivel2.escena]                                   [+ Acción]|
|--------------------------------------------------------------------------------------------|
| 3  CUANDO  la variable [vidas] llega a [0]                                     [x][^][v][-]|
|    HAZ     cambiar a la escena [fin.escena]                                      [+ Acción]|
|--------------------------------------------------------------------------------------------|
| [+ Evento (N)]                                         [Ver código (C)] [Pasar a script...]|
+--------------------------------------------------------------------------------------------+
| # fila 1                                                                                   |
| if name == "body_entered" and node_by_id(data).is_in_group("enemigos")                     |
|     if game_get("vidas") > 0                                                               |
|         game_add("vidas", -1)                                                              |
+--------------------------------------------------------------------------------------------+
```

- Lo que va entre corchetes es un valor: un clic lo edita con el control de su tipo (los de 2.7.2).
- La franja de abajo enseña el código de la fila elegida. Se quita con C. Es el mejor profesor: cambia el valor
  en la fila y cambia el número en el código.
- En 640x256, la hoja ocupa toda la ventana menos la barra de estado, y la franja de código empieza cerrada.
- Teclas: flechas mueven entre filas y partes; Return edita; N evento nuevo; A acción nueva en la fila; Y
  condición nueva; Supr quita; Alt + arriba y abajo reordenan; D duplica la fila; Amiga-C/X/V copian filas (también
  a otro nodo); espacio enciende o apaga la fila.

#### 3.3.3 Añadir un evento

Dos pasos, cada uno una lista con buscador:

```
+- Cuando... -------------------------+      +- Haz... ---------------------------+
| Buscar: [          ]                |      | Buscar: [          ]               |
| Corrientes                          |      | Corrientes                         |
|   Al empezar                        |      |   Sumar a una variable             |
|   Se pulsa una acción               |      |   Tocar un sonido                  |
|   Choca con...                      |      |   Quitar este nodo                 |
|   Entra en un área                  |      |   Crear una escena aquí            |
|   Pasa un tiempo                    |      |   Cambiar de escena                |
|   Una variable llega a...           |      |   Poner una animación              |
| Entrada >  Choques >  Tiempo >      |      | Nodo > Movimiento > Variables >    |
| Variables >  Nodo >  Señales >      |      | Sonido > Escena > Dibujo > Script >|
+-------------------------------------+      +------------------------------------+
```

- "Choca con..." pregunta enseguida con qué: un grupo, un nodo o "cualquiera".
- Tras elegir el evento se abre "Haz..." sin más clics: un evento sin acción no sirve de nada.
- **Atajo desde las señales (propuesto):** en la página Eventos de un nodo, "+ Evento" ofrece primero las señales
  que dan sus hijos y sus comportamientos. Un jugador con `Health` ve arriba "Health: se queda sin vida".
- **Atajo desde la vista:** con dos nodos elegidos, menú Nodo > "Cuando se tocan...": crea la fila en el primero.

#### 3.3.4 Tabla mínima de eventos

| Grupo | Evento | Parámetros | En Fragua |
|---|---|---|---|
| Nodo | Al empezar | | `_ready` |
| Nodo | En cada fotograma | | `_physics_process` |
| Nodo | Al quitarse | | señal al salir del árbol (propuesto) |
| Entrada | Se pulsa / se suelta / está pulsada una acción | acción | `action_just_pressed`, `_released`, `_pressed` |
| Entrada | Clic del ratón sobre el nodo | | (propuesto) |
| Choques | Choca con | grupo, nodo o cualquiera | `body_entered`, `area_entered` |
| Choques | Deja de tocar | grupo, nodo o cualquiera | `body_exited` |
| Choques | Toca el suelo / una pared / el techo | | `on_floor`, `on_wall`, `on_ceiling`; "landed" |
| Choques | Pisa un tile de tipo | sólido, escalera, daño... | `tile_at` |
| Tiempo | Cada cierto tiempo | segundos | un `Timer` que el editor añade solo |
| Tiempo | Pasado un tiempo desde que empieza | segundos | `Timer` de una vez |
| Dibujo | Acaba la animación | cuál | `animation_finished` |
| Dibujo | Sale de la pantalla / entra | | (propuesto; hoy `DestroyOffscreen` lo sabe) |
| Variables | Una variable llega a / pasa de / baja de | variable, valor | comparación al cambiar (propuesto: señal "changed" de `game_set`) |
| Señales | Un nodo emite una señal | nodo, señal | `connect` + `_signal` |
| Señales | Un comportamiento avisa | el suyo o el de un hijo | `_signal` |

Condiciones ("Y si"): comparar una variable; el otro nodo está en un grupo; el nodo toca el suelo; una acción
está pulsada; al azar, 1 de cada N; la animación actual es; una propiedad del nodo comparada con un valor.
"Si no" (una rama alternativa por fila) entra en la fase siguiente, no en la primera.

#### 3.3.5 Tabla mínima de acciones

| Grupo | Acción | Parámetros | En Fragua |
|---|---|---|---|
| Nodo | Quitar este nodo / otro nodo / el que me tocó | | `queue_free` |
| Nodo | Mostrar / ocultar | nodo | `visible` |
| Nodo | Meter en / sacar de un grupo | grupo | `add_to_group` |
| Nodo | Encender / apagar un comportamiento | cuál, cuánto tiempo | (propuesto) |
| Movimiento | Poner en una posición | x, y, o "donde está" otro nodo | `set_pos` |
| Movimiento | Mover | dx, dy | |
| Movimiento | Poner la velocidad | vx, vy | `body.vx`, `body.vy` |
| Movimiento | Saltar | fuerza | |
| Movimiento | Parar | | |
| Movimiento | Ir suave a un sitio | x, y, fotogramas, curva | `tween_ease` |
| Variables | Poner / sumar / restar | variable, valor | `game_set`, `game_add` |
| Variables | Poner una propiedad de un nodo | nodo, propiedad, valor | `fragua_prop_set` |
| Sonido | Tocar un sonido | fichero | `play_sound` |
| Sonido | Poner / parar la música | fichero | `play_music`, `stop_music` |
| Escena | Cambiar de escena | escena | `change_scene` |
| Escena | Volver a empezar esta escena | | `change_scene` con la misma |
| Escena | Crear una escena | escena, dónde, dentro de qué nodo | instanciar + `add_child` |
| Escena | Pausar / seguir | | `set_paused` |
| Escena | Salir del juego | | `quit` |
| Dibujo | Poner una animación | cuál | `play` |
| Dibujo | Poner un texto | nodo Label, texto o variable | `set_text`, `bind_label` |
| Dibujo | Soltar partículas | nodo Particles | `fragua_particles_burst` |
| Dibujo | Sacudir la cámara | fuerza, fotogramas | (propuesto) |
| Tiempo | Arrancar / parar un temporizador | nodo Timer | `start`, `stop` |
| Señales | Emitir una señal | nombre, dato | `emit` |
| Partida | Guardar / cargar la partida | | (plan de Fragua, sin hacer) |
| Script | **Llamar a una función de mi script** | función | llamada directa |

"Esperar N segundos" entre dos acciones no está: en código compilado sin corrutinas obliga a partir la fila en
dos y un temporizador, y el código que sale deja de parecerse a la fila. En su lugar: el evento "Pasado un tiempo"
y la acción "Arrancar un temporizador". Se explica en la ayuda con un ejemplo. Si en las pruebas con usuarios se
pide mucho, se añade generando el temporizador a la vista (como un nodo `Timer` que el usuario ve aparecer).

### 3.4 Variables del juego

- Se crean donde se usan: en cualquier desplegable de variable, "Nueva...". Nombre y valor inicial.
- Se ven todas en "Juego > Ajustes del juego > Variables".
- Un `Label` tiene la propiedad "Enseña la variable": elegir "puntos" hace el marcador. Sin eventos ni código.
- Son enteros. Para textos y listas: script.
- Variables **del nodo** (la vida de cada enemigo): las da un comportamiento (`Health`) o el script. En la primera
  versión no hay variables de nodo sueltas en la hoja: complican la interfaz y el código. Se revisa tras las
  pruebas.

### 3.5 Conflictos y avisos al montar

El editor conoce, por `api/fragua.json`, qué toca cada comportamiento ("mueve", "dibuja", "quita"). Con eso avisa:

- Dos comportamientos que **mueven** el mismo cuerpo: aviso, no error. Manda el de arriba (ver 5.6).
- Un evento "Choca con" en un nodo sin `Shape` ni `Area`: aviso con arreglo.
- Una acción sobre un nodo que ya no existe (se renombró o se quitó): la fila sale marcada con "!" y dice cuál.
  Renombrar un nodo desde el editor cambia las filas que lo nombran, en toda la escena.
- Una fila que nunca puede pasar ("vidas llega a 0" sin nada que reste vidas): aviso suave, se puede callar.

### 3.6 El código que se genera

#### 3.6.1 Dónde va

Para `nivel1.escena`:

| Fichero | Quién lo escribe | Qué lleva |
|---|---|---|
| `nivel1.escena` | El editor | La escena (JSON): nodos, propiedades, comportamientos, eventos |
| `nivel1.escena.dash` (propuesto: en un cajón `generado/`) | El editor, con el conversor de Fragua | La función que monta el árbol y un `struct` por hoja de eventos |
| `jugador.dash` | El usuario | Su script. El editor solo lo crea, vacío o con una función nueva al final. **No lo reescribe nunca.** |

- El fichero generado empieza diciendo lo que es:
  `# Generado por Forja desde nivel1.escena. No lo cambies aquí: se vuelve a escribir. Tu código va en los scripts.`
- Va a git si el usuario quiere (un juego se compila sin Forja) o no. Por defecto sí: el proyecto se compila con
  `dash` a secas.
- Forja lo abre en una pestaña de solo lectura (ver lo que se pide a Forja, sección 8).

#### 3.6.2 Cómo tiene que ser

Condiciones de calidad del código generado. Son requisitos de UX, no de estilo:

1. **Como lo escribiría una persona.** Nombres de los nodos del usuario (`jugador`, `moneda3`), sangrado de Dash,
   sin nombres con números raros ni tablas de datos.
2. **Una fila, un bloque**, con un comentario que es la frase de la fila:
   `# 1. Cuando choca con uno de "enemigos", y vidas > 0`.
3. **Mismo orden que en el editor**: los nodos en el orden del árbol, las filas en el orden de la hoja.
4. **Estable**: cambiar una fila cambia solo su bloque. Así git enseña diferencias pequeñas, y el usuario que mira
   el código ve qué cambió su clic.
5. **Solo API pública de Fragua.** Lo que el editor genera, el usuario lo puede escribir igual. Nada de funciones
   `fragua_*` internas.
6. **Sin relleno**: un nodo sin eventos no genera `struct`. Un comportamiento con valores de fábrica genera una
   línea.

Ejemplo de lo que sale para el jugador (ilustrativo: la API exacta la fija la rama `nodos`):

```
# Jugador: comportamientos
func nivel1_jugador() -> Node
    jugador = new_body("Jugador", 96, 128)
    jugador.add_child(new_animated_sprite("Dibujo", image_cached("jugador.iff"), 0, 0))
    jugador.add_child(new_shape_rect("Caja", 4, 2, 24, 30))
    jugador.add_to_group("jugador")
    jugador.add_behavior(Platformer(speed: Fixed(2), jump: Fixed(5)))
    jugador.add_behavior(Health(lives: 3))
    jugador.add_behavior(JugadorEventos())
    return jugador
end

# Jugador: eventos
struct JugadorEventos: Script
    func _signal(n: Node, name: String, from: Node, data: Int)
        # 1. Cuando choca con uno de "enemigos", y vidas > 0
        if name == "body_entered" and from.is_in_group("enemigos")
            if game_get("vidas") > 0
                game_add("vidas", -1)
                play_sound("ay.8svx")
            end
        end
        # 2. Cuando entra en el área Meta
        if name == "area_entered" and from.name == "Meta"
            change_scene(nivel2())
        end
    end
    ...
end
```

#### 3.6.3 Cómo se enseña

- **C** en cualquier sitio del editor: "Ver código". Enseña el del nodo elegido.
  - En la hoja de eventos: la franja de abajo, con la fila elegida.
  - En el árbol o la vista: una pestaña de solo lectura en Forja con el `.escena.dash`, con el cursor en el nodo.
- **Ida y vuelta:** en esa pestaña, una tecla (Return) sobre una línea vuelve al editor con el nodo y la fila de
  esa línea elegidos. El conversor escribe, junto al `.dash`, una tabla "línea → nodo, fila" (`.mapa`, propuesto).
  Esa misma tabla sirve para los errores (5.4) y para el depurador.
- **Con colores de Dash.** Las pestañas de solo lectura de las extensiones (`VISTA`) hoy llevan un color por línea.
  Se pide a Forja abrir un fichero de verdad en modo de solo lectura, con su resaltado (sección 8).
- **El depurador de Forja para en el código generado** como en cualquier otro. Con la tabla, la barra de estado
  dice además: "Jugador, fila 1".

### 3.7 De eventos a script, sin perder nada

Tres puertas, de la más pequeña a la más grande.

**Puerta 1: una acción que llama a tu código.** En cualquier fila, la acción "Llamar a una función de mi script".
- Si el nodo no tiene script, el editor lo crea: `jugador.dash`, con un `struct Jugador: Script` y las cuatro
  funciones vacías.
- Pide el nombre de la función, la añade al final del `struct` (vacía, con un comentario) y abre Forja ahí.
- La fila queda: `HAZ llamar a doble_salto()`.
- Es la puerta de Godot: una señal conectada a una función. Se aprende a programar de función en función.

**Puerta 2: una fila pasa a ser código.** Menú de la fila > "Pasar esta fila a mi script".
- El editor copia el bloque generado de la fila a una función nueva del script: `func al_chocar_enemigo(...)`.
- La fila se queda en la hoja con el mismo evento y condiciones, y **una sola acción**: llamar a esa función.
- Nada cambia en el juego. El usuario ahora puede tocar el cuerpo de la función.
- Se deshace en el editor (la fila vuelve). La función copiada se queda en el script: el editor no borra código
  del usuario. Lo dice: "La función al_chocar_enemigo sigue en jugador.dash."

**Puerta 3: todo el nodo pasa a script.** Botón "Pasar a script..." de la hoja.
- Enseña antes lo que va a hacer, en una pestaña de cambios como la de "Cambiar en el proyecto" de Forja: el
  código que se añadirá a `jugador.dash`. Return acepta, Esc no.
- Añade al script del usuario los métodos de `JugadorEventos`, fundidos en su `struct`. Si el script ya tiene
  `_signal`, **no lo mezcla**: añade `_signal_eventos(...)` y una línea de llamada al principio del `_signal` del
  usuario. Mezclar código a ciegas es la forma segura de romper algo.
- La hoja no se borra: queda **apagada**, en tenue, con un rótulo: "Pasada a jugador.dash el 17-11-2026. Ya no se
  usa." Sirve de recuerdo de lo que hacía. Botón "Volver a usar la hoja": la enciende y avisa de que el script
  hace lo mismo, con la lista de funciones a quitar a mano.
- Los comportamientos **no** se pasan a script con esto. Siguen siendo piezas. Para ver cómo están hechos: "Ver el
  código del comportamiento" abre su fuente de Fragua, de solo lectura. Para cambiar uno: "Copiar a mi proyecto
  como comportamiento propio" (3.2.3).

Lo que garantiza "sin perder nada":
- El juego hace lo mismo antes y después de cada puerta. Se comprueba con una prueba automática: generar, pasar a
  script, compilar y comparar la salida de una partida grabada (sección 9).
- Ninguna puerta borra nada: ni filas, ni código.
- La vuelta atrás existe en las tres, y dice con claridad qué queda por limpiar a mano.

### 3.8 La página Script

```
| [Prop.][Comp.][Event.][Script]               |
+----------------------------------------------+
| Script: jugador.dash          [Abrir (Return)]|
| struct Jugador                                |
|   _ready                                      |
|   _physics_process                            |
|   doble_salto          <- fila 4              |
|   al_chocar_enemigo    <- fila 1              |
| Propiedades del script                        |
|   fuerza_doble  [===|--] 4.0                  |
| [Quitar el script del nodo]  [Cambiar...]     |
```

- Sin script: dos botones, "Crear un script" (de una plantilla por tipo de nodo, con comentarios que explican cada
  función) y "Usar uno que ya hay...".
- La lista de funciones sale de los símbolos de Forja. Un clic va a la función.
- Las propiedades exportadas del script se editan aquí, como las de un comportamiento.
- Un mismo script puede estar en varios nodos y en varias escenas.

---

## 4. Recorridos de usuario

Convenciones: "→" es lo que hace el usuario. "Ve:" es lo que cambia en pantalla. Los tiempos y clics son
objetivos (por medir) en un A1200 con disco duro y pantalla de 640x256, salvo que se diga. "Clic" cuenta también
una tecla.

### 4.1 Primer juego en 10 minutos, desde una plantilla

Quién: alguien que nunca ha usado Forja. Meta: un juego suyo, cambiado y jugando, en 10 minutos.

1. → Abre Forja. Ve: la bienvenida con "Nuevo proyecto".
2. → Proyecto > Nuevo proyecto. Ve: las plantillas. Bajo "Juego", seis con una captura cada una: Plataformas,
   Cenital, Matamarcianos, Puzle, Carreras, Isométrico. Y "Juego vacío".
3. → Elige "Plataformas", escribe "MiJuego", Return. Ve: el proyecto creado y **la escena `nivel1.escena` abierta
   en el editor de escenas**, no un fichero de código. En el centro, un nivel pequeño con un muñeco, tres monedas
   y un enemigo. Una franja arriba de la vista: "Pulsa F5 para jugar. Esc vuelve aquí." (se quita con un clic y no
   vuelve).
4. → F5. Ve: "Compilando...", y el juego. Juega 30 segundos. Esc.
5. Ve: el editor igual que lo dejó. Barra: "Jugaste 31 s."
6. → Clic en el muñeco. Ve: el marco con asas, "Jugador" marcado en el árbol.
7. → Tab (pasa al inspector), clic en "Comp.". Ve: `Platformer` con sus deslizadores.
8. → Arrastra "Salto" de 5 a 8. → F5. Ve: salta más. Primer cambio propio: minuto 3.
9. → Esc. → Clic en una moneda, D (duplicar), la arrastra a una plataforma alta. Repite dos veces.
10. → Tab hasta Recursos, página Imágenes, clic en `jugador.iff`, [Editar]. Ve: el editor de Sprites con el
    muñeco. Le cambia el color de la camiseta. Amiga-S. Cierra.
11. Ve: en la vista de la escena, el muñeco con la camiseta nueva.
12. → Clic en el enemigo, página "Event.". Ve: una fila: "Cuando choca con jugador > restar 1 a vidas". → Clic en
    [1], escribe 2, Return.
13. → F5. Juega con sus cambios. Minuto 9.

Cuenta: 0 líneas de código. Unos 25 clics. Tres editores tocados sin perderse.

Lo que este recorrido exige al diseño:
- La plantilla abre la escena, no el `main.dash`.
- El juego de la plantilla es bonito y corto, y enseña un nodo de cada clase corriente.
- F5 funciona a la primera, sin preguntas.
- Volver del editor de Sprites refresca la vista sola.

### 4.2 Plataformas, desde una escena vacía

Meta: jugador que anda y salta, suelo de tiles, enemigo que patrulla, monedas, meta. 30 minutos.

1. → Amiga-B > Escena. Nombre "nivel1". Ve: escena con un nodo raíz `Node2D` "Nivel1".
2. **El mapa.** → A (añadir), "ti", Return. Ve: `TileMap` añadido; el inspector pide "Mapa: [...] [Nuevo]".
   → [Nuevo]. Ve: el editor de Mapas, que pide el tileset. Elige `tiles.iff`. Pinta el suelo y dos plataformas.
   Pasa a la capa de choques y pinta lo sólido. Amiga-S. Vuelve.
   Ve: el mapa en la vista. La rejilla de la vista ha tomado 16.
3. **El jugador.** → A, "bo", Return. Ve: `Body` "Body" con un hijo `Shape` ya puesto, y la fila "¿Qué quieres que
   haga?". → "Jugador de plataformas". Ve: `Platformer` en Comp.
4. → F2, "Jugador", Return.
5. → Recursos > Imágenes, arrastra `jugador.iff` sobre "Jugador" en el árbol. Ve: un hijo `AnimatedSprite`, y la
   caja del `Shape` ajustada al tamaño del fotograma.
6. → En la vista, arrastra el jugador sobre el suelo. → Fin. Ve: baja hasta apoyarse.
7. → F6. Anda y salta sobre el mapa. Esc. (Minuto 8.)
8. **La cámara.** → Con "Nivel1" elegido, A, "ca", Return. Inspector: "Sigue a: [Elegir]". → [Elegir], clic en el
   jugador. Ve: el marco de la cámara en la vista.
9. **El enemigo, como escena.** → Amiga-B > Escena, "bicho". A, Body, "Patrulla". Arrastra `bicho.iff`. Amiga-S.
   → Vuelve a la pestaña nivel1. Recursos > Escenas, arrastra `bicho.escena` a la vista, tres veces.
   → Elige uno, grupos: "enemigos". Aviso del editor: "¿Poner el grupo en la escena bicho, para todos? [Sí] [Solo
   este]". → Sí.
10. **Las monedas.** → Otra escena "moneda": `Area` con `Pickup` (variable "puntos", suma 1, sonido). Instancia
    ocho con Ctrl + clic (sellar).
11. **El daño.** → Jugador > Comp. > + `Health` (vida 3). → Event. > + Evento > "Choca con..." > grupo "enemigos"
    > Haz: "Health: hacer daño 1". → + Evento > "Health: se queda sin vida" > "Volver a empezar esta escena".
12. **La meta.** → A, Area, "Meta". La coloca al final. En el jugador: + Evento > "Entra en un área" > Meta >
    "Cambiar de escena" > `nivel2.escena` (aún no existe: el selector ofrece "Nueva escena...").
13. → F5. Juega el nivel entero.

Puntos finos:
- Paso 5: arrastrar una imagen sobre un `Body` crea el sprite como hijo. Sobre la vista vacía crearía un `Sprite`
  suelto.
- Paso 9: la pregunta del grupo enseña la diferencia entre instancia y escena en el momento en que importa.
- Animaciones del jugador: `Platformer` busca animaciones llamadas "idle", "run", "jump" y "fall" en el
  `AnimatedSprite` hijo y las pone solo. Si no existen, no pasa nada. Se dice en su ayuda. (Propuesto para Fragua.)

### 4.3 Vista cenital / RPG por tiles

Meta: un pueblo, un personaje que anda por casillas, una puerta que lleva a otra escena, un cartel con texto.

1. → Plantilla "Cenital" o escena vacía. Ajustes de la escena: gravedad no hay (la cenital no la tiene: los
   comportamientos de esta plantilla no la usan).
2. → `TileMap` con `pueblo.fmap`. En Mapas: capas "suelo", "cosas" y "choques".
3. → `Body` "Heroe" > "¿Qué quieres que haga?" > "Se mueve en 8 direcciones". En Comp., `EightWay`: direcciones 4.
   O bien, para paso de casilla en casilla como en los RPG clásicos: quitar `EightWay` y poner `GridMove` (lado
   16, 8 fotogramas por paso).
4. → Animaciones: `EightWay` y `GridMove` buscan "walk_down", "walk_up", "walk_left", "walk_right".
5. **Orden de dibujo.** El héroe debe pasar por detrás de las copas de los árboles. Dos formas, las dos a la vista:
   - la capa "encima" del mapa (copas, tejados) con capa de dibujo mayor que la del héroe; es lo que hace RPG
     Maker con sus tiles de estrella (de memoria);
   - en el nodo padre de los personajes, la propiedad "Ordenar por Y" (propuesto, como `y_sort` de Godot, de
     memoria): el que está más abajo se pinta encima.
6. **La puerta.** → En Mapas, capa de objetos: un objeto de clase "puerta" en la entrada de la casa. De vuelta en
   la escena, inspector del `TileMap` > "Objetos del mapa": "puerta → puerta.escena". `puerta.escena` es un `Area`
   con una propiedad exportada "destino" y un evento: "Cuando entra jugador > cambiar a la escena [destino]".
   → Clic en la puerta en la vista; en su inspector, destino: `casa.escena`, y "Aparece en: [Entrada]" (un nodo
   `Node2D` de la otra escena, elegido por nombre).
7. **El cartel.** → `Area` "Cartel" con evento "Cuando el jugador está dentro y se pulsa 'acción' > enseñar el
   texto [Bienvenido a Villa Arriba]". La acción "Enseñar un texto" abre un cuadro de diálogo del juego (escena
   `dialogo.escena` de la plantilla) y pausa el resto.
8. → F5.

Puntos finos:
- Pasar de una escena a otra conservando "por dónde entro" es el caso que más cuesta al principiante de Godot (de
  memoria). Aquí es una propiedad de la acción "Cambiar de escena": "Aparece en".
- Vida, oro y objetos entre escenas: variables del juego. No se pierden al cambiar de escena.
- Diálogos largos, inventario, combates: script. La plantilla trae el cuadro de diálogo hecho, con su código, como
  ejemplo de escalón 4.

### 4.4 Matamarcianos con scroll

Meta: nave, disparos, oleadas, fondo que avanza, jefe.

1. → Plantilla "Matamarcianos" o vacía. Ajustes de la escena: tamaño del nivel 320x4096 (vertical).
2. → `TileMap` del fondo. `Camera` con `Scroller` (vy = -1).
3. → `Body` "Nave": `EightWay` + propiedad "No sale de la cámara" (propuesto: en `EightWay`, "Límite: pantalla").
   Como hija, un `Node2D` "Canon" con `Shooter` (escena `bala.escena`, cadencia 8, acción "disparar").
4. → `bala.escena`: `Area` + `Bullet` (arriba, 6) + `DestroyOffscreen`. Grupo "balas".
5. **Usar el sprite de hardware.** En el `Sprite` de la nave y en el de la bala, casilla "Sprite de hardware". La
   burbuja lo explica: "No gasta CPU. 16 de ancho, 3 colores. Hay 8." La barra de estado cuenta: "HW 3/8". Si se
   pasan, aviso.
6. **Las oleadas.** Dos formas:
   - colocar los enemigos en el nivel, a mano, donde tienen que aparecer. Se activan al entrar en la cámara
     (propiedad de la escena `enemigo`: "Dormido hasta que se ve", propuesto). Es lo más visual: el nivel se ve
     entero en la vista, con zoom "encajar" y modo Cajas.
   - `Spawner` con una lista: cada 2 s, 5 de `enemigo.escena`, en x al azar.
7. → `enemigo.escena`: `Area` + `Path` o `Sine` + `Health` (1) + evento "Choca con balas > Health: daño 1, quitar
   el que me tocó" + "Health: sin vida > crear `explosion.escena` aquí, sumar 100 a puntos, quitarme".
8. **El jefe.** Un `Area` al final del nivel, "ParaElScroll": "Cuando entra la cámara > apagar Scroller, crear
   `jefe.escena`".
9. → F5.

Puntos finos:
- **Presupuesto a la vista.** En un matamarcianos se llega pronto al límite del Amiga. La barra de estado enseña
  una estimación: "BOBs en pantalla: 14 (unos 22 ms: no cabe a 50 Hz en A1200)". Detalle en 5.2.
- El scroll suave depende del scroll de hardware en Dash, que hoy no está. Sin él, el editor es igual; el juego va
  por pantallazos o con franja. El editor no promete lo que el motor no da: el `Scroller` dice en su ayuda qué
  necesita.

### 4.5 Puzle

Meta: un juego de empujar cajas (tipo Sokoban) o de casar fichas. Sin física.

1. → Plantilla "Puzle". Ve: un tablero de 10x8 casillas de 24 píxeles, centrado.
2. → Rejilla 24, imán puesto. Todo cae en casilla.
3. → `Body` "Obrero" con `GridMove` (lado 24).
4. → `caja.escena`: `Body` con `GridMove` + propiedad "Se deja empujar" (propuesto, en `GridMove`). Grupo "cajas".
5. → `meta.escena`: `Area`. Evento: "Cuando entra una de cajas > sumar 1 a puestas". "Cuando sale una de cajas >
   restar 1 a puestas".
6. → En la raíz: evento "Cuando puestas llega a [4] > cambiar a la escena siguiente".
7. → `Label` "Movimientos", enseña la variable "pasos". En el obrero: "GridMove: da un paso > sumar 1 a pasos".
8. → Deshacer del juego (tecla U en el juego): no hay acción sin código. Es el sitio donde el recorrido enseña la
   puerta 1: "Llamar a una función de mi script". La plantilla trae `deshacer.dash` hecho y comentado.
9. → F5.

Variante con ratón (casar fichas): `Draggable` con "ajusta a rejilla", evento "Clic del ratón sobre el nodo".

Puntos finos:
- Los niveles de un puzle son datos. Lo natural es **un mapa por nivel con objetos**, y una sola escena que carga
  el mapa "nivel N". La plantilla lo hace así. Evita 30 escenas casi iguales.
- La vista en un puzle es pequeña: en 640x256 cabe entera a 1x. Buen género para la primera prueba con usuarios.

### 4.6 Carreras de lado: la moto del tutorial

Es el tutorial-curso (`docs/tutorial/moto.md` de Fragua). Este recorrido es su esqueleto, capítulo a capítulo. El
juego es original: nombre, gráficos, sonidos y niveles propios.

| Capítulo | Qué se hace | Qué se aprende | Escalón |
|---|---|---|---|
| 1. La pista | Proyecto vacío. `TileMap` largo (200x16). Suelo y cielo en Mapas. F6: se ve la pista. | Proyecto, escena, mapa | 1 |
| 2. La moto | `Body` "Moto", imagen, `Shape`. `Vehicle`: fuego acelera, atrás frena. F6: corre y se sale de la pantalla. | Nodos, comportamientos | 2 |
| 3. La cámara | `Camera` que sigue a la moto, adelantada (propiedad "Adelanto": 80). | Cámara, propiedades | 1 |
| 4. Rampas y saltos | Tiles de pendiente en la capa de choques. Deslizador de gravedad. | Choques del mapa, afinar jugando | 2 |
| 5. Coches y autobuses | `coche.escena` y `autobus.escena`: `Body` estático con `Shape`. Colocarlos con sellado. Grupo "obstaculos". | Escenas e instancias, grupos | 1 |
| 6. Caerse | Evento: "Choca con obstaculos > poner animación 'caida', apagar Vehicle 50 fotogramas, restar 1 a vidas". | Eventos y acciones | 3 |
| 7. Aterrizar bien o mal | Evento "Vehicle: aterriza" con condición "velocidad de caída > 6". Primera vez que la hoja se queda corta: hace falta mirar también el ángulo. → "Pasar esta fila a mi script". | Puerta 2: de fila a código | 3 → 4 |
| 8. Marcador y tiempo | Escena `hud.escena`: `Label` con "velocidad", "tiempo" y "vidas". `Timer`. | Interfaz, variables | 1, 3 |
| 9. El motor suena | `AudioPlayer` en bucle. Script de 5 líneas: el tono sube con la velocidad. | Script propio desde cero | 4 |
| 10. El rival | `rival.escena`: `Body` con `Vehicle` y un script que decide cuándo acelerar y saltar. | Script con lógica | 4 |
| 11. Meta, menú y niveles | `Area` de meta, escena de menú, tres pistas. | Cambio de escena | 3 |
| 12. Pulido | Partículas de polvo, sacudida de cámara, fundidos. Medir en A500. | Efectos, presupuesto | 2, 4 |

Requisitos de UX del tutorial:
- **Cada capítulo acaba en F5 y algo nuevo que se nota.** Ninguno dura más de 20 minutos.
- **El proyecto de cada capítulo viene hecho** (`examples/moto/cap03/`), para quien se pierde o quiere saltar.
- **Capturas del editor de verdad**, hechas por las pruebas automáticas (sección 9). Si el editor cambia, la
  prueba falla y la captura del tutorial se rehace: el tutorial no envejece sin que se note.
- El capítulo 7 es el corazón del curso: el paso de "sin código" a código llega porque el juego lo pide, no porque
  toca.
- En Forja: "Ayuda > Curso: la moto" abre el capítulo en la ventana de la ayuda, con un botón "Abrir el proyecto
  de este capítulo".

### 4.7 Isométrico

Meta: una habitación con suelo en rombo, un personaje que anda, un mueble tras el que se pasa, un escalón.
Detalle del diseño en la sección 6.

1. → Plantilla "Isométrico". Ve: la vista con rejilla en rombo y una habitación de 8x8.
2. → Clic en el personaje. El inspector dice "Casilla: 3, 4  Altura: 0", no "x 144, y 96". (Los píxeles están en
   un bloque plegado, "Posición en pantalla", de solo lectura.)
3. → Flechas: el personaje se mueve por las casillas, siguiendo los ejes del rombo. Arrastrar: salta de casilla en
   casilla, con el rombo de destino iluminado.
4. → Recursos, arrastra `mesa.escena` a la vista. Ve: un rombo sigue al puntero y dice qué casilla. Suelta.
5. → Mueve el personaje detrás de la mesa. Ve: la mesa lo tapa. Nadie tocó capas: el orden sale de la casilla.
6. → Elige una caja, Re Pág. Ve: sube una altura; una línea a trazos baja hasta su casilla, y su sombra en el
   suelo. Inspector: "Altura: 1".
7. → Comp. del personaje: `IsoMove`. F6: anda con las flechas en diagonal de pantalla.
8. → Ver > "Solo la altura 0" (tecla Alt + 0..9): lo de más arriba se ve tramado. Para editar el suelo sin que
   estorbe lo que hay encima.
9. → F5.

### 4.8 Menú, marcador y cambio de escena

Meta: pantalla de título con "Jugar" y "Salir", marcador en el juego, pantalla de fin.

1. **El menú.** → Amiga-B > Escena > plantilla de escena "Menú" (las escenas también tienen plantillas: Vacía,
   Nivel, Personaje, Menú, Marcador). Ve: un título y dos `Label` con `Button`.
2. → Clic en "Jugar". Event.: "Button: pulsado > cambiar a la escena [nivel1.escena]". En "Salir": "salir del
   juego".
3. → Los `Button` se encadenan solos por orden en el árbol: arriba y abajo cambian el elegido, fuego o Return
   pulsa. Con ratón, clic. Sin tocar nada.
4. → Juego > Ajustes del juego > Escena inicial: `menu.escena`. (O botón derecho sobre la pestaña de la escena >
   "Es la escena inicial".)
5. **El marcador.** → Amiga-B > Escena > "Marcador". Ve: la vista con solo el marco de la pantalla (es una escena
   de interfaz). Dos `Label`: "Puntos" (enseña "puntos", con el texto "PUNTOS " delante) y "Vidas".
6. → En `nivel1.escena`: Recursos > Escenas, arrastra `marcador.escena` al árbol. Cae en la capa "interfaz" sola,
   porque la escena está marcada como de interfaz.
7. → Para que las vidas sean dibujos y no un número: `Label` no vale. Nodo `Sprite` con la propiedad "Repetir según
   la variable" (propuesto): pinta el corazón tantas veces como diga "vidas".
8. **El fin.** → Escena `fin.escena` desde la plantilla "Menú": "FIN", `Label` con "puntos", botón "Otra vez".
9. → En el jugador: "Cuando vidas llega a 0 > cambiar a la escena fin".
10. → Evento en la raíz de `menu.escena`: "Al empezar > poner puntos a 0, poner vidas a 3".
11. → F5: menú, juego, fin y vuelta.

Puntos finos:
- **Mapa de escenas (propuesto, fase 7):** "Juego > Mapa de escenas" dibuja las escenas como cajas y los "cambiar
  de escena" como flechas. Se ve de un golpe si una escena no tiene salida o nadie llega a ella.
- Un fundido entre escenas: opción de la acción "Cambiar de escena": "Con fundido [x]".
- La pausa: en la plantilla, la tecla P ya pausa. Es un evento de la raíz, a la vista, para que se pueda cambiar.

### 4.9 Depurar un fallo de choques

Caso: "las monedas no se cogen". Es el fallo más corriente.

1. → F8 en el editor (siguiente aviso). Ve: nada sobre monedas. No es un fallo que el editor vea.
2. → Mayúsculas + F6 (probar con formas). Ve: el juego con las formas de choque encima: cajas de cuerpos en un
   trazo, áreas a rayas, y las celdas sólidas del mapa tramadas.
3. Ve: la moneda no tiene marco alguno. → Esc.
4. → Clic en la moneda. Inspector: es una instancia de `moneda.escena`. Return: abre la escena. El `Area` no tiene
   `Shape`... pero el editor habría avisado. Sí lo tiene. Mira la página Prop.: "Capa de choque [ ][2]", "Choca
   con [1]". El jugador está en la capa 1 y **mira** a la 1. La moneda está en la 2.
5. El editor puede decirlo. → Con el jugador y la moneda elegidos: menú Nodo > **"¿Por qué no chocan?"**
   (propuesto). Ve una ventanita:

   ```
   Jugador (Body) y Moneda (Area)
     [bien] Los dos tienen forma.
     [bien] Las formas se pueden tocar (no están apagadas).
     [MAL ] Capas: Moneda está en la capa 2 y Jugador solo choca con la 1.
            [Hacer que Jugador choque con la capa 2]
     [bien] Jugador tiene un evento o comportamiento que escucha: Pickup en Moneda.
   ```
6. → Pulsa el botón. F6. Se cogen.

La lista que comprueba "¿Por qué no chocan?": formas presentes; formas con tamaño mayor que cero; capas y
máscaras; alguno de los dos es `Area` o los dos son cuerpos sólidos; alguien escucha la señal; el grupo del evento
existe y el otro nodo está en él; el comportamiento está encendido.

Más herramientas de depuración, en el juego compilado para probar (no en el que se entrega):

| Tecla en el juego | Qué hace |
|---|---|
| F1 | Formas de choque sí o no |
| F2 | Nombres de los nodos junto a cada uno |
| F3 | Medidor: ms de lógica, de física y de dibujo; nodos; BOBs; fotogramas perdidos |
| F4 | Pausa. Con la pausa, F5 avanza un fotograma |
| F6 | Cámara libre con las flechas (con pausa) |
| Clic en un nodo (con pausa) | Enseña sus propiedades en una esquina. Al volver al editor, ese nodo queda elegido |

Y en el editor, mientras el juego corre en pausa (fase 6): la pestaña del árbol tiene dos vistas, "Escena" y "En
marcha". La segunda enseña el árbol del juego tal como está (con las balas y los enemigos creados), y el inspector
sus valores, en solo lectura. Es el árbol "Remoto" de Godot (de memoria). Habla con el juego por un puerto ARexx
propio del juego en modo de prueba, como hace la extensión Demos con la demo en marcha.

Otros fallos de choques y qué los destapa:

| Síntoma | Lo enseña |
|---|---|
| El jugador atraviesa el suelo | F1: el mapa no tiene capa de choques, o no está tramada donde debería |
| Se queda enganchado en una esquina | F1 + F4/F5 fotograma a fotograma: la caja es más ancha que el dibujo |
| La bala atraviesa al enemigo | F3: velocidad mayor que el ancho del enemigo. Aviso del editor: "Bullet a 12 px por fotograma y Shape de 8: puede saltárselo" |
| Choca dos veces | "En marcha": el evento está en la escena y también en la instancia |
| Choca con lo que no debe | "¿Por qué no chocan?" al revés: dice por qué sí chocan |

### 4.10 De "sin código" a código

Quién: quien ya hizo un juego con eventos y quiere algo que la hoja no da. Caso: salto doble.

1. → Jugador > Event. > + Evento > "Se pulsa una acción" > saltar.
2. → Y si: "no toca el suelo". (Está en la lista.)
3. → Busca la condición "no ha saltado ya en el aire". No está. Ve, al final de la lista de condiciones: "¿No
   encuentras lo que buscas? [Escribirlo en código]".
4. → Pulsa. Ve: "Se creará jugador.dash con una función para este evento. [Crear]". → Crear.
5. Ve: Forja delante, `jugador.dash` abierto, con esto, y el cursor en la línea vacía:

   ```
   # El script de Jugador. Lo que escribas aquí es tuyo: Forja no lo cambia.
   struct Jugador: Script
       # Fila 5 de los eventos: cuando se pulsa "saltar" y no toca el suelo.
       func salto_en_el_aire(n: Node)
           |
       end
   end
   ```
6. → Vuelve al editor un momento (Amiga-M, o clic). C sobre la fila 1 de `Platformer`... no: C sobre el
   comportamiento enseña cómo salta `Platformer`: `n.body.vy = -self.jump`. Lo copia.
7. → En su función escribe, con el completado de Forja ofreciendo `n.body.`:

   ```
   if not self.ya_salto
       n.body.vy = Fixed(-4)
       self.ya_salto = true
   end
   ```
   y declara `ya_salto: Bool` en el `struct`. Forja marca errores al guardar, como siempre.
8. → Falta ponerlo a `false` al tocar el suelo. Vuelve a la hoja: + Evento > "Toca el suelo" > "Llamar a una
   función de mi script" > "Nueva: al_aterrizar". Forja abre la función. Escribe `self.ya_salto = false`.
9. → F6. Salta dos veces.

Después, cuando quiera más:
- Fila a fila: "Pasar esta fila a mi script" (puerta 2). Ve su fila escrita en Dash, y ya la puede cambiar.
- Todo: "Pasar a script..." (puerta 3), con la vista previa de cambios.
- Y al revés: su función con propiedades exportadas puede ser un comportamiento para otros nodos.

Lo que cuida este recorrido:
- El paso a código sale **donde se nota la falta**, en la lista de condiciones y de acciones.
- La primera función es de tres líneas, en un fichero casi vacío, con el contexto escrito en un comentario.
- Hay de dónde copiar: el código generado y el de los comportamientos, a una tecla.
- F1 sobre `n.body` abre la ayuda de Fragua, con ejemplo.

---

## 5. Casos difíciles y de borde

### 5.1 Escenas grandes y muchos nodos

| Problema | Respuesta |
|---|---|
| Pintar 300 nodos tarda | La vista pinta solo lo que cae dentro. Una rejilla de celdas dice qué nodos hay en cada zona. |
| Aun así tarda (zoom "encajar") | Con más de N nodos visibles (por medir; del orden de 60 en A1200) la vista pasa sola a Cajas, y lo dice: "Cajas (muchos nodos)". Al acercar, vuelve. |
| Arrastrar va a tirones | Al arrastrar se mueve solo un marco (dibujo con XOR, como las gomas del Workbench). Lo demás no se repinta hasta soltar. |
| Desplazar la vista va a tirones | Se copia lo que ya está pintado (`ScrollRaster`) y se pinta solo la tira nueva. Como hace el juego. |
| El árbol tiene 500 líneas | Se pinta solo lo que se ve. Las ramas se abren cerradas al cargar, salvo la raíz. El buscador filtra. |
| Mil monedas | No se ponen mil nodos. Para lo repetido que no se mueve: objetos del mapa, que el nodo `TileMap` convierte en nodos al cargar, o por zonas. El editor lo sugiere al pasar de 100 instancias iguales. |
| Nivel de 20 pantallas | El `TileMap` no se pinta entero: solo las celdas visibles, de una tira cada vez. En "encajar", el mapa va en Cajas. |
| Cargar tarda | Medidor con el nombre de lo que carga. Las imágenes, a medida que se ven. Esc para: la escena queda abierta con lo cargado y el resto en Cajas. |

Tope duro (propuesto): 2.000 nodos por escena en el editor. Al llegar, dice por qué y qué hacer (partir en
escenas). Mejor un tope claro que un cuelgue.

### 5.2 Presupuesto del juego: decir antes de jugar si va a ir lento

El editor sabe cuánto cuesta cada cosa (la tabla de costes de Fragua, medida en A1200 y A500) y lo suma para la
peor pantalla de la escena:

```
Presupuesto (A1200, 20 ms por fotograma)        [A500] [A1200] [RTG]
  Dibujo    12 BOBs de 16x16, 2 de 32x32     26,2 ms   ########## MAL
  Lógica    38 nodos con script o comp.       0,4 ms   .
  Física    14 cuerpos                         1,1 ms   .
  Sprites de hardware  3 de 8
  Chip      imágenes 148 K, pantalla 100 K   de 2.048 K
  Consejo: pasa las balas (6) a sprites de hardware: ahorra 9,6 ms.  [Hacerlo]
```

- Se abre con un clic en la zona de memoria de la barra de estado, o con B.
- Es una estimación y lo dice. La medida de verdad es F3 en el juego.
- Sirve para enseñar cómo es un Amiga: por qué las balas son sprites de hardware.

### 5.3 Memoria justa (en el Amiga donde corre Forja)

- La barra de estado enseña lo que usa la escena en el editor.
- Las imágenes se cargan una vez por fichero, aunque haya cien nodos con ella.
- La pila de deshacer guarda cambios, no copias de la escena. Con tope (propuesto: 256 K): al pasarlo se olvidan
  los pasos más viejos, y se dice una vez.
- Con poca memoria libre (propuesto: menos de 500 K de fast, o 200 K de chip):
  - la vista pasa a Cajas y suelta las imágenes;
  - aviso en la barra: "Poca memoria: vista en Cajas";
  - antes de F5: "Para compilar hacen falta unos 2 MB y hay 1,2. [Cerrar los otros editores y jugar] [Cancelar]".
    Compilar suma 1,9 MB (medido en Forja).
- Si falta memoria al cargar una escena: se abre lo que cabe, en Cajas, y nunca se guarda una escena a medio
  cargar encima de la buena (el botón Guardar se apaga y explica por qué).
- Guardar es seguro: se escribe en un fichero nuevo y luego se renombra. Si el disco se llena, el viejo sigue.

### 5.4 Errores en scripts y en el código generado

| Caso | Qué ve el usuario |
|---|---|
| El script del usuario no compila | Forja delante, en la línea del error, como siempre. En el editor de escenas, el nodo con ese script lleva "!" en el árbol. La barra: "jugador.dash, línea 12: ...". |
| El código generado no compila | Es un fallo del editor o del conversor, no del usuario. Se dice así: "Forja ha generado código que no compila. No es culpa tuya." Con el nodo y la fila señalados (por la tabla de líneas) y un botón "Guardar un informe" que junta la escena y el error. |
| Un script no tiene la función que una fila llama (se renombró) | Aviso en el editor **antes** de compilar: la fila lleva "!". Botón: "Elegir otra función" o "Crearla". |
| El script no cumple `Script` | Aviso en la página Script, con lo que falta. Hoy Dash da la línea de otro fichero en este error (bitácora de Fragua): se pide arreglarlo en Dash. |
| Error al jugar: campo de `nil` | Dash da fichero y línea. El editor lo traduce: "Se usó un nodo que no existe: 'Jugador/Arma' en la fila 3 de Enemigo". Al volver, ese nodo queda elegido. |
| El juego se cuelga (bucle sin fin en un script) | Amiga-. en el editor lo para (lo que Forja ya hace al parar un programa). El editor no se cuelga: es otro proceso. |
| El juego tumba el Amiga (modo sin sistema) | Antes de F5 en ese modo, la primera vez: aviso de que si falla hay que reiniciar, y que todo está guardado. El editor guarda todo antes, siempre, en ese modo. |
| `get_node` con una ruta que no existe, en un script | El editor no lo ve (es código). Sí puede avisar al guardar el script si la ruta es un texto fijo y no existe en la escena. Fase posterior. |

Regla: un error al jugar nunca deja al usuario delante de código generado sin decirle de qué nodo es.

### 5.5 Recursos que faltan o cambian

| Caso | Respuesta |
|---|---|
| Falta una imagen al abrir la escena | La escena se abre. El nodo se ve como una caja con una cruz y su nombre. Aviso con [Buscar...] y [Quitar la imagen]. El nombre del fichero **no se borra** de la escena al guardar: puede que el disco no esté puesto. |
| Falta una escena instanciada | El nodo se ve como "(falta bicho.escena)". Sus cambios locales se guardan tal cual. |
| Faltan muchos (se movió un cajón) | Un solo aviso: "Faltan 14 ficheros de `graficos/`. [Buscar el cajón...]". Elegir el cajón nuevo los arregla todos. |
| Se renombra un recurso desde el editor | Se cambian todas las escenas del proyecto que lo usan. Antes, la lista de cambios, como el renombrar de Forja. |
| Se renombra fuera | Es el caso "falta". "Buscar..." ofrece primero los ficheros con el mismo tamaño o parecido nombre. |
| La imagen cambia de tamaño | Los `Shape` no cambian solos. Aviso: "jugador.iff ha pasado de 32x32 a 24x32. [Ajustar las cajas] [Dejarlo]". |
| Se quita una animación que un nodo usa | Aviso en el nodo. El desplegable enseña la que falta entre paréntesis. |
| La imagen tiene más colores que la pantalla del juego | Aviso con el número. [Abrir en Sprites]. |
| Se borra del mapa la capa de choques | Aviso en el `TileMap`: "Sin capa de choques: los cuerpos no chocarán con el mapa." |
| Escena que se instancia a sí misma (o en círculo) | No se deja: el selector de escenas no la ofrece, y si llega por el fichero, se abre como "(ciclo)". |
| Rutas | Siempre relativas al cajón del proyecto, con `/`. Un proyecto se puede mover de cajón y de disco. |

### 5.6 Conflictos entre comportamientos y entre escalones

- **Dos que mueven** (`Platformer` y `EightWay`): los dos funcionan, uno tras otro, y el resultado es raro. Aviso
  al añadir el segundo: "Ya hay uno que mueve: Platformer. [Cambiarlo por EightWay] [Poner los dos]". Poner los
  dos es válido (un `Platformer` con un `Sine`), por eso no se prohíbe.
- **Orden**: de arriba abajo, y se ve: los bloques están numerados. Cambiar el orden es arrastrar o [^][v].
- **Uno que quita y otro que usa** (`DestroyOffscreen` y un evento "Al quitarse"): sin conflicto, pero el evento
  "Al quitarse" existe para eso.
- **Hoja y script que hacen lo mismo** (tras la puerta 3, si se vuelve a encender la hoja): aviso fijo en la
  página Eventos mientras dure.
- **Instancia y escena**: una fila de eventos en la escena `bicho` vale para todos. Una instancia puede **añadir**
  filas y **apagar** las heredadas, no cambiarlas (propuesto). Las heredadas se ven en tenue con ">". Cambiar una
  heredada pide abrir la escena. Así no hay tres versiones de la misma fila.
- **Mismo evento en dos filas**: se ejecutan las dos, en orden. Es lo normal. No es un aviso.
- **Señales en cadena** (A avisa a B, que avisa a A): Fragua reparte la cola una vez por fotograma, así que no se
  cuelga: da una vuelta por fotograma. El editor avisa si ve el ciclo en las filas.

### 5.7 Deshacer tras ejecutar

- Jugar no cambia la escena ni la pila. Tras Esc, Amiga-Z deshace lo último que se hizo **antes** de jugar.
- El menú lo dice: "Deshacer: subir Salto a 8". Sin sorpresa.
- Como F5 guarda, deshacer después deja la escena "cambiada" (con `*`), que es la verdad: ya no es la guardada.
- Los valores cambiados "al momento" durante una prueba (3.2.1) **sí** son cambios del editor: cada deslizador
  movido es un paso de la pila, igual que sin el juego en marcha.
- Si se cierra y se abre la escena, la pila se pierde. Se dice en la ayuda, no en un aviso.
- "Volver a lo guardado" (menú Escena) es un paso más de la pila: también se deshace.

### 5.8 Ficheros abiertos o cambiados fuera

| Caso | Respuesta |
|---|---|
| El `.escena` cambia en disco con el editor abierto (git, otro editor) | Al volver la ventana delante (suceso `VUELTA` de Forja) se mira la fecha. Sin cambios en el editor: se recarga y se dice. Con cambios: "nivel1.escena ha cambiado en el disco. [Quedarme con lo mío] [Cargar lo del disco] [Ver diferencias]". |
| Ver diferencias | En texto, nodo a nodo: "Jugador: x 96 → 112", "+ Moneda9". Por eso el JSON de la escena se escribe estable: una propiedad por línea, en orden fijo. Sirve también para git. |
| Conflicto de git dentro del `.escena` | No se puede abrir como escena. Se dice qué es, y se ofrece abrirlo como texto en Forja. |
| El sprite o el mapa se guarda en su editor | La vista se refresca sola (`GUARDADO`). |
| El script cambia en Forja | La página Script relee los símbolos. Si desaparece una función que una fila llama: "!" en la fila. |
| Se edita a mano el `.escena.dash` generado | No se puede en Forja (solo lectura). Si se hace fuera: al generar, el editor ve que la marca del fichero no casa y pregunta: "El código generado se cambió a mano. Se va a perder. [Guardar copia y seguir] [Cancelar]". |
| La misma escena abierta dos veces (dos Forjas) | El segundo la abre en solo lectura, con aviso. Un fichero de cerrojo en `T:`. |
| Una escena y la escena que la instancia, abiertas a la vez | Al guardar la de dentro, la de fuera se refresca. Si la de dentro tiene cambios sin guardar, la de fuera enseña la guardada y lo dice en la pestaña. |
| Forja se cierra con escenas sin guardar | Lo de siempre de las extensiones: `SINGUARDAR`, y Forja pregunta. |
| Corte de luz o cuelgue | Copia de seguridad cada pocos minutos en el cajón del proyecto (`nivel1.escena.copia`, propuesto, se apaga). Al abrir: "Hay una copia más nueva de esta escena. [Usarla] [No]". |

### 5.9 MUI 3.8 frente a MUI 5

El editor tiene que ir igual en los dos. Las reglas, que salen de lo aprendido en Forja:

| Tema | MUI 3.8 | Decisión |
|---|---|---|
| Clases de fuera (NList, Listtree, TextEditor) | No vienen | No se usan. Árbol, listas con miniatura y hoja de eventos van en lienzos propios. Los campos de texto son de una línea. |
| Menús que cambian con la ventana abierta | Cierran y abren la ventana | Los menús del editor son fijos. Lo que cambia (escenas recientes) va en una ventanita, no en el menú. |
| Dejar el cursor en un campo al abrir una ventana | Se pierde; Forja lo arregla dándolo dos veces | Las ventanitas con buscador usan el mismo arreglo. Se prueba en 3.8. |
| Arrastre en lienzo con búfer | Llega el primer movimiento y no el soltar; en MUI 5, nada | Lienzos sin búfer donde se arrastra, o arreglarlo en Dash (se pide). Todo arrastre tiene tecla. |
| Arrastrar entre dos objetos (de Recursos a la vista) | Hay que probarlo en los dos (`mui_on_drop`) | Si falla en uno: "elegir y luego clic para soltar" hace lo mismo. Es además más cómodo con un ratón malo. |
| Burbujas de ayuda | Las hay en los dos (de memoria) | Se usan, sin depender: la barra de estado enseña el mismo texto. |
| Menú de contexto | Lo hay en los dos (de memoria) | Se usa, sin depender (menú Nodo). |
| Pestañas (`mui_register_begin`) | Gastan alto | En pantalla pequeña, `mui_cycle`. |
| Rueda del ratón | No siempre | Todo tiene tecla. |
| Velocidad de pintado | En RTG con 3.8, bien; en AGA, lento | Calidades de vista y arrastre con marco. |

Regla de pruebas: cada fase pasa en MUI 5 (A1200, 3.1) y en MUI 3.8 (`sys32rtg38`), como el resto de Forja.

### 5.10 Sin RTG

- **640x256 con 4 colores** (un Workbench de fábrica): vista en Cajas. Todo el editor funciona. Las imágenes se
  ven en la miniatura de Recursos con tramado. Para verlas bien: F7.
- **640x256 con 16 colores** (AGA, recomendado): Aproximada. El editor pide a la pantalla los lápices que pueda.
- **Forja en su propia pantalla** (ya se puede, pantalla `FORJA`): se aconseja al crear el primer proyecto de
  juego: "Para ver los gráficos mejor, Forja puede abrir su pantalla con 64 colores. [Hacerlo]". Es lo que más
  mejora la experiencia sin RTG.
- **El píxel alto**: en 640x256 el juego de 320x256 se pinta a 2x1 y se ve con su forma. En 640x512 entrelazado, a
  2x2. El editor lo calcula del modo de pantalla; no se pregunta.
- **Chip**: en un Amiga sin fast, las imágenes del editor y las de la pantalla comparten los 2 MB. De ahí el modo
  Cajas automático con poca memoria (5.3).
- **Velocidad**: en AGA, pintar en una ventana de 8 planos es lo más lento del editor. La vista en 640x256 es
  pequeña a propósito, y se puede bajar la pantalla de Forja a 16 colores.
- **F7 (probar parada) es la respuesta de fondo**: la escena en su pantalla de verdad, con su paleta. Nadie
  necesita RTG para ver cómo queda su juego.

### 5.11 Otros casos

- **Nombres**: dos hermanos con el mismo nombre no se dejan (se añade un número). Nombres con espacios o acentos:
  se dejan en el árbol; en el código se convierten ("Señor Bicho" → `senor_bicho`) y, si dos chocan, se numeran.
  El inspector enseña el nombre en el código cuando difiere.
- **Palabras de Dash como nombre** (`end`, `func`): se dejan en el árbol; en el código llevan un `_`.
- **Escena sin guardar nunca y F6**: pide el nombre antes.
- **Proyecto sin escena inicial y F5**: "¿Cuál es la primera escena? [esta] [elegir...]".
- **Pegar entre proyectos**: los recursos que no están en el destino se listan: [Copiarlos] [Pegar sin ellos].
- **Idioma**: una escena hecha con Forja en castellano se abre igual en inglés. En el fichero van los nombres de
  la API, nunca los traducidos.
- **Versiones**: el `.escena` lleva la versión del formato y la de Fragua. Una escena más nueva que el editor se
  abre en solo lectura, con lo que no entiende guardado tal cual. Nunca se guarda perdiendo datos que no se
  entienden.
- **Un nodo de un tipo que Fragua ya no tiene**: se ve como "(desconocido: Luz)" y se conserva.
- **Accesibilidad**: todo con teclado; nada solo por color; la fuente es la de MUI del usuario; los iconos de la
  barra tienen texto en la burbuja y en el menú.
- **Zurdos y ratones de un botón**: no se usa nunca el botón derecho como única vía, ni el del medio.

---

## 6. Isométrico

### 6.1 El problema de UX

En isométrico todo lo que el principiante da por hecho deja de valer: arriba no es "y menos", lo que está "detrás"
depende de dos números, y poner algo "en esa casilla" con el ratón pide una cuenta. Las herramientas que lo
resuelven mal obligan a pensar en píxeles. El diseño: **en una escena isométrica se piensa en casillas y alturas,
y los píxeles son un detalle que el editor calcula.**

### 6.2 La proyección es de la escena

- Propiedad de la escena: "Proyección": **Plana** (por defecto) o **Isométrica**.
- En isométrica, dos datos más: ancho y alto del rombo. Por defecto 32x16 (2:1), que es lo que se dibuja bien con
  píxeles. Otros corrientes: 64x32, 16x8. "Alto de un nivel de altura": por defecto, el alto del rombo.
- Cambiar una escena con cosas de plana a isométrica pregunta: "[Convertir las posiciones a casillas] [Dejarlas]".
- Los nodos de interfaz no cambian nunca: van en píxeles de pantalla.

### 6.3 Lo que cambia en la vista

```
                    /\
                   /  \            Casilla 3,4  Altura 0
                  /\  /\
                 /  \/  \          (rombo iluminado bajo el puntero)
                /\  /\  /\
               /  \/##\/  \
              /\  /\##/\  /\
             /  \/  \/  \/  \
             \  /\  /\  /\  /
              \/  \/  \/  \/
               \  /\  /\  /
                \/  \/  \/
                 \  /\  /
                  \/  \/
                   \  /
                    \/
```

- **Rejilla en rombo.** G la enseña. El rombo bajo el puntero se ilumina y la barra dice su casilla.
- **Mover es por casillas.** Arrastrar salta de rombo en rombo. Las flechas siguen los ejes del rombo: arriba es
  "arriba a la derecha" en pantalla. Con un dibujito de los ejes en la esquina de la vista, que dice qué flecha es
  cuál. Con el imán quitado (S) se mueve libre, en fracciones de casilla.
- **La altura es otra cosa.** Re Pág y Av Pág suben y bajan un nivel. Alt + arrastrar en vertical, también. Al
  subir, se ven: la **plomada** (una línea a trazos hasta su casilla) y la **huella** (el rombo de su casilla
  marcado en el suelo). Sin eso, un objeto alto y uno lejano se confunden: están en el mismo sitio de la pantalla.
- **El origen de un nodo es su base**, no su esquina. Al arrastrar una imagen a una escena isométrica, el editor
  pone el origen en el centro del borde de abajo, y lo enseña con una cruz. Se ajusta en el inspector ("Apoyo") o
  arrastrando la cruz con Alt. Es el fallo más corriente: el muñeco que flota o se hunde media casilla.
- **Tamaño en casillas.** Un mueble de 2x1 lo dice en su `Shape`: "Ocupa: 2 x 1 casillas, 1 de alto". La huella
  enseña las dos casillas. El choque en isométrico es por casillas y altura, no por la caja del dibujo.

### 6.4 El orden de dibujo, sin que el usuario lo piense

- En una escena isométrica, el orden lo pone Fragua: primero lo de más atrás (menor casilla x + casilla y), y a
  igualdad, lo de menos altura. La capa (`z`) sigue existiendo, pero solo para separar suelo, cosas e interfaz.
- El editor pinta con ese mismo orden. Lo que se ve es lo que saldrá.
- **Cuando falla** (objetos de varias casillas que se cruzan: es un límite conocido del método), el editor lo ve
  y avisa: "Mesa y Banco no se pueden ordenar bien: se cruzan. [Partir Mesa en dos trozos] [Dejarlo]". Mejor decir
  el límite que dejar que el usuario lo descubra jugando.
- Para casos raros, un "Ajuste de orden" por nodo (-2 a +2), en un bloque plegado "Avanzado".

### 6.5 Alturas sin lío

- **Filtro de altura**: Alt + 0 a 9 enseña "hasta la altura N"; lo de más arriba, tramado y sin poder elegirse.
  Alt + punto vuelve a todas. Como los pisos de un editor de mapas.
- **Sombra de altura**: "Ver > Teñir por altura" pone un tramado distinto a cada nivel, en modo Cajas. Para ver un
  nivel con varias alturas de un golpe.
- El **mapa** isométrico: el editor de Mapas necesita tiles en rombo y, para las alturas, una capa por nivel
  (decisión de `MAPAS_DISENO.md`: hoy los tiles son cuadrados; este diseño pide reabrirla). En la escena, el
  `TileMap` isométrico se ve con sus capas apiladas.
- Rampas y escaleras: un tipo de celda de choque "rampa" con dirección. Fuera de la primera entrega.

### 6.6 El inspector en isométrico

```
| Nombre    [Mesa          ]             |
| Casilla   x[ 3 ] y[ 4 ]                |
| Altura    [ 0 ] [-][+]                 |
| Ocupa     [ 2 ] x [ 1 ]  alto [ 1 ]    |
| Apoyo     x[ 16] y[ 28]  [Al centro]   |
| > Posición en pantalla  (144, 96)      |
| > Avanzado                             |
```

"Posición en pantalla" va plegada y es de solo lectura. Quien la busca la encuentra; quien no, no la ve.

### 6.7 Qué se entrega primero y qué después

1. Primero: proyección de escena, rejilla en rombo, mover por casillas, apoyo, orden automático, `IsoMove`,
   plantilla. Suelo hecho con un sprite grande o con nodos, sin mapa isométrico.
2. Después: alturas con plomada y filtro, `Shape` en casillas, choques por casilla.
3. Después: tiles en rombo en Mapas y `TileMap` isométrico con capas por altura.
4. Después: rampas, objetos que se cruzan partidos solos.

Lo que el principiante no ve nunca: la fórmula. Lo que el que sabe puede ver: C enseña en el código
`iso_to_screen(cx, cy, h)`, que es una función pública de Fragua (propuesto).

---

## 7. Pensando en el 3D con MiniGL

El 3D va aparte ("Fragua 3D": RTG, MiniGL, `Float`; `docs/3D_DISENO.md`). No se diseña aquí. Lo que sí se decide
aquí es no cerrarle la puerta.

| Decisión de ahora | Por qué no cierra el 3D |
|---|---|
| **El editor se monta desde `api/fragua.json`**: nodos, propiedades, tipos de control, comportamientos, eventos, acciones | `Node3D`, `Camera3D`, `MeshInstance3D` y `Light3D` entran añadiendo entradas, no código del editor |
| **La vista es una pieza cambiable ("visor") con una interfaz pequeña**: pintar, qué hay bajo el puntero, pasar de pantalla a mundo y al revés, asas del elegido | Hoy hay dos visores: plano e isométrico. El 3D es el tercero. El isométrico obliga a hacerlo bien ya: es el ensayo. |
| **Árbol, inspector, comportamientos, eventos, script, recursos y deshacer no saben de proyecciones** | Sirven tal cual |
| **Las posiciones en el `.escena` son listas**: `"pos": [96, 128]` | `[x, y, z]` sin cambiar de formato. Igual escala y giro (`"rot": [0]` → tres ángulos) |
| **Los números del fichero admiten decimales**, aunque la 2D use enteros y `Fixed` | El 3D usa `Float` |
| **Cada escena dice su clase**: `"clase": "2d"`, `"iso"`, y un día `"3d"` | El editor elige visor y el conversor elige Fragua o Fragua 3D. Una escena 3D en un editor viejo se abre en solo lectura. |
| **Las cuatro herramientas (elegir, mover, girar, escalar) existen ya**, aunque girar y escalar estén casi apagadas en 2D | Son las del 3D. Las teclas no cambian. |
| **El inspector tiene control de "vector de N números"** | Vale para 2 y para 3 |
| **Los recursos son por clase, con páginas que se añaden** | "Modelos" (`.lwo`, `.obj`) y "Materiales" son páginas nuevas |
| **Las unidades no están en el nombre de las propiedades** (`speed`, no `speed_px`); la unidad va en `api/fragua.json` y el inspector la enseña | En 3D la unidad es otra |
| **La interfaz del juego (`Label`, `Button`) es una capa aparte, en píxeles de pantalla** | Un marcador 2D encima de una escena 3D, como en Godot (de memoria) |
| **"Probar parada" (F7) ya existe como forma de ver lo que la vista no puede** | Sin MiniGL en la máquina, el editor 3D enseña árbol e inspector y la vista en alambre; F7 hace el resto donde haya aceleración |
| **El presupuesto y las calidades de vista son por visor** | El visor 3D tendrá las suyas (alambre, plano, con texturas) |
| **Los comportamientos declaran para qué clase de nodo valen** | `Platformer` no se ofrece a un `Node3D`; un `Orbit` 3D no se ofrece a un `Body` |
| **Eventos y acciones hablan de nodos, grupos, variables y señales**, no de píxeles | Casi todos valen en 3D |

Lo que **no** se hace ahora: ningún visor 3D, ningún nodo 3D, ninguna cámara libre. Solo se evita escribir "x, y"
donde debería poner "posición".

Una advertencia: no llevar esto demasiado lejos. El criterio es "no cuesta casi nada hoy". Si una generalidad para
el 3D complica el editor 2D, se deja para cuando el 3D exista.

---

## 8. Plan de entrega por fases

Cada fase deja algo que una persona puede usar y una prueba automática que lo comprueba. El orden busca que cada
fase sirva sin las siguientes.

### Fase 0. El formato y un juego hecho a mano

- **Usable:** una escena escrita a mano en JSON se convierte en `.dash`, compila y corre. Las seis plantillas de
  juego existen como proyectos, aunque se editen a mano.
- **Se comprueba:** `tools/escena.py` con escenas de prueba; el `.dash` generado compila con `./dash` y `./dash
  --gcc`; las plantillas corren en el emulador.
- **De Fragua:** formato `.escena` (F1), conversor (F2), `api/fragua.json` (H1), plantilla (H2). En el formato: la
  parte "editor" (rejilla, zoom), posiciones como listas, clase de escena, versión.
- **De Forja:** nada.
- **De Dash:** `f()[0]` y el fallo de `x.close()` con `--gcc` ayudan, no bloquean.

### Fase 1. Árbol e inspector, sin vista

- **Usable:** abrir un `.escena`, ver el árbol, añadir, quitar, renombrar, mover y duplicar nodos, cambiar
  propiedades con sus controles, guardar, F5 y F6. Deshacer. Se puede montar una escena entera poniendo números.
- **Se comprueba:** prueba que crea una escena de 5 nodos solo con teclas, la guarda, compara el JSON, la ejecuta y
  mira la salida. En MUI 5 y 3.8, en 640x256 y en RTG.
- **De Fragua:** `api/fragua.json` completo para los nodos de la capa 2, con tipos de control y rangos.
- **De Forja:** extensión con `tipos = .escena` y `nuevo`; plantillas de proyecto que abren una escena al crearse;
  saber cuándo acaba el programa ejecutado y con qué código (hoy: `ESTADO` a intervalos; mejor un suceso
  `EJECUTADO rc`, propuesto).
- **De Dash:** nada nuevo.

### Fase 2. La vista

- **Usable:** ver la escena, elegir, mover con ratón y flechas, rejilla, imán, zoom, desplazar, capas, las tres
  calidades. Disposición de 640x256 y de pantalla grande.
- **Se comprueba:** arrastres simulados (`input_drag`) y posición final en la sonda; capturas comparadas; tiempos
  de pintado con tope (escena de 50 nodos: menos de 1 s entera, menos de 100 ms al mover uno, por medir).
- **De Fragua:** una función o tabla que diga el rectángulo y el orden de pintado de cada nodo, la misma que usa
  el juego, para que el editor no la duplique.
- **De Forja:** nada.
- **De Dash:** arrastre fiable en lienzos (`input_drag` con búfer, en MUI 5 y 3.8); pintar un BOB escalado 2x1
  para el píxel alto, o que el editor haga el BOB mayor como ya hace Mapas con su zoom.

### Fase 3. Recursos, instancias y los otros editores

- **Usable:** páginas de recursos con miniaturas; arrastrar o colocar con Return; instanciar escenas y abrirlas;
  cambios locales de una instancia; doble clic abre Sprites o Mapas y la vista se refresca; objetos del mapa como
  nodos; recursos que faltan.
- **Se comprueba:** escena con tres instancias, cambio en la escena de dentro que llega a las tres; quitar un
  fichero y abrir: aviso y nada perdido al guardar.
- **De Fragua:** instancias con propiedades cambiadas en el formato; objetos del mapa a escenas.
- **De Forja:** que una extensión pueda pedir abrir un fichero de otra (`ABRIR` ya lo pasa a quien toque) y
  enterarse de que se guardó (`GUARDADO`, ya está). Poner delante la ventana de otra extensión (propuesto).
- **De Dash:** `mui_on_drop` entre lienzos probado en MUI 3.8 y 5.

### Fase 4. Comportamientos

- **Usable:** página Comportamientos, con los doce de Fragua; "¿Qué quieres que haga?"; avisos de conflicto;
  ajustes del juego (acciones de entrada, variables). **Primer hito grande: el recorrido 4.1 completo.**
- **Se comprueba:** el recorrido 4.1 grabado, con su cuenta de clics y segundos.
- **De Fragua:** fase E entera; cada comportamiento descrito en `api/fragua.json` con lo que toca ("mueve",
  "dibuja") y para qué nodos vale; animaciones por nombre en `Platformer` y `EightWay`.
- **De Forja:** ayuda de Fragua en F1 (fichas desde `api/fragua.json`, como la ayuda de Dash) y completado.
- **De Dash:** nada nuevo.

### Fase 5. Eventos, acciones y código

- **Usable:** hoja de eventos por nodo, con las tablas mínimas; C enseña el código; ida y vuelta entre código y
  fila; las tres puertas a script; página Script. **Segundo hito: recorridos 4.2, 4.8 y 4.10.**
- **Se comprueba:** por cada evento y cada acción, una escena mínima que lo usa, compila y da la salida esperada;
  "pasar a script" no cambia la salida de una partida grabada; el código generado es idéntico entre dos
  generaciones seguidas (estable).
- **De Fragua:** F3; señales de los comportamientos; la tabla "línea → nodo, fila" del conversor; el conversor
  disponible en el Amiga (hoy `tools/escena.py` es de Python: en el Amiga hace falta en Dash, dentro de la
  extensión o como orden aparte).
- **De Forja:** abrir un fichero en solo lectura con resaltado y con un rótulo ("Generado: no se edita");
  suceso de una tecla en esa pestaña para volver a la extensión; añadir una función a un `struct` de un fichero
  abierto (`CAMBIAR` ya existe; hace falta saber la línea del `end` del struct: los símbolos de Forja la tienen,
  falta darla por ARexx, propuesto: `SIMBOLOS fichero`).
- **De Dash:** el error de "no cumple la interfaz" con la línea buena.

### Fase 6. Depurar

- **Usable:** probar con formas; teclas F1 a F6 en el juego de prueba; "¿Por qué no chocan?"; errores al jugar que
  llevan al nodo; presupuesto; árbol "En marcha". **Hito: recorrido 4.9.**
- **Se comprueba:** una escena con cada fallo de choques de 4.9, y que la herramienta lo nombra; un error de `nil`
  provocado, y que el editor elige el nodo.
- **De Fragua:** modo de depuración (dibujo de formas, medidor, pausa y paso, puerto ARexx del juego); tabla de
  costes como datos.
- **De Forja:** que el depurador pueda decir a una extensión dónde paró (propuesto).
- **De Dash:** nada nuevo, salvo lo que pida el puerto.

### Fase 7. Géneros, plantillas y el curso

- **Usable:** los comportamientos propuestos (`GridMove`, `Vehicle`, `Shooter`, `Spawner`, `Path`, `Scroller`,
  `Sine`, `Button`); las seis plantillas terminadas; plantillas de escena; el curso de la moto con su proyecto por
  capítulo; mapa de escenas. **Hito: recorridos 4.3 a 4.6.**
- **Se comprueba:** cada plantilla corre en A1200 y A500 a 50 Hz o dice lo que pierde; cada capítulo del curso se
  rehace con una prueba grabada.
- **De Fragua:** esos comportamientos; cámara con scroll suave.
- **De Forja:** el curso en la ventana de la ayuda, con "Abrir el proyecto de este capítulo".
- **De Dash:** **scroll de hardware** (el matamarcianos y la moto lo piden); reservar canales de sonido.

### Fase 8. Isométrico

- **Usable:** lo de 6.7, en sus cuatro pasos. **Hito: recorrido 4.7.**
- **De Fragua:** proyección isométrica, orden por profundidad, `IsoMove`, `iso_to_screen`, choques por casilla.
- **De Forja (Mapas):** tiles en rombo y capas por altura.
- **De Dash:** `tilemap_draw` con tiles en rombo, si se quiere rápido.

### Fase 9. Pulido

- Historial de deshacer, ajuste a otros nodos, copia de seguridad, diferencias de escenas, comportamientos del
  usuario, valores al momento durante la prueba.
- Prueba en un Amiga de verdad (Forja aún no se ha probado en uno).

### Fase 10. 3D

- Aparte, cuando Fragua 3D exista. El visor 3D y la página de modelos.

### Orden y dependencias, en una línea

0 → 1 → 2 → 3 → 4 → 5 son una cadena. 6 puede ir en paralelo con 5. 7 necesita 4 y 5. 8 necesita 2 y 3. Lo que
puede bloquear desde fuera: el conversor en el Amiga (fase 5), el arrastre en lienzos (fase 2) y el scroll de
hardware (fase 7).

---

## 9. Cómo se prueba la UX

### 9.1 Tres clases de prueba

| Clase | Qué responde | Con qué |
|---|---|---|
| **Automática** | ¿Sigue funcionando, y cuesta lo mismo? | El emulador, como las pruebas de Forja |
| **Recorrido grabado** | ¿Se puede hacer la tarea entera, y en cuántos pasos? | Guiones de teclas y clics sobre FS-UAE, con capturas |
| **Con personas** | ¿Se entiende? | Gente del grupo de Dash, con un guion y un cronómetro |

Las dos primeras no dicen si algo se entiende. La tercera no se puede repetir cada día. Hacen falta las tres.

### 9.2 Pruebas automáticas en el emulador

Sobre lo que Forja ya tiene: `input_click`, `input_drag`, `input_key`, `input_text`, `input_menu`, y la sonda (un
fichero en `RAM:` donde el editor escribe su estado, como Sprites).

- **La sonda del editor de escenas** (`RAM:forja-escena.txt`): disposición en uso, página del panel, nodo elegido,
  herramienta, zoom, calidad, número de nodos, pasos de deshacer, avisos; y una línea por nodo con tipo, nombre,
  posición y rectángulo en la vista. Con eso una prueba pregunta "¿dónde está el Jugador en pantalla?" y pincha
  ahí, sin coordenadas fijas.
- **Cada orden, por sus tres caminos:** una prueba por orden que la hace con ratón, con tecla y con menú, y
  compara el resultado. Si una vía se rompe, se nota.
- **Matriz de máquinas**, la de Forja: A1200 con MUI 5 a 640x256; A1200 a velocidad real (`REAL=1`); RTG con MUI
  5; RTG con MUI 3.8 (`sys32rtg38`); CoffinOS a 1280x1024. Y dos más para este editor: 640x256 con 4 colores, y
  640x512 entrelazado.
- **Ida y vuelta del fichero:** abrir y guardar cada escena de prueba sin tocarla da el mismo fichero, byte a byte.
- **Generación estable:** generar dos veces da el mismo `.dash`. Cambiar una propiedad cambia las líneas
  esperadas y ninguna más.
- **El generado compila y hace lo que dice:** por cada evento y acción, escena mínima, compilar por los dos
  caminos de Dash, ejecutar con una partida grabada (`action_force` de Fragua simula la entrada) y comparar la
  salida.
- **Memoria:** con tope, como `tests/memoria.sh` de Forja. Escena de 50 nodos abierta: no más de N K (por medir).
  Abrir y cerrar 20 veces: la memoria vuelve.
- **Tiempos con tope:** abrir la escena de la plantilla; pintar la vista; mover un nodo; F6 hasta el primer
  fotograma. Medidos a velocidad real. Una subida del 20 % hace fallar la prueba.
- **Casos de borde de la sección 5, uno por uno:** fichero que falta, escena cambiada en disco, memoria baja
  (se reserva memoria antes para dejar poca), script que no compila, escena de 1.000 nodos.
- **Capturas comparadas:** de cada disposición y cada ventanita, en cada máquina de la matriz. Se miran a mano
  cuando cambian. Las mismas capturas alimentan el manual y el curso.

### 9.3 Recorridos grabados

Cada recorrido de la sección 4 es un guion: una lista de pasos con lo que se pulsa y lo que hay que ver (por la
sonda o por una captura).

- El guion se ejecuta en el emulador y da tres números: **clics** (pulsaciones de ratón más teclas de orden, sin
  contar el texto escrito), **segundos de máquina** (lo que tarda el Amiga en responder, sumado) y **cambios de
  panel o de ventana**.
- Los segundos de persona no los da el emulador. Se estiman con un modelo sencillo de tiempos por gesto (del
  estilo del "keystroke-level model", de memoria: algo más de 1 s por apuntar con el ratón, unas décimas por
  tecla, algo más de 1 s por decidir). Sirve para comparar dos diseños, no como cifra de verdad.
- Los guiones se guardan con el repositorio. Si una fase sube los clics de un recorrido, hay que justificarlo.
- Del guion sale también un vídeo o una tira de capturas, para el curso y la web.

### 9.4 Métricas y objetivos

Objetivos de partida (por medir; se fijan de verdad con la primera versión que funcione y se bajan desde ahí):

| Tarea | Clics | Segundos de máquina (A1200) | Notas |
|---|---:|---:|---|
| De "Nuevo proyecto" a jugar la plantilla | 6 | 25 | Recorrido 4.1, pasos 1 a 4 |
| Cambiar una propiedad de un comportamiento y jugar | 4 | 15 | |
| Añadir un nodo corriente | 3 | 1 | A, dos letras, Return |
| Añadir un sprite desde un recurso | 2 | 1 | Arrastrar, o elegir y Return |
| Duplicar y colocar 8 monedas | 10 | 3 | Sellado |
| Añadir un evento con una acción | 6 | 2 | |
| Hacer que un marcador enseñe los puntos | 5 | 2 | |
| Instanciar una escena y cambiarle una propiedad | 5 | 2 | |
| Ver el código de un nodo | 1 | 2 | C |
| Pasar una fila a script | 3 | 3 | |
| Encontrar por qué dos nodos no chocan | 4 | 3 | |
| De F6 a ver el juego (20 nodos) | 1 | 15 | 3 s en 68040 |
| Volver del juego al editor | 1 | 1 | |
| Deshacer el último cambio | 1 | 0,2 | |

Otras medidas:
- **Tiempo hasta el primer cambio propio** en el recorrido 4.1: menos de 3 minutos.
- **Respuesta al arrastrar:** menos de 100 ms entre mover el ratón y ver moverse el marco, en A1200.
- **Errores sin salida:** número de avisos del editor que no llevan botón de arreglo ni dicen qué hacer. Objetivo:
  cero.
- **Órdenes sin tecla** y **órdenes solo con botón derecho o arrastre**: cero. Lo cuenta una prueba que recorre la
  tabla de órdenes.
- **Líneas de código generado por fila de evento:** de 3 a 8. Si salen 30, el código no es legible.

### 9.5 Con personas

- **Quién:** tres perfiles, del grupo de Dash. Alguien que nunca programó; alguien que hizo algo en AMOS, Blitz o
  GameMaker; alguien que programa en Dash o en C. Con cinco personas por ronda salen casi todos los problemas
  gordos (regla conocida de las pruebas de uso, de memoria).
- **Qué:** el recorrido 4.1 sin ayuda, en voz alta. Luego una tarea abierta: "haz que al coger diez monedas se
  abra una puerta".
- **Qué se apunta:** dónde se paran más de 10 s; qué buscan y dónde lo buscan (eso dice dónde tendría que estar);
  qué palabra no entienden; si encuentran F5, Tab, C y el paso a código sin que se lo digan; si acaban.
- **En qué máquina:** la suya, si puede ser. Un Amiga de verdad con su ratón enseña cosas que el emulador no.
- **Cuándo:** al acabar las fases 4, 5 y 7. Antes de la 4 no hay bastante que probar.
- **Antes de tener editor:** una prueba de papel de las listas "Añadir nodo", "Cuando..." y "Haz...". Se enseña la
  lista y se pregunta: "¿dónde pincharías para que el enemigo desaparezca al tocarlo?". Arregla nombres y grupos
  cuando cambiarlos aún es gratis.
- Cada idea o aviso de una persona se apunta con su nombre, como pide la regla del proyecto.

### 9.6 Qué se mira en cada fase antes de darla por hecha

1. Sus pruebas automáticas pasan en toda la matriz.
2. Los recorridos que toca están grabados, con sus tres números, y no empeoran los de antes.
3. Capturas en 640x256 con 4 colores y en 1280x1024, miradas una a una.
4. Memoria y tiempos dentro del tope.
5. Ningún aviso sin salida y ninguna orden sin tecla.
6. La ayuda (F1) de todo lo nuevo existe en castellano y en inglés.

---

## 10. Preguntas abiertas para el usuario

1. **Nombres en el inspector:** ¿los de la API con el castellano al lado (propuesto), o solo en castellano para
   quien empieza?
2. **F5 guarda sin preguntar** (propuesto, como Godot de memoria), ¿o pregunta?
3. **El código generado, ¿a git por defecto?** (Propuesto: sí, para compilar sin Forja.)
4. **Hoja de eventos por nodo** (propuesto) ¿o también una hoja de la escena entera, como Construct?
5. **Tiles en rombo en Mapas:** la decisión de 2026-11-03 fue solo cuadrados. El isométrico con mapa pide
   reabrirla.
6. **"Esperar" como acción:** fuera de la primera versión (3.3.5). ¿Vale?
7. **Variables de nodo en la hoja de eventos:** fuera de la primera versión (3.4). ¿Vale?
8. **Orden de fases:** ¿el curso de la moto (fase 7) antes que depurar (fase 6)?
9. **Conversor en el Amiga:** ¿dentro de la extensión, en Dash, o una orden aparte que también sirva sin Forja?

## 11. Glosario corto

| Palabra | Qué es |
|---|---|
| Escena | Un árbol de nodos guardado en un `.escena`. Se puede meter dentro de otra. |
| Instancia | Una escena puesta dentro de otra. Sigue a su fichero, salvo en lo que se le cambie. |
| Nodo | Una pieza del juego: un dibujo, un cuerpo, un área, un texto. |
| Comportamiento | Una pieza lista que hace algo con el nodo: andar y saltar, patrullar. Tiene propiedades. |
| Evento | Algo que pasa: un choque, una tecla, un tiempo. |
| Acción | Algo que se hace cuando pasa un evento. |
| Hoja de eventos | Las filas de eventos y acciones de un nodo. |
| Script | Código Dash del usuario para un nodo. |
| Recurso | Un fichero del proyecto que se usa en una escena: imagen, mapa, sonido, escena. |
| Vista | La zona del editor donde se ve y se coloca la escena. |
| Visor | La pieza de la vista que sabe de una proyección: plana, isométrica, 3D. |
| Calidad | Cómo pinta la vista: Cajas, Aproximada o Fiel. |
