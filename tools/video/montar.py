"""El montaje del vídeo de Trasfondo: de la toma (toma.json y toma.mkv) a un vídeo de 1920x1080 con aire de demo.
(Sale del de Tachyon: mismas columnas, rótulos y scroller, con los colores y el logo de Trasfondo.)

    python3 montar.py <carpeta de la toma> <salida.mp4> [--prueba SEGUNDOS]

- En el centro, la pantalla del Amiga (RTG, 1280x1024) a escala 1:1, con subtítulos, clics, recuadros y acercamientos.
- A la izquierda, el logo, el capítulo y la lista de lo que hace Trasfondo: se mueve sola y marca lo que se está viendo.
- A la derecha, la música que suena (el mod, sus autores y su demo), con su espectro y una bola Boing que bota.
- Abajo, un scroller de los de siempre con lo que se va viendo; al final, los saludos.
- Entre capítulos, rótulos azul Workbench 1.3 en Topaz (como el vídeo de Trasfondo). Al final, los créditos.
- Las esperas de la toma (cargar, arrancar) van aceleradas, con su aviso. La música dura más que el vídeo: se
  apaga al final de los créditos.
"""
import json
import math
import multiprocessing
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from textos import TEXTOS

W, H, FPS = 1920, 1080, 25
V = os.path.expanduser("~/.cache/video-forja")
TOPAZ = os.path.expanduser("~/.cache/video-trasfondo/fuentes/TopazPlus_a1200_v1.0.ttf")
ICONO = os.path.expanduser("~/Projects/webs-freemem/sitios/trasfondo/public/iconos/trasfondo.png")
MUSICA = os.path.join(V, "musica", "overload.wav")

AZUL_WB = (0, 85, 170)
NARANJA = (80, 200, 255)          # el cian de Trasfondo (la gráfica de la CPU del panel): el color de acento
MARCA = (255, 150, 40)            # recuadros y clics sobre la pantalla del Amiga, que es azul: en ámbar, que se vean
BLANCO = (232, 238, 246)
FONDO = (12, 26, 54)              # el azul noche de la web de Trasfondo
AZUL = (19, 38, 74)
TENUE = (10, 48, 72)              # fondo del rasgo de ahora en la lista
GRIS = (120, 128, 150)
PX, PY = 320, 0                   # la pantalla del Amiga en el vídeo
BANDA = 1024                      # la franja del scroller, debajo
PORTADA, RÓTULO, CIERRE_MIN, CIERRE_MAX = 9.0, 2.8, 14.0, 26.0
FACTORES = {8: 6, 6: 4, 4: 3, 3: 2}   # lo acelerado en la toma, tal como va en el vídeo
VEL_SCROLL = 170                  # píxeles por segundo


def fuente(tam):
    return ImageFont.truetype(TOPAZ, tam)


def limpio(t):
    return t.replace("▸", ">").replace("’", "'").replace("—", "-").replace("·", "·")


def envolver(texto, f, ancho):
    palabras, lineas, l = texto.split(), [], ""
    for p in palabras:
        prueba = (l + " " + p).strip()
        if f.getlength(prueba) <= ancho:
            l = prueba
        else:
            lineas.append(l)
            l = p
    if l:
        lineas.append(l)
    return lineas


