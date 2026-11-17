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

`tests/completar.sh <worktree de Dash>`: `tests/completar.dash` escribe "pri" en `main.dash` (sale la lista con Print
y Tab lo mete), "con" (conectar, de `red.dash`, que importa; Return lo mete), "(" (la ayuda de sus argumentos), va a
la definición de conectar con Amiga-J (abre `red.dash` en su línea) y vuelve con Amiga-U, completa un campo tras un
punto con flechas y Return, mira la ayuda de un builtin, busca dónde se usa mover (Amiga-H) y va a su definición con
Ctrl+clic. `tests/codigo_base.sh <worktree de Dash>` prueba `src/codigo.dash` sin ventana (símbolos, locales, campos,
ayuda, definición, dónde se usa) y mide lo que tarda con los fuentes de Forja.

`tests/compilar.sh <worktree de Dash> <cajón con dashc.amiga y los dashc_*.drt>`: `tests/compilar.dash` ejecuta el
programa (Amiga-E: compila con dashc y lo ejecuta; su salida debe tener "Naves: 2"), mete un error, compila
(Amiga-K) y hace clic en el error de la salida: el cursor debe ir a su línea. dashc para el Amiga sale de
`make amiga` en `dashc/` de Dash.

`tests/salida.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/salida.dash` ejecuta un programa que escribe 60
líneas y prueba la salida: se ve lo último, su barra la sube, un clic elige una línea y Amiga-C la copia, arrastrando
se eligen varias, un clic en el editor devuelve Amiga-C al editor; y abre las preferencias (con `ENV:FORJA_PREFERENCIAS`,
que solo mira la sonda).

`tests/botones.sh <worktree de Dash> <cajón con dashc.amiga y los dashc_*.drt> [captura.png]`: `tests/botones.dash`
prueba la barra de botones con el ratón: el puntero encima ilumina Ejecutar, Seguir en gris no hace nada, Compilar
compila, Depurar depura un programa que tarda (con el depurador encendido y Compilar en gris) y Parar lo para. Con
`captura.png`, guarda `captura-encima.png` y `captura-depurando.png` (las hace el propio Amiga con `screen_save_png`).

`tests/clic.sh <worktree de Dash> <cajón con dashc.amiga y los dashc_*.drt>`: `tests/clic.dash` hace clic con el
ratón mientras depura (lo contó David Martínez): en el editor, el código no salta y el cursor se queda donde se pulsó;
en el panel de las variables, no se abre el fichero de la lista que hay debajo; ya sin depurar, la lista vuelve a
abrir ficheros. Con `FORJA=otro/cajón` prueba las fuentes de ese cajón (para ver que la prueba falla sin el arreglo).
`RAM:forja-vistas.txt` (con la sonda) apunta la primera línea de cada dibujo entero del editor.

Las de uso a fondo (`docs/PRUEBAS_LOOP.md`). Todas reciben `<worktree de Dash> <cajón con dashc.amiga y los
dashc_*.drt>`:

- `tests/proyecto.sh`: un programa de varios ficheros en un cajón con un espacio ("Mi juego": main.dash,
  fisica.dash y lib/pantalla.dash). Ejecuta desde un módulo (se compila main.dash), guarda al ejecutar lo que no
  estaba guardado, hace clic en un error de otro fichero y depura entre ficheros (F6, F7, puntos en dos ficheros).
- `tests/grande.sh`: un fichero de 1505 líneas. Ir al final, Amiga-L, buscar, escribir sin repintar todo, ejecutar,
  deshacer y rehacer. Anota lo que tarda el dibujo.
- `tests/errores.sh`: un programa que falla al ejecutarse en un módulo. El error sale en rojo y a la vista, y un clic
  lleva a su línea.
- `tests/parar.sh`: Parar un bucle sin fin. Necesita Dash con Ctrl-C en los bucles.
- `tests/salir.sh`: salir con un programa ejecutándose y con otro parado en el depurador. No debe quedar nada vivo.
  Arranca Forja él mismo.
- `tests/sesion.sh`: abrir lo de la última vez, cerrar con cambios (Descartar) y una sesión con un disco que no
  está, sin el requester de "Inserta el volumen". Arranca Forja él mismo.

