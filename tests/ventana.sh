#!/bin/sh
# Forja en FS-UAE con capturas, abriendo tests/prueba/juego/main.dash.
#
#   tests/ventana.sh DASH_DIR captura.png [segundos...]
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
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash" >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} --system "$tmp/sys" --autoclose ${CIERRE:-30} $shots "$aqui/src/main.dash"
