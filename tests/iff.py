#!/usr/bin/env python3
"""IFF ILBM para las pruebas del editor de sprites: crea imágenes de prueba y lee las que guarda Forja.

    python3 tests/iff.py escribir salida.iff entrada.txt [--comprimir] [--mascara] [--frja "1 0 16 6"] [--grab X,Y]
    python3 tests/iff.py leer fichero.iff
    python3 tests/iff.py prueba          # se prueba a sí mismo

entrada.txt: la primera línea "ancho alto planos"; después una fila de píxeles por línea, un color por cifra
hexadecimal (dos cifras por píxel si hay más de 4 planos). Puede acabar con una línea "paleta RRGGBB RRGGBB ...".

leer escribe lo mismo que entrada.txt (con la paleta), y antes, si los hay, "FRJA ..." y "GRAB x y". Solo usa la
biblioteca estándar.
"""
import struct
import sys


def byterun1(datos):
    """Comprime una fila con ByteRun1 (como DPaint)."""
    sal = bytearray()
    i = 0
    n = len(datos)
    while i < n:
        j = i
        while j + 1 < n and datos[j + 1] == datos[i] and j - i < 127:
            j += 1
        if j > i:
            sal += bytes([(257 - (j - i + 1)) & 255, datos[i]])
            i = j + 1
            continue
        j = i
        while j + 1 < n and j - i < 127 and not (j + 2 < n and datos[j + 1] == datos[j + 2]):
            j += 1
        sal += bytes([j - i]) + datos[i:j + 1]
        i = j + 1
    return bytes(sal)


def des_byterun1(datos, pos, cuantos):
    sal = bytearray()
    while len(sal) < cuantos:
        c = datos[pos]
        pos += 1
        if c < 128:
            sal += datos[pos:pos + c + 1]
            pos += c + 1
        elif c > 128:
            sal += bytes([datos[pos]]) * (257 - c)
            pos += 1
    return bytes(sal[:cuantos]), pos


def trozo(tipo, datos):
    t = tipo.encode() + struct.pack(">I", len(datos)) + datos
    return t + (b"\0" if len(datos) & 1 else b"")


