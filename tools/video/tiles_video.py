#!/usr/bin/env python3
"""El tileset del vídeo: 6 tiles de 16 (hierba, tierra, ladrillo, agua, nube y moneda) con los 16 colores de la
paleta por defecto de un BOB del editor de sprites de Forja. Así el muñeco que se dibuja en el vídeo y el mapa
comparten colores en el juego (juego.dash pone en la pantalla los del tileset).

    python3 tiles_video.py tiles.txt      # y luego: tests/iff.py escribir tiles.iff tiles.txt --frja "1 0 16 6"
"""
import sys

PAL = "000000 FFFFFF 777777 BBBBBB 444444 AA0000 FF5555 AA5500 FFAA00 FFFF55 00AA00 55FF55 00AAAA 55FFFF 0000AA 5555FF"
NEGRO, BLANCO, GRIS, CLARO, OSCURO, GRANATE, ROJO, MARRON, NARANJA, AMARILLO, VERDE, VERDE2 = range(12)
AZUL, AZUL2 = 14, 15


def tile(t, x, y):
    if t == 0:   # hierba sobre tierra
        if y < 3:
            return VERDE2 if (x + y) % 3 else VERDE
        if y < 5:
            return VERDE if (x * 7 + y) % 4 else MARRON
        return MARRON if (x * 3 + y * 5) % 7 else OSCURO
    if t == 1:   # tierra
        return MARRON if (x * 3 + y * 5) % 7 else OSCURO
    if t == 2:   # ladrillo
        if y % 4 == 3 or (x + (8 if (y // 4) % 2 else 0)) % 16 == 0:
            return GRIS
        return GRANATE if (x + y) % 3 else ROJO
    if t == 3:   # agua
        return AZUL2 if (x + y // 2) % 6 < 2 else AZUL
    if t == 4:   # nube (transparente alrededor)
        dx, dy = x - 7.5, y - 9
        d = dx * dx / 2 + dy * dy * 2
        return BLANCO if d < 30 else (CLARO if d < 40 else NEGRO)
    dx, dy = x - 7.5, y - 7.5   # moneda
    r = dx * dx + dy * dy
    return AMARILLO if r < 25 else (NARANJA if r < 36 else NEGRO)


filas = ["".join("%X" % tile(t, x, y) for t in range(6) for x in range(16)) for y in range(16)]
open(sys.argv[1], "w").write("96 16 4\n" + "\n".join(filas) + "\npaleta " + PAL + "\n")
