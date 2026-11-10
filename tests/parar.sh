#!/bin/sh
# Parar un programa que no acaba nunca mientras se ejecuta (tests/parar.dash), en FS-UAE. Enseña lo que anotó; acaba
# con "TODO BIEN" si todo fue bien.
#
#   tests/parar.sh DASH_DIR DASHC_AMIGA
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$forja/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/bucle" "$tmp/sys/Dash"
printf 'Main\n    i = 0\n    while true\n        i = i + 1\n    end\nend\n' > "$tmp/sys/Prueba/bucle/main.dash"
"$dash/dash" "$aqui/tests/parar.dash" -o "$tmp/sys/Prueba/Parar"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/bucle/main.dash"
  echo "Run >NIL: DH0:Prueba/Parar"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-300} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/parar.txt" 2>/dev/null || echo "FALLO: no hay registro"
