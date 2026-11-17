#!/bin/sh
# Proyectos en Forja (pasos 3.1 y 3.2 de docs/FORJA_LOOP.md, tests/forja_proyecto.dash): un proyecto nuevo de cada
# plantilla por ARexx (NUEVOPROYECTO), que se compila con la orden dash del Amiga; la orden del Shell se ejecuta con
# los argumentos del proyecto; PROPIEDAD; las ventanas Propiedades y Nuevo proyecto; y, con un Workbench 3.5 o más
# (SISTEMA de 3.2), abrir un proyecto desde su icono. Enseña lo que anotó; acaba con "TODO BIEN".
#
#   tests/forja_proyecto.sh DASH_DIR DASHC_AMIGA [capturas/]
#
# DASHC_AMIGA: el cajón con dash para el Amiga (make amiga en dashc/ de Dash: dashc.amiga y los dashc_*.drt).
#   SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1 tests/forja_proyecto.sh ...   # con MUI 3.8 (y el icono, en 3.2: con LoadWB)
set -e
dash=$1; dashc=$2; capturas=${3:-}
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
python3 "$aqui/tools/plantillas.py" --comprobar
maquina=""
if [ -n "$RTG" ]; then
  cp -r "${SISTEMA:-$HOME/.cache/dash-emu/sys32rtg8}" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba" "$tmp/sys/Forja" "$tmp/sys/Proyectos"
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/sys/Forja/Forja"
# la imagen del icono de los .forja, como en el paquete
mkdir -p "$tmp/sys/Forja/Iconos"
python3 -c "import sys; sys.path.insert(0, '$aqui/tools'); from plantillas import icono_proyecto; open('$tmp/sys/Forja/Iconos/proyecto.info', 'wb').write(icono_proyecto())"
"$dash/dash" "$aqui/tests/forja_proyecto.dash" -o "$tmp/ProyectoT"
# la orden dash en DH0:Dash, con sus runtimes (dash_mc.drt, dash_fpu.drt...) y lib/ (lib/amiga/gl.dash de la 3D)
mkdir -p "$tmp/sys/Dash"
cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dash"
for f in "$dashc"/dashc_*.drt; do cp "$f" "$tmp/sys/Dash/$(basename "$f" | sed 's/^dashc_/dash_/')"; done
cp -r "$dash/lib" "$tmp/sys/Dash/lib"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashc DH0:Dash/dash"
  echo "SetEnv Forja/proyectos DH0:Proyectos"
  echo "SetEnv Forja/buscar_dash no"
  echo "SetEnv FORJA_SONDA 1"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-600} --system "$tmp/sys" $maquina ${RTG:+--workbench} ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/ProyectoT" || true
if [ -n "$capturas" ]; then
  mkdir -p "$capturas"
  for f in "$tmp"/disco/Prueba/*.png; do [ -f "$f" ] && cp "$f" "$capturas/"; done
fi
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/proyecto.txt" 2>/dev/null || echo "FALLO: no hay registro"
