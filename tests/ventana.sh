#!/bin/sh
# Forja en FS-UAE con capturas, abriendo tests/prueba/juego/main.dash.
#
#   tests/ventana.sh DASH_DIR captura.png [segundos...]
#
#   CATALOGOS=1 tests/ventana.sh ...   # con build/Catalogs (tools/catalogos.py catalog): sale en inglés
#   RTG=1 tests/ventana.sh ...   # en AmigaOS 3.2 con tarjeta gráfica de 256 colores (sys32rtg8): se ven los colores
#   PRUEBA= tests/ventana.sh ...   # sin abrir ningún fichero: la bienvenida, con el logo de Dash
#   SPRITE=1 tests/ventana.sh ...  # abre en el editor de sprites una nave de ejemplo
#   ACOPLADO=1 tests/ventana.sh ... # abre en el editor de sprites un sprite acoplado de ejemplo
#   PANTALLA=1 tests/ventana.sh ... # con la preferencia de abrir Forja en su propia pantalla
#
# DASH_DIR: el worktree de Dash 2.0 que compila (./dash y tools/emu_run.py). Forja se cierra sola a los 30
# segundos. Una captura por cada segundo dado (por defecto 12): captura-12.png...
set -e
dash=$1; png=$2; shift 2
[ $# -gt 0 ] || set -- 12
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# el sistema con MUI y las fuentes del Workbench (Helvetica)
maquina=""
if [ -n "$RTG" ]; then
  cp -r "$HOME/.cache/dash-emu/sys32rtg8" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba"
# con CATALOGOS=1, el catálogo inglés junto al programa (PROGDIR:Catalogs; el sistema emulado está en inglés)
[ -z "$CATALOGOS" ] || cp -r "$aqui/build/Catalogs" "$tmp/sys/Catalogs"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
# SPRITE=1: abre una nave de ejemplo (un BOB de 32x32 de 16 colores y 4 fotogramas, hecho con tests/iff.py)
if [ -n "$SPRITE" ]; then
  python3 -I - "$tmp/nave.txt" <<'PY'
import math, sys
filas = []
for y in range(32):
    fila = ""
    for f in range(4):
        for x in range(32):
            dx, dy = x - 15.5, y - 15.5
            r = math.hypot(dx, dy)
            c = 0
            if abs(dx) < 3 and 2 < y < 28:
                c = 9 if y > 20 else 12
            if r < 13 and abs(dy) < 4 + abs(dx) / 3 and abs(dx) > 2:
                c = 3 if dy < 0 else 2
            if 24 <= y <= 27 and abs(dx) < 2 + f:
                c = 8 + f % 2
            if r < 3:
                c = 13
            fila += "%X" % c
    filas.append(fila)
pal = "000000 FFFFFF 777777 BBBBBB 444444 AA0000 FF5555 AA5500 FFAA00 FFFF55 00AA00 55FF55 00AAAA 55FFFF 0000AA 5555FF"
open(sys.argv[1], "w").write("128 32 4\n" + "\n".join(filas) + "\npaleta " + pal + "\n")
PY
  python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/nave.iff" "$tmp/nave.txt" --frja "1 0 32 6"
  PRUEBA=${PRUEBA-DH0:Prueba/juego/nave.iff}
fi
# ACOPLADO=1: abre un sprite acoplado de ejemplo (16x16, 15 colores y el transparente, 2 fotogramas)
if [ -n "$ACOPLADO" ]; then
  python3 -I - "$tmp/acoplado.txt" <<'PY'
import math, sys
filas = []
for y in range(16):
    fila = ""
    for f in range(2):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            r = math.hypot(dx, dy)
            c = 0
            if r < 7.5:
                c = 1 + min(14, int(r * 2))
            if r < 7.5 and abs(dx) < 1 + f and y > 9:
                c = 15
            fila += "%X" % c
    filas.append(fila)
pal = " ".join("%02X%02X%02X" % (17 * i, 255 - 12 * i, 64 + 12 * i) for i in range(16))
pal = "000000 " + pal.split(" ", 1)[1]
open(sys.argv[1], "w").write("32 16 4\n" + "\n".join(filas) + "\npaleta " + pal + "\n")
PY
  python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/acoplado.iff" "$tmp/acoplado.txt" --frja "1 1 16 6"
  PRUEBA=${PRUEBA-DH0:Prueba/juego/acoplado.iff}
fi
# PANTALLA=1: la preferencia ENV:Forja/pantalla
[ -z "$PANTALLA" ] || printf 'MakeDir >NIL: ENV:Forja\nSetEnv Forja/pantalla si\n' >> "$tmp/sys/S/Startup-Extra"
prueba=${PRUEBA-DH0:Prueba/juego/main.dash}
[ -z "$prueba" ] || echo "SetEnv FORJA_PRUEBA $prueba" >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} $maquina --system "$tmp/sys" --autoclose ${CIERRE:-30} $shots "$aqui/src/main.dash"
