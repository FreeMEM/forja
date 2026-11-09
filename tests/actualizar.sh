#!/bin/sh
# La actualización de Dash desde Forja (src/actualizar.dash, tests/actualizar.dash) en FS-UAE, contra un GitHub de
# mentira en el PC: un servidor HTTP local con la respuesta de la API y dos tar hechos con tools/paquete_amiga.py de
# Dash, uno bueno y otro estropeado. Enseña lo que pasó; acaba con "TODO BIEN" si todo fue bien.
#
#   tests/actualizar.sh DASH_DIR
#
# DASH_DIR: el Dash que compila (y cuyo tools/paquete_amiga.py hace el tar).
#   REAL=1 tests/actualizar.sh ...   # con la CPU emulada a la velocidad de un A1200 (68020 a 14 MHz), no al máximo
#   GRANDE=tar tests/actualizar.sh ...   # con un tar de verdad (build/dash-X.Y.Z-amiga.tar) en lugar del pequeño
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'kill $servidor 2>/dev/null; rm -rf "$tmp"' EXIT
puerto=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')
python3 - "$dash" "$tmp/web" "$puerto" "${GRANDE:-}" <<'PY'
import json, shutil, sys
from pathlib import Path
dash, web, puerto, grande = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, str(dash / "tools"))
from paquete_amiga import tar_actualizar
caj = web.parent / "Dash"
(caj / "Forja/Catalogs/english").mkdir(parents=True)
(caj / "lib/red").mkdir(parents=True)
(caj / "dash").write_bytes(b"\0\0\x03\xf3$VER: dash 2.8.0 (9.11.2026)\n")
(caj / "LEEME").write_bytes(b"el nuevo\n")
(caj / "Forja/Catalogs/english/Forja.catalog").write_bytes("catálogo\n".encode("latin-1"))
(caj / "lib/red/http.dash").write_bytes(b"red\n")
(caj / "Instalar").write_bytes(b"no va\n")
for d in ("bien", "roto"):
    (web / d).mkdir(parents=True)
tar = web / "bien/dash-2.8.0-amiga.tar"
if grande:
    shutil.copy(grande, tar)
else:
    tar_actualizar(caj, tar)
import tarfile
datos = bytearray(tar.read_bytes())
# el CRC del último fichero, estropeado (el mismo tamaño: solo lo ve la comprobación)
with tarfile.open(tar) as t:
    ultimo = t.getmembers()[-1]
datos[ultimo.offset_data + ultimo.size - 8] ^= 0x55
(web / "roto/dash-2.8.0-amiga.tar").write_bytes(datos)
for d in ("bien", "roto"):
    t = web / d / "dash-2.8.0-amiga.tar"
    (web / d / "latest").write_text(json.dumps({"tag_name": "v2.8.0", "assets": [
        {"name": "dash-2.8.0-amiga.lha", "size": 5, "browser_download_url": "http://127.0.0.1:%s/no" % puerto},
        {"name": t.name, "size": t.stat().st_size,
         "browser_download_url": "http://127.0.0.1:%s/%s/%s" % (puerto, d, t.name)}]}))
PY
(cd "$tmp/web" && exec python3 -m http.server "$puerto" --bind 127.0.0.1 >/dev/null 2>&1) &
servidor=$!
cp -r "$HOME/.cache/dash-emu/sys31" "$tmp/sys"
echo "$puerto" > "$tmp/puerto"
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-400} --system "$tmp/sys" --set bsdsocket_library=1 \
    ${REAL:+--set uae_cpu_speed=real} --file "$tmp/puerto" "$aqui/tests/actualizar.dash"
