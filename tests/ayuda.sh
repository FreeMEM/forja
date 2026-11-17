#!/bin/sh
# La ayuda de Dash y los errores marcados en Forja (tests/ayuda.dash), en FS-UAE. Forja va como en el paquete de Dash:
# DH0:Dash/Forja/Forja, la ayuda en DH0:Dash/Ayuda (tools/gen_ayuda.py de Dash) y la orden en DH0:Dash/dash. Enseña lo
# que anotó; acaba con "TODO BIEN".
#
#   tests/ayuda.sh DASH_DIR DASHC_AMIGA [capturas/]
#
# DASHC_AMIGA: el cajón con dashc.amiga y los dashc_*.drt (make amiga en dashc/ de Dash; con --check).
# capturas/: guarda ahí ayuda-ficha.png, ayuda-probar.png, ayuda-buscar.png, ayuda-grupo.png y errores.png.
#   RTG=1 tests/ayuda.sh ...                        # AmigaOS 3.2 con tarjeta gráfica de 256 colores y MUI 5
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...  # con MUI 3.8 (el sistema de CoffinOS)
#   REAL=1 ...                                      # la CPU a la velocidad de un A1200 (68020 a 14 MHz)
set -e
dash=$1; dashc=$2; capturas=${3:-}
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
python3 "$dash/tools/gen_ayuda.py" --salida "$tmp/sys/Dash/Ayuda" > /dev/null
rm -f "$tmp/sys/Dash/Ayuda/"*.guide
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dash"
for f in "$dashc"/dashc_*.drt; do cp "$f" "$tmp/sys/Dash/$(basename "$f" | sed 's/dashc_/dash_/')"; done
cp -r "$dash/lib" "$tmp/sys/Dash/lib"
"$dash/dash" "$aqui/tests/ayuda.dash" -o "$tmp/Prueba"
{
  echo "C:MakeDir >NIL: ENV:Forja"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Prueba" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  for f in ayuda-ficha ayuda-probar ayuda-buscar ayuda-grupo errores buscar-fallo-0 buscar-fallo-1; do cp "$tmp/disco/Prueba/$f.png" "$capturas/" 2>/dev/null || true; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/ayuda.txt" 2>/dev/null || echo "FALLO: no hay registro"
