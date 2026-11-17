#!/bin/sh
# Esc con un programa propio en marcha (lo vio el vídeo de Forja): el juego de la plantilla abre su pantalla sin
# ventana, así que el teclado sigue en Forja. tests/esc.dash pulsa Esc (y Ctrl-C a Forja) mientras corre: Forja no
# debe cerrarse. Enseña lo que anotó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/esc.sh DASH_DIR DASHC_AMIGA
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...   # con MUI 3.8 (el sistema de CoffinOS)
#   COFFIN=1 ...                                     # en la máquina CoffinOS (DASH_KICKSTART_32, DASH_EMU_DISK_COFFIN)
set -e
dash=$1; dashc=$2; shift 2
aqui=$(cd "$(dirname "$0")/.." && pwd)
forja=${FORJA:-$aqui}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
if [ -n "$COFFIN" ]; then
  # la máquina CoffinOS (MUI 3.8 con sus preferencias, Trasfondo...): todo en una carpeta montada como Proyecto:
  r="$tmp/raiz"
  mkdir -p "$r/esc" "$r/Dash"
  "$dash/dash" "$forja/src/main.dash" -o "$r/Forja"
  cp "$aqui/tests/prueba/esc/main.dash" "$r/esc/"
  sed 's/^const EN_COFFIN = false/const EN_COFFIN = true/' "$aqui/tests/esc.dash" > "$tmp/esc.dash"
  "$dash/dash" "$tmp/esc.dash" -o "$r/ProbarEsc"
  cp "$dashc/dashc.amiga" "$r/Dash/dash"
  for f in "$dashc"/dashc_*.drt; do cp "$f" "$r/Dash/$(basename "$f" | sed 's/dashc_/dash_/')"; done
  cp -r "$dash/lib" "$r/Dash/lib"
  cd "$dash" && python3 tools/emu_run.py --machine coffin --timeout ${TIEMPO:-300} $EXTRA --cd "$r" "$r/ProbarEsc" || true
  iconv -f latin1 -t utf-8 "$r/esc.txt" 2>/dev/null || echo "FALLO: no hay registro"
  exit 0
fi
maquina=""
if [ -n "$RTG" ]; then
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
"$dash/dash" "$forja/src/main.dash" -o "$tmp/Forja"
mkdir -p "$tmp/sys/Prueba/esc" "$tmp/sys/Dash"
cp "$aqui/tests/prueba/esc/main.dash" "$tmp/sys/Prueba/esc/"
"$dash/dash" "$aqui/tests/esc.dash" -o "$tmp/sys/Prueba/ProbarEsc"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/esc/main.dash"
  echo "Run >NIL: DH0:Prueba/ProbarEsc"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py $maquina --timeout ${TIEMPO:-300} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/esc.txt" 2>/dev/null || echo "FALLO: no hay registro"
