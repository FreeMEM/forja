"""Las miniaturas de YouTube (1280x720): de fondo, una pantalla entera de la toma (Forja en Coffin), que se funde a la
izquierda con el negro de Forja; ahí, el logo y el lema en Topaz. Una zona de la captura (x0,y0,x1,y1), ampliada en
un recuadro naranja unido a su sitio.

    python3 miniatura.py <captura.png> en|es <salida.jpg> [versión] [x0,y0,x1,y1]"""
import sys

import numpy as np
from PIL import Image, ImageDraw

from montar import BLANCO, FONDO, NARANJA, fuente, logo

LEMA = {"en": ["THE DASH IDE", "ON THE AMIGA ITSELF"], "es": ["EL ENTORNO DE DASH", "EN EL PROPIO AMIGA"]}
PIE = {"en": "Editor, debugger, sprites, maps", "es": "Editor, depurador, sprites, mapas"}


def miniatura(captura, lengua, ver, PANEL):
    W, H = 1280, 720
    cap = Image.open(captura).convert("RGB")
    img = Image.new("RGB", (W, H), FONDO)
    # el escritorio, a lo alto, pegado a la derecha
    esc = H / cap.height
    ew = round(cap.width * esc)
    ex = W - ew
    img.paste(cap.resize((ew, H), Image.LANCZOS), (ex, 0))
    # se funde con el negro hacia la izquierda
    a = np.zeros((H, W), np.uint8)
    x0, x1 = ex + 40, ex + 330
    for x in range(W):
        a[:, x] = 255 if x < x0 else (0 if x > x1 else int(255 * (x1 - x) / (x1 - x0)))
    img = Image.composite(Image.new("RGB", (W, H), FONDO), img, Image.fromarray(a))
    d = ImageDraw.Draw(img, "RGBA")
    # el sitio del panel en el escritorio
    px0, py0 = ex + PANEL[0] * esc, PANEL[1] * esc
    px1, py1 = ex + PANEL[2] * esc - 2, PANEL[3] * esc
    d.rectangle([px0, py0, px1, py1], outline=NARANJA + (255,), width=3)
    # el panel ampliado, con marco y sombra, y unido a su sitio
    k = min(1.5, 430 / (PANEL[3] - PANEL[1]))                          # que quepa debajo del logo
    zoom = cap.crop(PANEL).resize((round((PANEL[2] - PANEL[0]) * k), round((PANEL[3] - PANEL[1]) * k)), Image.LANCZOS)
    zx, zy = 790, 250
    d.line([(px0, py1), (zx, zy)], fill=NARANJA + (200,), width=3)
    d.line([(px1, py1), (zx + zoom.width + 12, zy)], fill=NARANJA + (200,), width=3)
    d.rectangle([zx + 14, zy + 14, zx + zoom.width + 26, zy + zoom.height + 26], fill=(0, 0, 0, 150))
    d.rectangle([zx, zy, zx + zoom.width + 12, zy + zoom.height + 12], fill=NARANJA + (255,))
    img.paste(zoom, (zx + 6, zy + 6))
    d = ImageDraw.Draw(img)
    # el logo, el lema y el pie
    lg = logo(500)
    img.paste(lg, (40, 44), lg)
    y = 44 + lg.height + 44
    for i, l in enumerate(LEMA[lengua]):
        f = fuente(50)
        d.text((44, y + 4), l, font=f, fill=(0, 0, 0))
        d.text((40, y), l, font=f, fill=BLANCO if i == 0 else NARANJA)
        y += 64
    y += 16
    d.rectangle([40, y, 400, y + 8], fill=NARANJA)
    d.text((40, y + 26), PIE[lengua], font=fuente(30), fill=(180, 176, 168))
    # la versión, en una placa
    fv = fuente(44)
    ancho = int(fv.getlength(ver)) + 40
    d.rounded_rectangle([40, H - 110, 40 + ancho, H - 50], 10, fill=NARANJA)
    d.text((60, H - 104), ver, font=fv, fill=FONDO)
    d.text((40 + ancho + 24, H - 95), "AmigaOS 3.x", font=fuente(30), fill=BLANCO)
    return img


if __name__ == "__main__":
    zona = tuple(int(v) for v in sys.argv[5].split(",")) if len(sys.argv) > 5 else (400, 200, 700, 440)
    miniatura(sys.argv[1], sys.argv[2], sys.argv[4] if len(sys.argv) > 4 else "0.1", zona).save(sys.argv[3], quality=92)
