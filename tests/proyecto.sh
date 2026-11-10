#!/bin/sh
# Forja con un programa de varios ficheros en un cajón con un espacio (tests/proyecto.dash, con tests/prueba/proyecto
# copiado a "DH0:Prueba/Mi juego"): ejecutar desde un módulo, guardar al ejecutar, un error en otro fichero, depurar
# entre ficheros; en FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/proyecto.sh DASH_DIR DASHC_AMIGA
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (dashc.amiga y los dashc_*.drt). FORJA=otro/cajón prueba las
# fuentes de otro cajón.
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$forja/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Dash"
cp -r "$aqui/tests/prueba/proyecto" "$tmp/sys/Prueba/Mi juego"
"$dash/dash" "$aqui/tests/proyecto.dash" -o "$tmp/sys/Prueba/Proyecto"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA \"DH0:Prueba/Mi juego/main.dash\""
  echo "Run >NIL: DH0:Prueba/Proyecto"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-600} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/proyecto.txt" 2>/dev/null || echo "FALLO: no hay registro"
