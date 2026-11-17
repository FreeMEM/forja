#!/bin/sh
# La extensión Demos dentro de Forja con un usuario de prueba (tests/demos_forja.dash) y la demo de la plantilla
# corriendo (con musica.mod de tests/mod_ejemplo.py), en FS-UAE. Después compila la demo como quedó: con el copper que
# metió la extensión en main.dash, y la versión final (VIVO = false) con las pistas exportadas. Acaba con "TODO BIEN"
# dos veces.
#
#   tests/demos_forja.sh DASH_DIR [capturas/]
#
# Necesita DASH_KICKSTART (3.1). Sin RTG, en el A1200 con chipset (el sonido y el copper de verdad).
#   RTG=1 ...                                          # AmigaOS 3.2 con tarjeta gráfica de 256 colores y MUI 5
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...     # con MUI 3.8 (el sistema de CoffinOS)
set -e
dash=$1; capturas=${2:-}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
maquina=""
if [ -n "$RTG" ]; then
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
mkdir -p "$tmp/sys/Prueba/demo" "$tmp/plt"
. "$aqui/tests/extension.sh"
extension Demos demos
# la demo de la plantilla, compilada, con su música
for f in "$aqui"/plantillas/demo/*; do sed 's/%NOMBRE%/Barras/g' "$f" > "$tmp/plt/$(basename "$f")"; done
"$dash/dash" "$tmp/plt/main.dash" -o "$tmp/sys/Prueba/demo/Barras"
cp "$tmp/plt/"* "$tmp/sys/Prueba/demo/"
python3 -I "$aqui/tests/mod_ejemplo.py" "$tmp/sys/Prueba/demo/musica.mod"
"$dash/dash" "$aqui/tests/demos_forja.dash" -o "$tmp/sys/Prueba/DemosForja"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/demo/demo.sync"
  echo "Run >NIL: DH0:Prueba/DemosForja"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-480} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/demos_forja.txt" 2>/dev/null || echo "FALLO: no hay registro"
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  for f in sincronia medidor musica copper partes; do cp "$tmp/disco/Prueba/$f.png" "$capturas/" 2>/dev/null || true; done
fi
# la demo como quedó: con el copper en main.dash, y la versión final con las pistas exportadas
d="$tmp/disco/Prueba/demo"
bien=1
if grep -q "# copper: degradado" "$d/main.dash" && grep -q "copper_move(0x102" "$d/main.dash" && grep -q "PARTE_FIN" "$d/main.dash" && "$dash/dash" "$d/main.dash" -o "$tmp/conCopper"; then echo "bien: main.dash con el copper (dos registros) y las partes compila"; else echo "FALLO: main.dash con el copper y las partes"; bien=0; fi
sed 's/^const VIVO = true/const VIVO = false/' "$d/main.dash" > "$d/final.dash"
if grep -q "brillo" "$d/pistas_datos.dash" && "$dash/dash" "$d/final.dash" -o "$tmp/final"; then echo "bien: la versión final con pistas_datos.dash compila"; else echo "FALLO: la versión final"; bien=0; fi
[ $bien = 1 ] && echo "TODO BIEN"
