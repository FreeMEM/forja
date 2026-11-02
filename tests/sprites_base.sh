#!/bin/sh
# src/sprites.dash sin ventana (tests/sprites_base.dash), en FS-UAE. Acaba con "TODO BIEN".
#
#   tests/sprites_base.sh DASH_DIR
#
# Con un sistema (sys31muisslweb): los textos del editor usan locale.library, que el Kickstart 3.1 no trae en ROM.
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} --system "$tmp/sys" "$aqui/tests/sprites_base.dash"
