#!/bin/sh
# Abrir lo de la última vez y cerrar con cambios (tests/sesion.dash, que arranca Forja él mismo), en FS-UAE. Enseña lo
# que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/sesion.sh DASH_DIR DASHC_AMIGA
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Dash"
"$dash/dash" "$forja/src/main.dash" -o "$tmp/sys/Prueba/Forja"
cp -r "$aqui/tests/prueba/proyecto" "$tmp/sys/Prueba/Mi juego"
"$dash/dash" "$aqui/tests/sesion.dash" -o "$tmp/Sesion"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
# la extensión Sprites y un sprite en el proyecto: la sesión lo vuelve a abrir con ella
. "$aqui/tests/extension.sh"
extension Sprites editor_sprites
python3 -I - "$tmp/nave.txt" <<'PY'
import sys
filas = ["".join("%X" % ((x * 7 + y * 3) % 4 if (x + y) % 3 else 0) for x in range(16)) for y in range(16)]
open(sys.argv[1], "w").write("16 16 2\n" + "\n".join(filas) + "\npaleta 000000 FF0000 00FF00 0000FF\n")
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/Mi juego/nave.iff" "$tmp/nave.txt"
mkdir -p "$tmp/sys/Prefs/Env-Archive/Forja"
{
  echo "Assign ENVARC: DH0:Prefs/Env-Archive"
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-500} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Sesion" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sesion.txt" 2>/dev/null || echo "FALLO: no hay registro"
