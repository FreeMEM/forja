#!/bin/sh
# src/extensiones.dash y src/marcas.dash sin ventana (tests/extensiones_base.dash), en FS-UAE. Acaba con "TODO BIEN".
#
#   tests/extensiones_base.sh DASH_DIR
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
cd "$dash" && python3 tools/emu_run.py --dash2 --timeout ${TIEMPO:-120} --system "$tmp/sys" "$aqui/tests/extensiones_base.dash"
