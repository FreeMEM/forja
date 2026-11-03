#!/usr/bin/env python3
"""Mapas de tiles IFF FORM FMAP (los de tilemap_save de Dash y el editor de mapas de Forja), para las pruebas.

    python3 tests/fmap.py escribir mapa.fmap ANCHO ALTO TILE TILESET [nombre:celdas ...] [@x,y,clase,nombre,sprite ...]
        celdas: los valores separados por comas, fila a fila (los que falten, 0); un nombre acabado en "!" es
        una capa de choques. Lo que empieza por "@" es un objeto.
    python3 tests/fmap.py leer mapa.fmap      # ancho alto tile tileset, y una línea por capa
    python3 tests/fmap.py prueba              # se prueba a sí mismo
"""
import struct
import sys


def escribir(ruta, ancho, alto, tile, tileset, capas, objetos=()):
    """capas: lista de (nombre, tipo, visible, celdas); objetos: lista de (x, y, clase, nombre, sprite)"""
    trozos = [b"MHDR" + struct.pack(">I5H", 10, 1, ancho, alto, tile, len(capas))]
    t = tileset.encode("latin-1")
    trozos.append(b"TSET" + struct.pack(">I", len(t)) + t + (b"\0" if len(t) % 2 else b""))
    for nombre, tipo, visible, celdas in capas:
        n = nombre.encode("latin-1")
        cab = bytes([tipo, 1 if visible else 0, len(n)]) + n + (b"\0" if (3 + len(n)) % 2 else b"")
        celdas = list(celdas) + [0] * (ancho * alto - len(celdas))
        datos = cab + struct.pack(">%dH" % (ancho * alto), *celdas[:ancho * alto])
        trozos.append(b"LAYR" + struct.pack(">I", len(datos)) + datos)
    if objetos:
        datos = struct.pack(">H", len(objetos))
        for x, y, clase, nombre, sprite in objetos:
            o = struct.pack(">hh", x, y)
            for t in (clase, nombre, sprite):
                t = t.encode("latin-1")
                o += bytes([len(t)]) + t
            datos += o + (b"\0" if len(o) % 2 else b"")
        trozos.append(b"OBJS" + struct.pack(">I", len(datos)) + datos + (b"\0" if len(datos) % 2 else b""))
    cuerpo = b"FMAP" + b"".join(trozos)
    with open(ruta, "wb") as f:
        f.write(b"FORM" + struct.pack(">I", len(cuerpo)) + cuerpo)


def leer(ruta, con_objetos=False):
    """(ancho, alto, tile, tileset, [(nombre, tipo, visible, celdas)]); con_objetos, también la lista de objetos
    (x, y, clase, nombre, sprite)"""
    d = open(ruta, "rb").read()
    assert d[0:4] == b"FORM" and d[8:12] == b"FMAP", "no es un FORM FMAP"
    fin = 8 + struct.unpack(">I", d[4:8])[0]
    p = 12
    ancho = alto = tile = 0
    tileset = ""
    capas = []
    objetos = []
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
        elif nombre == b"OBJS":
            q = 2
            for _ in range(struct.unpack(">H", c[:2])[0]):
                x, y = struct.unpack(">hh", c[q:q + 4])
                q += 4
                t = []
                for _ in range(3):
                    n = c[q]
                    t.append(c[q + 1:q + 1 + n].decode("latin-1"))
                    q += 1 + n
                if (4 + 3 + sum(len(x) for x in t)) % 2:
                    q += 1
                objetos.append((x, y, t[0], t[1], t[2]))
        p += 8 + largo + (largo & 1)
    if con_objetos:
        return ancho, alto, tile, tileset, capas, objetos
    return ancho, alto, tile, tileset, capas


def main():
    a = sys.argv[1:]
    if a and a[0] == "escribir":
        capas = []
        objetos = []
        for c in a[6:]:
            if c.startswith("@"):
                x, y, clase, nombre, sprite = (c[1:].split(",") + ["", "", ""])[:5]
                objetos.append((int(x), int(y), clase, nombre, sprite))
                continue
            nombre, celdas = c.split(":", 1)[0], c.split(":", 1)[1] if ":" in c else ""
            tipo = 1 if nombre.endswith("!") else 0
            capas.append((nombre.rstrip("!"), tipo, True, [int(x) for x in celdas.split(",") if x != ""]))
        escribir(a[1], int(a[2]), int(a[3]), int(a[4]), a[5], capas or [("fondo", 0, True, [])], objetos)
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
        o = [(16, 160, "jugador", "", ""), (40, -3, "moneda", "oro", "moneda.iff")]
        escribir(r, 2, 2, 8, "", [("a", 0, True, [])], o)
        assert leer(r, True)[5] == o, leer(r, True)
        print("bien")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
