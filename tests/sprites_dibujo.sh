#!/bin/sh
# Lo que tarda el dibujo del editor de sprites (tests/sprites_dibujo.dash) con 16x16, 32x32 y 64x64, en FS-UAE.
# Acaba con "TODO BIEN" si todo fue bien.
#
#   tests/sprites_dibujo.sh DASH_DIR [captura.png segundos...]
#
# Necesita DASH_KICKSTART (3.1). REAL=1: la CPU a la velocidad de un A1200 (68020 a 14 MHz).
# RTG=1: AmigaOS 3.2 con tarjeta gráfica de 256 colores (sys32rtg8), para ver los colores en las capturas.
set -e
dash=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
maquina=""
if [ -n "$RTG" ]; then
  cp -r "$HOME/.cache/dash-emu/sys32rtg8" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
# tres imágenes con muchos tramos (lo peor para el dibujo)
python3 -I - "$tmp" <<'PY'
import sys
d = sys.argv[1]
for nombre, lado, planos in (("a16", 16, 2), ("b32", 32, 4), ("c64", 64, 4)):
    n = 1 << planos
    filas = ["".join("%X" % ((x // 2 + y // 3 + x * y // 7) % n) for x in range(lado)) for y in range(lado)]
    paleta = " ".join("%06X" % (((i * 97) % 256) << 16 | ((i * 53) % 256) << 8 | (i * 151) % 256) for i in range(n))
    open("%s/%s.txt" % (d, nombre), "w").write("%d %d %d\n" % (lado, lado, planos) + "\n".join(filas) + "\npaleta " + paleta + "\n")
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/a16.iff" "$tmp/a16.txt" --frja "1 1 16 6"
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/b32.iff" "$tmp/b32.txt"
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/c64.iff" "$tmp/c64.txt"
# d32.iff: como un sprite de verdad (una bola de 3 colores sobre el transparente)
python3 -I - "$tmp/d32.txt" <<'PY'
import sys
f = []
for y in range(32):
    f.append("".join("0" if (x - 15.5) ** 2 + (y - 15.5) ** 2 > 225 else ("1" if (x - 15.5) ** 2 + (y - 15.5) ** 2 > 160 else ("3" if x + y < 24 else "2")) for x in range(32)))
open(sys.argv[1], "w").write("32 32 2\n" + "\n".join(f) + "\npaleta 000000 203060 4080E0 E0F0FF\n")
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/d32.iff" "$tmp/d32.txt"
"$dash/dash" "$aqui/tests/sprites_dibujo.dash" -o "$tmp/sys/Prueba/SpritesDibujo"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
  echo "Run >NIL: DH0:Prueba/SpritesDibujo"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sprites_dibujo.txt" 2>/dev/null || echo "FALLO: no hay registro"
