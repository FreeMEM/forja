# Pruebas de Forja

En FS-UAE, con el worktree de Dash 2.0 que compila (hoy `.worktrees/ide-piezas`) y `DASH_KICKSTART` puesto:

    tests/ventana.sh ~/Projects/FreeMEMLang/.worktrees/ide-piezas captura.png 15

Abre `tests/prueba/juego/main.dash` (en el emulador, `DH0:Prueba/juego/`) y saca una captura por cada segundo
dado. `CIERRE=s` cambia cuándo se cierra Forja (30 s) y `TIEMPO=s` el tope del emulador.

Con un usuario de prueba: `tests/teclas.sh <worktree de Dash> [captura.png segundos...]`. `tests/teclas.dash`
escribe un programa en el editor (sangría automática, Tab, Retroceso), corta con Mayúsculas + Alt + izquierda y
Amiga-X, pega, deshace dos veces y pone el cursor con un clic. Comprueba el texto con la sonda de Forja
(`ENV:FORJA_SONDA`) y acaba con "TODO BIEN".
