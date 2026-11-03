"""El guion del vídeo de Trasfondo, en Coffin R65 (Amiberry, RTG a 1280x1024). Se lanza con Coffin recién preparado
(preparar.py en|es: Trasfondo 0.9 descomprimido en Traspaso, el idioma de Locale de la toma y el agente en marcha).

    python3 guion.py <carpeta de la toma> en|es

Las dos tomas hacen lo mismo; cambia el idioma del sistema (y así el de Trasfondo y su instalador). Los subtítulos
van en los dos idiomas: el montaje usa el de la toma.

Lo que no se hace: cambiar el idioma en Locale con Trasfondo en marcha (después no se deja parar: se queda el panel
congelado, visto en la 0.9.3).
"""
import os
import sys
import tempfile
import time

import numpy as np
from PIL import Image

import agente
import amiga
import piloto as p
from amiberry import orden
from rodaje import Rodaje

CARPETA, L = sys.argv[1], sys.argv[2]
ES = L == "es"


def ultima_version():
    """La última versión publicada de Trasfondo (la que se bajará la 0.9 al ponerse al día), sin la "v"."""
    import json
    import urllib.request
    rel = json.load(urllib.request.urlopen("https://api.github.com/repos/FreeMEM/trasfondo/releases?per_page=5"))
    return next(r["tag_name"] for r in rel if r["tag_name"].startswith("v") and not r["prerelease"]).lstrip("v")


VER = ultima_version()

RAMIGA, CTRL, LALT = 0x80, 0x08, 0x10
K_RETURN, K_X, K_T = 0x44, 0x32, 0x14
TRASPASO, RAM_DISK = (38, 250), (27, 45)
# El panel (arriba a la derecha, en RTG a 1280x1024) y sus partes, medidos en capturas
PANEL = (1018, 26, 258, 206)
FECHA, CPU, MEMORIA = (1020, 28, 254, 26), (1020, 56, 254, 36), (1020, 96, 254, 20)
TAREAS, DISCOS = (1020, 119, 254, 52), (1020, 178, 254, 52)
PILOTO = (1070, 28, 60, 14)          # el piloto verde y su número, junto a "Trasfondo"
ZOOM_PANEL = (960, 16, 320, 256)     # el panel con algo de fondo alrededor, en 5:4
# TrasfondoPrefs: dónde está cada cosa dentro de su ventana. Cambia con el idioma (los textos) y con la versión (la
# 0.10 trae tres botones de ciclo más): se mide cada vez que la ventana sale con otro tamaño
PREFS = "Preferencias de Trasfondo" if ES else "Trasfondo Pref"
P = {}
_tamano = None
# Exchange, agrandada hasta y = 300: Trasfondo es el último de la lista; los botones van en un solo gadget
EX_TRASFONDO, EX_OCULTAR, EX_VER, EX_ACTIVO, EX_BORRAR = (42, 155), (240, 95), (370, 95), (240, 116), (370, 116)

r = Rodaje(CARPETA, L, VER)


def esperar_ventana(titulo, tope=20):
    t = time.time()
    while time.time() - t < tope:
        v = amiga.ventana(titulo)
        if v:
            return v
        time.sleep(0.3)
    raise RuntimeError("no sale la ventana " + titulo)


def esperar_sin(titulo, tope=20):
    t = time.time()
    while amiga.ventana(titulo) and time.time() - t < tope:
        time.sleep(0.3)


def en(titulo, dx, dy):
    v = amiga.ventana(titulo)
    return v[2] + dx, v[3] + dy


def doble(x, y, dur=0.9):
    p.mover_a(x, y, dur); time.sleep(0.3); p.clic(2)


def uno(x, y, dur=0.8):
    p.mover_a(x, y, dur); time.sleep(0.2); p.clic()


def arrastrar(desde, hasta, dur=1.4):
    p.mover_a(*desde)
    orden("SEND_MOUSE", 0, 0, 1)
    time.sleep(0.25)
    p.mover_a(*hasta, dur=dur, botones=1)
    time.sleep(0.3)
    orden("SEND_MOUSE", 0, 0, 0)
    time.sleep(0.4)


def esperar(seg, factor=6):
    """Una espera: en el vídeo, acelerada."""
    r.acelerar(factor)
    time.sleep(seg)
    r.normal()


def deprisa(factor=3):
    """Un trozo de manejo del Workbench que en el vídeo va más rápido (sin aviso de espera: factor < 4)."""
    r.acelerar(factor)


def marcar(nombre, zona, dur):
    r.marcar(nombre, *zona, dur)


