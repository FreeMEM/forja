#!/bin/bash
# El menú Git de Forja: tests/git.dash maneja dashgit por ARexx (GIT y SALIDA) en FS-UAE, con push a un servidor
# git del PC (tests/servidor_git.py de dashgit). Acaba con "TODO BIEN" si todo fue bien.
#
#   tests/git.sh DASH_DIR [DASHGIT_DIR [captura.png segundos...]]      (DASHGIT_DIR: por defecto ~/Projects/dashgit)
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
puerto=$((20000 + RANDOM % 20000))
trap 'kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
chmod -R u+w "$tmp/sys"
mkdir -p "$tmp/sys/Prueba" "$tmp/srv"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$aqui/tests/git.dash" -o "$tmp/sys/Prueba/Git"
"$dash/dash" "$dg/src/main.dash" -o "$tmp/sys/C/dashgit"
git init -q --bare "$tmp/srv/origen.git"
git -C "$tmp/srv/origen.git" config http.receivepack true
python3 "$dg/tests/servidor_git.py" "$tmp/srv" $puerto &
srv=$!
{
  echo "C:MakeDir ENV:Forja"
  echo "SetEnv Forja/dashgit DH0:C/dashgit"
  echo "SetEnv SERVIDOR http://127.0.0.1:$puerto/origen.git"
  echo "SetEnv FORJA_SONDA 1"
  [ -n "$ESPERA" ] && echo "SetEnv ESPERA $ESPERA"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/main.dash"
  echo "Run >NIL: DH0:Prueba/Git"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-500} --set bsdsocket_library=1 --system "$tmp/sys" --keep "$tmp/disco" $shots "$tmp/Forja" >/dev/null 2>&1 || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/git.txt" 2>/dev/null || echo "FALLO: no hay registro"
[ "$(git -C "$tmp/srv/origen.git" log --format=%s main 2>/dev/null | tr '\n' '|')" = "segundo, con espacios|primero|" ] && echo "bien: el servidor tiene los dos commits" || echo "FALLO: el servidor no tiene los commits"