`tests/rexx.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/rexx.dash` maneja Forja por su puerto ARexx
(ABRIR, ABIERTO, SELECCION, CAMBIAR, TEXTO, GUARDAR, COMPILAR, ERRORES, EJECUTAR). La prueba con Inferencia a la vez
está en el repo de Inferencia: `FORJA=~/Projects/forja PERMISO=Si tests/usuario.sh <worktree> tests/juntos.dash`.

`tests/diseno.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/diseno.dash` usa el editor de ventanas con
`ventana.dashui`: elige un botón en el árbol, cambia su texto, prueba un número mal escrito, abre la vista previa,
deshace (en un paso), rehace y guarda; después añade un objeto, lo mueve, lo quita y cambia una opción del menú.

`tests/depurar.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/depurar.dash` pone un punto de parada con F9,
depura (Amiga-G) y comprueba la línea, la pila y las variables con F10, F5, F6 y F7, y la salida al acabar.

`tests/arbol.sh <worktree de Dash> <cajón con dashc.amiga> [captura.png]`: `tests/arbol.dash` prueba el árbol de las
variables (idea de David Martínez) con `tests/prueba/arbol/main.dash`: despliega con clics un struct, uno dentro de
otro y listas (la de 150 números enseña 100 y "... 50 más"), se desplaza a lo ancho con las flechas y con la barra
de abajo y a lo alto con las flechas, y mira que lo desplegado sigue así tras F5. `ENV:FORJA_ARBOL` (con la sonda)
da la zona del panel y la y de cada fila. Con `captura.png`, guarda `captura-desplegado.png`, `captura-ancho.png` y
`captura-lista.png` (las hace el propio Amiga); `RTG=1`, en AmigaOS 3.2 con tarjeta gráfica (ventana grande y colores).

`tests/depurar_ventana.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/depurar_ventana.dash` depura
`tests/prueba/gravedad/main.dash` (`examples/fixed_gravedad.dash` de Dash, que abre su propia ventana): para en la
línea 42, comprueba que Forja vuelve a ser la ventana activa (la del programa se queda el teclado al abrirse) y que F10
avanza a la 45 y a la 46.

Con Dash 2.4.0, `tests/depurar.sh` falla por un fallo de dashc: una función que no se usa (`conectar` de `red.dash`)
deja en la información de depuración una línea que no es un NOP, y el depurador escribe un NOP ahí al seguir; el
programa cae con "Program failed (error #80000004)".

`tests/buscar.sh <worktree de Dash> <cajón con dashc.amiga>`: `tests/buscar.dash` busca, cambia todo y va a una
línea por ARexx, y abre las ventanas de buscar (Amiga-F) e ir a la línea (Amiga-L) por teclado.

Los editores de sprites y de mapas son extensiones (`extensiones/Sprites`, `extensiones/Mapas`): sus pruebas las
compilan y las ponen en `DH0:Prueba/Extensiones` (`tests/extension.sh`), y miran su ventana ("Sprites: x", "Mapas: x")
con su sonda: `RAM:forja-sprites-sonda.txt` y `ENV:FORJA_SPRITES_LIENZO`, `FORJA_SPRITE`, `FORJA_SPRITE_PANEL`,
`FORJA_SPRITE_BOTONES`, `FORJA_SPRITES_PESTANAS`, `FORJA_SPRITES_DIBUJO` (y `RAM:forja-mapas-sonda.txt`,
`FORJA_MAPAS_LIENZO`, `FORJA_MAPA`, `FORJA_MAPA_BOTONES`, `FORJA_MAPAS_DIBUJO`). Amiga-Q se pulsa en la ventana de Forja,
que pregunta por los que la extensión tiene sin guardar.

Editor de sprites (`docs/SPRITES_LOOP.md`): `tests/sprites_base.sh <worktree de Dash>` prueba `extensiones/Sprites/sprites.dash` sin
ventana (píxeles, deshacer y rehacer). `python3 tests/iff.py` crea imágenes IFF ILBM de prueba y lee las que guarda
Forja (`python3 tests/iff.py prueba` se prueba a sí mismo).
`tests/sprites_iff.sh <worktree de Dash>` lee pinceles de `iff.py` (ByteRun1, plano de máscara, GRAB), escribe y
vuelve a leer, comprueba que `bob_load` y `sprite_load` cargan lo escrito y que `iff.py` lo lee igual. Necesita
`DASH_KICKSTART` (3.1): con la ROM de AROS, `sprite_load` se queda colgado.