def bola_boing(d, giro=0.0):
    """La bola Boing: esfera de cuadros rojos y blancos, girada (giro en radianes) como en la demo de 1984."""
    y, x = np.mgrid[0:d, 0:d].astype(float)
    r = d / 2
    nx, ny = (x - r + 0.5) / r, (y - r + 0.5) / r
    dentro = nx * nx + ny * ny <= 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    inc = math.radians(-20)
    rx = nx * math.cos(inc) - ny * math.sin(inc)
    ry = nx * math.sin(inc) + ny * math.cos(inc)
    lon = np.arctan2(rx, nz) + giro
    lat = np.arcsin(np.clip(ry, -1, 1))
    c = (np.floor((lon + math.pi) / (math.pi / 8)) + np.floor((lat + math.pi / 2) / (math.pi / 8))) % 2
    luz = 0.55 + 0.45 * np.clip(-0.4 * nx - 0.5 * ny + 0.75 * nz, 0, None)
    rojo = np.stack([230 * luz, 30 * luz, 30 * luz], -1)
    blanco = np.stack([245 * luz] * 3, -1)
    rgb = np.where(c[..., None] == 1, rojo, blanco)
    a = np.where(dentro, 255, 0)
    return Image.fromarray(np.dstack([rgb, a]).astype("uint8"), "RGBA")


def rotulo(titulo, subtitulo="", numero=""):
    """Un rótulo entre capítulos: azul Workbench 1.3, Topaz, raya naranja."""
    img = Image.new("RGB", (W, H), AZUL_WB)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):
        d.line([(0, y + 3), (W, y + 3)], fill=(0, 76, 153))
    x0, y = 180, 360
    if numero:
        d.text((x0, y - 70), numero, font=fuente(40), fill=(150, 185, 235))
    d.text((x0, y), titulo, font=fuente(96), fill=BLANCO)
    y += 96 + 30
    d.rectangle([x0, y, x0 + 520, y + 10], fill=NARANJA)
    y += 50
    for l in envolver(subtitulo, fuente(44), 1500):
        d.text((x0, y), l, font=fuente(44), fill=(220, 230, 255))
        y += 64
    bola = bola_boing(220, 0.6)
    img.paste(bola, (W - 420, 330), bola)
    return img


