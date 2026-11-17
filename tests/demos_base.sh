#!/bin/sh
# La extensión Demos sin ventana (tests/demos_base.dash), en FS-UAE, con la demo de la plantilla corriendo aparte
# (con musica.mod de tests/mod_ejemplo.py). Después compila el código de copper que escribió. Acaba con "TODO BIEN"
# dos veces.
#
#   tests/demos_base.sh DASH_DIR
#
# Necesita DASH_KICKSTART (3.1). En el A1200 con chipset (el sonido y el copper de verdad).
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba/demo" "$tmp/plt"
python3 -I "$aqui/tests/mod_ejemplo.py" "$tmp/sys/Prueba/musica.mod"
# la demo de la plantilla, con su música
for f in "$aqui"/plantillas/demo/*; do sed 's/%NOMBRE%/Barras/g' "$f" > "$tmp/plt/$(basename "$f")"; done
"$dash/dash" "$tmp/plt/main.dash" -o "$tmp/sys/Prueba/demo/Barras"
cp "$tmp/plt/demo.sync" "$tmp/sys/Prueba/demo/"
cp "$tmp/sys/Prueba/musica.mod" "$tmp/sys/Prueba/demo/"
"$dash/dash" "$aqui/tests/demos_base.dash" -o "$tmp/Prueba"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Prueba" || true
# el código de copper que escribió, compilado aquí
for f in copper_gen copper_tabla; do
  if [ ! -f "$tmp/disco/Prueba/$f.dash" ]; then echo "FALLO: no está $f.dash"; exit 0; fi
done
{ cat "$tmp/disco/Prueba/copper_gen.dash"; echo; cat "$tmp/disco/Prueba/copper_tabla.dash" | sed 's/copper_degradado/copper_tabla/'; 
  printf 'Main\n    if screen_open_custom(320, 256, 1, "x")\n        copper_degradado()\n        t = copper_tabla()\n        amiga_free(t, 512)\n        screen_close()\n    end\nend\n'; } > "$tmp/gen.dash"
if "$dash/dash" "$tmp/gen.dash" -o "$tmp/gen"; then echo "bien: el código de copper compila"; echo "TODO BIEN"; else echo "FALLO: el código de copper no compila"; cat "$tmp/gen.dash" | head -30; fi
