#!/bin/sh
# La memoria que usa Forja al arrancar (tests/memoria.dash), en FS-UAE: sin extensiones, con Git o con todas.
#
#   MEMORIA=nada|git|todas tests/memoria.sh DASH_DIR [DASHC_AMIGA [DASHGIT_DIR]]
#
# DASHC_AMIGA: el cajón con dashc para el Amiga (dashc.amiga y los dashc_*.drt): con él, también lo que usa al
# compilar. DASHGIT_DIR: por defecto ~/Projects/dashgit.
#   RTG=1 SISTEMA=~/.cache/dash-emu/sys32rtg38 ...    # AmigaOS 3.2 con tarjeta gráfica y MUI 3.8 (68040)
#   REAL=1 ...                                         # la CPU a la velocidad de un A1200
#   FORJA=otro/cajón ...                               # las fuentes de Forja de otro cajón (para comparar)
#
# Con "git", el proyecto (tests/prueba/juego) es un repositorio de git con un commit, y Git usa el servidor de
# dashgit. Con "todas": Git, Inferencia (el copiloto; sin Inferencia, que no arranca hasta usarla), Sprites y Mapas.
set -e
dash=$1
dashc=${2:-}
dg=${3:-$HOME/Projects/dashgit}
que=${MEMORIA:-nada}
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
chmod -R u+w "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/Extensiones"
"$dash/dash" "${FORJA:-$aqui}/src/main.dash" -o "$tmp/sys/Prueba/Forja"
cp -r "$aqui/tests/prueba/juego" "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/memoria.dash" -o "$tmp/Memoria"
. "$aqui/tests/extension.sh"
if [ "$que" != "nada" ]; then
  extension Git git
  "$dash/dash" "$dg/src/main.dash" -o "$tmp/sys/C/dashgit"
  echo "SetEnv Forja/dashgit DH0:C/dashgit" >> "$tmp/sys/S/Startup-Extra"
  (cd "$tmp/sys/Prueba/juego" && git init -q && git add -A && git -c user.name=Prueba -c user.email=prueba@ejemplo.org commit -qm primero)
fi
if [ "$que" = "todas" ]; then
  extension Inferencia copiloto Copiloto
  extension Sprites editor_sprites
  extension Mapas editor_mapas
  python3 -I -c "import sys; open(sys.argv[1], 'w').write('16 16 2\n' + '\n'.join(['0123' * 4] * 16) + '\npaleta 000000 E0E0E0 E08030 3060C0\n')" "$tmp/nave.txt"
  python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/nave.iff" "$tmp/nave.txt" --frja "1 1 16 6"
  python3 -I "$aqui/tests/mapa_ejemplo.py" "$tmp/tiles.txt" "$tmp/capas.txt"
  python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/tiles.iff" "$tmp/tiles.txt" --frja "1 0 16 6"
  python3 -I "$aqui/tests/fmap.py" escribir "$tmp/sys/Prueba/juego/nivel.fmap" 40 20 16 tiles.iff $(tr " " "\n" < "$tmp/capas.txt" | grep -v "^@\|^choques!")
fi
if [ -n "$dashc" ]; then
  mkdir -p "$tmp/sys/Dash"
  cp "$dashc/dashc.amiga" "$tmp/sys/Dash/dashc"
  cp "$dashc"/dashc_*.drt "$tmp/sys/Dash/"
  echo "SetEnv Forja/dashc DH0:Dash/dashc" >> "$tmp/sys/S/Startup-Extra"
fi
{
  echo "C:MakeDir >NIL: ENV:Forja"
  echo "SetEnv Forja/extensiones DH0:Prueba/Extensiones"
  echo "SetEnv MEMORIA $que"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-600} $maquina --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" "$tmp/Memoria" > /dev/null 2>&1 || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/memoria.txt" 2>/dev/null || echo "FALLO: no hay registro"
