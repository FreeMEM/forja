#!/bin/sh
# El editor de sprites de principio a fin con un usuario de prueba (tests/sprites.dash), en FS-UAE; después compara
# con tests/iff.py el pincel.iff guardado con lo que enseñaba el editor, y que sprite_load lo lea.
# Acaba con "TODO BIEN" dos veces si todo fue bien.
#
#   tests/sprites.sh DASH_DIR [captura.png segundos...]
#
# Necesita DASH_KICKSTART (3.1). REAL=1: la CPU a la velocidad de un A1200. RTG=1: AmigaOS 3.2 con 256 colores.
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
# pincel.iff: como uno de DPaint (ByteRun1, sin FRJA), 48x16 en 2 planos
python3 -I - "$tmp/pincel.txt" <<'PY'
import sys
f = ["".join("%X" % ((x * 5 + y) % 4 if (x // 3 + y) % 4 else 0) for x in range(48)) for y in range(16)]
open(sys.argv[1], "w").write("48 16 2\n" + "\n".join(f) + "\npaleta 000000 F0E0D0 30A050 C04020\n")
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/pincel.iff" "$tmp/pincel.txt" --comprimir
"$dash/dash" "$aqui/tests/sprites.dash" -o "$tmp/sys/Prueba/Sprites"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/pincel.iff"
  echo "Run >NIL: DH0:Prueba/Sprites"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-300} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" > /dev/null || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sprites.txt" 2>/dev/null || echo "FALLO: no hay registro"
python3 -I - "$aqui/tests" "$tmp" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import iff
d = sys.argv[2]
try:
    l = open(d + "/disco/Prueba/esperado.txt", encoding="latin-1").read().split("\n")
    cab = l[1].split()
    ancho, alto, nf = int(cab[0]), int(cab[1]), int(cab[4])
    filas = l[2:2 + nf * alto]
    tira = ["".join(filas[f * alto + y] for f in range(nf)) for y in range(alto)]
    g = iff.leer(d + "/disco/Prueba/juego/pincel.iff")
    leido = ["".join("%X" % c for c in fila) for fila in g["filas"]]
    bien = leido == tira and g["frja"] == "1 1 16 6" and g["planos"] == 2
    print(("bien: " if bien else "FALLO: ") + "iff.py: pincel.iff guardado igual que en el editor (%d fotogramas, FRJA %s)" % (nf, g["frja"]))
    if bien:
        print("TODO BIEN")
except Exception as e:
    print("FALLO: iff.py: " + repr(e))
PY
