# Pruebas de Forja

En FS-UAE, con el worktree de Dash 2.0 que compila (hoy `.worktrees/ide-piezas`) y `DASH_KICKSTART` puesto:

    tests/ventana.sh ~/Projects/FreeMEMLang/.worktrees/ide-piezas captura.png 15

Abre `tests/prueba/juego/main.dash` (en el emulador, `DH0:Prueba/juego/`) y saca una captura por cada segundo
dado. `RTG=1` lo hace en AmigaOS 3.2 con tarjeta gráfica de 256 colores (`sys32rtg8`), donde se ven los colores
de la sintaxis; con los 4 colores del Workbench 3.1 casi todo sale blanco. `CIERRE=s` cambia cuándo se cierra Forja (30 s) y `TIEMPO=s` el tope del emulador.

Con un usuario de prueba: `tests/teclas.sh <worktree de Dash> [captura.png segundos...]`. `tests/teclas.dash`
escribe un programa en el editor (sangría automática, Tab, Retroceso), corta con Mayúsculas + Alt + izquierda y
Amiga-X, pega, deshace dos veces y pone el cursor con un clic. Comprueba el texto con la sonda de Forja
(`ENV:FORJA_SONDA`), anota cuánto tarda un dibujo entero y acaba con "TODO BIEN". `REAL=1` emula la CPU a la
velocidad de un A1200 (68020 a 14 MHz) en lugar de al máximo.

`tests/ficheros.sh <worktree de Dash>`: `tests/ficheros.dash` abre `red.dash` desde el panel del proyecto, cambia
de pestaña, guarda `main.dash` con Amiga-S (que sigue en UTF-8) y cierra una pestaña con cambios: Amiga-W pregunta,
Cancelar (Esc) la deja y Descartar (D) la cierra sin guardar. Los diálogos de abrir y guardar como (ASL) no se prueban solos.

`tests/compilar.sh <worktree de Dash> <cajón con dashc.amiga y los dashc_*.drt>`: `tests/compilar.dash` ejecuta el
programa (Amiga-E: compila con dashc y lo ejecuta; su salida debe tener "Naves: 2"), mete un error, compila
(Amiga-K) y hace clic en el error de la salida: el cursor debe ir a su línea. dashc para el Amiga sale de
`make amiga` en `dashc/` de Dash.

`tests/salida.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/salida.dash` ejecuta un programa que escribe 60
líneas y prueba la salida: se ve lo último, su barra la sube, un clic elige una línea y Amiga-C la copia, arrastrando
se eligen varias, un clic en el editor devuelve Amiga-C al editor; y abre las preferencias (con `ENV:FORJA_PREFERENCIAS`,
que solo mira la sonda).

`tests/rexx.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/rexx.dash` maneja Forja por su puerto ARexx
(ABRIR, ABIERTO, SELECCION, CAMBIAR, TEXTO, GUARDAR, COMPILAR, ERRORES, EJECUTAR). La prueba con Inferencia a la vez
está en el repo de Inferencia: `FORJA=~/Projects/forja PERMISO=Si tests/usuario.sh <worktree> tests/juntos.dash`.

`tests/diseno.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/diseno.dash` usa el editor de ventanas con
`ventana.dashui`: elige un botón en el árbol, cambia su texto, prueba un número mal escrito, abre la vista previa,
deshace (en un paso), rehace y guarda; después añade un objeto, lo mueve, lo quita y cambia una opción del menú.

`tests/depurar.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/depurar.dash` pone un punto de parada con F9,
depura (Amiga-G) y comprueba la línea, la pila y las variables con F10, F5, F6 y F7, y la salida al acabar.

`tests/buscar.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/buscar.dash` busca, cambia todo y va a una
línea por ARexx, y abre las ventanas de buscar (Amiga-F) e ir a la línea (Amiga-L) por teclado.

Editor de sprites (`docs/SPRITES_LOOP.md`): `tests/sprites_base.sh <worktree de Dash>` prueba `src/sprites.dash` sin
ventana (píxeles, deshacer y rehacer). `python3 tests/iff.py` crea imágenes IFF ILBM de prueba y lee las que guarda
Forja (`python3 tests/iff.py prueba` se prueba a sí mismo).
`tests/sprites_iff.sh <worktree de Dash>` lee pinceles de `iff.py` (ByteRun1, plano de máscara, GRAB), escribe y
vuelve a leer, comprueba que `bob_load` y `sprite_load` cargan lo escrito y que `iff.py` lo lee igual. Necesita
`DASH_KICKSTART` (3.1): con la ROM de AROS, `sprite_load` se queda colgado.

`tests/sprites_forja.sh <worktree de Dash>`: `tests/sprites_forja.dash` abre `nave.iff` (de `iff.py`), lo ve en el
panel del proyecto, cambia de pestaña, guarda con Amiga-S, crea un BOB con Amiga-B, compila desde la pestaña del
sprite (compila el `.dash` abierto) y prueba Inferencia; `iff.py` comprueba el fichero guardado.

`tests/sprites_dibujo.sh <worktree de Dash> [captura.png segundos...]` mide el dibujo entero del editor de sprites
con 16x16, 32x32 y 64x64 (píxeles casi al azar, lo peor) y una bola de 32x32 (como un sprite de verdad).
`REAL=1` para los tiempos de un A1200; `RTG=1` para ver los colores en las capturas.

