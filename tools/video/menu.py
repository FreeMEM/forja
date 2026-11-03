"""Los menús emergentes de Coffin: salen junto al puntero con el botón derecho y se quedan abiertos hasta un clic.
Cada caja es una ventana sin título de Intuition (se leen exactas de la memoria): la de los títulos, a la izquierda,
y la del submenú abierto, a su derecha. Recuerdan el último título usado (lo ponen bajo el puntero), así que todo se
mide al abrirlos. La letra es tan pequeña que no se lee: las entradas van por su sitio."""
import time

import amiga
import piloto as p

# Las entradas de cada menú (src/navegador.dashui), con sus separadores: 12 píxeles por entrada y 6 por separador.
ENTRADAS = {
    "Project": ["New window", "Close window", "New tab", "Close tab", "---", "Go to address", "---", "About...",
                "---", "Quit"],
    "Navigate": ["Back", "Forward", "Reload", "Stop", "---", "Home page", "History"],
    "Bookmarks": ["Show bookmarks", "Add or remove this page", "---", "Use as home page"],
    "Tools": ["Cookies", "Downloads", "Search engine...", "---", "Check for updates",
              "Don't tell me about new versions"],
}
TITULOS = list(ENTRADAS)
_fijas = set()


def _cajas():
    """Las ventanas del menú abierto, de izquierda a derecha: (x, y, ancho, alto)."""
    return sorted(w[1:] for w in amiga.ventanas_sin_titulo() if w[0] not in _fijas)


def abrir(x, y, dur=0.7):
    global _fijas
    _fijas = {w[0] for w in amiga.ventanas_sin_titulo()}
    p.mover_a(x, y, dur)
    p.clic(1, 2)
    t = time.time()
    while not _cajas() and time.time() - t < 3:
        time.sleep(0.1)
    time.sleep(0.3)


def titulo(cual):
    x, y, an, al = _cajas()[0]
    return x + 14, round(y + 10 + 12.7 * TITULOS.index(cual))


def entrada(cual, nombre):
    k = s = 0
    for e in ENTRADAS[cual]:
        if e == nombre:
            break
        if e == "---":
            s += 1
        else:
            k += 1
    x, y, an, al = _cajas()[-1]
    return x + 40, y + 7 + 12 * k + 6 * s


def caja():
    """El rectángulo que cubre todo el menú abierto (para marcarlo o acercarse)."""
    c = _cajas()
    x0 = min(a[0] for a in c); y0 = min(a[1] for a in c)
    x1 = max(a[0] + a[2] for a in c); y1 = max(a[1] + a[3] for a in c)
    return x0, y0, x1 - x0, y1 - y0


def cerrar():
    if _cajas():
        x, y = amiga.puntero()
        p.clic(1, 2)
        time.sleep(0.4)


def ir_a(cual, nombre, pausa=0.5):
    """Con el título ya abierto: a la entrada, primero en horizontal (sin pasar por otro título)."""
    tx, ty = amiga.puntero()
    ex, ey = entrada(cual, nombre)
    p.mover_a(ex, ty, 0.4)
    p.mover_a(ex, ey, 0.5); time.sleep(pausa)


def elegir(x, y, cual, nombre, dur=0.7, pausa=0.5):
    """Abre el menú en (x, y), va al título y pulsa la entrada."""
    abrir(x, y, dur)
    tx, ty = titulo(cual)
    p.mover_a(tx, ty, 0.5); time.sleep(pausa)
    ex, ey = entrada(cual, nombre)
    p.mover_a(ex, ty, 0.4)                 # primero en horizontal, sin pasar por otro título
    p.mover_a(ex, ey, 0.5); time.sleep(pausa)
    p.clic()
