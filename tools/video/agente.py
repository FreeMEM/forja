"""Órdenes al agente que corre dentro del Amiga (ver ../agente/agente.c), por su buzón en memoria."""
import time

import amiga
from amiberry import orden

TECLA, LANZAR, ESCRIBIR, ABAJO, ARRIBA, SALIR = 1, 2, 3, 4, 5, 9


MAGIA, PEDIDA, HECHA, ORDEN, A, B, TEXTO = 36, 40, 44, 48, 52, 56, 60


_buzon = None


def buzon():
    """El puerto público "agente" (ExecBase->PortList): su dirección es la del buzón. Se busca una vez (recorrer la
    lista cuesta cientos de lecturas por el socket) y se comprueba su marca antes de usarlo."""
    global _buzon
    if _buzon and amiga.rd(_buzon + MAGIA) == 0x50494C4F:
        return _buzon
    n = amiga.rd(amiga.rd(4) + 392)
    for _ in range(500):
        if not amiga.rd(n):
            break
        if amiga.cadena(amiga.rd(n + 10)) == "agente" and amiga.rd(n + MAGIA) == 0x50494C4F:
            _buzon = n
            return n
        n = amiga.rd(n)
    raise RuntimeError("el agente no está en marcha")


def _wr(addr, w, v):
    r = orden("WRITE_MEM", addr, w, v)
    assert r.startswith("OK"), r


def pedir(cual, a=0, b=0, texto="", tope=30):
    bz = buzon()
    datos = texto.encode("latin-1") + b"\0"
    datos += b"\0" * (-len(datos) % 4)
    for i in range(0, len(datos), 4):
        _wr(bz + TEXTO + i, 4, int.from_bytes(datos[i:i + 4], "big"))
    _wr(bz + ORDEN, 4, cual)
    _wr(bz + A, 4, a & 0xFFFFFFFF)
    _wr(bz + B, 4, b & 0xFFFFFFFF)
    n = (amiga.rd(bz + PEDIDA) + 1) & 0xFFFFFFFF
    _wr(bz + PEDIDA, 4, n)
    t = time.time()
    while amiga.rd(bz + HECHA) != n:
        if time.time() - t > tope:
            raise RuntimeError("el agente no contesta")
        time.sleep(0.05)


def lanzar(orden_shell):
    pedir(LANZAR, texto=orden_shell)


def escribir(texto):
    pedir(ESCRIBIR, texto=texto)


def tecla(codigo, calificador=0):
    pedir(TECLA, codigo, calificador)


MODIFICADORES = ((0x01, 0x60), (0x08, 0x63), (0x10, 0x64), (0x40, 0x66), (0x80, 0x67))   # calificador -> tecla cruda


def combo(codigo, calificador):
    """Una tecla con Mayúsculas, Ctrl, Alt o Amiga de verdad: primero se pulsan esas teclas, y se mantienen."""
    mods = [(q, r) for (q, r) in MODIFICADORES if calificador & q]
    for q, r in mods:
        pedir(ABAJO, r, calificador)
    tecla(codigo, calificador)
    for q, r in reversed(mods):
        pedir(ARRIBA, r, 0)
