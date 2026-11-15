"""La toma: ffmpeg graba la ventana de Amiberry en la pantalla virtual (x11grab, 25 cuadros por segundo, sin
pérdida) mientras el guion maneja el Amiga; el guion va marcando subtítulos, capítulos, rasgos, clics, recuadros,
acercamientos y tramos acelerados con la hora de la toma. El montaje (montar.py) hace el vídeo con eso.

La hora del primer cuadro se mide con lo que ffmpeg cuenta (-progress): así la hora de la toma y la del vídeo
grabado cuadran aunque ffmpeg tarde en arrancar."""
import json
import os
import subprocess
import threading
import time

import numpy as np
from PIL import Image

import amiga
import piloto

FPS = 25
PANTALLA = ":80"


def ventana_amiberry():
    """(x, y) de la ventana de Amiberry en la pantalla virtual: lo que no es negro."""
    f = "/tmp/claude-1000/ventana_amiberry.png"
    os.makedirs(os.path.dirname(f), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "x11grab", "-video_size", "2560x1600", "-i", PANTALLA,
                    "-frames:v", "1", f], check=True)
    a = np.asarray(Image.open(f).convert("L"))
    ys, xs = np.where(a > 0)
    os.remove(f)
    return int(xs.min()), int(ys.min())


class Rodaje:
    def __init__(self, carpeta, lengua, version=""):
        self.carpeta = carpeta
        self.version = version
        self.lengua = lengua
        os.makedirs(carpeta, exist_ok=True)
        self.subtitulos = []       # [t0, t1, {"en": ..., "es": ...}]
        self.capitulos = []        # (t, clave)
        self.rasgos = []           # (t, clave): lo que se va viendo, para la lista de la izquierda y el scroller
        self.clics = []            # (t, x, y)
        self.marcas = []           # (t, dur, nombre, x, y, ancho, alto): recuadros que se resaltan
        self.zooms = []            # (t0, t1, x, y, ancho, alto): acercamientos
        self.rapidos = []          # [t0, t1, factor]: tramos que van acelerados (esperas)
        self.voces = []            # (t, clave): cuándo empieza cada locución (voz_<lengua>/<clave>.wav)
        self._t0 = None

    def ahora(self):
        return time.time() - self._t0

    def _progreso(self):
        """Lee el -progress de ffmpeg: con el primer número de cuadros, cuándo fue el primero."""
        for linea in self._ff.stdout:
            if linea.startswith("frame=") and self.video_inicio is None:
                n = int(linea.split("=")[1])
                if n > 0:
                    self.video_inicio = self.ahora() - n / FPS

    def empezar(self):
        s = amiga.pantalla()
        self.pantalla = (amiga.rd(s + 12, 2), amiga.rd(s + 14, 2))
        x, y = ventana_amiberry()
        self.video = os.path.join(self.carpeta, "toma.mkv")
        self.video_inicio = None
        self._t0 = time.time()
        self._ff = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "x11grab", "-framerate", str(FPS), "-video_size",
             f"{self.pantalla[0]}x{self.pantalla[1]}", "-i", f"{PANTALLA}+{x},{y}", "-c:v", "libx264rgb",
             "-preset", "ultrafast", "-qp", "0", "-progress", "pipe:1", self.video],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self._progreso, daemon=True).start()
        rodaje = self
        self._clic_original = piloto.clic

        def clic(veces=1, boton=1):
            if boton == 1:
                x, y = amiga.puntero()
                rodaje.clics.append((rodaje.ahora(), x, y))
            rodaje._clic_original(veces, boton)
        piloto.clic = clic
        while self.video_inicio is None:
            time.sleep(0.05)

    def decir(self, en, es):
        self.callar()
        self.subtitulos.append([self.ahora(), None, {"en": en, "es": es}])

    def hablar(self, clave, en, es, dur):
        """Una locución: su subtítulo y la hora de su voz. Devuelve cuándo acaba (para esperar con hasta())."""
        self.decir(en, es)
        self.voces.append((self.ahora(), clave))
        return self.ahora() + dur

    def hasta(self, t):
        """Espera a la hora t de la toma (lo que queda de una locución)."""
        while self.ahora() < t:
            time.sleep(0.05)

    def callar(self):
        if self.subtitulos and self.subtitulos[-1][1] is None:
            self.subtitulos[-1][1] = self.ahora()

    def capitulo(self, clave):
        self.callar()
        self.capitulos.append((self.ahora(), clave))

    def rasgo(self, clave):
        self.rasgos.append((self.ahora(), clave))

    def marcar(self, nombre, x, y, ancho, alto, dur=3.0):
        """Un recuadro naranja sobre esa zona de la pantalla del Amiga, durante dur segundos."""
        self.marcas.append((self.ahora(), dur, nombre, x, y, ancho, alto))

    def acercar(self, x, y, ancho, alto, dur):
        """Un acercamiento a esa zona de la pantalla del Amiga (mejor en proporción 5:4) durante dur segundos."""
        self.zooms.append((self.ahora(), self.ahora() + dur, x, y, ancho, alto))

    def acelerar(self, factor=6):
        """Desde aquí, el vídeo va factor veces más rápido (una espera); hasta normal(). Los subtítulos siguen: el
        montaje los alarga lo que haga falta para que se lean."""
        self.normal()
        self.rapidos.append([self.ahora(), None, factor])

    def normal(self):
        if self.rapidos and self.rapidos[-1][1] is None:
            self.rapidos[-1][1] = self.ahora()

    def acabar(self):
        self.callar()
        self.normal()
        fin = self.ahora()
        self._ff.stdin.write("q")
        self._ff.stdin.flush()
        self._ff.wait()
        piloto.clic = self._clic_original
        with open(os.path.join(self.carpeta, "toma.json"), "w") as f:
            json.dump({"lengua": self.lengua, "version": self.version, "fin": fin, "pantalla": self.pantalla, "video": "toma.mkv",
                       "video_inicio": self.video_inicio, "subtitulos": self.subtitulos,
                       "capitulos": self.capitulos, "rasgos": self.rasgos, "clics": self.clics,
                       "marcas": self.marcas, "zooms": self.zooms, "rapidos": self.rapidos,
                       "voces": self.voces}, f,
                      ensure_ascii=False, indent=1)
