#!/bin/sh
# El editor de mapas con un usuario de prueba (tests/mapas_forja.dash), en FS-UAE; después mira con tests/fmap.py el
# mapa que guardó. Acaba con "TODO BIEN" dos veces si todo fue bien.
#
#   tests/mapas_forja.sh DASH_DIR [captura.png segundos...]
#
# DASH_DIR: un Dash con tilemap_*. Necesita DASH_KICKSTART (3.1). RTG=1: AmigaOS 3.2 con 256 colores.
set -e
dash=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
maquina=""
if [ -n "$RTG" ]; then
  cp -r "$HOME/.cache/dash-emu/sys32rtg8" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
python3 -I "$aqui/tests/mapa_ejemplo.py" "$tmp/tiles.txt" "$tmp/capas.txt"
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/tiles.iff" "$tmp/tiles.txt" --frja "1 0 16 6"
# solo fondo y delante: la prueba pone ella la capa de choques y los objetos
python3 -I "$aqui/tests/fmap.py" escribir "$tmp/sys/Prueba/juego/nivel.fmap" 40 20 16 tiles.iff $(tr " " "\n" < "$tmp/capas.txt" | grep -v "^@\|^choques!")
"$dash/dash" "$aqui/tests/mapas_forja.dash" -o "$tmp/sys/Prueba/MapasForja"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/nivel.fmap"
  echo "Run >NIL: DH0:Prueba/MapasForja"
} >> "$tmp/sys/S/Startup-Extra"
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-300} $maquina --system "$tmp/sys" --keep "$tmp/disco" $shots "$tmp/Forja" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/mapas_forja.txt" 2>/dev/null || echo "FALLO: no hay registro"
# el mapa guardado: 41 de ancho, 3 capas (la nueva, de choques con una escalera, la segunda), lo pintado en la
# primera y los dos objetos
python3 -I - "$aqui/tests/fmap.py" "$tmp/disco/Prueba/juego/nivel.fmap" <<'PY'
import runpy, sys
f = runpy.run_path(sys.argv[1])
ancho, alto, tile, tileset, capas, objetos = f["leer"](sys.argv[2], True)
c = capas[0][3]
ch = capas[1][3]
ok = (ancho, alto, tile, tileset, len(capas)) == (41, 20, 16, "tiles.iff", 3) and c[1 * 41 + 2] == 16387 \
    and c[3 * 41 + 4] == 2 and c[4 * 41 + 8] == 2 and capas[2][0] == "delante" \
    and capas[1][1] == 1 and ch[1 * 41 + 3] == 3 and sum(1 for x in ch if x) == 1 \
    and [(o[0], o[1], o[2]) for o in objetos] == [(7 * 16, 2 * 16, "enemigo"), (2 * 16, 0, "jugador")]
print("bien: el mapa guardado" if ok else "FALLO: el mapa guardado: %r" % ((ancho, alto, tile, tileset, [x[:2] for x in capas], c[41:50], [i for i, x in enumerate(ch) if x], objetos),))
if ok:
    print("TODO BIEN")
PY
