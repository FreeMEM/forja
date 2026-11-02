#!/bin/sh
# Leer y escribir IFF ILBM en FS-UAE (tests/sprites_iff.dash), con los pinceles de tests/iff.py; después
# comprueba con iff.py los ficheros que escribió Forja. Acaba con "TODO BIEN" dos veces si todo fue bien.
#
#   tests/sprites_iff.sh DASH_DIR
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
python3 -I - "$tmp" <<'PY'
import sys
d = sys.argv[1]
def guarda(nombre, w, h, planos, f, paleta):
    filas = ["".join("%0*X" % (2 if planos > 4 else 1, f(x, y)) for x in range(w)) for y in range(h)]
    open(d + "/" + nombre, "w").write("%d %d %d\n" % (w, h, planos) + "\n".join(filas) + "\npaleta " + " ".join(paleta) + "\n")
guarda("pincel.txt", 48, 16, 2, lambda x, y: (x * 7 + y * 3) % 4 if (x + y) % 3 else 0, ["000000", "FF0000", "00FF00", "0000FF"])
guarda("grande.txt", 40, 10, 5, lambda x, y: (x + y * 3) % 32, ["%06X" % (i * 0x070503) for i in range(32)])
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/pincel.iff" "$tmp/pincel.txt" --comprimir
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/grande.iff" "$tmp/grande.txt" --mascara --grab 3,4
python3 -I "$aqui/tests/iff.py" leer "$tmp/sys/Prueba/pincel.iff" > "$tmp/sys/Prueba/pincel.txt"
python3 -I "$aqui/tests/iff.py" leer "$tmp/sys/Prueba/grande.iff" > "$tmp/sys/Prueba/grande.txt"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-180} --system "$tmp/sys" --keep "$tmp/disco" "$aqui/tests/sprites_iff.dash" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sprites_iff.txt" 2>/dev/null || echo "FALLO: no hay registro"
# lo que escribió Forja, leído por iff.py
python3 -I - "$aqui/tests" "$tmp" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import iff
d = sys.argv[2]
mal = 0
def ver(paso, cierto):
    global mal
    print(("bien: " if cierto else "FALLO: ") + paso)
    mal += 0 if cierto else 1
try:
    s = iff.leer(d + "/disco/Prueba/sale.iff")
    p = iff.leer(d + "/sys/Prueba/pincel.iff")
    ver("iff.py: sale.iff tiene los píxeles del pincel", s["filas"] == p["filas"] and s["paleta"] == p["paleta"])
    ver("iff.py: FRJA, GRAB y masking 2", s["frja"] == "1 1 16 9" and s["grab"] == (2, 5) and s["mascara"] == 2)
    g = iff.leer(d + "/disco/Prueba/grande2.iff")
    o = iff.leer(d + "/sys/Prueba/grande.iff")
    ver("iff.py: grande2.iff igual que grande.iff", g["filas"] == o["filas"] and g["paleta"] == o["paleta"] and g["grab"] == (3, 4))
except Exception as e:
    ver("iff.py: " + repr(e), False)
if mal == 0:
    print("TODO BIEN")
PY
