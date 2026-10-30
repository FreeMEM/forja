#!/bin/sh
# Forja en FS-UAE con capturas, abriendo tests/prueba/juego/main.dash.
#
#   tests/ventana.sh DASH_DIR captura.png [segundos...]
#
#   CATALOGOS=1 tests/ventana.sh ...   # con build/Catalogs (tools/catalogos.py catalog): sale en inglés
#   RTG=1 tests/ventana.sh ...   # en AmigaOS 3.2 con tarjeta gráfica de 256 colores (sys32rtg8): se ven los colores
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
echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash" >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} $maquina --system "$tmp/sys" --autoclose ${CIERRE:-30} $shots "$aqui/src/main.dash"
