#!/bin/sh
# La barra de botones de Forja con un usuario de prueba (tests/botones.dash), en FS-UAE: el puntero encima, un
# botón apagado, Compilar, Depurar y Parar. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/botones.sh DASH_DIR DASHC_AMIGA [captura.png [segundos...]]   # captura-encima.png y captura-depurando.png
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (dashc.amiga y los dashc_*.drt).
set -e
dash=$1; dashc=$2; shift 2
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Dash"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
# un programa que tarda, para pararlo mientras se depura
mkdir -p "$tmp/sys/Prueba/espera"
printf 'Main\n    for i in (1..60)\n        Print "vuelta #{i}"\n        time_delay(50)\n    end\nend\n' > "$tmp/sys/Prueba/espera/main.dash"
"$dash/dash" "$aqui/tests/botones.dash" -o "$tmp/sys/Prueba/Botones"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/espera/main.dash"
  echo "Run >NIL: DH0:Prueba/Botones"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-300} --system "$tmp/sys" --keep "$tmp/disco" $shots "$tmp/Forja" || true
# las capturas que hizo (el puntero encima de Ejecutar; depurando)
if [ -n "$png" ]; then
  for c in encima depurando; do cp "$tmp/disco/Prueba/$c.png" "${png%.png}-$c.png" 2>/dev/null || true; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/botones.txt" 2>/dev/null || echo "FALLO: no hay registro"
