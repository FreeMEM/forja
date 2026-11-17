#!/bin/sh
# Las pestañas que no caben (tests/pestanas.dash), como un usuario, en FS-UAE: 12 ficheros abiertos en 640 de ancho,
# los botones de la derecha, Ctrl Tab, Ctrl Mayús Tab y la lista de todas. Enseña lo que anotó; acaba con "TODO BIEN".
#
#   tests/pestanas.sh DASH_DIR [capturas/]
#   RTG=1 tests/pestanas.sh ...                        # AmigaOS 3.2 con tarjeta gráfica de 256 colores y MUI 5
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...     # con MUI 3.8 (el sistema de CoffinOS)
# capturas/: pestanas-botones.png, pestanas-lista.png y pestanas-caben.png.
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
"$dash/dash" "$aqui/tests/pestanas.dash" -o "$tmp/Prueba"
{
  echo "C:MakeDir >NIL: ENV:Forja"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv Forja/recordar no"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-300} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Prueba" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  cp "$tmp/disco/Prueba/"pestanas-*.png "$capturas/" 2>/dev/null || true
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/pestanas.txt" 2>/dev/null || echo "FALLO: no hay registro"
