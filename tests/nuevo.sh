#!/bin/sh
# Lo primero de alguien nuevo (tests/nuevo.dash): Forja sin fichero, Amiga-N, escribir, Ejecutar y guardar; en
# FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/nuevo.sh DASH_DIR DASHC_AMIGA
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
"$dash/dash" "$aqui/tests/nuevo.dash" -o "$tmp/sys/Prueba/UsuarioNuevo"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "Run >NIL: DH0:Prueba/UsuarioNuevo"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/nuevo.txt" 2>/dev/null || echo "FALLO: no hay registro"
