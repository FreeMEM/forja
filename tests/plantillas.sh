#!/bin/sh
# Las plantillas de Nuevo proyecto (plantillas/, paso 3.2), cada una compilada con la orden dash del PC y ejecutada en
# FS-UAE: la orden del Shell con argumentos (tests/plantillas_orden.dash la llama), la commodity, la aplicación MUI, el
# juego y la demo en un A1200 con MUI 5; la 3D en la máquina de CoffinOS (68040 con FPU) con MiniGL. Cada una corre
# unos segundos (--autoclose) y debe acabar con código 0; con capturas/, una captura de cada una.
# (Que compilan con la orden dash del Amiga, dentro de Forja, lo prueba tests/forja_proyecto.sh.) Las de
# plantillas.en/ (en inglés) solo se compilan.
#
#   tests/plantillas.sh DASH_DIR [capturas/]
#
# Necesita DASH_KICKSTART; para la 3D, DASH_KICKSTART_32, DASH_EMU_DISK_COFFIN y DASH_EMU_MINIGL (minigl.library).
set -e
dash=$1; capturas=${2:-}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
for t in orden commodity mui juego demo 3d; do
  mkdir -p "$tmp/$t"
  for f in "$aqui/plantillas/$t"/*; do sed 's/%NOMBRE%/Prueba/g' "$f" > "$tmp/$t/$(basename "$f")"; done
done
mal=0
# las de plantillas.en/ (el código en inglés, para el catálogo inglés de Forja): que compilen
for d in "$aqui/plantillas.en"/*/; do
  t=$(basename "$d")
  mkdir -p "$tmp/en/$t"
  cp "$tmp/$t"/* "$tmp/en/$t/"
  for f in "$d"*; do sed 's/%NOMBRE%/Prueba/g' "$f" > "$tmp/en/$t/$(basename "$f")"; done
  op=""; [ "$t" = 3d ] && op="--fpu"
  if "$dash/dash" $op "$tmp/en/$t/main.dash" -o "$tmp/en/$t/Prueba" > "$tmp/en/$t.log" 2>&1; then
    echo "en/$t: compila"
  else
    cat "$tmp/en/$t.log"; echo "FALLO: en/$t no compila"; mal=$((mal + 1))
  fi
done
uno() {
  # uno nombre segundos_de_la_captura opciones... programas...
  nombre=$1; cuando=$2; shift 2
  shot=""
  if [ -n "$capturas" ]; then mkdir -p "$capturas"; shot="--screenshot $cuando $capturas/plantilla-$nombre.png"; fi
  salida=$(cd "$dash" && python3 tools/emu_run.py --dash2 --timeout 150 $shot "$@" 2>&1) || true
  echo "$salida"
  if echo "$salida" | grep -q "RC=[1-9]\|TIMEOUT\|failed"; then
    echo "FALLO: $nombre"
    mal=$((mal + 1))
  fi
}
"$dash/dash" "$tmp/orden/main.dash" -o "$tmp/orden/Prueba"
uno orden 1 --system "$HOME/.cache/dash-emu/sys31mui" --file "$tmp/orden/Prueba" "$aqui/tests/plantillas_orden.dash"
uno commodity 20 --autoclose 30 --system "$HOME/.cache/dash-emu/sys31mui" "$tmp/commodity/main.dash"
uno mui 20 --autoclose 30 --system "$HOME/.cache/dash-emu/sys31mui" "$tmp/mui/main.dash"
uno juego 20 --autoclose 10 "$tmp/juego/main.dash"
uno demo 20 --autoclose 10 "$tmp/demo/main.dash"
if [ -n "$DASH_EMU_MINIGL" ] && [ -n "$DASH_EMU_DISK_COFFIN" ]; then
  uno 3d 25 --fpu --autoclose 40 --machine coffin --lib "$DASH_EMU_MINIGL" "$tmp/3d/main.dash"
else
  echo "(sin DASH_EMU_MINIGL y DASH_EMU_DISK_COFFIN: la 3D no se prueba)"
fi
if [ $mal -eq 0 ]; then echo "TODO BIEN"; else echo "$mal FALLOS"; fi
