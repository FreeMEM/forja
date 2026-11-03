"""Pasos sueltos del vídeo de Forja, medidos en Coffin R65 (RTG a 1280x1024). Los usa guion.py; también se pueden
probar sueltos (python3 -c "import pasos; pasos.instalar()")."""
import time

import agente
import amiga
import piloto as p
from amiberry import orden

RAMIGA, LAMIGA, CTRL, LALT, MAYUS = 0x80, 0x40, 0x08, 0x10, 0x01
K_RETURN, K_X = 0x44, 0x32
RAM_DISK, TRASPASO, PROGRAMS = (27, 45), (38, 250), (27, 115)
PAQUETE = "dash-2.2.0-amiga.lha"


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


def escribir(texto, return_=True):
    agente.escribir(texto)
    if return_:
        time.sleep(0.2)
        agente.tecla(K_RETURN)


def shell(x=330, y=300, ancho=700, alto=220):
    agente.lanzar(f'NewShell WINDOW "CON:{x}/{y}/{ancho}/{alto}/Shell/CLOSE"')
    return esperar_ventana("Shell")


def descomprimir():
    """Una Shell y la orden de LhA, que se ve escribir; luego se cierra la Shell."""
    shell()
    time.sleep(1.0)
    escribir(f"lha x Traspaso:{PAQUETE} RAM:")
    time.sleep(9)


def abrir_cajon_dash():
    """RAM Disk y, dentro, el cajón Dash recién descomprimido."""
    doble(*RAM_DISK)
    esperar_ventana("RAM Disk"); time.sleep(1.0)
    doble(*en("RAM Disk", 30, 30))
    return esperar_ventana("Dash")


def instalar_paso(cual):
    """Los botones del Installer (ventana de 496x210), medidos."""
    if cual == "seguir":                     # "Seguir con la instalación" y "Seguir" de las opciones
        uno(*en("Instalar", 127, 180))
    elif cual == "destino":                  # el campo del cajón: Programs:
        uno(*en("Instalar", 257, 145)); time.sleep(0.5)
        agente.tecla(K_X, RAMIGA); time.sleep(0.3)
        escribir("Programs:")
    elif cual == "seguir_destino":
        uno(*en("Instalar", 73, 165))
    elif cual == "final":                    # "Seguir" del mensaje del final y "Salir" de ¡Instalación completa!
        uno(*en("Instalar", 248, 197))


def instalar():
    """De principio a fin, sin rodaje: para probar."""
    descomprimir()
    p.cerrar("Shell")
    abrir_cajon_dash()
    doble(*en("Dash", 32, 32))
    esperar_ventana("Instalar"); time.sleep(2)
    instalar_paso("seguir"); time.sleep(1.5)
    instalar_paso("seguir"); time.sleep(1.5)
    instalar_paso("destino"); time.sleep(1.5)
    instalar_paso("seguir_destino"); time.sleep(4)
    instalar_paso("final"); time.sleep(1.5)
    instalar_paso("final"); time.sleep(1.5)
    esperar_sin("Instalar")


def abrir_cajon_instalado():
    agente.lanzar("""SYS:Rexxc/RX "ADDRESS WORKBENCH 'WINDOW Programs:Dash OPEN'" """)
    return esperar_ventana("Dash")


K_RETROCESO, K_A, K_N, K_S, K_E, K_K, K_W, K_O = 0x41, 0x20, 0x36, 0x21, 0x12, 0x27, 0x11, 0x18