def logo(ancho):
    """El logo de Trasfondo: su icono (el del Workbench, en píxeles grandes) y el nombre en Topaz, centrados en
    alto, con fondo transparente."""
    ic = Image.open(ICONO).convert("RGBA")
    k = 3                                                                  # el icono, a 3x en píxeles enteros
    ic = ic.resize((ic.width * k, ic.height * k), Image.NEAREST)
    f = fuente(200)
    texto = "Trasfondo"
    x0, y0, x1, y1 = f.getbbox(texto)
    alto = max(ic.height, y1 - y0)
    im = Image.new("RGBA", (ic.width + 60 + x1 - x0, alto), (0, 0, 0, 0))
    im.paste(ic, (0, (alto - ic.height) // 2), ic)
    ImageDraw.Draw(im).text((ic.width + 60 - x0, (alto - (y1 - y0)) // 2 - y0), texto, font=f, fill=BLANCO + (255,))
    return im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)


# --- La música: su espectro, cuadro a cuadro ------------------------------------------------------------------------
def espectro(wav, n_cuadros, bandas=16):
    """Para cada cuadro del vídeo, la altura (0-1) de cada banda del espectro de la música."""
    import wave
    w = wave.open(wav)
    sr, nch, ancho = w.getframerate(), w.getnchannels(), w.getsampwidth()
    datos = w.readframes(w.getnframes())
    tipo = {2: np.int16, 4: np.int32}[ancho]
    a = np.frombuffer(datos, tipo).astype(np.float32).reshape(-1, nch).mean(1)
    a /= np.abs(a).max() + 1e-9
    n = 2048
    lim = np.geomspace(40, 12000, bandas + 1)
    frec = np.fft.rfftfreq(n, 1 / sr)
    r = np.zeros((n_cuadros, bandas), np.float32)
    ventana = np.hanning(n)
    for i in range(n_cuadros):
        s = int(i / FPS * sr)
        trozo = a[s:s + n]
        if len(trozo) < n:
            break
        m = np.abs(np.fft.rfft(trozo * ventana))
        for b in range(bandas):
            sel = (frec >= lim[b]) & (frec < lim[b + 1])
            r[i, b] = m[sel].mean() if sel.any() else 0
    r = np.log1p(r * 4) / np.log1p(r.max() * 4 + 1e-9) if r.max() else r
    for i in range(1, n_cuadros):                                     # caen despacio, como en un VU
        r[i] = np.maximum(r[i], r[i - 1] * 0.86)
    return r


def duracion_wav(wav):
    import wave
    w = wave.open(wav)
    return w.getnframes() / w.getframerate()


# --- Las columnas ---------------------------------------------------------------------------------------------------
class Montaje:
    def __init__(self, toma, t, n_cuadros, lista, scroller):
        self.toma, self.t, self.lista = toma, t, lista
        self.logo = logo(290)
        self.f22, self.f26, self.f30, self.f32, self.f20 = fuente(22), fuente(26), fuente(30), fuente(32), fuente(20)
        self.espec = espectro(MUSICA, n_cuadros)
        self.bolas = [bola_boing(110, k * 2 * math.pi / 16 / 8) for k in range(16)]
        self.scroller = scroller
        self.lado = self._lado_derecho()

    def _lado_derecho(self):
        t = self.t["musica"]
        img = Image.new("RGB", (320, BANDA), FONDO)
        d = ImageDraw.Draw(img)
        y = 30
        d.text((20, y), t["suena"], font=self.f22, fill=NARANJA); y += 40
        d.text((20, y), t["tema"], font=fuente(36), fill=BLANCO); y += 48
        for l in t["autores"]:
            d.text((20, y), l, font=self.f26, fill=(200, 210, 235)); y += 32
        d.text((20, y), t["grupo"], font=self.f22, fill=GRIS); y += 44
        for l in t["demo"]:
            d.text((20, y), l, font=self.f20, fill=(170, 180, 205)); y += 26
        d.rectangle([20, 924, 300, 925], fill=(50, 56, 75))
        for i, l in enumerate(t["grabado"]):
            d.text((20, 936 + i * 26), l, font=self.f20, fill=GRIS)
        return img

    def fondo(self, capitulo, numero):
        """Lo fijo de un capítulo: columnas, logo, título y la música."""
        img = Image.new("RGB", (W, H), FONDO)
        img.paste(self.logo, (15, 26), self.logo)
        d = ImageDraw.Draw(img)
        d.text((20, 112), numero, font=self.f22, fill=NARANJA)
        y = 142
        for l in envolver(capitulo, self.f30, 285):
            d.text((20, y), l, font=self.f30, fill=BLANCO); y += 36
        d.rectangle([20, 236, 300, 237], fill=(50, 56, 75))
        img.paste(self.lado, (1600, 0))
        return img

    def lista_en(self, d, tv):
        """La lista de rasgos, a la izquierda: hecho (azul, con marca), el de ahora (blanco, con barra naranja) y lo
        que falta (gris). Se desplaza suave para que el de ahora quede a media altura."""
        hechos = [i for i, (tr, _) in enumerate(self.lista) if tr <= tv]
        act = hechos[-1] if hechos else -1
        paso = 34
        # posición suave: va hacia el actual
        objetivo = act
        if act >= 0:
            t_act = self.lista[act][0]
            prev = act - 1
            a = min(1, (tv - t_act) / 0.6)
            objetivo = prev + (act - prev) * (a * a * (3 - 2 * a))
        y0 = 560 - objetivo * paso
        for i, (tr, texto) in enumerate(self.lista):
            y = y0 + i * paso
            if y < 250 or y > 990:
                continue
            if i == act:
                a = min(1, (tv - tr) / 0.4)
                d.rectangle([12, y - 4, 12 + int(296 * a), y + 26], fill=TENUE)
                d.rectangle([12, y - 4, 16, y + 26], fill=NARANJA)
                d.text((26, y), texto, font=self.f22, fill=BLANCO)
            elif i < act:
                d.text((26, y), texto, font=self.f22, fill=(110, 150, 255))
            else:
                d.text((26, y), texto, font=self.f22, fill=(70, 76, 95))
        # que se apaguen arriba y abajo
        return d

    def derecha_viva(self, img, k, tv):
        d = ImageDraw.Draw(img)
        e = self.espec[min(k, len(self.espec) - 1)]
        x0, y0, alto = 1620, 520, 150
        for b, v in enumerate(e):
            h = int(alto * float(v))
            x = x0 + b * 17
            for y in range(y0 - h, y0, 6):                              # a trozos, como un VU de los de antes
                frac = (y0 - y) / alto
                col = (int(80 + 16 * frac), int(200 + 8 * frac), int(255 - 127 * frac)) if frac < 0.8 else MARCA
                d.rectangle([x, y, x + 12, y + 3], fill=col)
        d.rectangle([1620, y0 + 4, 1890, y0 + 5], fill=(50, 56, 75))
        # la bola Boing bota al ritmo (unos 125 pulsos por minuto: un bote cada dos)
        fase = (tv * 125 / 60 / 2) % 1
        yb = 820 - int(200 * (1 - (2 * fase - 1) ** 2))
        xb = 1700 + int(60 * math.sin(tv * 0.9))
        sombra = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
        bola = self.bolas[int(tv * 16) % 16]
        sombra.paste((0, 0, 0, 110), mask=bola.split()[3])
        img.paste(sombra, (xb + 18, yb + 14), sombra)
        img.paste(bola, (xb, yb), bola)

    def banda(self, img, tv):
        """El scroller de abajo, con onda y colores de copper."""
        tira = self.scroller
        off = int(tv * VEL_SCROLL)
        trozo = tira.crop((off, 0, off + W, tira.height))
        d = ImageDraw.Draw(img)
        d.rectangle([0, BANDA, W, H], fill=(6, 14, 30))
        d.line([(0, BANDA), (W, BANDA)], fill=NARANJA, width=2)
        base = BANDA + 8
        for x in range(0, W, 8):
            dy = int(5 * math.sin(x / 140 + tv * 3))
            col = trozo.crop((x, 0, x + 8, trozo.height))
            img.paste(col, (x, base + dy), col)


def tira_scroller(eventos, texto_final, t_total):
    """El scroller entero en una tira: cada texto entra por la derecha cuando toca (eventos: [(t, texto)]), sin
    pisarse; al final, los saludos. Letras con un degradado de copper."""
    f = fuente(36)
    pos, x_fin = [], W
    for (tv, texto) in eventos:
        x = max(int(tv * VEL_SCROLL) + W, x_fin + 120)
        pos.append((x, texto))
        x_fin = x + int(f.getlength(texto))
    x = max(x_fin + 200, int(t_total * VEL_SCROLL) + W - int(f.getlength(texto_final)))
    pos.append((x, texto_final))
    largo = max(x + int(f.getlength(texto_final)) + W, int(t_total * VEL_SCROLL) + 2 * W)
    mascara = Image.new("L", (largo, 40), 0)
    for x, t in pos:                       # cada frase aparte: Pillow no dibuja bien texto más allá de x = 32767
        trozo = Image.new("L", (int(f.getlength(t)) + 8, 40), 0)
        ImageDraw.Draw(trozo).text((0, 0), t, font=f, fill=255)
        mascara.paste(trozo, (x, 0))
    grad = np.zeros((40, 1, 3), np.uint8)
    for y in range(40):                                               # copper: verde, blanco, cian
        s = y / 39
        c = np.array([96, 208, 128]) * (1 - s) * 2 if s < 0.5 else np.array([80, 200, 255]) * (s - 0.5) * 2
        c = c + np.array([255, 255, 255]) * (1 - abs(s - 0.5) * 2) * 0.6
        grad[y, 0] = np.clip(c, 0, 255)
    color = Image.fromarray(np.repeat(grad, largo, 1))
    tira = color.convert("RGBA")
    tira.putalpha(mascara)
    return tira


# --- Componer un cuadro ---------------------------------------------------------------------------------------------
def acercar(cap, t, toma):
    for (t0, t1, x, y, an, al) in toma.get("zooms", []):
        if t0 <= t <= t1:
            a = max(0.0, min(1.0, (t - t0) / 0.8, (t1 - t) / 0.8))
            a = a * a * (3 - 2 * a)
            al = an * 4 / 5                                               # siempre 5:4
            x = max(0, min(1280 - an, x)); y = max(0, min(1024 - al, y))
            caja = (x * a, y * a, 1280 + (x + an - 1280) * a, 1024 + (y + al - 1024) * a)
            return cap.resize((1280, 1024), Image.LANCZOS, box=caja), (a, caja)
    return cap, None


def a_video(x, y, z):
    if z:
        a, (cx0, cy0, cx1, cy1) = z
        x = (x - cx0) * 1280 / (cx1 - cx0); y = (y - cy0) * 1024 / (cy1 - cy0)
    return PX + int(x), PY + int(y)


_m = None


def _iniciar(m):
    global _m
    _m = m


def _cuadro(trabajo):
    tipo = trabajo[0]
    m = _m
    if tipo == "fijo":                     # portada, rótulo o créditos: una imagen hecha, con el scroller
        _, k, tv, datos = trabajo
        img = Image.frombytes("RGB", (W, H), datos)
        m.banda(img, tv)
        return img.tobytes()
    _, k, tv, t, datos, base_k, rapido = trabajo
    toma = m.toma
    img = m.bases[base_k].copy()
    cap = Image.frombytes("RGB", tuple(toma["pantalla"]), datos)
    cap, z = acercar(cap, t, toma)
    img.paste(cap, (PX, PY))
    d = ImageDraw.Draw(img, "RGBA")
    for (tm, dur, _, x, y, an, al) in toma["marcas"]:
        if tm <= t <= tm + dur:
            a = min(1, (t - tm) / 0.3, (tm + dur - t) / 0.3)
            x0, y0 = a_video(x, y, z); x1, y1 = a_video(x + an, y + al, z)
            for q in range(3):
                d.rectangle([x0 - 4 - q, y0 - 4 - q, x1 + 4 + q, y1 + 4 + q], outline=MARCA + (int(230 * a),))
    for (tc, x, y) in toma["clics"]:
        q = (t - tc) * FPS
        if 0 <= q < 8:
            cx, cy = a_video(x, y, z)
            rr = 10 + q * 5
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=MARCA + (int(255 * (1 - q / 8)),), width=5)
    for (a, b, texto) in m.subs:
        if a <= tv < b:
            f = m.f32
            lineas = envolver(texto, f, 1180)[:2]
            alto = 46 * len(lineas) + 24
            y0 = PY + 1024 - alto - 24
            ancho = max(f.getlength(l) for l in lineas) + 48
            d.rounded_rectangle([960 - ancho / 2, y0, 960 + ancho / 2, y0 + alto], 10, fill=(0, 0, 0, 228))
            for i, l in enumerate(lineas):
                d.text((960 - f.getlength(l) / 2, y0 + 14 + i * 46), l, font=f, fill=BLANCO)
    if rapido:
        txt = f">> x{rapido}"
        d.rounded_rectangle([PX + 1280 - 150, 80, PX + 1280 - 20, 130], 8, fill=(0, 0, 0, 190))
        d.text((PX + 1280 - 135, 90), txt, font=m.f30, fill=NARANJA)
    m.lista_en(ImageDraw.Draw(img), tv)
    m.derecha_viva(img, k, tv)
    m.banda(img, tv)
    return img.tobytes()


def cuadros_toma(toma, carpeta):
    """Los cuadros de toma.mkv, en orden: (número, bytes)."""
    w, h = toma["pantalla"]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-i", os.path.join(carpeta, toma["video"]), "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = 0
    while True:
        datos = ff.stdout.read(w * h * 3)
        if len(datos) < w * h * 3:
            break
        yield n, datos
        n += 1


def srt_tiempo(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    args = sys.argv[1:]
    prueba = None
    if "--prueba" in args:
        i = args.index("--prueba"); prueba = float(args[i + 1]); del args[i:i + 2]
    carpeta, salida = args
    toma = json.load(open(os.path.join(carpeta, "toma.json")))
    lengua = toma["lengua"]
    T = con_version(TEXTOS[lengua], toma.get("version", ""))

    # El guion del vídeo: portada, por capítulo su rótulo y su trozo de toma (con las esperas aceleradas), créditos
    caps = toma["capitulos"]
    trozos = []
    for i, (t0, clave) in enumerate(caps):
        t1 = caps[i + 1][0] if i + 1 < len(caps) else toma["fin"]
        trozos.append((clave, t0, t1))

    def factor(t):
        for (a, b, f) in toma["rapidos"]:
            if a <= t < (b if b is not None else toma["fin"]):
                return FACTORES.get(f, f)
        return 0

    # horas de la toma de cada cuadro de cada trozo
    plan, tv = [], PORTADA
    marcas_t = []                        # (hora de la toma, hora del vídeo): para situar rasgos y subtítulos
    for n, (clave, t0, t1) in enumerate(trozos):
        plan.append(("rotulo", clave, n, tv)); tv += RÓTULO
        horas, t = [], t0
        while t < t1:
            horas.append(t)
            marcas_t.append((t, tv + len(horas) / FPS))
            t += (factor(t) or 1) / FPS
        plan.append(("toma", clave, n, tv, horas)); tv += len(horas) / FPS
    t_musica = duracion_wav(MUSICA)
    cierre = min(max(CIERRE_MIN, t_musica - tv), CIERRE_MAX)
    t_total = tv + cierre

    def a_video_t(t):
        for (a, b) in marcas_t:
            if a >= t:
                return b
        return marcas_t[-1][1]

    lista = [(a_video_t(t), T["rasgos"][c]) for (t, c) in toma["rasgos"] if c in T["rasgos"]]
    # los subtítulos, en horas del vídeo: como poco 2,4 s (si un tramo acelerado los acorta), sin pisar al siguiente
    subs = []
    for i, (t0, t1, textos) in enumerate(toma["subtitulos"]):
        a = a_video_t(t0)
        b = a_video_t(t1 if t1 is not None else toma["fin"])
        sig = a_video_t(toma["subtitulos"][i + 1][0]) if i + 1 < len(toma["subtitulos"]) else 1e9
        b = min(max(b, a + 2.4 + len(textos[lengua]) * 0.035), sig)
        subs.append((a, b, limpio(textos[lengua]), {lg: limpio(textos[lg]) for lg in ("en", "es")}))
    eventos = [(PORTADA - 4, T["scroll_portada"])]
    for (t, c) in toma["rasgos"]:
        if c in T["scroll"]:
            eventos.append((a_video_t(t), T["scroll"][c]))
    scroller = tira_scroller(eventos, T["saludos"], t_total)

    n_total = int(t_total * FPS)
    m = Montaje(toma, T, n_total + FPS, lista, scroller)
    m.lengua = lengua
    m.subs = [(a, b, t) for (a, b, t, _) in subs]
    m.bases = {n: m.fondo(T["capitulos"][clave][0], f"{n + 1:02d} / {len(trozos):02d}")
               for n, (clave, _, _) in enumerate(trozos)}
    print(f"vídeo: {t_total:.1f} s (música {t_musica:.1f} s, créditos {cierre:.1f} s)", flush=True)
    if prueba:
        t_total = min(t_total, prueba)
        n_total = int(t_total * FPS)

    crudo = salida + ".crudo.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", crudo], stdin=subprocess.PIPE)
    pool = multiprocessing.Pool(int(os.environ.get("PROCESOS", max(4, os.cpu_count() - 4))), initializer=_iniciar, initargs=(m,))

    def trabajos():
        k = 0
        fuente_toma = cuadros_toma(toma, carpeta)
        actual = (-1, None)
        fondo_portada = imagen_portada(T, solo_fondo=True)
        while k < PORTADA * FPS and k < n_total:
            yield ("fijo", k, k / FPS, cuadro_portada(T, fondo_portada, k / FPS)); k += 1
        for paso in plan:
            if k >= n_total:
                return
            if paso[0] == "rotulo":
                _, clave, n, tv0 = paso
                img = rotulo(T["capitulos"][clave][0], T["capitulos"][clave][1], f"{n + 1:02d} / {len(trozos):02d}")
                datos = img.tobytes()
                for _ in range(int(RÓTULO * FPS)):
                    if k >= n_total:
                        return
                    yield ("fijo", k, k / FPS, datos); k += 1
                continue
            _, clave, n, tv0, horas = paso
            for t in horas:
                if k >= n_total:
                    return
                idx = max(0, int(round((t - toma["video_inicio"]) * FPS)))
                while actual[0] < idx:
                    try:
                        actual = next(fuente_toma)
                    except StopIteration:
                        break
                yield ("toma", k, k / FPS, t, actual[1], n, factor(t))
                k += 1
        creditos = imagenes_creditos(T, n_total - k)
        for img in creditos:
            yield ("fijo", k, k / FPS, img); k += 1

    for datos in pool.imap(_cuadro, trabajos(), chunksize=8):
        ff.stdin.write(datos)
    ff.stdin.close()
    ff.wait()
    pool.close()

    # Subtítulos en los dos idiomas (para YouTube) y capítulos
    for lg in ("en", "es"):
        with open(f"{salida}.{lg}.srt", "w") as f:
            for i, (a, b, _, textos) in enumerate(subs, 1):
                f.write(f"{i}\n{srt_tiempo(a)} --> {srt_tiempo(b)}\n{textos[lg]}\n\n")
    capitulos = [(0.0, T["portada_capitulo"])] + [(p[3], T["capitulos"][p[1]][0]) for p in plan if p[0] == "rotulo"]
    capitulos.append((t_total - cierre, T["creditos_capitulo"]))
    with open(salida + ".capitulos.txt", "w") as f:
        for (a, nombre) in capitulos:
            f.write(f"{int(a) // 60}:{int(a) % 60:02d} {nombre}\n")
    with open(salida + ".ffmeta", "w") as f:
        f.write(";FFMETADATA1\ntitle=" + T["titulo"] + "\n")
        for i, (a, nombre) in enumerate(capitulos):
            b = capitulos[i + 1][0] if i + 1 < len(capitulos) else t_total
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(b * 1000)}\ntitle={nombre}\n")
    fin = n_total / FPS
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", crudo, "-i", MUSICA, "-i", salida + ".ffmeta",
                    "-map", "0:v", "-map", "1:a", "-map_metadata", "2", "-map_chapters", "2",
                    "-af", f"afade=t=in:d=0.5,afade=t=out:st={max(0, fin - 3):.2f}:d=3", "-t", f"{fin:.2f}",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", salida], check=True)
    os.remove(crudo)
    print(salida, f"{fin:.1f} s")


