#!/bin/sh
# Clics de ratón en Forja mientras depura (tests/clic.dash): el código no salta y el panel de las variables no abre
# ficheros (lo contó David Martínez), en FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/clic.sh DASH_DIR DASHC_AMIGA
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (dashc.amiga y los dashc_*.drt). FORJA=otro/cajón prueba las
# fuentes de otro cajón con este usuario de prueba.
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$forja/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Dash"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
# otro fichero en el cajón, para la lista de la izquierda
printf 'Main\n    Print "otro"\nend\n' > "$tmp/sys/Prueba/gravedad/otro.dash"
"$dash/dash" "$aqui/tests/clic.dash" -o "$tmp/sys/Prueba/Clic"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/gravedad/main.dash"
  echo "Run >NIL: DH0:Prueba/Clic"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/clic.txt" 2>/dev/null || echo "FALLO: no hay registro"
