"""El guion del vídeo de Forja, en Coffin R65 (Amiberry, RTG a 1280x1024), con la voz clonada. Se lanza con Coffin
recién preparado (preparar.py en|es: el paquete de Dash 2.2.0 y la carpeta juego en Traspaso, el idioma de Locale de
la toma y el agente en marcha).

    python3 guion.py <carpeta de la toma> en|es

Cada locución (locuciones_<lengua>.json, generadas en pegaso con locutar.py) suena mientras se hace lo que cuenta; lo
que tarda más que ella sigue después. Nunca se acelera el vídeo mientras suena una voz (el montaje la pone a su hora
del vídeo): las esperas se aceleran solo cuando la voz ha acabado, y antes de cada capítulo se espera a que acabe.
Los pasos (dónde está cada cosa) están medidos en pasos.py.
"""
import json
import os
import sys
import threading
import time

import agente
import amiga
import menu
import pasos as ps
import piloto as p
from rodaje import Rodaje

CARPETA, L = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(__file__))
VOZ = os.path.expanduser(f"~/.cache/video-forja/voz/voz_{L}")
TEXTO = {lg: json.load(open(os.path.join(AQUI, f"locuciones_{lg}.json"))) for lg in ("en", "es")}
DURA = json.load(open(os.path.join(VOZ, "duraciones.json")))
VERSION = "0.1"

F1, F5, F10 = 0x50, 0x54, 0x59
K_P, K_DERECHA = 0x19, 0x4E

# Los ejemplos, en la lengua de la toma (los de MyFiles:Juego también: preparar.py copia descargas/juego_en)
ES = L == "es"
SALUDA, HOLA_AMIGA, ABIERTA, HASTA = (("Hola desde Forja", "Hola, Amiga!", "La ventana se ha abierto", "Hasta luego")
                                      if ES else
                                      ("Hello from Forja", "Hello, Amiga!", "The window is open", "See you"))
VENTANA_UI, BOTON = ("Saludo", "_Di hola") if ES else ("Greeting", "_Say hi")
HOLA = f'''Window Saludo
    title "{SALUDA}"
    width 360
    height 110
end
'''
HOLA2 = f'''
Main
    Saludo.open
    gfx_pen(1)
    gfx_text_at(40, 50, "{HOLA_AMIGA}")
    Print "{ABIERTA}"
    EventLoop
        On Close
            Stop
        end
    end
end'''
SUMA = '''Main
    total = 0
    i = 1
    while i <= 5
        total = total + i
        i = i + 1
    end
    Print "Total: #{total}"
end'''

r = Rodaje(CARPETA, L, VERSION)
CAPITULOS = ['intro', 'instalar', 'editor', 'errores', 'depurar', 'ventanas', 'sprites', 'mapas', 'juego', 'pantalla', 'cierre']
DESDE = os.environ.get("DESDE", CAPITULOS[0])     # para probar: empezar en un capítulo (con lo de antes ya hecho)


def hacer(clave):
    return CAPITULOS.index(clave) >= CAPITULOS.index(DESDE)


def voz(clave, margen=0.35):
    """Empieza una locución (su subtítulo y su voz); devuelve cuándo acaba."""
    return r.hablar(clave, TEXTO["en"][clave], TEXTO["es"][clave], DURA[clave] + margen)


def esperar(seg, factor=6):
    """Una espera, acelerada en el vídeo (sin voz encima)."""
    r.acelerar(factor)
    time.sleep(seg)
    r.normal()


class deprisa:
    """Lo de dentro va acelerado en el vídeo, pero solo desde que acaba la voz que suena (fin)."""

    def __init__(self, fin=0.0, factor=3):
        self.fin, self.factor = fin, factor

    def __enter__(self):
        self.hilo = threading.Thread(target=self._luego, daemon=True)
        self.parar = False
        self.hilo.start()

    def _luego(self):
        while r.ahora() < self.fin and not self.parar:
            time.sleep(0.05)
        if not self.parar:
            r.acelerar(self.factor)

    def __exit__(self, *a):
        if r.ahora() < self.fin:            # lo de dentro acabó antes que la voz: no hay nada que acelerar
            self.parar = True
        self.hilo.join()
        r.normal()


