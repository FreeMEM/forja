#!/bin/sh
# Todas las pruebas del editor de sprites, una tras otra, con un resumen al final.
#
#   tests/sprites_todas.sh DASH_DIR
#
# Necesita DASH_KICKSTART (3.1). Tarda unos 20 minutos.
dash=$1
aqui=$(cd "$(dirname "$0")" && pwd)
mal=0
for t in base iff forja lapiz paleta herramientas tamano fotogramas cebolla animar codigo dibujo ""; do
  nombre=sprites${t:+_$t}
  salida=$("$aqui/$nombre.sh" "$dash" 2>&1)
  fallos=$(echo "$salida" | grep -c 'FALLO')
  if [ "$fallos" -eq 0 ] && echo "$salida" | grep -q 'TODO BIEN'; then
    echo "bien: $nombre"
  else
    echo "FALLO: $nombre ($fallos fallos)"
    echo "$salida" | grep 'FALLO' | head -5
    mal=$((mal + 1))
  fi
done
[ $mal -eq 0 ] && echo "TODO BIEN" || echo "$mal pruebas con fallos"
