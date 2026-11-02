#!/bin/sh
# src/sprites.dash sin ventana (tests/sprites_base.dash), en FS-UAE. Acaba con "TODO BIEN".
#
#   tests/sprites_base.sh DASH_DIR
set -e
dash=$1
aqui=$(cd "$(dirname "$0")/.." && pwd)
cd "$dash" && python3 tools/emu_run.py --timeout ${TIEMPO:-120} "$aqui/tests/sprites_base.dash"
