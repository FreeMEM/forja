#!/usr/bin/env python3
"""Mapas de tiles IFF FORM FMAP (los de tilemap_save de Dash y el editor de mapas de Forja), para las pruebas.

    python3 tests/fmap.py escribir mapa.fmap ANCHO ALTO TILE TILESET [capa:nombre:celdas ...]
        celdas: los valores separados por comas, fila a fila (los que falten, 0)
    python3 tests/fmap.py leer mapa.fmap      # ancho alto tile tileset, y una línea por capa
    python3 tests/fmap.py prueba              # se prueba a sí mismo
"""
import struct
import sys


def escribir(ruta, ancho, alto, tile, tileset, capas):
    """capas: lista de (nombre, tipo, visible, celdas)"""
    trozos = [b"MHDR" + struct.pack(">I5H", 10, 1, ancho, alto, tile, len(capas))]
    t = tileset.encode("latin-1")
    trozos.append(b"TSET" + struct.pack(">I", len(t)) + t + (b"\0" if len(t) % 2 else b""))
    for nombre, tipo, visible, celdas in capas:
        n = nombre.encode("latin-1")
        cab = bytes([tipo, 1 if visible else 0, len(n)]) + n + (b"\0" if (3 + len(n)) % 2 else b"")
        celdas = list(celdas) + [0] * (ancho * alto - len(celdas))
        datos = cab + struct.pack(">%dH" % (ancho * alto), *celdas[:ancho * alto])
        trozos.append(b"LAYR" + struct.pack(">I", len(datos)) + datos)
    cuerpo = b"FMAP" + b"".join(trozos)
    with open(ruta, "wb") as f:
        f.write(b"FORM" + struct.pack(">I", len(cuerpo)) + cuerpo)


def leer(ruta):
    """(ancho, alto, tile, tileset, [(nombre, tipo, visible, celdas)])"""
    d = open(ruta, "rb").read()
    assert d[0:4] == b"FORM" and d[8:12] == b"FMAP", "no es un FORM FMAP"
    fin = 8 + struct.unpack(">I", d[4:8])[0]
    p = 12
    ancho = alto = tile = 0
    tileset = ""
    capas = []
    while p + 8 <= fin:
        nombre, largo = d[p:p + 4], struct.unpack(">I", d[p + 4:p + 8])[0]
        c = d[p + 8:p + 8 + largo]
        if nombre == b"MHDR":
            _, ancho, alto, tile, _ = struct.unpack(">5H", c[:10])
        elif nombre == b"TSET":
            tileset = c.decode("latin-1")
        elif nombre == b"LAYR":
            n = c[2]
            cab = (3 + n + 1) & ~1
            celdas = list(struct.unpack(">%dH" % (ancho * alto), c[cab:cab + ancho * alto * 2]))
            capas.append((c[3:3 + n].decode("latin-1"), c[0], bool(c[1]), celdas))
        p += 8 + largo + (largo & 1)
    return ancho, alto, tile, tileset, capas


def main():
    a = sys.argv[1:]
    if a and a[0] == "escribir":
        capas = []
        for c in a[6:]:
            nombre, celdas = c.split(":", 1)[0], c.split(":", 1)[1] if ":" in c else ""
            capas.append((nombre, 0, True, [int(x) for x in celdas.split(",") if x != ""]))
        escribir(a[1], int(a[2]), int(a[3]), int(a[4]), a[5], capas or [("fondo", 0, True, [])])
    elif a and a[0] == "leer":
        ancho, alto, tile, tileset, capas = leer(a[1])
        print(ancho, alto, tile, tileset)
        for nombre, tipo, visible, celdas in capas:
            print(nombre, tipo, int(visible), ",".join(str(x) for x in celdas))
    elif a and a[0] == "prueba":
        import os
        import tempfile
        r = os.path.join(tempfile.mkdtemp(), "p.fmap")
        escribir(r, 3, 2, 16, "tiles.iff", [("fondo", 0, True, [1, 2, 16387]), ("x", 1, False, [0, 0, 0, 0, 0, 5])])
        assert leer(r) == (3, 2, 16, "tiles.iff", [("fondo", 0, True, [1, 2, 16387, 0, 0, 0]),
                                                   ("x", 1, False, [0, 0, 0, 0, 0, 5])]), leer(r)
        print("bien")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
