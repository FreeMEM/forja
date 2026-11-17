#!/bin/sh
# Las extensiones de Forja (tests/extensiones.dash), en FS-UAE: Contar (extensiones/Contar) y Eco
# (tests/extensiones/Eco) en DH0:Prueba/Extensiones, junto a Forja. Enseña lo que anotó; acaba con "TODO BIEN".
#
#   tests/extensiones.sh DASH_DIR [DASHC_AMIGA] [capturas/]
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (make amiga en dashc/): con él, también COMPILADO. capturas/: guarda
# ahí marcas.png, gestor.png y gestor-apagada.png (las hace el propio Amiga).
#   RTG=1 tests/extensiones.sh ...      # AmigaOS 3.2 con tarjeta gráfica de 256 colores y MUI 5 (sys32rtg8)
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 ...   # con MUI 3.8 (el sistema de CoffinOS)
#   REAL=1 ...                          # la CPU a la velocidad de un A1200 (68020 a 14 MHz)
set -e
dash=$1; dashc=${2:-}; capturas=${3:-}
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
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Prueba/Extensiones/Contar" "$tmp/sys/Prueba/Extensiones/Eco"
# Forja en DH0:Prueba (sus extensiones, en DH0:Prueba/Extensiones). La prueba es el programa que espera el emulador y arranca
# Forja ella misma (como tests/salir.sh), para poder mirar qué queda tras salir de Forja
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/sys/Prueba/Forja"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
echo "un dibujo" > "$tmp/sys/Prueba/dibujo.eco"
"$dash/dash" "$aqui/tests/extensiones.dash" -o "$tmp/Prueba"
cp "$aqui/extensiones/Contar/manifiesto.txt" "$tmp/sys/Prueba/Extensiones/Contar/"
"$dash/dash" "$aqui/extensiones/Contar/contar.dash" -o "$tmp/sys/Prueba/Extensiones/Contar/Contar"
cp "$aqui/tests/extensiones/Eco/manifiesto.txt" "$tmp/sys/Prueba/Extensiones/Eco/"
# una extensión para instalar desde un cajón con el gestor (su programa no se arranca: el de Contar, con otro nombre)
mkdir -p "$tmp/sys/Fuera/Saludo"
printf 'nombre = Saludo\nversion = 1.0\nautor = Prueba\ndescripcion = Para probar el gestor.\nprograma = Saludo\narranque = menu\nmenu = Saludar | | saludo\n' > "$tmp/sys/Fuera/Saludo/manifiesto.txt"
cp "$tmp/sys/Prueba/Extensiones/Contar/Contar" "$tmp/sys/Fuera/Saludo/Saludo"
"$dash/dash" "$aqui/tests/extensiones/Eco/eco.dash" -o "$tmp/sys/Prueba/Extensiones/Eco/Eco"
if [ -n "$dashc" ]; then
  mkdir -p "$tmp/sys/Dash"
  cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
  cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
fi
{
  echo "C:MakeDir >NIL: ENV:Forja"
  [ -z "$dashc" ] || echo "SetEnv Forja/dashc DH0:Dash/dashc"
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-600} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Prueba" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  for f in marcas gestor gestor-apagada panel-lista panel-charla sugerencia-varias; do cp "$tmp/disco/Prueba/$f.png" "$capturas/" 2>/dev/null || true; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/extensiones.txt" 2>/dev/null || echo "FALLO: no hay registro"
