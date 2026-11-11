#!/bin/sh
# Forja con un fichero de 1505 líneas (tests/grande.dash): ir al final, ir a una línea, buscar, escribir, ejecutar y
# deshacer; en FS-UAE. Enseña lo que anotó (con lo que tarda el dibujo); acaba con "TODO BIEN" si todo fue bien.
#
#   tests/grande.sh DASH_DIR DASHC_AMIGA
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$forja/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/grande" "$tmp/sys/Dash"
# 300 funciones de 5 líneas y un Main: 1505 líneas; Total: 2 + 151 + 301 = 454
python3 -c '
for i in range(1, 301):
    print("func f%d(x: Int) -> Int\n    y = x + %d\n    return y\nend\n" % (i, i))
print("Main\n    t = 0\n    t = t + f1(1) + f150(1) + f300(1)\n    Print \"Total: #{t}\"\nend")
' > "$tmp/sys/Prueba/grande/main.dash"
"$dash/dash" "$aqui/tests/grande.dash" -o "$tmp/sys/Prueba/UsuarioGrande"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/grande/main.dash"
  echo "Run >DH0:Prueba/grande.log DH0:Prueba/UsuarioGrande"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-600} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} $EXTRA --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/grande.txt" 2>/dev/null || { echo "FALLO: no hay registro"; cat "$tmp/disco/Prueba/grande.log" 2>/dev/null; }
