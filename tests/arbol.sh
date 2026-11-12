#!/bin/sh
# El árbol de las variables del depurador de Forja (idea de David Martínez) con un usuario de prueba
# (tests/arbol.dash), en FS-UAE: despliega con clics un struct, uno dentro de otro y listas, pide más elementos de
# una lista larga, se desplaza a lo ancho y a lo alto, y lo desplegado sigue así tras un paso. Enseña lo que anotó;
# acaba con "TODO BIEN" si todo fue bien.
#
#   tests/arbol.sh DASH_DIR DASHC_AMIGA [captura.png [segundos...]]   # captura-desplegado.png, -ancho.png, -lista.png
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (make amiga en dashc/: dashc.amiga y los dashc_*.drt).
#   RTG=1 tests/arbol.sh ...    # en AmigaOS 3.2 con tarjeta gráfica: ventana grande y colores (para las capturas)
#   REAL=1 tests/arbol.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz), no al máximo
set -e
dash=$1; dashc=$2; shift 2
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
# RTG=1: en AmigaOS 3.2 con tarjeta gráfica (sys32rtg8), con una ventana más grande y los colores de verdad
maquina=""
if [ -n "$RTG" ]; then
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/arbol.dash" -o "$tmp/sys/Prueba/UsarArbol"
# dashc en DH0:Dash, con sus runtimes al lado (los busca en PROGDIR:)
mkdir -p "$tmp/sys/Dash"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/arbol/main.dash"
  echo "Run >NIL: DH0:Prueba/UsarArbol"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} --system "$tmp/sys" $maquina ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
# las capturas que hizo el propio Amiga
if [ -n "$png" ]; then
  for c in desplegado ancho lista; do cp "$tmp/disco/Prueba/$c.png" "${png%.png}-$c.png" 2>/dev/null || true; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/arbol.txt" 2>/dev/null || echo "FALLO: no hay registro"
