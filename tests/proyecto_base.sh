#!/bin/sh
# src/proyecto.dash (el .forja), src/expresion.dash (las expresiones del depurador) y las plantillas
# (src/plantillas_datos.dash) sin ventana (tests/proyecto_base.dash), en FS-UAE. Acaba con "TODO BIEN".
#
#   tests/proyecto_base.sh DASH_DIR
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
python3 "$aqui/tools/plantillas.py" --comprobar
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cd "$dash" && python3 tools/emu_run.py --dash2 --timeout ${TIEMPO:-120} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} "$aqui/tests/proyecto_base.dash"
