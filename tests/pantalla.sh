#!/bin/sh
# Forja en su propia pantalla (preferencia ENV:Forja/pantalla), con un usuario de prueba (tests/pantalla.dash), en
# FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/pantalla.sh DASH_DIR [captura.png segundos...]
#
# DASH_DIR: un Dash con screen_make_default. Necesita DASH_KICKSTART (3.1).
set -e
dash=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/pantalla.dash" -o "$tmp/sys/Prueba/Pantalla"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/pantalla si"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
  echo "Run >NIL: DH0:Prueba/Pantalla"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-180} --system "$tmp/sys" --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/pantalla.txt" 2>/dev/null || echo "FALLO: no hay registro"