def teclear(codigo, ritmo=0.06):
    """Escribe código en el editor de Forja como una persona: a trozos, con Return entre líneas. El editor deja en
    cada línea nueva la sangría de la anterior: se añaden los espacios que faltan o se quitan con Retroceso (uno por
    nivel)."""
    antes = 0
    for i, linea in enumerate(codigo.split("\n")):
        if i > 0:
            agente.tecla(K_RETURN); time.sleep(ritmo * 2)
        texto = linea.lstrip(" ")
        sangria = len(linea) - len(texto) if texto else antes
        if sangria < antes:                     # el Retroceso de Forja quita un nivel de sangría (4 espacios)
            for _ in range((antes - sangria + 3) // 4):
                agente.tecla(K_RETROCESO); time.sleep(0.05)
        elif sangria > antes:
            agente.escribir(" " * (sangria - antes))
        antes = sangria
        for j in range(0, len(texto), 3):
            agente.escribir(texto[j:j + 3]); time.sleep(ritmo)


def abrir_forja():
    """Desde el cajón instalado: el cajón Forja y su icono."""
    for t in ("Dash", "RAM Disk"):
        while amiga.ventana(t):
            p.cerrar(t); time.sleep(0.4)
    abrir_cajon_instalado(); time.sleep(0.8)
    doble(*en("Dash", 275, 35))
    esperar_ventana("Forja"); time.sleep(0.8)
    doble(*en("Forja", 32, 35))
    t = time.time()
    while time.time() - t < 20:
        v = amiga.ventana("Forja")
        if v and v[4] > 1000:
            return v
        time.sleep(0.3)
    raise RuntimeError("Forja no abre")


def forja():
    """La ventana grande de Forja (la del cajón también se llama Forja)."""
    for w in amiga.ventanas():
        if w[1] == "Forja" and w[4] > 1000:
            return w[1:]
    return None


def guardar_como(ruta):
    """Amiga-S con un fichero sin nombre: la petición de ficheros de ASL; se escribe la ruta entera."""
    agente.tecla(K_S, RAMIGA); time.sleep(1.5)
    agente.tecla(K_X, RAMIGA); time.sleep(0.2)
    agente.escribir(ruta); time.sleep(0.3)
    agente.tecla(K_RETURN); time.sleep(0.8)          # reparte la ruta en Drawer y File
    agente.tecla(K_RETURN); time.sleep(1.5)          # y guarda


def env(nombre):
    """Una variable de ENV: del Amiga (las de la sonda de Forja dicen dónde está cada cosa)."""
    import os
    f = os.path.expanduser("~/.cache/video-forja/traspaso/env.txt")
    if os.path.exists(f):
        os.remove(f)
    agente.lanzar(f"C:GetEnv {nombre} >Traspaso:env.txt")
    t = time.time()
    while time.time() - t < 5:
        if os.path.exists(f):
            time.sleep(0.2)
            return open(f, encoding="latin-1").read().strip()
        time.sleep(0.1)
    return ""


def campos(nombre):
    return [int(x) for x in env(nombre).split()]


def salida_lineas():
    """El texto de la salida de Forja (la sonda lo deja en RAM:forja-salida.txt)."""
    import os
    f = os.path.expanduser("~/.cache/video-forja/traspaso/salida.txt")
    if os.path.exists(f):
        os.remove(f)
    agente.lanzar("C:Copy RAM:forja-salida.txt Traspaso:salida.txt")
    t = time.time()
    while time.time() - t < 5 and not os.path.exists(f):
        time.sleep(0.1)
    time.sleep(0.2)
    return open(f, encoding="latin-1").read().split("\n")


def clic_en_salida(texto):
    """Un clic en la primera línea de la salida que lleva ese texto."""
    x, y, fila, primera, _ = campos("FORJA_SALIDA")
    f = forja()
    for i, l in enumerate(salida_lineas()):
        if texto in l:
            uno(f[1] + x + 120, f[2] + y + (i - primera) * fila + fila // 2)
            return True
    return False


def cursor():
    """(línea, columna) del cursor en el editor, desde 0 (la primera línea de RAM:forja-sonda.txt)."""
    import os
    f = os.path.expanduser("~/.cache/video-forja/traspaso/sonda.txt")
    if os.path.exists(f):
        os.remove(f)
    agente.lanzar("C:Copy RAM:forja-sonda.txt Traspaso:sonda.txt")
    t = time.time()
    while time.time() - t < 5 and not os.path.exists(f):
        time.sleep(0.1)
    time.sleep(0.2)
    c = open(f, encoding="latin-1").readline().split()
    return int(c[0]), int(c[1])


def linea_y(i):
    """La y (en la pantalla) del centro de la línea i del editor (desde 0, con la primera arriba)."""
    f = forja()
    ex, ey, ew, eh = campos("FORJA_EDITOR")
    return f[2] + ey + 20 + 10 * i + 5


def margen_x():
    f = forja()
    ex, ey, ew, eh = campos("FORJA_EDITOR")
    return f[1] + ex + 12