`tests/sprites_forja.sh <worktree de Dash>`: `tests/sprites_forja.dash` hace que Forja abra `nave.iff` (de `iff.py`) en
la extensión, lo pone delante desde el panel del proyecto, guarda con Amiga-S (Forja lo dice), crea un BOB con Amiga-B
en Forja (la petición con lo que hacen las extensiones) y compila desde el sprite (el `main.dash` de su cajón);
`iff.py` comprueba el fichero guardado.

`tests/sprites_dibujo.sh <worktree de Dash> [captura.png segundos...]` mide el dibujo entero del editor de sprites
con 16x16, 32x32 y 64x64 (píxeles casi al azar, lo peor) y una bola de 32x32 (como un sprite de verdad).
`REAL=1` para los tiempos de un A1200; `RTG=1` para ver los colores en las capturas.

Editor de mapas (`docs/MAPAS_DISENO.md`): `tests/mapas_base.sh <Dash>` prueba `extensiones/Mapas/mapas.dash` sin ventana
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

`tests/actualizar.sh <worktree de Dash>`: `tests/actualizar.dash` prueba `src/actualizar.dash` sin ventana contra un
GitHub de mentira en el PC (un servidor HTTP local con la respuesta de la API y dos tar hechos con
`tools/paquete_amiga.py` de Dash, uno bueno y otro con un CRC estropeado). Un Dash 2.7.0 de mentira en `DH0:Dash`: el
estropeado no cambia nada, Cancelar tampoco, el bueno lo pone al día (y respeta lo que no trae), al día no pregunta y
la consulta automática solo avisa, una vez al día. `GRANDE=build/dash-X.Y.Z-amiga.tar` usa uno de verdad (unos 70 s
en el emulador; dos comprobaciones del contenido fallan, porque son del pequeño).

Extensiones (`docs/EXTENSIONES.md`): `tests/extensiones_base.sh <worktree de Dash>` prueba `src/extensiones.dash` y
`src/marcas.dash` sin ventana (manifiestos, apagadas, menú y teclas, tipos, la cola con su tope, el aviso en ENV:,
marcas, la barra, activar e instalar desde un cajón). `tests/extensiones.sh <worktree de Dash> [<cajón con
dashc.amiga>] [capturas/]`: `tests/extensiones.dash` pone en `DH0:Extensiones` la de ejemplo, Contar, y Eco
(`tests/extensiones/Eco`, que apunta lo que le llega). Contar arranca con Forja y cuenta en la barra; su menú, su
tecla (Ctrl Alt D) y CAMBIADO; la API por ARexx (y lo que cuesta una orden); Eco arranca con su menú y recibe MENU,
GUARDADO, ABIERTO, ACTIVO, PROYECTO, EDITAR, MARCA (un clic en su marca), CERRADO y COMPILADO; Eco se cae (Forja lo
dice y la vuelve a arrancar) y se cuelga (Forja sigue contestando); el gestor la desactiva y la activa. Con
`capturas/`, guarda `marcas.png`, `gestor.png` y `gestor-apagada.png`. `input_menu` no llega a los menús de MUI: las
opciones se eligen con la sonda (`ENV:FORJA_EVENTO` con su evento). Con MUI 3.8:
`SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 tests/extensiones.sh ...`.

Ayuda de Dash y errores marcados (pasos 3.4 y 3.5 de `docs/FORJA_LOOP.md`). Las dos hacen la ayuda con
`tools/gen_ayuda.py` de Dash y necesitan una orden `dash` del Amiga con `--check` (`make amiga` en `dashc/` de Dash):

- `tests/ayuda_base.sh <worktree de Dash> [<cajón con dashc.amiga>]`: `tests/ayuda_base.dash` prueba `src/ayuda.dash` y
  `src/errores.dash` sin ventana: encontrar la ayuda (junto al compilador), una ficha con sus enlaces y su ejemplo para
  Probar, partirla a otro ancho, un clic en un enlace y en un nombre del código, atrás y adelante, buscar, el índice;
  leer los errores de dash, moverlos al escribir y el siguiente (F8); y `dash --check` del Amiga, también en segundo
  plano. Mide lo que tarda cada cosa.
