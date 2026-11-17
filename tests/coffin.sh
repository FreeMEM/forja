#!/bin/bash
# Forja de punta a punta en la máquina CoffinOS de Dash (tests/coffin.dash; MUI 3.8, 68040 con JIT, RTG de
# 1280x1024): DASH_KICKSTART_32 y DASH_EMU_DISK_COFFIN, y DASH_EMU_MINIGL para la plantilla 3D. Todo va en una carpeta
# del PC montada como Proyecto: (Forja, sus extensiones, la ayuda de Dash, la orden dash del Amiga y dashgit); lo que
# anota la prueba y sus capturas (coffin-*.png) quedan ahí. Acaba con "TODO BIEN".
#
#   tests/coffin.sh DASH_DIR DASHC_AMIGA [capturas/] [DASHGIT_DIR]
#
# DASHC_AMIGA: el cajón con dashc.amiga y los dashc_*.drt (make amiga en dashc/ de Dash).
set -e
dash=$1; dashc=$2; capturas=${3:-}; dg=${4:-$HOME/Projects/dashgit}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
r="$tmp/raiz"
mkdir -p "$r/Extensiones" "$r/Dash"
"$dash/dash" "$aqui/src/main.dash" -o "$r/Forja"
for e in "Git git" "Inferencia copiloto Copiloto" "Sprites editor_sprites" "Mapas editor_mapas" "Demos demos"; do
  set -- $e
  mkdir -p "$r/Extensiones/$1"
  cp "$aqui/extensiones/$1/manifiesto.txt" "$r/Extensiones/$1/"
  "$dash/dash" "$aqui/extensiones/$1/$2.dash" -o "$r/Extensiones/$1/${3:-$1}"
done
python3 "$dash/tools/gen_ayuda.py" --salida "$r/Ayuda" > /dev/null
rm -f "$r/Ayuda/"*.guide
cp "$dashc/dashc.amiga" "$r/Dash/dash"
for f in "$dashc"/dashc_*.drt; do cp "$f" "$r/Dash/$(basename "$f" | sed 's/dashc_/dash_/')"; done
cp -r "$dash/lib" "$r/Dash/lib"
"$dash/dash" "$dg/src/main.dash" -o "$r/dashgit"
"$dash/dash" "$aqui/tests/coffin.dash" -o "$r/Coffin"
libs=""
[ -n "$DASH_EMU_MINIGL" ] && libs="--lib $DASH_EMU_MINIGL"
cd "$dash" && python3 tools/emu_run.py --machine coffin --timeout ${TIEMPO:-900} $libs --cd "$r" "$r/Coffin" > "$tmp/salida.txt" 2>&1 || true
if [ -f "$r/coffin.txt" ]; then iconv -f latin1 -t utf-8 "$r/coffin.txt"; else echo "FALLO: no hay registro"; tail -20 "$tmp/salida.txt"; fi
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  cp "$r"/coffin-*.png "$capturas/" 2>/dev/null || true
fi
