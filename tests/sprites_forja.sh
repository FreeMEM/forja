#!/bin/sh
# El editor de sprites dentro de Forja con un usuario de prueba (tests/sprites_forja.dash), en FS-UAE; después
# comprueba con tests/iff.py el nave.iff que guardó Forja. Acaba con "TODO BIEN" dos veces si todo fue bien.
#
#   tests/sprites_forja.sh DASH_DIR [captura.png segundos...]
#
# Necesita DASH_KICKSTART (3.1).  REAL=1: la CPU a la velocidad de un A1200.
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
# nave.iff: un sprite de hardware de 3 fotogramas, sin GRAB (al guardar, Forja lo pone)
python3 -I - "$tmp/nave.txt" <<'PY'
import sys
filas = ["".join("%X" % ((x * 7 + y * 3) % 4 if (x + y) % 3 else 0) for x in range(48)) for y in range(16)]
open(sys.argv[1], "w").write("48 16 2\n" + "\n".join(filas) + "\npaleta 000000 FF0000 00FF00 0000FF\n")
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/nave.iff" "$tmp/nave.txt" --frja "1 1 16 6"
"$dash/dash" "$aqui/tests/sprites_forja.dash" -o "$tmp/sys/Prueba/SpritesForja"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/nave.iff"
  echo "Run >NIL: DH0:Prueba/SpritesForja"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sprites_forja.txt" 2>/dev/null || echo "FALLO: no hay registro"
python3 -I - "$aqui/tests" "$tmp" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import iff
d = sys.argv[2]
try:
    antes = iff.leer(d + "/sys/Prueba/juego/nave.iff")
    despues = iff.leer(d + "/disco/Prueba/juego/nave.iff")
    bien = despues["filas"] == antes["filas"] and despues["frja"] == "1 1 16 6" and despues["grab"] == (0, 0)
    print(("bien: " if bien else "FALLO: ") + "iff.py: nave.iff guardado con sus píxeles, FRJA y GRAB")
    if bien:
        print("TODO BIEN")
except Exception as e:
    print("FALLO: iff.py: " + repr(e))
PY
