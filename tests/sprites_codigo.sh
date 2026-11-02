#!/bin/sh
# El botón Código del editor de sprites (tests/sprites_codigo.dash), en FS-UAE; después mete cada código copiado en
# un programa, lo compila con Dash y lo ejecuta en el emulador con su IFF: tiene que cargarlo.
# Acaba con "TODO BIEN" dos veces si todo fue bien.
#
#   tests/sprites_codigo.sh DASH_DIR
#
# Necesita DASH_KICKSTART (3.1).
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Forja"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
python3 -I - "$tmp" <<'PY'
import sys
d = sys.argv[1]
f = ["".join("%X" % ((x * 7 + y * 3) % 4 if (x + y) % 3 else 0) for x in range(48)) for y in range(16)]
open(d + "/nave.txt", "w").write("48 16 2\n" + "\n".join(f) + "\npaleta 000000 FF0000 00FF00 0000FF\n")
f = ["".join("%X" % ((x + y) % 16 if (x % 32 - 16) ** 2 + (y - 16) ** 2 < 200 else 0) for x in range(64)) for y in range(32)]
open(d + "/bola.txt", "w").write("64 32 4\n" + "\n".join(f) + "\npaleta " + " ".join("%06X" % (i * 0x101010) for i in range(16)) + "\n")
PY
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/nave.iff" "$tmp/nave.txt" --frja "1 1 16 6"
python3 -I "$aqui/tests/iff.py" escribir "$tmp/sys/Prueba/juego/bola.iff" "$tmp/bola.txt" --frja "1 0 32 4"
"$dash/dash" "$aqui/tests/sprites_codigo.dash" -o "$tmp/sys/Prueba/SpritesCodigo"
{
  echo "SetEnv FORJA_SONDA 1"
  echo "SetEnv FORJA_PRUEBA DH0:Prueba/juego/nave.iff"
  echo "Run >NIL: DH0:Prueba/SpritesCodigo"
} >> "$tmp/sys/S/Startup-Extra"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-240} --system "$tmp/sys" --keep "$tmp/disco" "$tmp/Forja" > /dev/null || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/sprites_codigo.txt" 2>/dev/null || echo "FALLO: no hay registro"
# cada código, dentro de un programa con su pantalla y una ventana en ella (gfx_rgb8 sin ventana cuelga el programa:
# es de Dash, tarea 15d de docs/SPRITES_LOOP.md), compilado y ejecutado con los IFF
python3 -I - "$tmp" <<'PY'
import sys
d = sys.argv[1]
def programa(nombre, codigo, planos, despues):
    cuerpo = "\n".join("        " + l for l in codigo.splitlines())
    open("%s/%s.dash" % (d, nombre), "w").write(
        'Main\n    dir_change("DH0:Prueba/juego")\n    if screen_open_custom(320, 200, %d, "Prueba")\n        window_create("Prueba", 0, 12, 320, 180, 2)\n%s\n%s\n        window_close(0)\n        screen_close()\n    end\nend\n'
        % (planos, cuerpo, "\n".join("        " + l for l in despues)))
programa("usa_sprite", open(d + "/disco/Prueba/codigo_sprite.txt", encoding="utf-8").read(), 2,
         ["sprite_frame(0, 2)", 'Print "sprite: fin"', "sprite_free(0)"])
programa("usa_bob", open(d + "/disco/Prueba/codigo_bob.txt", encoding="utf-8").read(), 4,
         ["bob_frame(0, 1)", "bob_pos(0, 10, 10)", "bob_draw(0)", 'Print "bob: fin"', "bob_free(0)"])
PY
rm -rf "$tmp/sys2"; cp -r "$tmp/disco" "$tmp/sys2"
salida=$(cd "$dash" && python3 tools/emu_run.py --timeout 120 --system "$tmp/sys2" "$tmp/usa_sprite.dash" "$tmp/usa_bob.dash" 2>&1 || true)
echo "$salida" | grep -E 'fin|No se puede|RC=|rror' || true
if echo "$salida" | grep -q 'sprite: fin' && echo "$salida" | grep -q 'bob: fin' && ! echo "$salida" | grep -q 'No se puede'; then
  echo "bien: el código copiado compila y carga el sprite y el BOB"
  echo "TODO BIEN"
else
  echo "FALLO: el código copiado no carga"
  echo "$salida" | tail -30
fi