def zona_forja():
    """Las tres partes de Forja en la pantalla: ficheros, editor y salida (x, y, ancho, alto)."""
    f = ps.forja()
    ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
    sx, sy, fila, _, _ = ps.campos("FORJA_SALIDA")
    ficheros = (f[1] + 4, f[2] + ey, ex - 10, eh)
    editor = (f[1] + ex, f[2] + ey, ew, eh)
    salida = (f[1] + 4, f[2] + sy - 16, f[3] - 8, f[4] - sy + 8)
    return ficheros, editor, salida


def raton_en_forja():
    f = ps.forja()
    p.mover_a(f[1] + 640, f[2] + 420, 0.5)
    time.sleep(0.3)


def linea_salida(texto):
    """El recuadro de la última línea de la salida que lleva ese texto."""
    x, y, fila, primera, _ = ps.campos("FORJA_SALIDA")
    f = ps.forja()
    lineas = ps.salida_lineas()
    for i in range(len(lineas) - 1, -1, -1):
        if texto in lineas[i]:
            return (f[1] + x - 4, f[2] + y + (i - primera) * fila - 2, 760, fila + 4)
    return None


def linea_editor(i):
    f = ps.forja()
    ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
    return (f[1] + ex, ps.linea_y(i) - 6, 560, 12)


def columna_x(c):
    """La x de la columna c del editor (medida: 8 píxeles por letra, la primera a 36 del borde de la zona)."""
    f = ps.forja()
    ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
    return f[1] + ex + 36 + 8 * c + 2


def esperar_estado(estado, tope=30):
    t = time.time()
    while time.time() - t < tope:
        if ps.env("FORJA_ESTADO") == estado:
            return True
        time.sleep(0.4)
    return False


def preparar_carpeta():
    """Sin que se vea: la carpeta de trabajo con el tileset, la ventana de saludo y el juego, y la sonda de Forja."""
    agente.lanzar("C:MakeDir MyFiles:Juego")
    time.sleep(0.5)
    agente.lanzar("C:Copy Traspaso:juego/#? MyFiles:Juego/ QUIET")
    agente.lanzar("C:SetEnv FORJA_SONDA 1")
    time.sleep(2)


if DESDE == CAPITULOS[0]:
    preparar_carpeta()