- `tests/ayuda.sh <worktree de Dash> <cajón con dashc.amiga> [capturas/]`: `tests/ayuda.dash`, con Forja como en el
  paquete de Dash (`DH0:Dash/Forja/Forja`, `DH0:Dash/Ayuda`, `DH0:Dash/dash`): F1 sobre `file_seek` abre su ficha; un
  clic en un enlace, Atrás y Adelante; Probar ejecuta el ejemplo en una pestaña sin nombre; buscar "sonido"; Índice y
  enlaces de la portada; F1 sobre un nombre del proyecto sigue dando sus argumentos; un error al guardar se marca, F8 va
  a él, sigue a su línea al escribir encima y se quita al arreglarlo; uno escrito sin guardar se marca tras la pausa y
  deshacer lo quita. Con `capturas/`, `ayuda-ficha.png`, `ayuda-probar.png`, `ayuda-buscar.png`, `ayuda-grupo.png` y
  `errores.png`. Con MUI 3.8: `SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 tests/ayuda.sh ...`.
El copiloto (`extensiones/Inferencia`): `tests/copiloto.sh <worktree de Dash> <repositorio de Inferencia> [<cajón con
dashc.amiga>] [capturas/]` arranca Forja con el copiloto y la Inferencia de verdad, contra el servidor falso de
Inferencia (`tests/servidor_falso.py` de su repositorio) con los guiones de `tests/guiones_copiloto`, y la ayuda de
Dash (`AYUDA=.../Dash.ayuda`; si no, la de `build/ayuda` de Dash, de `tools/gen_ayuda.py`). `tests/copiloto.dash`, sobre
`tests/prueba/copiloto/main.dash`: documentar la función (con la ayuda, la vista, `a`, Amiga-Z), cambiar el código
(su ventana, `r`), explicar la selección y preguntar (a la conversación), escribir la prueba (fichero nuevo), con dashc
explicar y arreglar un error (compila antes), y las sugerencias al escribir (SUGERENCIA y Tab). Guarda
`copiloto-*.png` en `capturas/`. Con MUI 3.8: `SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`; `SOLO=sugerencias`, solo lo
último. El servidor usa el puerto 40900 del PC: `flock /run/user/1000/dash-emu-red.lock tests/copiloto.sh ...`.

El editor cómodo (fase 2 de `docs/FORJA_LOOP.md`):

- `tests/editor_base.sh <worktree de Dash>`: `tests/editor_base.dash` prueba sin ventana `src/sintaxis.dash` (los
  colores de la gramática, también la cabecera y las líneas de un bloque `asm`), `src/editor.dash` (comentar, duplicar,
  subir, bajar y borrar líneas; cerrar solos paréntesis y comillas; el `end` solo; la pareja de un paréntesis y de un
  bloque; buscar y cambiar con expresiones regulares; marcadores que siguen a su texto; plegar), `src/buscar.dash`
  (buscar y cambiar en `tests/prueba/editor`, con un fichero abierto sin guardar y otro en el disco) y `src/teclas.dash`
  (las teclas por defecto y las de un fichero). Mide lo que tarda partir una línea, buscar la pareja de una función
  larga, buscar en el proyecto y las cuentas de las filas con bloques plegados.
- `tests/editor.sh <worktree de Dash> [capturas/]`: `tests/editor.dash`, como un usuario, sobre
  `tests/prueba/editor/main.dash` (con un bloque `asm`): el `end` solo y los paréntesis al escribir; Ctrl /, Ctrl D,
  Ctrl Mayús K, Ctrl Alt arriba y Amiga-Z; la pareja de `func`, `asm` y un paréntesis, y Ctrl M; una tecla con el
  puntero en la salida; Ctrl Mayús F y un clic en lo encontrado; cambiar en el proyecto (la pestaña de cambios y la
  pregunta) y deshacerlo; el esquema (Ctrl O), abrir un fichero (Ctrl P) e ir a un nombre (Ctrl T); marcadores (Ctrl
  F3, F3, Mayús F3) que siguen a su línea; renombrar `doble` (F2) en `main.dash`, abierto, y en `util.dash`, en el
  disco; plegar con F4 y desplegar con la tecla de `ENV:Forja/teclas` (la prueba cambia una tecla y un color, y pone
  una línea mala en cada fichero: se dicen en la salida). Mide el repintado al mover el cursor (dos líneas) y el
  dibujo entero. Con `capturas/`: `editor-colores.png`, `editor-pareja.png`, `editor-cambios.png`,
  `editor-esquema.png`, `editor-renombrar.png` y `editor-plegado.png`. `RTG=1` (256 colores), `REAL=1` (la CPU de un
  A1200) y con MUI 3.8 `SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`.