def escribir(ruta, ancho, alto, planos, filas, paleta, comprimir=False, mascara=False, frja=None, grab=None):
    fila_bytes = (ancho + 15) // 16 * 2
    bmhd = struct.pack(">HHhhBBBBHBBhh", ancho, alto, 0, 0, planos, 1 if mascara else 2, 1 if comprimir else 0, 0, 0,
                       10, 11, ancho, alto)
    cuerpo = bytearray()
    for y in range(alto):
        for p in range(planos + (1 if mascara else 0)):
            fila = bytearray(fila_bytes)
            for x in range(ancho):
                c = filas[y][x]
                bit = (c >> p) & 1 if p < planos else (1 if c else 0)
                if bit:
                    fila[x // 8] |= 0x80 >> (x % 8)
            cuerpo += byterun1(bytes(fila)) if comprimir else fila
    cmap = b"".join(struct.pack(">BBB", (c >> 16) & 255, (c >> 8) & 255, c & 255) for c in paleta[:1 << planos])
    datos = b"ILBM" + trozo("BMHD", bmhd) + trozo("CMAP", cmap)
    if grab:
        datos += trozo("GRAB", struct.pack(">hh", *grab))
    if frja:
        datos += trozo("FRJA", frja.encode())
    datos += trozo("BODY", bytes(cuerpo))
    with open(ruta, "wb") as f:
        f.write(b"FORM" + struct.pack(">I", len(datos)) + datos)


def leer(ruta):
    """Devuelve un diccionario: ancho, alto, planos, mascara, compresion, paleta, filas, frja, grab."""
    d = open(ruta, "rb").read()
    if d[0:4] != b"FORM" or d[8:12] != b"ILBM":
        raise ValueError("no es un IFF ILBM")
    r = {"frja": None, "grab": None, "paleta": []}
    pos = 12
    cuerpo = None
    while pos + 8 <= len(d):
        tipo = d[pos:pos + 4].decode("latin-1")
        n = struct.unpack(">I", d[pos + 4:pos + 8])[0]
        c = d[pos + 8:pos + 8 + n]
        if tipo == "BMHD":
            (r["ancho"], r["alto"], _, _, r["planos"], r["mascara"], r["compresion"], _, r["transparente"], _, _, _,
             _) = struct.unpack(">HHhhBBBBHBBhh", c[:20])
        elif tipo == "CMAP":
            r["paleta"] = [(c[i] << 16) | (c[i + 1] << 8) | c[i + 2] for i in range(0, n - 2, 3)]
        elif tipo == "GRAB":
            r["grab"] = struct.unpack(">hh", c[:4])
        elif tipo == "FRJA":
            r["frja"] = c.decode("latin-1")
        elif tipo == "BODY":
            cuerpo = c
        pos += 8 + n + (n & 1)
    ancho, alto, planos = r["ancho"], r["alto"], r["planos"]
    fila_bytes = (ancho + 15) // 16 * 2
    filas = []
    p = 0
    for y in range(alto):
        fila = [0] * ancho
        for pl in range(planos + (1 if r["mascara"] == 1 else 0)):
            if r["compresion"] == 1:
                datos, p = des_byterun1(cuerpo, p, fila_bytes)
            else:
                datos = cuerpo[p:p + fila_bytes]
                p += fila_bytes
            if pl < planos:
                for x in range(ancho):
                    if datos[x // 8] & (0x80 >> (x % 8)):
                        fila[x] |= 1 << pl
        filas.append(fila)
    r["filas"] = filas
    return r


def texto(r):
    cifras = 2 if r["planos"] > 4 else 1
    lineas = []
    if r["frja"]:
        lineas.append("FRJA " + r["frja"])
    if r["grab"]:
        lineas.append("GRAB %d %d" % r["grab"])
    lineas.append("%d %d %d" % (r["ancho"], r["alto"], r["planos"]))
    for f in r["filas"]:
        lineas.append("".join("%0*X" % (cifras, c) for c in f))
    lineas.append("paleta " + " ".join("%06X" % c for c in r["paleta"]))
    return "\n".join(lineas) + "\n"


def de_texto(t):
    lineas = [l.strip() for l in t.splitlines() if l.strip() and not l.startswith(("FRJA", "GRAB"))]
    paleta = []
    if lineas[-1].startswith("paleta"):
        paleta = [int(c, 16) for c in lineas.pop().split()[1:]]
    ancho, alto, planos = (int(x) for x in lineas[0].split())
    cifras = 2 if planos > 4 else 1
    filas = [[int(l[i:i + cifras], 16) for i in range(0, ancho * cifras, cifras)] for l in lineas[1:1 + alto]]
    while len(paleta) < (1 << planos):
        g = len(paleta) * 255 // max(1, (1 << planos) - 1)
        paleta.append((g << 16) | (g << 8) | g)
    return ancho, alto, planos, filas, paleta


def prueba():
    import os
    import tempfile
    filas = [[(x * 3 + y) % 16 if (x + y) % 5 else 0 for x in range(37)] for y in range(9)]
    filas[0] = [7] * 37                     # una fila que se repite: ByteRun1 la comprime
    paleta = [i * 0x111111 for i in range(16)]
    with tempfile.TemporaryDirectory() as d:
        for comprimir in (False, True):
            for mascara in (False, True):
                ruta = os.path.join(d, "p.iff")
                escribir(ruta, 37, 9, 4, filas, paleta, comprimir, mascara, "1 0 37 6", (3, 4))
                r = leer(ruta)
                assert r["filas"] == filas, (comprimir, mascara)
                assert r["paleta"] == paleta and r["frja"] == "1 0 37 6" and r["grab"] == (3, 4)
                assert de_texto(texto(r))[3] == filas
    print("iff.py: TODO BIEN")


def main(args):
    if args and args[0] == "prueba":
        prueba()
    elif len(args) >= 3 and args[0] == "escribir":
        ancho, alto, planos, filas, paleta = de_texto(open(args[2]).read())
        frja = args[args.index("--frja") + 1] if "--frja" in args else None
        grab = tuple(int(v) for v in args[args.index("--grab") + 1].split(",")) if "--grab" in args else None
        escribir(args[1], ancho, alto, planos, filas, paleta, "--comprimir" in args, "--mascara" in args, frja, grab)
    elif len(args) == 2 and args[0] == "leer":
        sys.stdout.write(texto(leer(args[1])))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
