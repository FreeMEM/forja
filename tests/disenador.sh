#!/bin/sh
# El diseñador visual de ventanas de Forja (lo pidió Jose) con un usuario de prueba (tests/disenador.dash): clic,
# arrastrar, paleta, árbol y doble clic al código, en FS-UAE. Enseña lo que anotó; acaba con "TODO BIEN".
#
#   tests/disenador.sh DASH_DIR DASHC_AMIGA [captura.png segundos...]
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (make amiga en dashc/: dashc.amiga y los dashc_*.drt).
#   RTG=1 tests/disenador.sh ...  # en AmigaOS 3.2 con tarjeta gráfica
#   REAL=1 tests/disenador.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz), no al máximo
set -e
dash=$1; dashc=$2; shift 2
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
maquina=""
if [ -n "$RTG" ]; then
  # RTG=1: AmigaOS 3.2 con tarjeta gráfica (más sitio para la ventana dibujada)
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/disenador.dash" -o "$tmp/sys/Prueba/Disenador"
# dashc en DH0:Dash, con sus runtimes al lado (los busca en PROGDIR:)
mkdir -p "$tmp/sys/Dash"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv DISENADOR_ESPERA ${ESPERA:-0}"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/ventana/ventana.dashui"
  echo "Run >NIL: DH0:Prueba/Disenador"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py $maquina --timeout ${TIEMPO:-400} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/disenador.txt" 2>/dev/null || echo "FALLO: no hay registro"