def hay_piloto():
    """¿Sale el piloto verde de versión nueva junto a "Trasfondo"? (por su color, en una captura)"""
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "c.png")
        orden("SCREENSHOT", f)
        x, y, an, al = PILOTO
        a = np.asarray(Image.open(f).convert("RGB")).astype(int)[y:y + al, x:x + an]
    verde = (np.abs(a - np.array([156, 180, 92])).max(2) < 30).sum()
    return verde > 12


def prefs(cual, dur=0.8):
    uno(*en(PREFS, *P[cual]), dur)


def abrir_prefs():
    """La abre, la mide si hace falta y la activa (pulsando en su barra de título: los botones de ciclo no hacen
    caso si la ventana no está activa)."""
    agente.lanzar("SYS:Prefs/TrasfondoPrefs")
    v = esperar_ventana(PREFS)
    time.sleep(1.0)
    if (v[4], v[5]) != _tamano:
        medir_prefs()
    v = amiga.ventana(PREFS)
    uno(v[2] + v[4] // 2, v[3] + 5, 0.5)
    time.sleep(0.3)


def medir_prefs():
    """Los sitios de los gadgets de TrasfondoPrefs, leídos de la ventana (cuesta segundos: en el vídeo, acelerado).
    Van en este orden: seis casillas de qué se ve, cuántas tareas, tecla, (desde la 0.10: cada cuánto, fondo y
    color,) oculto, GitHub, estado, Actualizar, Guardar, Usar y Cancelar."""
    global _tamano
    r.acelerar(8)
    v = amiga.ventana(PREFS)
    g = [x for x in amiga.gadgets(v[0]) if x[2] > 0 and x[3] > 0 and x[1] - v[3] >= 22]
    rel = lambda x: (x[0] - v[2] + min(x[2] // 2, 14), x[1] - v[3] + x[3] // 2)
    centro = lambda x: (x[0] - v[2] + x[2] // 2, x[1] - v[3] + x[3] // 2)
    P.clear()
    # el orden de las casillas cambia con la versión: 15 gadgets en la 0.9, 18 en la 0.10 (tres ciclos), 21 en la
    # 0.11 (dos columnas: temperatura y gráficas de la memoria y de la red)
    if len(g) >= 21:
        i = dict(tareas=5, discos=6, memgrafica=4, cuantas=9, tecla=11, cada=12, fondo=13, color=14)
    elif len(g) >= 18:
        i = dict(tareas=3, discos=4, cuantas=6, tecla=7, cada=8, fondo=9, color=10)
    else:
        i = dict(tareas=3, discos=4, cuantas=6, tecla=7)
    # los ciclos, en su icono de la izquierda: en el 3.2, pulsar en el texto abre la lista y no cambia nada
    glifo = lambda x: (x[0] - v[2] + 10, x[1] - v[3] + x[3] // 2)
    for k, n in i.items():
        P[k] = glifo(g[n]) if k in ("cada", "fondo", "color") else rel(g[n])
    P.update(estado=(g[-5][0] - v[2], g[-5][1] - v[3], g[-5][2], g[-5][3]),
             actualizar=centro(g[-4]), guardar=centro(g[-3]), usar=centro(g[-2]), cancelar=centro(g[-1]))
    print("prefs:", v[4], v[5], P, flush=True)
    _tamano = (v[4], v[5])
    r.normal()


def campo(cual, texto):
    """Escribe en un campo de TrasfondoPrefs: lo vacía (Amiga-X) y escribe, a ritmo de persona."""
    prefs(cual)
    time.sleep(0.3)
    agente.tecla(K_X, RAMIGA)
    time.sleep(0.2)
    agente.escribir(texto)
    agente.tecla(K_RETURN)
    time.sleep(0.4)


def trabajo():
    """Algo de trabajo para la CPU: que la gráfica y las tareas tengan algo que enseñar."""
    agente.lanzar("C:List SYS: ALL >NIL:")


r.empezar()
try:
    time.sleep(1.2)

    # --- 1. Instalar -------------------------------------------------------------------------------------------------
    r.capitulo("instalar")
    r.decir("Here's Trasfondo 0.9, freshly unpacked from its .lha. Let's install it!",
            "Aquí está Trasfondo 0.9, recién descomprimido de su .lha. ¡Vamos a instalarlo!")
    deprisa()
    doble(*TRASPASO, 1.0)
    esperar_ventana("Traspaso"); time.sleep(1.0)
    doble(*en("Traspaso", 55, 34))
    esperar_ventana("Trasfondo"); time.sleep(0.8)
    r.normal()
    r.decir("Inside: the installer, Trasfondo itself, its preferences and the README.",
            "Dentro: el instalador, el propio Trasfondo, sus preferencias y el LEEME.")
    v = amiga.ventana("Trasfondo")
    r.marcar("cajon", v[2] + 10, v[3] + 20, 330, 60, 3)
    time.sleep(3.2)
    r.decir("Double-click Instalar: the good old Amiga Installer.",
            "Doble clic en Instalar: el Installer de toda la vida.")
    r.rasgo("instalar")
    doble(*en("Trasfondo", 32, 35))
    deprisa(4)
    esperar_ventana("Instalar"); time.sleep(1.5)
    r.normal()
    uno(*en("Instalar", 127, 180)); time.sleep(1.2)            # modo de instalación
    uno(*en("Instalar", 127, 180)); time.sleep(1.8)            # opciones
    r.decir("Start it with the Workbench every time? Yes: it goes into SYS:WBStartup.",
            "¿Que arranque solo con el Workbench? Sí: va a SYS:WBStartup.")
    r.rasgo("wbstartup")
    time.sleep(3.2)
    uno(*en("Instalar", 127, 180)); time.sleep(2.0)            # Sí
    r.decir("Its preferences go to SYS:Prefs. And start it right now? Yes!",
            "Sus preferencias, a SYS:Prefs. ¿Y lo pone en marcha ya? ¡Sí!")
    time.sleep(2.5)
    uno(*en("Instalar", 127, 180)); time.sleep(2.5)            # Sí: en marcha
    r.decir("There it is, top right. Installed in seconds.",
            "Ahí está, arriba a la derecha. Instalado en un momento.")
    marcar("panel", PANEL, 3.5)
    time.sleep(3.5)
    uno(*en("Instalar", 248, 197)); time.sleep(1.0)
    uno(*en("Instalar", 248, 197)); time.sleep(0.8)
    deprisa()
    p.cerrar("Trasfondo"); p.cerrar("Traspaso")
    time.sleep(0.8)
    r.normal()
    r.callar()

    # --- 2. Qué enseña -----------------------------------------------------------------------------------------------
    r.capitulo("panel")
    trabajo()
    r.decir("Trasfondo is painted on the Workbench backdrop itself: behind your icons and windows.",
            "Trasfondo va pintado en el propio fondo del Workbench: detrás de los iconos y las ventanas.")
    r.rasgo("fondo")
    r.acercar(*ZOOM_PANEL, 34)
    time.sleep(4.5)
    r.decir("Date and time, in your system's language.", "La fecha y la hora, en el idioma del sistema.")
    r.rasgo("fecha")
    marcar("fecha", FECHA, 3)
    time.sleep(3.2)
    r.decir("CPU in use, and its recent history.", "La CPU en uso y su historia reciente.")
    r.rasgo("cpu")
    marcar("cpu", CPU, 4)
    time.sleep(4.2)
    r.decir("Free Chip and Fast memory.", "La memoria Chip y Fast libre.")
    r.rasgo("memoria")
    marcar("memoria", MEMORIA, 3)
    time.sleep(3.2)
    trabajo()
    r.decir("The tasks using the most CPU, measured for real, task by task. No guessing.",
            "Las tareas que más CPU toman, medidas de verdad, tarea a tarea. Nada de estimar.")
    r.rasgo("tareas")
    marcar("tareas", TAREAS, 5)
    time.sleep(5.5)
    r.decir("Every mounted disk: how full it is, and its size.",
            "Cada disco montado: cuánto está lleno y su tamaño.")
    r.rasgo("discos")
    marcar("discos", DISCOS, 4)
    time.sleep(4.5)
    r.decir("With a network card, it also shows the traffic and the WiFi signal. Any TCP/IP stack.",
            "Con tarjeta de red, también el tráfico y la señal de la WiFi. Con cualquier pila TCP/IP.")
    r.rasgo("red")
    time.sleep(4.5)
    r.callar()
    time.sleep(0.5)
    r.decir("It never gets in the way: icons stay on top, as always.",
            "No estorba nunca: los iconos quedan por encima, como siempre.")
    r.rasgo("iconos")
    arrastrar(RAM_DISK, (1150, 140), 1.6)
    r.acercar(*ZOOM_PANEL, 5)
    time.sleep(3.5)
    arrastrar((1150, 140), RAM_DISK, 1.2)
    time.sleep(1.0)
    r.decir("In true colour it's translucent: your wallpaper shows through.",
            "Con color real es translúcido: se ve el fondo de pantalla a través.")
    r.rasgo("velo")
    r.acercar(*ZOOM_PANEL, 5)
    time.sleep(5)
    r.callar()

    # --- 3. Se pone al día solo --------------------------------------------------------------------------------------
    r.capitulo("actualizar")
    r.acelerar(8)                                             # el aviso sale un minuto después de arrancar
    t = time.time()
    while not hay_piloto() and time.time() - t < 120:
        time.sleep(1)
    r.normal()
    assert hay_piloto(), "no sale el piloto verde"
    r.decir(f"We installed 0.9 on purpose. See the green light? {VER} is out!",
            f"Hemos instalado la 0.9 a propósito. ¿Ves el piloto verde? ¡Ha salido la {VER}!")
    r.acercar(*ZOOM_PANEL, 4.5)
    marcar("piloto", (PILOTO[0] - 4, PILOTO[1] - 2, PILOTO[2] + 8, PILOTO[3] + 4), 4)
    time.sleep(4.5)
    r.decir("It checks GitHub by itself, without slowing anything down. Let's open TrasfondoPrefs...",
            "Lo mira él solo en GitHub, sin frenar nada. Abrimos TrasfondoPrefs...")
    r.rasgo("actualiza")
    abrir_prefs()
    time.sleep(1.5)
    v = amiga.ventana(PREFS)
    e = P["estado"]
    r.marcar("estado", v[2] + e[0], v[3] + e[1], e[2], e[3], 3)
    time.sleep(3)
    r.decir("One click on Update: it downloads it, checks it and restarts with the new one.",
            "Un clic en Actualizar: la baja, comprueba que llegó entera y vuelve a arrancar con la nueva.")
    prefs("actualizar")
    time.sleep(2.5)
    r.acelerar(4)
    t = time.time()
    while hay_piloto() and time.time() - t < 60:              # el piloto se va al arrancar la nueva
        time.sleep(1)
    time.sleep(4)
    r.normal()
    r.decir(f"Done: Trasfondo {VER}. No Aminet, no unpacking: straight from GitHub!",
            f"Listo: Trasfondo {VER}. Sin Aminet ni descomprimir nada: ¡directo de GitHub!")
    v = amiga.ventana(PREFS)
    r.marcar("estado", v[2] + e[0], v[3] + e[1], e[2], e[3], 3.5)
    time.sleep(4)
    prefs("cancelar")
    esperar_sin(PREFS)
    r.decir(f"And {VER} uses much less CPU: it only repaints what changed.",
            f"Y la {VER} gasta mucha menos CPU: solo repinta lo que ha cambiado.")
    r.rasgo("ligero")
    r.acercar(*ZOOM_PANEL, 5)
    marcar("tareas", TAREAS, 4.5)
    time.sleep(5)
    r.callar()

    # --- 4. A tu gusto -----------------------------------------------------------------------------------------------
    r.capitulo("prefs")
    r.decir("TrasfondoPrefs says what you see. Let's take out the tasks and the disks...",
            "TrasfondoPrefs dice qué se ve. Quitamos las tareas y los discos...")
    r.rasgo("prefs")
    abrir_prefs()
    time.sleep(0.5)
    prefs("tareas"); time.sleep(0.8)
    prefs("discos"); time.sleep(1.0)
    r.decir("...and Use: the panel changes right away, no restart needed.",
            "...y Usar: el panel cambia al momento, sin reiniciar nada.")
    r.rasgo("almomento")
    prefs("usar")
    esperar_sin(PREFS)
    r.acercar(*ZOOM_PANEL, 4.5)
    time.sleep(4.5)
    r.decir("The tasks again, but only three. And the disks back.",
            "Vuelven las tareas, pero solo tres. Y los discos otra vez.")
    abrir_prefs()
    prefs("tareas"); time.sleep(0.6)
    prefs("discos"); time.sleep(0.6)
    campo("cuantas", "3")
    time.sleep(0.6)
    if "memgrafica" in P:
        r.decir(f"New in {VER}: graphs for memory and network too. Here, the memory one.",
                f"Nuevo en la {VER}: gráficas también de la memoria y de la red. Aquí, la de la memoria.")
        r.rasgo("memgrafica")
        prefs("memgrafica"); time.sleep(2.5)
    r.decir("How often it measures: every 1, 2, 5 or 10 seconds. Less often, less CPU.",
            "Cada cuánto mide: 1, 2, 5 o 10 segundos. Menos a menudo, menos CPU.")
    r.rasgo("cada")
    for _ in range(4):                                        # 2 -> 5 -> 10 -> 1 -> 2: se ven todos y se queda en 2
        prefs("cada", 0.4); time.sleep(0.9)
    time.sleep(0.6)
    r.decir("A solid background instead of the see-through one, in the colour you like...",
            "Fondo fijo en vez de transparente, del color que quieras...")
    r.rasgo("color")
    prefs("fondo"); time.sleep(1.0)
    for _ in range(5):                                        # azul noche -> negro -> gris -> azul -> verde -> granate
        prefs("color", 0.3); time.sleep(0.7)
    time.sleep(0.6)
    r.decir("And a hotkey to hide it and bring it back.",
            "Y una tecla rápida para ocultarlo y traerlo.")
    r.rasgo("tecla")
    campo("tecla", "ctrl alt t")
    time.sleep(0.8)
    r.decir("Save: and it stays that way for good.", "Guardar: y así se queda para siempre.")
    prefs("guardar")
    esperar_sin(PREFS)
    r.acercar(*ZOOM_PANEL, 5)
    time.sleep(5)
    trabajo()
    r.decir("Ctrl-Alt-T: gone... and back, with its history complete: it kept measuring.",
            "Ctrl-Alt-T: se va... y vuelve, con la historia completa: no ha dejado de medir.")
    time.sleep(1.2)
    agente.tecla(K_T, CTRL | LALT)
    time.sleep(2.5)
    agente.tecla(K_T, CTRL | LALT)
    r.acercar(*ZOOM_PANEL, 4)
    time.sleep(4)
    r.callar()

    # --- 5. Commodity ------------------------------------------------------------------------------------------------
    r.capitulo("exchange")
    r.decir("It's a commodity: it's right there in Exchange, with the others.",
            "Es una commodity: sale en Exchange, con las demás.")
    r.rasgo("exchange")
    deprisa(4)
    agente.lanzar("SYS:Tools/Commodities/Exchange")
    esperar_ventana("Exchange"); time.sleep(1.5)
    v = amiga.ventana("Exchange")
    arrastrar((v[2] + v[4] - 4, v[3] + v[5] - 4), (v[2] + v[4] - 4, 300), 0.8)   # más alta: se ve la lista
    time.sleep(0.8)
    r.normal()
    uno(*en("Exchange", *EX_TRASFONDO))
    time.sleep(1.8)
    r.decir("Hide: the panel goes away, but it keeps measuring.",
            "Ocultar: se quita el panel, pero sigue midiendo.")
    uno(*en("Exchange", *EX_OCULTAR)); time.sleep(3.2)
    r.decir("Show: back again.", "Ver: de vuelta.")
    uno(*en("Exchange", *EX_VER)); time.sleep(3.2)
    r.decir("Switched off, it stops measuring too: it costs nothing at all.",
            "Desactivado, deja también de medir: no gasta nada.")
    uno(*en("Exchange", *EX_ACTIVO)); time.sleep(3.5)
    uno(*en("Exchange", *EX_ACTIVO)); time.sleep(2.5)
    r.decir("And Remove closes it, leaving the backdrop just as it was.",
            "Y Borrar lo cierra: el fondo queda como estaba.")
    uno(*en("Exchange", *EX_BORRAR)); time.sleep(4)
    deprisa()
    p.cerrar("Exchange")
    time.sleep(0.8)
    r.normal()
    r.callar()

    # --- 6. Escrito en Dash ------------------------------------------------------------------------------------------
    r.capitulo("dash")
    r.decir("It comes back every time the Workbench starts. Or now, by hand...",
            "Vuelve solo cada vez que arranca el Workbench. O ahora, a mano...")
    agente.lanzar("SYS:WBStartup/trasfondo")
    time.sleep(4)
    trabajo()
    r.decir("About 500 lines of Dash, compiled to plain 68000 code: no FPU needed.",
            "Unas 500 líneas de Dash, compiladas a código de 68000: no le hace falta FPU.")
    r.rasgo("dash")
    r.acercar(*ZOOM_PANEL, 14)
    time.sleep(5)
    r.decir("AGA or a graphics card, English or Spanish, following your system's language.",
            "En AGA o con tarjeta gráfica, en inglés o en castellano, según el idioma del sistema.")
    r.rasgo("idiomas")
    time.sleep(5)
    r.decir(f"Trasfondo {VER}: free and open source. Enjoy it!",
            f"Trasfondo {VER}: libre y de código abierto. ¡Que lo disfrutes!")
    r.rasgo("libre")
    time.sleep(5)
finally:
    r.acabar()
print("toma:", round(r.ahora(), 1), "s")
