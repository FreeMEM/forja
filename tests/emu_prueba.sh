#!/bin/sh
# Ejecuta un programa de prueba de Dash (sin ventana) en FS-UAE, con el sistema de las pruebas de Forja y los
# fuentes de Forja en DH0:Prueba/forja (para importarlos desde ahí). Enseña su salida.
#
#   tests/emu_prueba.sh DASH_DIR tests/lienzo_base.dash
set -e
dash=$1; prog=$2
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/forja"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
cp "$aqui"/src/*.dash "$aqui"/src/*.dashui "$tmp/sys/Prueba/forja/"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} --system "$tmp/sys" "$aqui/$prog"
