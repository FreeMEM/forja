#!/bin/sh
# El lápiz del editor de sprites con un usuario de prueba (tests/sprites_lapiz.dash), en FS-UAE.
# Acaba con "TODO BIEN" si todo fue bien.
#
#   tests/sprites_lapiz.sh DASH_DIR [captura.png segundos...]
#
# Necesita DASH_KICKSTART (3.1). REAL=1: la CPU a la velocidad de un A1200.
set -e
dash=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
python3 -I -c "import sys; open(sys.argv[1], 'w').write('16 16 2\n' + '\n'.join(['0' * 16] * 16) + '\npaleta 000000 E0E0E0 E08030 3060C0\n')" "$tmp/vacio.txt"
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/vacio.iff" "$tmp/vacio.txt" --frja "1 1 16 6"
"$dash/dash" "$aqui/tests/sprites_lapiz.dash" -o "$tmp/sys/Prueba/SpritesLapiz"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/vacio.iff"
  echo "Run >NIL: DH0:Prueba/SpritesLapiz"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sprites_lapiz.txt" 2>/dev/null || echo "FALLO: no hay registro"
