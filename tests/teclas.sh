#!/bin/sh
# Forja con un usuario de prueba (tests/teclas.dash) que escribe, selecciona, corta, pega, deshace y hace clic en
# el editor, en FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/teclas.sh DASH_DIR [captura.png segundos...]
#   REAL=1 tests/teclas.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz), no al máximo
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
: > "$tmp/sys/Prueba/vacio.dash"
"$dash/dash" "$aqui/tests/teclas.dash" -o "$tmp/sys/Prueba/Teclas"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/vacio.dash"
  echo "Run >NIL: DH0:Prueba/Teclas"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-180} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/teclas.txt" 2>/dev/null || echo "FALLO: no hay registro"
