#!/bin/sh
# src/codigo.dash sin ventana (tests/codigo_base.dash), en FS-UAE: símbolos, completar, ayuda de argumentos, ir a la
# definición y dónde se usa, con tests/prueba/juego; y lo que tarda con los fuentes de Forja. Acaba con "TODO BIEN".
#
#   tests/codigo_base.sh DASH_DIR
#   REAL=1 tests/codigo_base.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz)
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/forja" "$tmp/sys/Dash"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
cp "$aqui"/src/*.dash "$aqui"/src/*.dashui "$tmp/sys/Prueba/forja/"
cp -r "$dash/lib" "$tmp/sys/Dash/lib"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} "$aqui/tests/codigo_base.dash"