def con_version(o, ver):
    """Los textos con {ver} cambiado por la versión de la toma."""
    if isinstance(o, str):
        return o.replace("{ver}", ver)
    if isinstance(o, dict):
        return {k: con_version(v, ver) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return type(o)(con_version(v, ver) for v in o)
    return o


def cuadro_portada(T, fondo, t):
    """La portada animada: el logo entra desde la izquierda, la raya crece, los textos aparecen uno a uno y la bola
    Boing bota a la derecha."""
    img = fondo.copy()
    d = ImageDraw.Draw(img)
    suave = lambda a: max(0.0, min(1.0, a)) ** 0.5
    lg = logo(1000)
    a = suave((t - 0.2) / 1.2)
    img.paste(lg, (int(180 - 700 * (1 - a)), 300), lg)
    y = 300 + lg.height + 50
    d.rectangle([200, y, 200 + int(520 * suave((t - 1.2) / 0.8)), y + 10], fill=NARANJA)
    y += 50
    lineas = [(T["portada"][0], 44, BLANCO)] + [(l, 34, (170, 180, 210)) for l in T["portada"][1:]]
    for i, (texto, tam, col) in enumerate(lineas):
        a = max(0.0, min(1.0, (t - 2.0 - i * 0.7) / 0.5))
        if a > 0:
            f = fuente(tam)
            visible = texto[:int(len(texto) * a)]                      # como si se tecleara
            d.text((200, y), visible, font=f, fill=col)
        y += 76 if i == 0 else 50
    fase = (t * 0.9) % 1
    yb = 640 - int(330 * (1 - (2 * fase - 1) ** 2))
    bola = bola_boing(300, t * 2.2)
    alto = (640 - yb) / 330                                           # 0 en el suelo, 1 arriba del todo
    sw = int(260 * (1 - 0.45 * alto))
    ds = ImageDraw.Draw(img, "RGBA")
    ds.ellipse([W - 370 - sw // 2, 952, W - 370 + sw // 2, 984], fill=(0, 0, 0, int(140 - 70 * alto)))
    img.paste(bola, (W - 520, yb), bola)
    return img.tobytes()


def imagen_portada(T, solo_fondo=False):
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    for y in range(0, BANDA, 4):
        d.line([(0, y + 3), (W, y + 3)], fill=(15, 31, 62))
    if solo_fondo:
        return img
    lg = logo(1000)
    img.paste(lg, (180, 300), lg)
    y = 300 + lg.height + 50
    d.rectangle([200, y, 720, y + 10], fill=NARANJA)
    y += 50
    d.text((200, y), T["portada"][0], font=fuente(44), fill=BLANCO); y += 76
    for l in T["portada"][1:]:
        d.text((200, y), l, font=fuente(34), fill=(170, 180, 210)); y += 50
    bola = bola_boing(300, 0.3)
    img.paste(bola, (W - 520, 320), bola)
    return img


def imagenes_creditos(T, n):
    """Los créditos suben despacio sobre el fondo, con el logo arriba; n cuadros."""
    lineas = T["creditos"]
    alto_l = 52
    fijo = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(fijo)
    for y in range(0, BANDA, 4):
        d.line([(0, y + 3), (W, y + 3)], fill=(15, 31, 62))
    lg = logo(560)
    fijo.paste(lg, ((W - lg.width) // 2, 40), lg)
    tira = Image.new("RGB", (W, len(lineas) * alto_l + BANDA), FONDO)
    dt = ImageDraw.Draw(tira)
    for i, (estilo, texto) in enumerate(lineas):
        f = fuente(44 if estilo == "t" else 34)
        col = {"t": NARANJA, "n": BLANCO, "s": (160, 170, 200)}[estilo]
        dt.text(((W - f.getlength(texto)) / 2, BANDA * 0.6 + i * alto_l), texto, font=f, fill=col)
    zona = (0, 200, W, BANDA - 10)
    recorrido = tira.height - (zona[3] - zona[1]) - int(BANDA * 0.25)
    for k in range(n):
        a = k / max(1, n - 1)
        off = int(recorrido * min(1, a * 1.08))
        img = fijo.copy()
        trozo = tira.crop((0, off, W, off + zona[3] - zona[1]))
        img.paste(trozo, (0, zona[1]))
        yield img.tobytes()


if __name__ == "__main__":
    main()
