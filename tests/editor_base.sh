#!/bin/sh
# src/editor.dash, src/sintaxis.dash y src/teclas.dash sin ventana (tests/editor_base.dash), en FS-UAE: colores,
# comodidades de línea, la pareja, marcadores, buscar con expresiones regulares, plegar... Acaba con "TODO BIEN".
#
#   tests/editor_base.sh DASH_DIR
#   REAL=1 tests/editor_base.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz)
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} "$aqui/tests/editor_base.dash"
