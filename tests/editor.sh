#!/bin/sh
# El editor cómodo de Forja (fase 2) como un usuario (tests/editor.dash), en FS-UAE. Enseña lo que anotó; acaba con
# "TODO BIEN".
#
#   tests/editor.sh DASH_DIR [capturas/]
#   RTG=1 tests/editor.sh ...                        # AmigaOS 3.2 con tarjeta gráfica de 256 colores y MUI 5
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...   # con MUI 3.8 (el sistema de CoffinOS)
#   REAL=1 ...                                       # la CPU a la velocidad de un A1200 (68020 a 14 MHz)
# capturas/: guarda ahí editor-colores.png, editor-pareja.png y las de los pasos que siguen.
set -e
dash=$1; capturas=${2:-}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
maquina=""
if [ -n "$RTG" ]; then
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Dash/Forja"
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/sys/Dash/Forja/Forja"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/editor.dash" -o "$tmp/Prueba"
{
  echo "C:MakeDir >NIL: ENV:Forja"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/editor/main.dash"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-500} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Prueba" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  cp "$tmp/disco/Prueba/"editor-*.png "$capturas/" 2>/dev/null || true
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/editor.txt" 2>/dev/null || echo "FALLO: no hay registro"
