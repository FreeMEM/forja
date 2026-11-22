#!/bin/bash
# El Taller 3D (la extension de Titan Force) con un usuario de prueba (tests/taller3d.dash), en FS-UAE con RTG.
# Acaba con "TODO BIEN" si todo fue bien.
#
#   tests/taller3d.sh DASH_DIR ROBOT.tft [captura.png segundos...]
#
# Necesita DASH_KICKSTART_32 (3.2). SISTEMA: el de RTG (por defecto el de 32 bits, como CoffinOS).
set -e
dash=$1; shift
robot=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg32}" "$tmp/sys"
export DASH_EMU_SYS_32_RTG="$tmp/sys"
export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Amiberry/kickstarts/ks323_A1200_47.115_noSCSI.rom}"
mkdir -p "$tmp/sys/Prueba/titan"
cp "$robot" "$tmp/sys/Prueba/titan/"
. "$aqui/tests/extension.sh"
extension Taller3D editor_taller3d
"$dash/dash" "$aqui/tests/taller3d.dash" -o "$tmp/sys/Prueba/Taller3D"
{
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/titan/$(basename "$robot")"
  echo "Run >NIL: DH0:Prueba/Taller3D"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} --machine rtg --system "$tmp/sys" --keep "$tmp/disco" $shots "$tmp/Forja" > /dev/null || true
cp "$tmp/disco/Prueba/taller3d.txt" "${png%.png}.txt" 2>/dev/null; iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/taller3d.txt" || echo "FALLO: no hay registro"
