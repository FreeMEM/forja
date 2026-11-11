#!/bin/sh
# Salir de Forja con un programa en marcha y con otro parado en el depurador (tests/salir.dash, que arranca Forja él
# mismo), en FS-UAE: no debe quedar nada vivo. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/salir.sh DASH_DIR DASHC_AMIGA
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/espera" "$tmp/sys/Dash"
"$dash/dash" "$forja/src/main.dash" -o "$tmp/sys/Prueba/Forja"
printf 'Main\n    for i in (1..60)\n        Print "vuelta #{i}"\n        time_delay(50)\n    end\nend\n' > "$tmp/sys/Prueba/espera/main.dash"
"$dash/dash" "$aqui/tests/salir.dash" -o "$tmp/Salir"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/espera/main.dash"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Salir" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/salir.txt" 2>/dev/null || echo "FALLO: no hay registro"
