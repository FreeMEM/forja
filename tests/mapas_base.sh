#!/bin/sh
# src/mapas.dash sin ventana (tests/mapas_base.dash), en FS-UAE. Acaba con "TODO BIEN".
#
#   tests/mapas_base.sh DASH_DIR
#
# DASH_DIR: un Dash con tilemap_*. Con un sistema (sys31muisslweb): los textos usan locale.library.
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
cd "$dash" && python3 tools/emu_run.py --dash2 --timeout ${TIEMPO:-120} --system "$tmp/sys" "$aqui/tests/mapas_base.dash"