Editor de mapas (`docs/MAPAS_DISENO.md`): `tests/mapas_base.sh <Dash>` prueba `src/mapas.dash` sin ventana
(celdas, caja, relleno, capas, tamaño, deshacer, guardar y leer). `tests/mapas_forja.sh <Dash>`: `tests/mapas_forja.dash`
elige tiles, pinta, pone espejo, borra, arrastra el lápiz, hace una caja y un relleno, deshace, usa el cuentagotas,
crea una capa, cambia el ancho y el zoom, mueve la vista y guarda; `tests/fmap.py` mira el fichero guardado.
`tests/mapa_ejemplo.py` hace el tileset y el mapa de ejemplo; `MAPA=1 tests/ventana.sh ...` lo abre para capturas.

`tests/pantalla.sh <worktree de Dash>`: `tests/pantalla.dash` arranca Forja con la preferencia de su propia
pantalla y comprueba que Forja está en `FORJA`, que es la pública por defecto, que un programa que no dice pantalla
abre ahí su ventana, y que al salir la pantalla se cierra y vuelve el Workbench. Necesita un Dash con
`screen_make_default`. `PANTALLA=1 tests/ventana.sh ...` saca capturas con esa preferencia.

`tests/sprites_lapiz.sh <worktree de Dash>`: `tests/sprites_lapiz.dash` pinta con clic y arrastre (en recta y en
diagonal, sin huecos), borra con Alt + clic, coge el color con Ctrl + clic, y deshace y rehace por trazo.

`tests/sprites_paleta.sh <worktree de Dash>`: `tests/sprites_paleta.dash` elige el color con cifras, flechas y un
clic en la paleta, lo cambia con las barras R G B (clic y arrastre, en pasos de 4 bits en un sprite de hardware) y
deshace. `RTG=1` para verlo en 256 colores.

`tests/sprites_herramientas.sh <worktree de Dash>`: `tests/sprites_herramientas.dash` dibuja una línea y una caja
(hueca) arrastrando, rellena (sin entrar en la caja cerrada) y deshace el relleno de una vez, pone el agarre y usa
los botones del panel. La caja rellena (Mayúsculas al empezar) no se prueba: `input_drag` no lleva teclas.

`tests/sprites_tamano.sh <worktree de Dash>`: `tests/sprites_tamano.dash` cambia alto y ancho con Ctrl + flechas y
con los botones de la pestaña Tamaño, los colores (los píxeles pierden sus bits altos), el tipo con T (a sprite de
hardware corta a 16 de ancho y 2 planos) y deshace.

`tests/sprites_fotogramas.sh <worktree de Dash>`: `tests/sprites_fotogramas.dash` duplica (D), hace espejo (H, V),
va de un fotograma a otro (flechas), añade uno vacío (N), lo quita (Supr), lo mueve (Alt + flechas), desplaza el
dibujo (Mayúsculas + flechas), lo vacía (Retroceso), deshace, copia y pega (Amiga-C y Amiga-V) y usa la tira.

`tests/sprites_cebolla.sh <worktree de Dash>`: `tests/sprites_cebolla.dash` enciende y apaga la piel de cebolla (O)
y mira los píxeles de verdad en la pantalla (`screen_pixel`): una celda vacía enseña el color del fotograma
anterior solo con la cebolla encendida.

`tests/sprites_animar.sh <worktree de Dash>`: `tests/sprites_animar.dash` pone en marcha la vista animada (Espacio),
comprueba que los fotogramas pasan solos, cambia la velocidad (+ y -), la para, usa los botones de la pestaña
Animar y mira que cambiar de pestaña la para.

`tests/sprites_codigo.sh <worktree de Dash>`: `tests/sprites_codigo.dash` pulsa C en un sprite de hardware y en un
BOB y guarda lo copiado; después el script mete cada código en un programa (con su pantalla y una ventana), lo
compila con Dash y lo ejecuta en el emulador con su IFF: los dos tienen que cargar.

`tests/sprites.sh <worktree de Dash>`: el editor de sprites de principio a fin (`tests/sprites.dash`): abre un pincel
comprimido como los de DPaint, dibuja, rellena, deshace, duplica y voltea, lo pasa a sprite de hardware, guarda,
comprueba con `bob_load` y con `iff.py` que el fichero es lo que enseñaba el editor, mide el cambio de pestaña, crea
un BOB y sale descartando. `tests/sprites_todas.sh <worktree de Dash>` pasa todas las de sprites con un resumen
(unos 20 minutos).

Con la sonda, Forja apunta también los eventos que recibe en `RAM:forja-eventos.txt` (número de evento, y en los del
editor la tecla, el botón y los calificadores; en los de arrastre, su estado). Si la prueba tiene abierto un fichero
de la sonda cuando Forja lo escribe, AmigaDOS no deja escribirlo: Forja reintenta (`sonda_fichero`).

`tests/git.sh <worktree de Dash> [cajón de dashgit]`: `tests/git.dash` maneja dashgit desde Forja por ARexx (`GIT` y
`SALIDA`): init, config, status, add, commit, diff, commit -a con un mensaje con comillas, log y push a un servidor
git del PC (`tests/servidor_git.py` de dashgit). Necesita dashgit (por defecto `~/Projects/dashgit`).
