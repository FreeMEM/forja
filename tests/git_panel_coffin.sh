#!/bin/bash
# tests/git_panel.dash (la extensión Git) en la máquina coffin de Dash (MUI 3.8, 68040 con JIT, RTG): DASH_KICKSTART_32 y
# DASH_EMU_DISK_COFFIN. Enseña el registro; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/git_panel_coffin.sh DASH_DIR [DASHGIT_DIR [captura.png segundos...]]
set -e
dash=$1
dg=${2:-$HOME/Projects/dashgit}
shift; [ $# -gt 0 ] && shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
"$dash/dash" "$aqui/tests/git_panel.dash" -o "$tmp/GitPanel"
"$dash/dash" "$dg/src/main.dash" -o "$tmp/dashgit"
"$dash/dash" "$aqui/tests/git_panel_coffin.dash" -o "$tmp/Lanzar"
"$dash/dash" "$aqui/extensiones/Git/git.dash" -o "$tmp/Git"
cp "$aqui/extensiones/Git/manifiesto.txt" "$tmp/manifiesto.txt"
files=""
if [ -n "$PAUSA" ]; then echo "$PAUSA" > "$tmp/pausa"; files="--file $tmp/pausa"; fi
if [ -n "$SERVIDOR" ]; then echo "$SERVIDOR" > "$tmp/servidor"; files="$files --file $tmp/servidor"; fi
for f in Forja GitPanel dashgit Git manifiesto.txt; do files="$files --file $tmp/$f"; done
for f in main.dash red.dash ventana.dashui; do files="$files --file $aqui/tests/prueba/juego/$f"; done
cd "$dash" && python3 tools/emu_run.py --machine coffin --timeout ${TIEMPO:-400} $files $shots "$tmp/Lanzar" 2>&1