p.mover_a(640, 600, 0.3)
r.empezar()
try:
    # --- 1. Qué es Forja ---------------------------------------------------------------------------------------------
    if hacer("intro"):
        r.capitulo("intro")
        time.sleep(0.8)
        fin = voz("intro_1"); r.rasgo("coffin")
        p.mover_a(700, 520, 2.0)
        r.hasta(fin)
        fin = voz("intro_2")
        r.hasta(fin)
        fin = voz("intro_3")
        r.hasta(fin)
        time.sleep(0.4)

    # --- 2. Instalarlo -----------------------------------------------------------------------------------------------
    if hacer("instalar"):
        r.capitulo("instalar")
        fin = voz("instalar_1"); r.rasgo("paquete")
        ps.shell(); time.sleep(1.0)
        r.hasta(fin)
        fin = voz("instalar_2")
        ps.escribir(f"lha x Traspaso:{ps.PAQUETE} RAM:")
        r.hasta(fin)
        esperar(8)
        time.sleep(1.0)
        with deprisa():
            p.cerrar("Shell")
            ps.abrir_cajon_dash()
            time.sleep(1.0)
        fin = voz("instalar_3"); r.rasgo("instalador")
        ps.doble(*ps.en("Dash", 32, 32))
        ps.esperar_ventana("Instalar"); time.sleep(1.5)
        ps.instalar_paso("seguir"); time.sleep(1.5)
        ps.instalar_paso("seguir"); time.sleep(1.5)
        ps.instalar_paso("destino"); time.sleep(1.5)
        r.hasta(fin)
        ps.instalar_paso("seguir_destino")
        esperar(4, 4)
        time.sleep(1.5)
        ps.instalar_paso("final"); time.sleep(2.0)
        ps.instalar_paso("final"); time.sleep(1.0)
        ps.esperar_sin("Instalar")
        with deprisa():
            for t in ("Dash", "RAM Disk"):
                while amiga.ventana(t):
                    p.cerrar(t); time.sleep(0.4)
            ps.abrir_cajon_instalado(); time.sleep(1.0)
        fin = voz("instalar_4"); r.rasgo("cajon")
        x, y = ps.en("Dash", 275, 35)
        r.marcar("forja", x - 30, y - 26, 60, 52, 3.2)
        p.mover_a(x, y + 10, 1.0)
        r.hasta(fin)

    # --- 3. El editor ------------------------------------------------------------------------------------------------
    if hacer("editor"):
        r.capitulo("editor")
        if not ps.forja():                                      # (al probar desde aquí puede estar ya abierta)
            ps.doble(*ps.en("Dash", 275, 35))
            ps.esperar_ventana("Forja"); time.sleep(0.8)
            ps.doble(*ps.en("Forja", 32, 35))
            r.acelerar(4)
            t0 = time.time()
            while not ps.forja() and time.time() - t0 < 30:
                time.sleep(0.3)
            time.sleep(2.5)
            r.normal()
        raton_en_forja()
        agente.tecla(ps.K_N, ps.RAMIGA); time.sleep(1.5)          # Forja recién instalada empieza sin fichero
        ficheros, editor, salida = zona_forja()
        fin = voz("editor_1"); r.rasgo("ficheros")
        r.marcar("ficheros", *ficheros, 1.5); time.sleep(1.5)
        r.marcar("editor", *editor, 1.5); time.sleep(1.5)
        r.marcar("salida", *salida, 1.6)
        r.hasta(fin)
        raton_en_forja()
        fin = voz("editor_2"); r.rasgo("sintaxis")
        agente.tecla(ps.K_A, ps.RAMIGA); time.sleep(0.4)
        ps.teclear(HOLA)
        with deprisa(fin, 6):
            ps.teclear(HOLA2)
            time.sleep(0.6)
            ps.guardar_como("MyFiles:Juego/hola.dash")
        time.sleep(1.0)
        fin = voz("editor_3"); r.rasgo("compilar")
        agente.tecla(ps.K_E, ps.RAMIGA)
        ps.esperar_ventana(SALUDA, 20)
        r.hasta(fin)
        fin = voz("editor_4"); r.rasgo("salida")
        v = amiga.ventana(SALUDA)
        r.marcar("ventana", v[2], v[3], v[4], v[5], 2.2); time.sleep(2.2)
        m = linea_salida(ABIERTA)
        if m:
            r.marcar("salida", *m, 2.2)
        r.hasta(fin)
        time.sleep(0.5)
        p.cerrar(SALUDA)
        time.sleep(1.0)

    # --- 4. Los errores ----------------------------------------------------------------------------------------------
    if hacer("errores"):
        r.capitulo("errores")
        f = ps.forja()
        ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
        ps.uno(f[1] + ex + ew - 60, ps.linea_y(9)); time.sleep(0.5)
        agente.tecla(ps.K_RETURN); time.sleep(0.3)
        ps.teclear(f'gfx_txt_at(40, 75, "{HASTA}")')
        time.sleep(0.5)
        agente.tecla(ps.K_S, ps.RAMIGA); time.sleep(1.0)
        agente.tecla(ps.K_E, ps.RAMIGA)
        esperar_estado("libre", 15); time.sleep(1.5)
        fin = voz("errores_1"); r.rasgo("errores")
        m = linea_salida("Error")
        if m:
            r.marcar("error", *m, 3.0)
        r.hasta(fin)
        fin = voz("errores_2"); r.rasgo("clic")
        ps.clic_en_salida("Error"); time.sleep(1.0)
        r.marcar("linea", *linea_editor(10), 2.4)
        time.sleep(1.2)
        ps.uno(columna_x(9), ps.linea_y(10), 0.6); time.sleep(0.4)
        agente.escribir("e"); time.sleep(0.6)
        r.hasta(fin)
        agente.tecla(ps.K_S, ps.RAMIGA); time.sleep(1.0)
        agente.tecla(ps.K_E, ps.RAMIGA)
        ps.esperar_ventana(SALUDA, 20)
        time.sleep(2.5)
        p.cerrar(SALUDA)
        time.sleep(1.0)

    # --- 5. El depurador ---------------------------------------------------------------------------------------------
    if hacer("depurar"):
        r.capitulo("depurar")
        raton_en_forja()
        with deprisa(0, 6):
            agente.tecla(ps.K_N, ps.RAMIGA); time.sleep(1.5)
            agente.tecla(ps.K_A, ps.RAMIGA); time.sleep(0.4)
            ps.teclear(SUMA)
            time.sleep(0.5)
            ps.guardar_como("MyFiles:Juego/suma.dash")
        time.sleep(0.8)
        fin = voz("depurar_1"); r.rasgo("punto")
        time.sleep(1.5)
        ps.uno(ps.margen_x(), ps.linea_y(4)); time.sleep(0.5)
        r.marcar("punto", ps.margen_x() - 10, ps.linea_y(4) - 8, 260, 16, 2.5)
        r.hasta(fin)
        fin = voz("depurar_2")
        agente.tecla(F5)
        esperar_estado("depurando", 15); time.sleep(1.0)
        r.rasgo("pila")
        f = ps.forja()
        ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
        r.acercar(f[1], f[2] + 20, 560, 448, 9.0)
        time.sleep(1.2)
        r.marcar("variables", f[1] + 6, f[2] + ey, ex - 14, 70, 3.0)
        r.hasta(fin)
        fin = voz("depurar_3"); r.rasgo("paso")
        for _ in range(3):
            agente.tecla(F10); time.sleep(1.1)
        ps.uno(ps.margen_x(), ps.linea_y(4), 0.5); time.sleep(0.5)
        agente.tecla(F5)
        r.hasta(fin)
        esperar_estado("libre", 10); time.sleep(0.6)
        m = linea_salida("Total")
        if m:
            r.marcar("total", *m, 2.0)
        time.sleep(2.0)

    # --- 6. Ventanas MUI ---------------------------------------------------------------------------------------------
    if hacer("ventanas"):
        r.capitulo("ventanas")
        fin = voz("ventanas_1"); r.rasgo("dashui")
        raton_en_forja()
        ps.abrir("MyFiles:Juego/saludo.dashui")
        r.hasta(fin)
        fin = voz("ventanas_2"); r.rasgo("propiedades")
        f = ps.forja()
        ps.uno(f[1] + 396, f[2] + 168); time.sleep(1.0)
        d = ps.env("FORJA_DISENO").split()
        if not d or d[0] != "7":
            print("aviso: el árbol no tiene el botón en la fila 7:", d, flush=True)
        agente.tecla(K_DERECHA); time.sleep(0.6)
        agente.tecla(ps.K_RETURN); time.sleep(0.8)
        for _ in range(10):
            agente.tecla(ps.K_RETROCESO); time.sleep(0.1)
        agente.escribir(BOTON); time.sleep(0.6)
        agente.tecla(ps.K_RETURN); time.sleep(1.0)
        r.hasta(fin)
        fin = voz("ventanas_3"); r.rasgo("vista")
        raton_en_forja()
        agente.tecla(K_P, ps.RAMIGA)
        ps.esperar_ventana(VENTANA_UI, 15); time.sleep(1.0)
        v = amiga.ventana(VENTANA_UI)
        r.marcar("vista", v[2], v[3], v[4], v[5], 3.0)
        r.acercar(v[2] + v[4] // 2 - 240, v[3] + v[5] // 2 - 192, 480, 384, 4.5)
        r.hasta(fin)
        time.sleep(1.5)
        ps.uno(v[2] + 9, v[3] + 7); time.sleep(1.0)

    # --- 7. Sprites y BOBs -------------------------------------------------------------------------------------------
    if hacer("sprites"):
        r.capitulo("sprites")
        fin = voz("sprites_1"); r.rasgo("bob")
        ps.nuevo("b"); time.sleep(2.0)
        r.hasta(fin)
        fin = voz("sprites_2"); r.rasgo("herramientas")
        with deprisa(fin, 8):
            ps.muneco()
        time.sleep(0.8)
        with deprisa(0, 8):
            ps.letra("d"); time.sleep(0.8)
            ps.sonrisa()
            ps.antena_torcida()
        time.sleep(0.6)
        fin = voz("sprites_3"); r.rasgo("cebolla")
        time.sleep(2.6)
        ps.letra("o"); time.sleep(0.5)
        x0, y0 = ps.sp_celda(8, 0)
        r.acercar(x0 - 60, y0 - 20, 560, 448, max(3.0, fin - r.ahora() + 0.5))
        r.hasta(fin)
        time.sleep(0.8)
        ps.letra("o")
        with deprisa(0, 3):
            raton_en_forja()
            ps.guardar_como("MyFiles:Juego/muneco.iff")
        time.sleep(0.6)
        fin = voz("sprites_4"); r.rasgo("animar")
        ps.letra(" "); time.sleep(2.6)
        ps.letra(" "); time.sleep(0.4)
        r.rasgo("codigo")
        ps.letra("c"); time.sleep(0.8)
        _, _, salida = zona_forja()
        r.marcar("codigo", *salida, 2.5)
        r.hasta(fin)
        time.sleep(1.5)

    # --- 8. Mapas de tiles -------------------------------------------------------------------------------------------
    if hacer("mapas"):
        r.capitulo("mapas")
        fin = voz("mapas_1"); r.rasgo("tileset")
        ps.nuevo("m")
        ps.pedir_fichero("MyFiles:Juego/tiles.iff")
        r.hasta(fin)
        with deprisa(0, 8):
            ps.mp_boton(5002); time.sleep(0.6)
            ps.mp_boton(4000, veces=42, pausa=0.12)            # ancho: de 64 a 22
            ps.mp_boton(4002, veces=16, pausa=0.12)            # alto: de 32 a 16
            time.sleep(1.0)
        fin = voz("mapas_2")
        with deprisa(fin, 8):
            ps.nivel_fondo()
        time.sleep(0.6)
        fin = voz("mapas_3"); r.rasgo("capas")
        with deprisa(fin, 8):
            ps.nivel_delante()
            r.rasgo("choques")
            ps.nivel_choques()
        time.sleep(0.6)
        fin = voz("mapas_4"); r.rasgo("objetos")
        ps.nivel_objetos()
        r.hasta(fin)
        time.sleep(0.8)
        with deprisa(0, 3):
            raton_en_forja()
            ps.guardar_como("MyFiles:Juego/nivel.fmap")
        time.sleep(0.5)

    # --- 9. Un juego -------------------------------------------------------------------------------------------------
    if hacer("juego"):
        r.capitulo("juego")
        with deprisa(0, 3):
            ps.abrir("MyFiles:Juego/juego.dash")
        time.sleep(0.6)
        fin = voz("juego_1"); r.rasgo("tilemap")
        time.sleep(1.5)
        r.marcar("dibuja", *linea_editor(42), 3.5)        # tilemap_draw (la carga, más abajo, no se ve)
        time.sleep(4.5)
        r.marcar("choques", *linea_editor(18), 3.5)       # tilemap_get: la capa de choques
        r.hasta(fin)
        raton_en_forja()
        agente.tecla(ps.K_E, ps.RAMIGA)
        t0 = time.time()
        while ps.forja() and time.time() - t0 < 20:        # la pantalla del juego tapa la de Forja
            time.sleep(0.3)
        time.sleep(1.0)
        fin = voz("juego_2"); r.rasgo("juego")
        r.acercar(400, 320, 480, 384, 11.0)
        r.hasta(fin)
        time.sleep(9.0)
        p.clic(); time.sleep(2.5)

    # --- 10. Preferencias --------------------------------------------------------------------------------------------
    if hacer("pantalla"):
        r.capitulo("pantalla")
        f = ps.forja()
        menu.elegir(f[1] + 600, f[2] + 300, "Proyecto", "Preferencias...")
        t0 = time.time()
        while not ps.prefs() and time.time() - t0 < 10:
            time.sleep(0.3)
        time.sleep(0.6)
        fin = voz("pantalla_1"); r.rasgo("pantalla")
        v = ps.prefs()
        r.marcar("pantalla", v[1] + 6, v[2] + 80, v[3] - 12, 24, 3.5)
        r.acercar(v[1] + v[3] // 2 - 240, v[2] + v[4] // 2 - 192, 480, 384, max(3.0, fin - r.ahora()))
        r.hasta(fin)
        time.sleep(0.6)
        ps.uno(v[1] + v[3] - 33, v[2] + v[4] - 16); time.sleep(1.0)

    # --- 11. Libre ---------------------------------------------------------------------------------------------------
    if hacer("cierre"):
        r.capitulo("cierre")
        fin = voz("cierre_1"); r.rasgo("libre")
        r.hasta(fin)
        fin = voz("cierre_2")
        r.hasta(fin)
        time.sleep(1.5)
finally:
    r.acabar()
print("toma:", round(r.ahora(), 1), "s")
