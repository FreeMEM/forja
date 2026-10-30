#!/bin/sh
# Forja con un usuario de prueba (tests/ficheros.dash) que abre, cambia de pestaña, guarda y cierra ficheros,
# en FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/ficheros.sh DASH_DIR [captura.png segundos...]
#   REAL=1 tests/ficheros.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz), no al máximo
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
"$dash/dash" "$aqui/tests/ficheros.dash" -o "$tmp/sys/Prueba/Ficheros"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
  echo "Run >NIL: DH0:Prueba/Ficheros"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-180} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/ficheros.txt" 2>/dev/null || echo "FALLO: no hay registro"
