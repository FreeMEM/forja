# Pruebas de Forja

En FS-UAE, con el worktree de Dash 2.0 que compila (hoy `.worktrees/ide-piezas`) y `DASH_KICKSTART` puesto:

    tests/ventana.sh ~/Projects/FreeMEMLang/.worktrees/ide-piezas captura.png 15

Abre `tests/prueba/juego/main.dash` (en el emulador, `DH0:Prueba/juego/`) y saca una captura por cada segundo
dado. `CIERRE=s` cambia cuándo se cierra Forja (30 s) y `TIEMPO=s` el tope del emulador.
