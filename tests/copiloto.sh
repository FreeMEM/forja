#!/bin/sh
# El copiloto (extensiones/Inferencia) con Forja e Inferencia de verdad, en FS-UAE, contra el servidor falso de
# Inferencia (con los guiones de tests/guiones_copiloto): tests/copiloto.dash. Enseña lo que anotó; acaba con
# "TODO BIEN".
#
#   tests/copiloto.sh DASH_DIR INFERENCIA_DIR [DASHC_AMIGA] [capturas/]
#
# INFERENCIA_DIR: el repositorio de Inferencia (su src/main.dash y tests/servidor_falso.py). DASHC_AMIGA: el cajón con
# dashc para el Amiga (make amiga en dashc/): con él, también explicar y arreglar un error de compilar. La ayuda de
# Dash: AYUDA=.../Dash.ayuda (si no, la de DASH_DIR/build/ayuda, de tools/gen_ayuda.py).
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...   # con MUI 3.8 (Inferencia, con su ventana de una línea)
#   SOLO=sugerencias ...   # solo las sugerencias al escribir
# El servidor falso usa el puerto 40900 del PC: con otras pruebas de red a la vez, flock /run/user/1000/dash-emu-red.lock.
set -e
dash=$1; inferencia=$2; dashc=${3:-}; capturas=${4:-}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
srv=""
trap '[ -z "$srv" ] || kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
maquina=""
if [ -n "$RTG" ]; then
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
ext="$tmp/sys/Prueba/Extensiones/Inferencia"
mkdir -p "$tmp/sys/Prueba/Inferencia" "$ext"
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/sys/Prueba/Forja"
"$dash/dash" "$inferencia/src/main.dash" -o "$tmp/sys/Prueba/Inferencia/Inferencia"
cp "$aqui/extensiones/Inferencia/manifiesto.txt" "$ext/"
"$dash/dash" "$aqui/extensiones/Inferencia/copiloto.dash" -o "$ext/Copiloto"
cp -r "$aqui/tests/prueba/copiloto" "$tmp/sys/Prueba/"
cp "${AYUDA:-$dash/build/ayuda/Dash.ayuda}" "$tmp/sys/Prueba/Dash.ayuda"
"$dash/dash" "$aqui/tests/copiloto.dash" -o "$tmp/Prueba"
if [ -n "$dashc" ]; then
  mkdir -p "$tmp/sys/Dash"
  cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
fi
{
  echo "C:MakeDir >NIL: ENV:Forja ENV:Inferencia"
  [ -z "$dashc" ] || echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv Forja/inferencia DH0:Prueba/Inferencia/Inferencia"
  echo "SetEnv Inferencia/url http://127.0.0.1:40900/api/v1/chat/completions"
  echo "SetEnv Inferencia/clave clave-falsa"
  echo "SetEnv Inferencia/modelo modelo/prueba"
  echo "SetEnv Inferencia/ayuda DH0:Prueba/Dash.ayuda"
  echo "SetEnv FORJA_SONDA 1"
  [ -z "$SOLO" ] || echo "SetEnv COPILOTO_SOLO $SOLO"
} >> "$tmp/sys/S/Startup-Extra"
INFERENCIA_GUIONES="$aqui/tests/guiones_copiloto" python3 "$inferencia/tests/servidor_falso.py" 40900 2>/dev/null &
srv=$!
sleep 1
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-600} $maquina --system "$tmp/sys" --set bsdsocket_library=1 ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Prueba" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  for f in "$tmp"/disco/Prueba/copiloto-*.png; do [ -f "$f" ] && cp "$f" "$capturas/"; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/copiloto.txt" 2>/dev/null || echo "FALLO: no hay registro"
