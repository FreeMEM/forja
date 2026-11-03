#!/usr/bin/env python3
"""El mapa de ejemplo de las pruebas del editor de mapas: un tileset de 6 tiles de 16 (hierba, tierra, ladrillo,
agua, nube y una moneda) y un mapa de 40 x 20 con dos capas (fondo y delante) que los usa.

    python3 tests/mapa_ejemplo.py tiles.txt capas.txt

tiles.txt es para tests/iff.py escribir (con --frja "1 0 16 6"); capas.txt, los argumentos de capa de
tests/fmap.py escribir.
"""
import sys
pal = "000000 1F7A2E 3FBF4F 7A4A1F A0662E 8A2E1F C04A2E 1F3F9F 3F6FDF FFFFFF CFCFCF FFCF1F FF9F00 202020 606060 E0E0E0"
def tile(t, x, y):
    if t == 0:   # hierba sobre tierra
        return 2 if y < 4 else (1 if y < 6 else (3 if (x + y) % 5 else 4))
    if t == 1:   # tierra
        return 3 if (x * 3 + y) % 7 else 4
    if t == 2:   # ladrillo
        return 14 if y % 4 == 3 or (x + (8 if (y // 4) % 2 else 0)) % 16 == 0 else (5 if (x + y) % 3 else 6)
    if t == 3:   # agua
        return 8 if (x + y // 2) % 6 < 2 else 7
    if t == 4:   # nube (transparente alrededor)
        dx, dy = x - 7.5, y - 9
        return 9 if dx * dx / 2 + dy * dy * 2 < 30 else (10 if dx * dx / 2 + dy * dy * 2 < 40 else 0)
    dx, dy = x - 7.5, y - 7.5   # moneda
    r = dx * dx + dy * dy
    return 11 if r < 25 else (12 if r < 36 else 0)
filas = ["".join("%X" % tile(t, x, y) for t in range(6) for x in range(16)) for y in range(16)]
open(sys.argv[1], "w").write("96 16 4\n" + "\n".join(filas) + "\npaleta " + pal + "\n")
fondo, delante = [], []
for y in range(20):
    for x in range(40):
        suelo = 14 + (2 if 10 <= x < 16 else 0) - (3 if 24 <= x < 30 else 0)
        v = 0
        if y == suelo:
            v = 1
        elif y > suelo:
            v = 2
        if 10 <= x < 16 and y >= 15:
            v = 4
        if y == 8 and 18 <= x < 22:
            v = 3
        fondo.append(v)
        d = 0
        if (x, y) in ((3, 3), (12, 2), (31, 4)):
            d = 5
        if y == 7 and 18 <= x < 22:
            d = 6
        delante.append(d)
open(sys.argv[2], "w").write("fondo:" + ",".join(map(str, fondo)) + " delante:" + ",".join(map(str, delante)))
