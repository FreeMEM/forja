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
