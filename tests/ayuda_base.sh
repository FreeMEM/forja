#!/bin/sh
# src/ayuda.dash y src/errores.dash sin ventana (tests/ayuda_base.dash), en FS-UAE: la ayuda de Dash (la hace
# tools/gen_ayuda.py de Dash, en DH0:Dash/Ayuda), fichas, enlaces, historia, buscar, índice y Probar; los errores de
# dash y "dash --check" del Amiga. Mide lo que tarda; acaba con "TODO BIEN".
#
#   tests/ayuda_base.sh DASH_DIR [DASHC_AMIGA]
#   REAL=1 tests/ayuda_base.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz)
#
# DASHC_AMIGA: el cajón con dashc.amiga y los dashc_*.drt (make amiga en dashc/ de Dash): con él, también --check.
set -e
dash=$1; dashc=${2:-}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Dash"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
python3 "$dash/tools/gen_ayuda.py" --salida "$tmp/sys/Dash/Ayuda" > /dev/null
rm -f "$tmp/sys/Dash/Ayuda/"*.guide
if [ -n "$dashc" ]; then
  cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dash"
  cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
  for f in "$tmp/sys/Dash"/dashc_*.drt; do mv "$f" "$(echo "$f" | sed 's/dashc_/dash_/')"; done
  cp -r "$dash/lib" "$tmp/sys/Dash/lib"
fi
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} "$aqui/tests/ayuda_base.dash"
