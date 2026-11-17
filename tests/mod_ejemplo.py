#!/usr/bin/env python3
"""Un MOD de ProTracker pequeño para las pruebas de la extensión Demos (hecho aquí, sin bajar nada).

    python3 tests/mod_ejemplo.py salida.mod

Tres instrumentos (un bajo de onda cuadrada, una flauta de seno y un golpe de ruido), cuatro patrones y una canción
de seis posiciones (0 1 2 1 3 2). El patrón 0 empieza con F06 (velocidad 6). Unos 9 KB.
"""
import math
import random
import struct
import sys

PERIODOS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
TABLA = [856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480, 453,
         428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240, 226,
         214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120, 113]


def periodo(nota: str) -> int:
    """"C-2" -> 428"""
    nombre, octava = nota[:-1].rstrip("-"), int(nota[-1])
    return TABLA[(octava - 1) * 12 + PERIODOS[nombre]]


def celda(nota=None, ins=0, efecto=0, param=0) -> bytes:
    p = periodo(nota) if nota else 0
    return bytes([(ins & 0xF0) | (p >> 8), p & 0xFF, ((ins & 0x0F) << 4) | efecto, param])


def patron(n: int) -> bytes:
    bajo = ["C-1", "C-1", "G-1", "A#1"] if n != 3 else ["F-1", "F-1", "C-1", "C-1"]
    melodia = ["C-3", "D#3", "G-3", "A#3", "G-3", "D#3", "F-3", "D-3"]
    filas = []
    for f in range(64):
        c = [celda(), celda(), celda(), celda()]
        if f % 8 == 0:
            c[0] = celda(bajo[(f // 16) % 4], 1)
        if f % 4 == 0 and n > 0:
            c[1] = celda(melodia[(f // 4 + n) % 8], 2)
        if f % 16 == 4 or f % 16 == 12:
            c[2] = celda("C-2", 3)
        if n == 0 and f == 0:
            c[3] = celda(None, 0, 0xF, 6)          # velocidad 6
        if n == 2 and f % 16 == 8:
            c[3] = celda(None, 0, 0xC, 32)         # volumen 32 (para ver un efecto)
        filas.append(b"".join(c))
    return b"".join(filas)


def muestras():
    cuadrada = bytes(([100] * 16 + [156] * 16))                                 # 32 bytes, en bucle
    seno = bytes((int(round(math.sin(i * 2 * math.pi / 32) * 90)) & 0xFF) for i in range(32))
    random.seed(7)
    ruido = bytes((int(random.uniform(-1, 1) * 120 * (1 - i / 2000)) & 0xFF) for i in range(2000))
    return [("bajo", cuadrada, True), ("flauta", seno, True), ("golpe", ruido, False)]


def hacer() -> bytes:
    out = bytearray(b"forja demos".ljust(20, b"\0"))
    datos = muestras()
    for i in range(31):
        if i < len(datos):
            nombre, d, bucle = datos[i]
            out += nombre.encode().ljust(22, b"\0")
            out += struct.pack(">HBBHH", len(d) // 2, 0, 48 if i else 64, 0, len(d) // 2 if bucle else 1)
        else:
            out += bytes(22) + struct.pack(">HBBHH", 0, 0, 0, 0, 1)
    orden = [0, 1, 2, 1, 3, 2]
    out += bytes([len(orden), 127]) + bytes(orden + [0] * (128 - len(orden))) + b"M.K."
    for n in range(4):
        out += patron(n)
    for _, d, _ in datos:
        out += d
    return bytes(out)


if __name__ == "__main__":
    open(sys.argv[1], "wb").write(hacer())
