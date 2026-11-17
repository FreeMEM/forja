#!/bin/sh
# Ejecutar con perfil y con memcheck en Forja (paso 4.2, tests/perfil.dash): la pestaña Perfil (ordenar con un clic en
# un título, ir a una función con otro) y los avisos de memcheck como errores con clic. Enseña lo que anotó; acaba con
# "TODO BIEN".
#
#   tests/perfil.sh DASH_DIR DASHC_AMIGA [capturas/]
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 tests/perfil.sh ...   # con MUI 3.8
set -e
dash=$1; dashc=$2; capturas=${3:-}
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
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/perfil.dash" -o "$tmp/sys/Prueba/PerfilT"
mkdir -p "$tmp/sys/Dash"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dash"
for f in "$dashc"/dashc_*.drt; do cp "$f" "$tmp/sys/Dash/$(basename "$f" | sed 's/^dashc_/dash_/')"; done
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dash"
  echo "SetEnv Forja/buscar_dash no"
  echo "SetEnv FORJA_SONDA 1"
  # (dash del Amiga copia en línea las funciones pequeñas también con --profile, y el perfil solo ve Main: hasta que
  # Dash lo arregle, sin copiar en línea)
  echo "SetEnv DASHC_SIN_COPIAR 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/perfil/main.dash"
  echo "Run >NIL: DH0:Prueba/PerfilT"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-500} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Forja" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  for f in "$tmp"/disco/Prueba/*.png; do [ -f "$f" ] && cp "$f" "$capturas/"; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/perfil.txt" 2>/dev/null || echo "FALLO: no hay registro"
