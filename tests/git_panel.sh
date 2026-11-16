#!/bin/bash
# Git en Forja (tests/git_panel.dash): barra, panel del proyecto, margen, panel Cambios y diferencias, en FS-UAE
# con MUI 5. Acaba con "TODO BIEN" si todo fue bien; el git del PC comprueba el repositorio al final.
#
#   tests/git_panel.sh DASH_DIR [DASHGIT_DIR [captura.png segundos...]]   (DASHGIT_DIR: por defecto ~/Projects/dashgit)
set -e
dash=$1
dg=${2:-$HOME/Projects/dashgit}
shift; [ $# -gt 0 ] && shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap '[ -n "$GUARDAR" ] && cp -r "$tmp" "$GUARDAR"; rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/${SISTEMA:-sys31muisslweb}" "$tmp/sys"
chmod -R u+w "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/juego" "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/git_panel.dash" -o "$tmp/sys/Prueba/GitPanel"
"$dash/dash" "$dg/src/main.dash" -o "$tmp/sys/C/dashgit"
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashgit DH0:C/dashgit"
  echo "SetEnv FORJA_SONDA 1"
  [ -n "$ESPERA" ] && echo "SetEnv ESPERA $ESPERA"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
  echo "Run >NIL: DH0:Prueba/GitPanel"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-500} --system "$tmp/sys" ${REAL:+--set uae_cpu_speed=real} --keep "$tmp/disco" $shots "$tmp/Forja" >/dev/null 2>&1 || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/git_panel.txt" 2>/dev/null || echo "FALLO: no hay registro"
cd "$tmp/disco/Prueba/juego" 2>/dev/null && find . -name "*.uaem" -delete
[ "$(git log --format=%s 2>/dev/null | tr '\n' '|')" = "tercero desde el panel|primero|" ] && echo "bien: el git del PC ve los dos commits" || echo "FALLO: commits en el PC: $(git log --format=%s 2>&1 | tr '\n' '|')"
[ "$(git status --porcelain 2>/dev/null)" = "?? nuevo.dash" ] && echo "bien: el git del PC ve solo nuevo.dash sin seguir" || echo "FALLO: status en el PC: $(git status --porcelain 2>&1)"
