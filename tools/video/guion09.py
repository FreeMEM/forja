"""El guion del vídeo de Forja con todo (editor, ayuda, errores, depurador, git, copiloto, sprites y mapas, demos, 3D,
el diseñador de ventanas y extensiones), en Coffin R65 (Amiberry, RTG a 1280x1024) con la voz clonada. Se lanza con Coffin recién preparado
(preparar.py en|es) y el servidor de Inferencia de pruebas en marcha (servidor_inferencia.py).

    VIDEO_PAQUETE=dash-2.20.0-amiga.lha DESDE=capitulo python3 guion09.py <carpeta de la toma> en|es

Es el de la 0.8 (guion08.py) con el capítulo "ventanas" (el diseñador de ventanas, que pidió Jose) y sin copiar la
Inferencia aparte (el paquete ya la trae al día).

Cada locución (locuciones09_<lengua>.json, voz en ~/.cache/video-forja/voz/voz09_<lengua>) suena mientras se hace lo
que cuenta; lo que tarda más que ella sigue después. Nunca se acelera el vídeo mientras suena una voz.
Teclas: Amiga-X es la tecla Amiga derecha; Ctrl, Alt y Mayúsculas se mantienen de verdad (agente.combo).
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
VOZ = os.path.expanduser(f"~/.cache/video-forja/voz/voz09_{L}")
TEXTO = {lg: json.load(open(os.path.join(AQUI, f"locuciones09_{lg}.json"))) for lg in ("en", "es")}
DURA = json.load(open(os.path.join(VOZ, "duraciones.json")))
VERSION = os.environ.get("VIDEO_VERSION", "0.9")       # (provisional: el número lo decide el usuario)
ES = L == "es"
T_NUEVO = "Nuevo proyecto (Forja)" if ES else "New project (Forja)"
T_AYUDA = "Ayuda de Dash (Forja)" if ES else "Dash help (Forja)"
T_BUSCAR = "Buscar y cambiar (Forja)" if ES else "Find and replace (Forja)"
ps.PREF_MAPAS = "Mapas" if ES else "Maps"


def tt(es, en):
    """Un texto de la salida de Forja en la lengua de la toma."""
    return es if ES else en


S_VECES = tt("veces en", "times in")
S_PESTANA = tt("está en la pestaña", "is in the tab")
S_ACABO = tt("acabó con código", "ended with code")
S_COMPILADO = tt("Compilado en", "Compiled in")
S_CAMBIAR = tt("Cambiar:", "Change:")
S_BIEN = tt("2 bien", "2 passed")

CTRL, MAYUS, ALT, AM, LAM = 0x08, 0x01, 0x10, 0x80, 0x40
PROY = "MyFiles:Proyectos"
NAVE = PROY + "/Nave/main.dash"

r = Rodaje(CARPETA, L, VERSION)
CAPITULOS = ["intro", "instalar", "proyecto", "editor", "ayuda", "errores", "depurar", "git", "inferencia",
             "sprites", "demos", "tresd", "ventanas", "cierre"]
DESDE = os.environ.get("DESDE", CAPITULOS[0])


HASTA = os.environ.get("HASTA", CAPITULOS[-1])      # para probar: acabar en un capítulo


def hacer(clave):
    return CAPITULOS.index(DESDE) <= CAPITULOS.index(clave) <= CAPITULOS.index(HASTA)


def voz(clave, margen=0.35):
    return r.hablar(clave, TEXTO["en"][clave], TEXTO["es"][clave], DURA[clave] + margen)


def esperar(seg, factor=6):
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
        if r.ahora() < self.fin:
            self.parar = True
        self.hilo.join()
        r.normal()


# --- Teclas y órdenes ---------------------------------------------------------------------------------------------

K = {"up": 0x4C, "down": 0x4D, "right": 0x4E, "left": 0x4F, "tab": 0x42, "esc": 0x45, "del": 0x46, "bs": 0x41,
     "ret": 0x44, "space": 0x40, "f1": 0x50, "f2": 0x51, "f3": 0x52, "f4": 0x53, "f5": 0x54, "f6": 0x55, "f7": 0x56,
     "f8": 0x57, "f9": 0x58, "f10": 0x59}


def raw(c):
    if c in K:
        return K[c]
    for fila, base in (("1234567890", 0x01), ("qwertyuiop", 0x10), ("asdfghjkl", 0x20), ("zxcvbnm", 0x31)):
        if c in fila:
            return base + fila.index(c)
    raise ValueError(c)


def k(c, cal=0, pausa=0.3):
    """Una tecla con sus calificadores de verdad (Ctrl, Alt y Mayúsculas se mantienen; Amiga es la derecha)."""
    if cal:
        agente.combo(raw(c), cal)
    else:
        agente.tecla(raw(c), 0)
    time.sleep(pausa)


def teclas_n(c, n, cal=0, pausa=0.12):
    for _ in range(n):
        k(c, cal, pausa)


def escribir(texto, ritmo=0.05, trozo=3):
    """Texto en el editor como una persona, a trozos (el editor cierra pares y pone el end solo)."""
    for j in range(0, len(texto), trozo):
        agente.escribir(texto[j:j + trozo])
        time.sleep(ritmo)


def rx(cmd, puerto="FORJA.1", pausa=1.3):
    """Una orden ARexx a Forja (o a una extensión), sin esperar su respuesta."""
    agente.lanzar(f'SYS:Rexxc/RX "ADDRESS {puerto}; {cmd}"')
    time.sleep(pausa)


def abrir_en(ruta, linea, pausa=1.3):
    rx(f"ABRIR '{ruta}' {linea}", pausa=pausa)


def texto_de(ruta):
    """El texto del fichero abierto en Forja (ARexx TEXTO), para saber en qué línea está cada cosa."""
    f = os.path.expanduser("~/.cache/video-forja/traspaso/texto.txt")
    if os.path.exists(f):
        os.remove(f)
    agente.lanzar(f"""SYS:Rexxc/RX "OPTIONS RESULTS; ADDRESS FORJA.1; TEXTO '{ruta}'; SAY RESULT" >Traspaso:texto.txt""")
    t = time.time()
    while time.time() - t < 8 and not os.path.exists(f):
        time.sleep(0.2)
    time.sleep(1.0)
    return open(f, encoding="latin-1").read().split("\n")


def linea_con(ruta, texto, desde=0):
    """El número de línea (desde 1) de la primera línea del fichero que lleva ese texto."""
    for i, l in enumerate(texto_de(ruta)):
        if i >= desde and texto in l:
            return i + 1
    raise RuntimeError("no hay " + texto)


def zona_forja():
    f = ps.forja()
    ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
    sx, sy, fila, _, _ = ps.campos("FORJA_SALIDA")
    ficheros = (f[1] + 4, f[2] + ey, ex - 10, eh)
    editor = (f[1] + ex, f[2] + ey, ew, eh)
    salida = (f[1] + 4, f[2] + sy - 16, f[3] - 8, f[4] - sy + 8)
    return ficheros, editor, salida


def raton_en_forja(x=640, y=420):
    f = ps.forja()
    p.mover_a(f[1] + x, f[2] + y, 0.5)
    time.sleep(0.3)


def linea_salida(texto):
    x, y, fila, primera, _ = ps.campos("FORJA_SALIDA")
    f = ps.forja()
    lineas = ps.salida_lineas()
    for i in range(len(lineas) - 1, -1, -1):
        if texto in lineas[i]:
            return (f[1] + x - 4, f[2] + y + (i - primera) * fila - 2, 760, fila + 4)
    return None


def esperar_estado(estado, tope=30):
    t = time.time()
    while time.time() - t < tope:
        if ps.env("FORJA_ESTADO") == estado:
            return True
        time.sleep(0.4)
    return False


def esperar_salida(texto, tope=30):
    t = time.time()
    while time.time() - t < tope:
        if any(texto in l for l in ps.salida_lineas()[-12:]):
            return True
        time.sleep(0.5)
    return False


def guardar():
    agente.tecla(raw("s"), AM)
    time.sleep(1.5)


def aceptar_cambio():
    """La vista de diferencias de Inferencia: la tecla a la aplica."""
    agente.escribir("a")
    time.sleep(1.2)


def proyecto_abierto():
    f = ps.forja()
    return f is not None


def preparar_carpeta():
    """Sin que se vea: carpetas de trabajo, los ficheros de la toma, la sonda de Forja y la configuración del copiloto."""
    for c in (f"C:MakeDir {PROY} MyFiles:Juego",
              "C:Copy Traspaso:juego/#? MyFiles:Juego/ QUIET",
              "C:Copy Traspaso:ficheros/suma.dash Traspaso:ficheros/musica.mod MyFiles:Juego/ QUIET",
              "C:SetEnv FORJA_SONDA 1",
              "C:MakeDir >NIL: ENV:Inferencia",
              "C:SetEnv Forja/inferencia DASH:Inferencia/Inferencia",
              "C:SetEnv Inferencia/url http://127.0.0.1:40977/api/v1/chat/completions",
              "C:SetEnv Inferencia/clave clave-falsa",
              "C:SetEnv Inferencia/modelo modelo/video",
              "C:SetEnv Inferencia/ayuda DASH:Ayuda/Dash.ayuda"):
        agente.lanzar(c)
        time.sleep(0.5)
    time.sleep(1.5)


def a_forja():
    """Forja delante y con el teclado: un clic en su panel de ficheros (sin tocar nada)."""
    f = ps.forja()
    ps.uno(f[1] + 25, f[2] + 600, 0.5)               # la franja del panel de ficheros: las ventanas de las extensiones no la tapan
    time.sleep(0.4)


def parar_programa(parte):
    """Acaba un programa de Forja con Ctrl-C (Break), por su número de proceso (Status): Esc le llega a Forja también y la
    deja colgada. parte: un trozo de su nombre."""
    f = os.path.expanduser("~/.cache/video-forja/traspaso/st.txt")
    if os.path.exists(f):
        os.remove(f)
    agente.lanzar("C:Status >Traspaso:st.txt")
    time.sleep(2.0)
    for l in open(f, encoding="latin-1").read().split("\n"):
        if parte in l and l.startswith("Process"):
            num = l.split(":")[0].split()[1]
            agente.lanzar(f"C:Break {num} C")
            time.sleep(2.0)
            return True
    return False


def ir_a_columna(col):
    """Lleva el cursor a esa columna de su línea (desde 0) con las flechas (la sonda dice dónde está)."""
    _, c = ps.cursor()
    while c != col:
        teclas_n("right" if c < col else "left", abs(col - c), 0, 0.08)
        _, c = ps.cursor()


def forja_delante():
    """La pantalla de Forja delante (si el programa de antes dejó delante la del Workbench: el botón de profundidad)."""
    for _ in range(3):
        s = amiga.pantalla()
        if amiga.cadena(amiga.rd(s + 26)) == "FORJA":
            return
        p.mover_a(1267, 10, 0.5)
        p.clic()
        time.sleep(1.5)


def cerrar_extensiones():
    """Las ventanas de las extensiones (Sprites, Mapas, Demos...) tapan la de Forja y no se dejan cerrar con cambios
    sin guardar: se deja Forja delante con un clic en su franja de la izquierda, que ellas no tapan."""
    forja_delante()
    a_forja()


def lienzo(nombre, tope=10):
    """Dónde se ve algo del diseñador de ventanas (un tipo de la paleta, "vista", un objeto con nombre, "titulo" o
    "props"), en la pantalla: (x, y, ancho, alto), por la sonda de Forja (ENV:FORJA_LIENZO); None si no está."""
    t0 = time.time()
    while time.time() - t0 < tope:
        for trozo in (ps.env("FORJA_LIENZO") or "").split():
            if ":" in trozo and trozo.split(":")[0] == nombre:
                x, y, w, h = (int(n) for n in trozo.split(":", 1)[1].split(","))
                f = ps.forja()
                return (f[1] + x, f[2] + y, w, h)
        time.sleep(0.4)
    return None


def cerrar_ventanas(*titulos):
    for t in titulos:
        v = amiga.ventana(t)
        if v:
            p.cerrar(t)


if DESDE == CAPITULOS[0]:
    preparar_carpeta()
p.mover_a(640, 600, 0.3)
r.empezar()
try:
    # --- 1. Qué es ---------------------------------------------------------------------------------------------------
    if hacer("intro"):
        try:
            r.capitulo("intro")
            time.sleep(0.8)
            fin = voz("intro_1"); r.rasgo("coffin")
            p.mover_a(700, 520, 2.0)
            r.hasta(fin)
            fin = voz("intro_2")
            r.hasta(fin)
            time.sleep(0.4)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 2. Instalarlo -----------------------------------------------------------------------------------------------
    if hacer("instalar"):
        try:
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
            r.rasgo("instalador")
            ps.doble(*ps.en("Dash", 32, 32))
            ps.esperar_ventana("Instalar"); time.sleep(1.5)
            ps.instalar_paso("seguir"); time.sleep(1.5)
            ps.instalar_paso("seguir"); time.sleep(1.5)
            ps.instalar_paso("destino"); time.sleep(1.5)
            ps.instalar_paso("seguir_destino")
            time.sleep(1.5)
            ps.instalar_paso("seguir")                      # "¿Lo pongo al día ahí?": Sí
            esperar(5, 4)
            time.sleep(1.5)
            ps.instalar_paso("final"); time.sleep(2.0)
            ps.instalar_paso("final"); time.sleep(1.0)
            ps.esperar_sin("Instalar")
            with deprisa():
                for t in ("Dash", "RAM Disk"):
                    while amiga.ventana(t):
                        p.cerrar(t); time.sleep(0.4)
                ps.abrir_cajon_instalado(); time.sleep(1.0)
            fin = voz("instalar_3"); r.rasgo("cajon")
            x, y = ps.en("Dash", 275, 35)
            r.marcar("forja", x - 30, y - 26, 60, 52, 3.2)
            p.mover_a(x, y + 10, 1.0)
            r.hasta(fin)
            ps.doble(x, y)
            ps.esperar_ventana("Forja"); time.sleep(0.8)
            ps.doble(*ps.en("Forja", 32, 35))
            r.acelerar(4)
            t0 = time.time()
            while not ps.forja() and time.time() - t0 < 40:
                time.sleep(0.3)
            time.sleep(3.0)
            r.normal()
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 3. Proyecto desde una plantilla -----------------------------------------------------------------------------
    if hacer("proyecto"):
        try:
            r.capitulo("proyecto")
            raton_en_forja()
            fin = voz("proyecto_1"); r.rasgo("plantilla")
            menu.abrir(640, 420)
            tx, ty = menu.titulo("Proyecto")
            p.mover_a(tx, ty, 0.5); time.sleep(0.4)
            ex, ey = menu.entrada("Proyecto", "Nuevo proyecto...")
            p.mover_a(ex, ty, 0.4)
            p.mover_a(ex, ey, 0.5)
            r.hasta(fin)
            p.clic()                                                    # Nuevo proyecto...: se abre su ventana
            v = ps.esperar_ventana(T_NUEVO, 10); time.sleep(1.0)
            r.marcar("dialogo", v[2] - 4, v[3] - 4, v[4] + 8, v[5] + 8, 2.5)
            r.acercar(v[2] + v[4] // 2 - 200, v[3] + v[5] // 2 - 160, 400, 320, 3.0)
            time.sleep(3.0)
            ps.uno(v[2] + 199, v[3] + 103, 0.6)                          # Cancelar
            time.sleep(0.8)
            fin = voz("proyecto_2")
            rx(f"NUEVOPROYECTO 'juego' '{PROY}' 'Nave'", pausa=4.0)
            r.hasta(fin)
            time.sleep(0.5)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 4. El editor ------------------------------------------------------------------------------------------------
    if hacer("editor"):
        try:
            r.capitulo("editor")
            if DESDE == "editor":
                rx(f"ABRIR '{NAVE}' 1", pausa=2.0)
            raton_en_forja()
            ficheros, editor, salida = zona_forja()
            fin = voz("editor_1"); r.rasgo("colores")
            r.marcar("ficheros", *ficheros, 1.5); time.sleep(1.5)
            r.marcar("editor", *editor, 1.5); time.sleep(1.5)
            r.marcar("salida", *salida, 1.6)
            r.hasta(fin)
            # una función nueva, en la línea en blanco entre dos funciones
            n = linea_con(NAVE, "func pintar_marcador") - 1
            abrir_en(NAVE, n, pausa=1.5)
            a_forja_editor = None
            fin = voz("editor_2"); r.rasgo("pares")
            escribir("func saludar(nombre: String) -> String")
            k("ret", 0, 0.5)
            escribir('return "Hola, " + nombre')
            r.hasta(fin)
            k("down"); agente.combo(raw("right"), ALT); time.sleep(0.3)      # tras el end, con su línea en blanco
            k("ret", 0, 0.4)
            n_ret = n + 1
            # comentar, duplicar, mover
            fin = voz("editor_3"); r.rasgo("lineas")
            abrir_en(NAVE, n_ret, pausa=1.2)
            menu.elegir(640, 420, "Editor", "Comentar o descomentar", pausa=0.6)
            time.sleep(1.2)
            menu.elegir(640, 420, "Editor", "Comentar o descomentar", pausa=0.4)
            time.sleep(0.8)
            k("d", CTRL, 1.0)
            k("down", CTRL | ALT, 1.0)
            k("up", CTRL | ALT, 1.0)
            k("k", CTRL | MAYUS, 1.0)
            r.hasta(fin)
            # esquema
            fin = voz("editor_4"); r.rasgo("esquema")
            k("o", CTRL, 1.5)
            escribir("marc", 0.15)
            time.sleep(1.0)
            k("ret", 0, 1.0)
            r.hasta(fin)
            # ir a un nombre
            fin = voz("editor_5"); r.rasgo("simbolo")
            k("t", CTRL, 1.5)
            escribir("hacer_j", 0.15)
            time.sleep(1.0)
            k("ret", 0, 1.0)
            r.hasta(fin)
            # buscar en el proyecto (lo del cursor)
            fin = voz("editor_6"); r.rasgo("buscar")
            k("f", CTRL | MAYUS, 1.5)
            for _ in range(3):
                if esperar_salida(S_VECES, 3):
                    break
            m = linea_salida(S_VECES)
            if m:
                r.marcar("buscar", *m, 3.0)
            time.sleep(1.5)
            ps.clic_en_salida("main.dash:")
            r.hasta(fin)
            cerrar_ventanas(T_BUSCAR)
            # plegar
            fin = voz("editor_7"); r.rasgo("plegar")
            abrir_en(NAVE, linea_con(NAVE, "func pintar_celda") + 2, pausa=1.3)
            k("f4", 0, 1.5)
            time.sleep(1.5)
            k("f4", 0, 1.0)
            r.hasta(fin)
            guardar()
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 5. La ayuda de Dash -----------------------------------------------------------------------------------------
    if hacer("ayuda"):
        try:
            r.capitulo("ayuda")
            if DESDE == "ayuda":
                rx(f"ABRIR '{NAVE}' 1", pausa=2.0)
            n = linea_con(NAVE, "gfx_rect(x, y")
            abrir_en(NAVE, n, pausa=1.5)
            teclas_n("right", 10)
            fin = voz("ayuda_1"); r.rasgo("f1")
            k("f1", 0, 3.0)
            v = ps.esperar_ventana(T_AYUDA, 10)
            r.marcar("ficha", v[2] + 280, v[3] + 40, v[4] - 300, 300, 3.0)
            r.hasta(fin)
            fin = voz("ayuda_2"); r.rasgo("buscaayuda")
            ps.uno(v[2] + 380, v[3] + 26, 0.8); time.sleep(0.4)
            agente.tecla(raw("x"), AM); time.sleep(0.3)
            escribir("rect", 0.2)
            time.sleep(0.5)
            k("ret", 0, 2.0)
            r.hasta(fin)
            fin = voz("ayuda_3"); r.rasgo("probar")
            ps.uno(v[2] + 198, v[3] + 26, 0.8)                 # el botón Probar
            esperar_salida(S_ACABO, 25)
            r.hasta(fin)
            time.sleep(1.0)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 6. Errores y ejecutar ---------------------------------------------------------------------------------------
    if hacer("errores"):
        try:
            r.capitulo("errores")
            if DESDE == "errores":
                rx(f"ABRIR '{NAVE}' 1", pausa=2.0)
            a_forja()
            n = linea_con(NAVE, "func saludar")
            abrir_en(NAVE, n, pausa=1.5)
            agente.combo(raw("right"), ALT); time.sleep(0.3)
            fin = voz("errores_1"); r.rasgo("errores")
            k("ret", 0, 0.4)
            escribir("Print salud(nombre)")
            time.sleep(0.5)
            guardar()
            esperar_estado("libre", 15); time.sleep(2.0)
            r.hasta(fin)
            fin = voz("errores_2"); r.rasgo("f8")
            k("f8", 0, 1.5)
            m = linea_salida("Error")
            if m:
                r.marcar("error", *m, 2.5)
            time.sleep(1.0)
            k("k", CTRL | MAYUS, 1.0)                           # borra la línea del error
            guardar()
            time.sleep(1.5)
            r.hasta(fin)
            fin = voz("errores_3"); r.rasgo("compilar")
            agente.tecla(raw("k"), AM)
            esperar_salida(S_COMPILADO, 20)
            r.hasta(fin)
            fin = voz("errores_4"); r.rasgo("juego")
            agente.tecla(raw("e"), AM)
            t0 = time.time()
            while ps.forja() and time.time() - t0 < 20:
                time.sleep(0.3)
            time.sleep(2.0)
            r.acercar(400, 320, 480, 384, 6.0)
            r.hasta(fin)
            time.sleep(1.0)
            parar_programa("Nave/Nave")
            esperar_estado("libre", 15)
            forja_delante()
            time.sleep(1.0)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 7. El depurador ---------------------------------------------------------------------------------------------
    if hacer("depurar"):
        try:
            r.capitulo("depurar")
            rx(f"ABRIR '{PROY}/Nave/main.dash' 1", pausa=1.5) if not ps.forja() else None
            agente.lanzar(f"C:Copy MyFiles:Juego/suma.dash {PROY}/Nave/ QUIET")
            time.sleep(1.0)
            abrir_en(f"{PROY}/Nave/suma.dash", 6, pausa=2.0)
            a_forja()
            fin = voz("depurar_1"); r.rasgo("punto")
            k("f9", 0, 1.0)
            f = ps.forja()
            r.marcar("punto", ps.margen_x() - 10, f[2] + 85 + 50 - 6, 300, 14, 2.5)
            r.hasta(fin)
            fin = voz("depurar_2"); r.rasgo("condicion")
            menu.elegir(640, 420, "Depurar", "Condición del punto de parada...", pausa=0.6)
            time.sleep(1.2)
            escribir("i == 7", 0.2)
            time.sleep(0.6)
            k("ret", 0, 1.0)
            r.hasta(fin)
            fin = voz("depurar_3"); r.rasgo("pila")
            k("f5", 0, 0.3)
            esperar_estado("depurando", 20); time.sleep(1.5)
            menu.elegir(640, 420, "Depurar", "Vigilar una expresión...", pausa=0.6)
            time.sleep(1.0)
            escribir("total * 2", 0.2)
            time.sleep(0.5)
            k("ret", 0, 1.0)
            f = ps.forja()
            ex, ey, ew, eh = ps.campos("FORJA_EDITOR")
            r.acercar(f[1], f[2] + 20, 560, 448, 6.0)
            r.hasta(fin)
            fin = voz("depurar_4"); r.rasgo("raton")
            p.mover_a(f[1] + ex + 120, f[2] + 85 + 50, 0.8)
            p.mover_a(f[1] + ex + 128, f[2] + 85 + 50, 0.4)
            time.sleep(2.2)
            r.rasgo("cambiar")
            menu.elegir(640, 420, "Depurar", "Cambiar valor...", pausa=0.6)
            time.sleep(1.0)
            escribir("total = 100", 0.2)
            time.sleep(0.6)
            k("ret", 0, 1.2)
            r.hasta(fin)
            fin = voz("depurar_5")
            k("f5", 0, 0.3)
            esperar_estado("libre", 15); time.sleep(0.6)
            m = linea_salida("Total")
            if m:
                r.marcar("total", *m, 2.5)
            r.hasta(fin)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 8. Git ------------------------------------------------------------------------------------------------------
    if hacer("git"):
        try:
            r.capitulo("git")
            # sin que se vea: el repositorio con lo que hay ahora
            for c in ("init", "config user.name FreeMEM", "config user.email forja@amiga", "add -A", "commit -m Inicio"):
                rx(f"GIT '{c}'", "FORJAEXT.GIT", pausa=2.0)
            esperar_estado("libre", 15)
            abrir_en(NAVE, 1, pausa=1.5)
            a_forja()
            fin = voz("git_1"); r.rasgo("rama")
            f = ps.forja()
            r.marcar("rama", f[1] + f[3] - 320, f[2] + 4, 300, 28, 3.0)
            r.hasta(fin)
            fin = voz("git_2"); r.rasgo("rayas")
            abrir_en(NAVE, linea_con(NAVE, "const IZQUIERDA"), pausa=1.5)
            agente.combo(raw("right"), ALT); time.sleep(0.3)
            k("ret", 0, 0.4)
            escribir("const VIDAS = 3")
            time.sleep(0.5)
            guardar()
            time.sleep(3.0)
            r.hasta(fin)
            fin = voz("git_3"); r.rasgo("cambios")
            menu.elegir(640, 420, "Git", "Cambios y confirmar...", pausa=0.6)
            time.sleep(2.0)
            f = ps.forja()
            ps.uno(f[1] + 19, f[2] + 70, 0.8); time.sleep(1.0)             # la casilla del fichero
            r.rasgo("diferencias")
            ps.doble(f[1] + 81, f[2] + 70)
            time.sleep(2.5)
            r.hasta(fin)
            fin = voz("git_4"); r.rasgo("commit")
            ps.uno(f[1] + 146, f[2] + f[4] - 122, 0.8); time.sleep(0.4)
            escribir("Anado las vidas", 0.12)
            time.sleep(0.6)
            k("ret", 0, 3.0)
            r.hasta(fin)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 9. El copiloto ----------------------------------------------------------------------------------------------
    if hacer("inferencia"):
        try:
            r.capitulo("inferencia")
            abrir_en(NAVE, linea_con(NAVE, "gfx_pen(1)"), pausa=1.5)
            a_forja()
            fin = voz("inferencia_1"); r.rasgo("copiloto")
            r.hasta(fin)
            # cambiar el código
            fin = voz("inferencia_2"); r.rasgo("cambiarcod")
            k("c", CTRL | ALT, 3.0)
            escribir("Muestra tambien las vidas", 0.1)
            time.sleep(0.6)
            k("ret", 0, 0.3)
            f = ps.forja()
            time.sleep(1.0)
            if S_CAMBIAR not in "\n".join(ps.salida_lineas()[-6:]) and not esperar_salida(S_PESTANA, 3):
                ps.uno(f[1] + f[3] - 123, f[2] + f[4] - 23)                    # el botón Pedir
            esperar_salida(S_PESTANA, 40)
            time.sleep(1.5)
            r.rasgo("aceptar")
            r.hasta(fin)
            fin = voz("inferencia_3")
            aceptar_cambio()
            time.sleep(1.0)
            r.hasta(fin)
            # la prueba de saludar
            fin = voz("inferencia_4"); r.rasgo("prueba")
            abrir_en(NAVE, linea_con(NAVE, "func saludar") + 1, pausa=1.5)
            menu.elegir(640, 420, "Inferencia", "Escribir la prueba", pausa=0.6)
            esperar_salida(S_PESTANA, 40)
            time.sleep(2.0)
            aceptar_cambio()
            esperar_salida(S_BIEN, 30)
            time.sleep(2.0)
            r.hasta(fin)
            # un error de compilar: explicar y arreglar
            fin = voz("inferencia_5"); r.rasgo("explicar")
            n = linea_con(NAVE, "gfx_circle_fill")
            abrir_en(NAVE, n, pausa=1.5)
            ir_a_columna(22)                                    # tras gfx_circle_fil
            k("del", 0, 0.6)                                    # gfx_circle_fil: falta una ele
            guardar()
            time.sleep(2.0)
            k("e", CTRL | ALT, 0.5)
            t0 = time.time()
            while not amiga.ventana("Inferencia") and time.time() - t0 < 60:
                time.sleep(0.5)
            time.sleep(4.0)
            r.hasta(fin)
            fin = voz("inferencia_6"); r.rasgo("arreglar")
            a_forja()
            menu.elegir(640, 420, "Inferencia", "Arreglar el error", pausa=0.6)
            esperar_salida(S_PESTANA, 40)
            time.sleep(2.0)
            aceptar_cambio()
            time.sleep(1.5)
            guardar()
            r.hasta(fin)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 10. Sprites y mapas -----------------------------------------------------------------------------------------
    if hacer("sprites"):
        try:
            r.capitulo("sprites")
            cerrar_extensiones()
            a_forja()
            fin = voz("sprites_1"); r.rasgo("bob")
            ps.nuevo("b"); time.sleep(2.0)
            r.hasta(fin)
            fin = voz("sprites_2")
            with deprisa(fin, 8):
                ps.muneco()
                ps.letra("d"); time.sleep(0.8)
                ps.sonrisa()
            time.sleep(0.5)
            ps.letra(" "); time.sleep(2.4)
            ps.letra(" "); time.sleep(0.4)
            r.hasta(fin)
            with deprisa(0, 3):
                ps.guardar_como(f"{PROY}/Nave/muneco.iff")
            time.sleep(0.6)
            cerrar_extensiones()
            fin = voz("sprites_3"); r.rasgo("mapa")
            a_forja()
            ps.nuevo("m")
            ps.pedir_fichero("MyFiles:Juego/tiles.iff")
            with deprisa(0, 8):
                ps.mp_boton(5002); time.sleep(0.6)
                ps.mp_boton(4000, veces=42, pausa=0.12)
                ps.mp_boton(4002, veces=16, pausa=0.12)
                time.sleep(1.0)
                ps.nivel_fondo()
            r.hasta(fin)
            time.sleep(0.8)
            with deprisa(0, 3):
                ps.guardar_como(f"{PROY}/Nave/nivel.fmap")
            time.sleep(0.5)
            cerrar_extensiones()
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 11. Demos ---------------------------------------------------------------------------------------------------
    if hacer("demos"):
        try:
            r.capitulo("demos")
            cerrar_extensiones()
            DEMO = f"{PROY}/Demo/main.dash"
            agente.lanzar(f"C:Delete {PROY}/Demo ALL QUIET")
            time.sleep(1.0)
            rx(f"NUEVOPROYECTO 'demo' '{PROY}' 'Demo'", pausa=4.0)
            agente.lanzar(f"C:Copy MyFiles:Juego/musica.mod {PROY}/Demo/ QUIET")
            time.sleep(1.0)
            a_forja()
            fin = voz("demos_1"); r.rasgo("demo")
            r.hasta(fin)
            fin = voz("demos_2"); r.rasgo("asm")
            n = linea_con(DEMO, "asm")
            abrir_en(DEMO, n, pausa=1.5)
            ficheros, editor, salida = zona_forja()
            r.marcar("asm", editor[0], editor[1] + 10 * 8, 700, 90, 3.0)
            r.hasta(fin)
            fin = voz("demos_3"); r.rasgo("pistas")
            menu.elegir(640, 420, "Demos", "Pistas de sincronía", pausa=0.6)
            v = ps.esperar_ventana("Demos", 10); time.sleep(1.0)
            f = ps.forja()
            ps.uno(f[1] + 60, f[2] + 100, 0.8)                         # demo.sync en el panel
            time.sleep(1.5)
            agente.tecla(raw("e"), AM)                                  # la demo (Amiga-E llega a Forja)
            esperar_estado("ejecutando", 40); time.sleep(4.0)
            agente.combo(raw("m"), LAM); time.sleep(2.0)                 # la pantalla de Forja otra vez delante
            r.hasta(fin)
            fin = voz("demos_4"); r.rasgo("claves")
            k("down", 0, 0.3)
            teclas_n("down", 8, 0, 0.1)
            agente.escribir("6"); time.sleep(0.3)
            k("ret", 0, 1.5)
            k("v", 0, 4.0)                                              # la pantalla de la demo, delante
            agente.combo(raw("m"), LAM); time.sleep(2.0)                 # y la de Forja otra vez
            forja_delante()
            r.hasta(fin)
            fin = voz("demos_5"); r.rasgo("mod")
            agente.tecla(raw("2"), AM); time.sleep(1.5)
            rx(f"ABRIR '{PROY}/Demo/musica.mod'", pausa=2.5)        # el módulo, en el visor
            k("space", 0, 3.0)
            k("right", 0, 1.0)
            r.hasta(fin)
            k("space", 0, 0.5)
            fin = voz("demos_6"); r.rasgo("copper")
            agente.tecla(raw("1"), AM); time.sleep(2.0)
            r.hasta(fin)
            fin = voz("demos_7"); r.rasgo("raster")
            agente.tecla(raw("4"), AM); time.sleep(1.5)
            agente.tecla(raw("e"), AM)                                   # otra vez la demo, para que haya qué medir
            esperar_estado("ejecutando", 40); time.sleep(3.0)
            agente.combo(raw("m"), LAM); time.sleep(2.0)
            forja_delante()
            time.sleep(3.0)
            r.hasta(fin)
            fin = voz("demos_8"); r.rasgo("partes")
            agente.tecla(raw("5"), AM); time.sleep(2.0)
            r.hasta(fin)
            time.sleep(1.0)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 12. 3D ------------------------------------------------------------------------------------------------------
    if hacer("tresd"):
        try:
            r.capitulo("tresd")
            cerrar_extensiones()
            agente.lanzar(f"C:Delete {PROY}/Cubo ALL QUIET")
            time.sleep(1.0)
            rx(f"NUEVOPROYECTO '3d' '{PROY}' 'Cubo'", pausa=4.0)
            a_forja()
            fin = voz("tresd_1"); r.rasgo("cubo")
            agente.tecla(raw("e"), AM)
            time.sleep(8.0)
            v = None
            for w in amiga.ventanas():
                if w[1] == "" and w[4] < 400:
                    v = w
            if v:
                r.marcar("cubo", v[2], v[3], v[4], v[5], 3.0)
            r.hasta(fin)
            time.sleep(2.0)
            parar_programa("Cubo/Cubo")
            esperar_estado("libre", 15)
            forja_delante()
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 13. El diseñador de ventanas (lo pidió Jose) -----------------------------------------------------------------
    if hacer("ventanas"):
        try:
            r.capitulo("ventanas")
            cerrar_extensiones()
            agente.lanzar(f"C:Delete {PROY}/Saludo ALL QUIET")
            time.sleep(1.0)
            fin = voz("ventanas_1"); r.rasgo("disenador")
            rx(f"NUEVOPROYECTO 'mui' '{PROY}' 'Saludo'", pausa=4.0)
            rx(f"ABRIR '{PROY}/Saludo/ventana.dashui' 1", pausa=2.5)
            raton_en_forja(200, 600)
            r.hasta(fin)
            fin = voz("ventanas_2"); r.rasgo("paleta")
            t = lienzo("titulo"); li = lienzo("limpiar"); b = lienzo("button"); vi = lienzo("vista"); pr = lienzo("props")
            # cerca: la paleta, la ventana y las propiedades (a 1280x1024 se ven pequeñas), mientras se cuenta y se arrastra
            zx, zy = b[0] - 16, b[1] - 40
            r.acercar(zx, zy, 1000, 800, DURA["ventanas_2"] + DURA["ventanas_3"] + 4.0)
            r.marcar("ventana", t[0] - 6, t[1] - 6, t[2] + 12, li[1] + li[3] - t[1] + 16, 2.2)
            time.sleep(2.2)
            r.marcar("paleta", b[0] - 4, b[1] - 3, vi[0] + vi[2] - b[0] + 8, b[3] + 6, 2.2)
            p.mover_a(b[0] + b[2] // 2, b[1] + b[3] // 2, 1.0)        # el nombre del icono sale al pasar por encima
            time.sleep(1.2)
            r.marcar("props", pr[0] - 2, pr[1] - 2, pr[2] + 4, pr[3] * 7 + 4, 2.0)
            r.hasta(fin)
            fin = voz("ventanas_3"); r.rasgo("arrastrar")
            b = lienzo("button"); li = lienzo("limpiar")
            ps.arrastrar((b[0] + b[2] // 2, b[1] + b[3] // 2), (li[0] + li[2] - 8, li[1] + li[3] // 2), dur=1.6)
            time.sleep(1.5)
            pr = lienzo("props")                                       # el botón nuevo, elegido: su label, la primera
            ps.uno(pr[0] + pr[2] // 2, pr[1] + pr[3] // 2, 0.7)
            time.sleep(0.6)
            teclas_n("bs", 8)
            escribir("_Hasta luego", 0.08, 2)
            k("ret")
            time.sleep(1.0)
            r.hasta(fin)
            fin = voz("ventanas_4"); r.rasgo("doblec")
            li = lienzo("limpiar"); t = lienzo("titulo")
            nx, ny = (li[0] + li[2] + t[0] + t[2]) // 2, li[1] + li[3] // 2   # el botón nuevo, a la derecha de limpiar
            p.mover_a(nx, ny, 0.8)
            time.sleep(0.4)
            p.clic(2)
            time.sleep(3.0)
            _, editor, _ = zona_forja()
            r.marcar("codigo", *editor, 2.5)
            r.hasta(fin)
            fin = voz("ventanas_5"); r.rasgo("ejecutar_ui")
            teclas_n("del", len("# hasta_luego"), 0, 0.1)            # el comentario del if nuevo, por su código
            escribir('mui_set_text(v.saludo, "Hasta luego")', 0.06, 3)
            time.sleep(0.8)
            agente.tecla(raw("e"), AM)                                 # Amiga-E: guarda, compila y ejecuta
            t0 = time.time()
            while not amiga.ventana("Saludo") and time.time() - t0 < 40:
                time.sleep(0.4)
            time.sleep(1.5)
            v = amiga.ventana("Saludo")
            if v:
                r.marcar("programa", v[2] - 4, v[3] - 4, v[4] + 8, v[5] + 8, 3.0)
                r.acercar(v[2] + v[4] // 2 - 250, v[3] + v[5] // 2 - 200, 500, 400, 5.0)
                p.mover_a(v[2] + v[4] * 5 // 6, v[3] + v[5] - 14, 1.0)   # el tercer botón de la fila de abajo
                time.sleep(0.4)
                p.clic()
                time.sleep(2.5)
            r.hasta(fin)
            time.sleep(1.0)
            if amiga.ventana("Saludo"):
                p.cerrar("Saludo")
            esperar_estado("libre", 15)
            forja_delante()
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

    # --- 14. Extensiones ---------------------------------------------------------------------------------------------
    if hacer("cierre"):
        try:
            r.capitulo("cierre")
            a_forja()
            fin = voz("cierre_1"); r.rasgo("gestor")
            menu.elegir(640, 420, "Extensiones", "Gestor de extensiones...", pausa=0.6)
            time.sleep(2.5)
            r.hasta(fin)
            fin = voz("cierre_2"); r.rasgo("libre")
            r.hasta(fin)
            time.sleep(1.5)
        except Exception:
            import traceback
            traceback.print_exc()
            print("FALLO en el capítulo, sigo con el siguiente", flush=True)

finally:
    r.acabar()
print("toma:", round(r.ahora(), 1), "s")
