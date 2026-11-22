"""Pasos sueltos del vídeo de Forja, medidos en Coffin R65 (RTG a 1280x1024). Los usa guion.py; también se pueden
probar sueltos (python3 -c "import pasos; pasos.instalar()")."""
import os
import time

import agente
import amiga
import piloto as p
from amiberry import orden

RAMIGA, LAMIGA, CTRL, LALT, MAYUS = 0x80, 0x40, 0x08, 0x10, 0x01
K_RETURN, K_X = 0x44, 0x32
RAM_DISK, TRASPASO, PROGRAMS = (27, 45), (38, 250), (27, 115)
PAQUETE = os.environ.get("VIDEO_PAQUETE", "dash-2.17.0-amiga.lha")


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
    agente.lanzar("""SYS:Rexxc/RX "ADDRESS WORKBENCH 'WINDOW Programs:Programming/Dash OPEN'" """)
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
    # (Copy y no GetEnv, que corta las largas, como FORJA_LIENZO)
    agente.lanzar(f"C:Copy ENV:{nombre} Traspaso:env.txt QUIET")
    t = time.time()
    while time.time() - t < 5:
        if os.path.exists(f):
            time.sleep(0.3)
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
    """Un clic en la última línea de la salida que lleva ese texto."""
    x, y, fila, primera, _ = campos("FORJA_SALIDA")
    f = forja()
    lineas = salida_lineas()
    for i in range(len(lineas) - 1, -1, -1):
        if texto in lineas[i]:
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


def abrir(ruta):
    """Amiga-O y la ruta entera en la petición de ASL."""
    agente.tecla(K_O, RAMIGA); time.sleep(1.5)
    agente.tecla(K_X, RAMIGA); time.sleep(0.2)
    agente.escribir(ruta); time.sleep(0.3)
    agente.tecla(K_RETURN); time.sleep(0.8)
    agente.tecla(K_RETURN); time.sleep(2)


PREF_MAPAS = "Mapas"      # "Maps" en inglés


def zona_ext(prefijo, variable):
    """La esquina del lienzo de una extensión en la pantalla: la de su ventana (el título empieza por prefijo) más lo
    que dice su variable de la sonda ("x y ancho alto", desde la esquina de la ventana)."""
    for w in amiga.ventanas():
        if w[1].startswith(prefijo):
            x, y, an, al = [int(c) for c in env(variable).split()]
            return w[2] + x, w[3] + y
    raise RuntimeError("no hay ventana " + prefijo)


# --- El editor de sprites ---

def sp_celda(cx, cy):
    """El centro de la celda cx, cy de la rejilla del editor de sprites, en la pantalla."""
    zx, zy = zona_ext("Sprites", "FORJA_SPRITES_LIENZO")
    gx, gy, z = campos("FORJA_SPRITE")
    return zx + gx + cx * z + z // 2, zy + gy + cy * z + z // 2


def arrastrar(desde, hasta, dur=0.8):
    p.mover_a(*desde, dur=0.5)
    orden("SEND_MOUSE", 0, 0, 1)
    time.sleep(0.15)
    p.mover_a(*hasta, dur=dur, botones=1)
    time.sleep(0.15)
    orden("SEND_MOUSE", 0, 0, 0)
    time.sleep(0.5)


def letra(c, cal=0):
    """Una tecla por su letra o cifra (el teclado del Amiga, en códigos crudos)."""
    fila1 = "1234567890"
    fila2 = "qwertyuiop"
    fila3 = "asdfghjkl"
    fila4 = "zxcvbnm"
    if c in fila1:
        k = 0x01 + fila1.index(c)
    elif c in fila2:
        k = 0x10 + fila2.index(c)
    elif c in fila3:
        k = 0x20 + fila3.index(c)
    elif c in fila4:
        k = 0x31 + fila4.index(c)
    elif c == " ":
        k = 0x40
    else:
        raise ValueError(c)
    agente.tecla(k, cal)
    time.sleep(0.25)


def muneco(cara="seria"):
    """Un muñeco en el fotograma actual: la cabeza (caja y relleno), los ojos, la boca y la antena."""
    letra("6"); letra("b")
    arrastrar(sp_celda(8, 8), sp_celda(23, 27), 1.0)
    letra("9"); letra("f")
    uno(*sp_celda(15, 15), 0.6); time.sleep(0.6)
    letra("1"); letra("p")
    for x, y in ((12, 13), (13, 13), (12, 14), (13, 14), (18, 13), (19, 13), (18, 14), (19, 14)):
        uno(*sp_celda(x, y), 0.25)
    letra("5"); letra("l")
    if cara == "seria":
        arrastrar(sp_celda(12, 21), sp_celda(19, 21), 0.6)
    else:
        arrastrar(sp_celda(11, 19), sp_celda(12, 21), 0.4)
        arrastrar(sp_celda(13, 22), sp_celda(18, 22), 0.5)
        arrastrar(sp_celda(19, 21), sp_celda(20, 19), 0.4)
    letra("6")
    arrastrar(sp_celda(15, 7), sp_celda(15, 3), 0.5)
    letra("8"); letra("p")
    for x, y in ((14, 2), (15, 2), (16, 2), (15, 1)):
        uno(*sp_celda(x, y), 0.25)


def sonrisa():
    """El segundo fotograma: el mismo muñeco sonriendo (se tapa la boca con el color de la cara)."""
    letra("9"); letra("l")
    arrastrar(sp_celda(12, 21), sp_celda(19, 21), 0.5)
    letra("5")
    arrastrar(sp_celda(11, 19), sp_celda(12, 21), 0.4)
    arrastrar(sp_celda(13, 22), sp_celda(18, 22), 0.5)
    arrastrar(sp_celda(19, 21), sp_celda(20, 19), 0.4)


def montar_rapido():
    """Para medir, sin rodaje: Dash descomprimido en RAM:, ENV:Forja/dashc y la carpeta MyFiles:Juego con el tileset
    y el juego; Forja abierta desde RAM:Dash/Forja (con la sonda)."""
    agente.lanzar(f"System:C/lha x Traspaso:{PAQUETE} RAM: >NIL:")
    time.sleep(12)
    agente.lanzar("C:MakeDir ENV:Forja MyFiles:Juego")
    agente.lanzar('C:SetEnv Forja/dashc "RAM:Dash/dash"')
    agente.lanzar("C:SetEnv FORJA_SONDA 1")
    agente.lanzar("C:Copy Traspaso:juego/#? MyFiles:Juego/")
    time.sleep(2)
    agente.lanzar("Run >NIL: RAM:Dash/Forja/Forja")
    t = time.time()
    while time.time() - t < 30 and not forja():
        time.sleep(0.5)
    time.sleep(3)
    return forja()


def nuevo(cual):
    """Amiga-B y en la petición "Nuevo sprite": s (sprite), b (BOB) o m (mapa). Espera a la petición antes."""
    f = forja()
    p.mover_a(f[1] + 600, f[2] + 400, 0.5); time.sleep(0.3)
    agente.tecla(0x35, RAMIGA)
    t = time.time()
    while time.time() - t < 10:
        if any(w[1] in ("Nuevo sprite", "New sprite") for w in amiga.ventanas()):
            break
        time.sleep(0.2)
    time.sleep(0.6)
    letra(cual)


def pedir_fichero(ruta, titulos=("Tileset del mapa", "The map's tileset", "Sprite del objeto", "The object's sprite")):
    """Espera a la petición de ficheros y escribe la ruta entera."""
    t = time.time()
    while time.time() - t < 10:
        if any(w[1] in titulos for w in amiga.ventanas()):
            break
        time.sleep(0.2)
    time.sleep(0.6)
    agente.tecla(K_X, RAMIGA); time.sleep(0.2)
    agente.escribir(ruta); time.sleep(0.3)
    agente.tecla(K_RETURN); time.sleep(0.8)
    agente.tecla(K_RETURN); time.sleep(2)


# --- El editor de mapas ---

def mp_celda(cx, cy):
    """El centro de la celda cx, cy del mapa en la pantalla (con la vista en 0, 0)."""
    zx, zy = zona_ext(PREF_MAPAS, "FORJA_MAPAS_LIENZO")
    gx, gy, lado, cols, filas = campos("FORJA_MAPA")
    return zx + gx + cx * lado + lado // 2, zy + gy + cy * lado + lado // 2


def mp_botones():
    r = {}
    for b in env("FORJA_MAPA_BOTONES").split():
        a, x, y = b.split(",")
        r[int(a)] = (int(x), int(y))
    return r


def mp_boton(accion, veces=1, pausa=0.25):
    zx, zy = zona_ext(PREF_MAPAS, "FORJA_MAPAS_LIENZO")
    x, y = mp_botones()[accion]
    p.mover_a(zx + x, zy + y, 0.6); time.sleep(0.2)
    for _ in range(veces):
        p.clic(); time.sleep(pausa)


def mp_caja(tile_accion, c1, c2):
    """La herramienta caja (B) con un tile del panel (su acción: 1000 + tile, o 2000 + tipo de choque)."""
    mp_boton(tile_accion); time.sleep(0.3)
    letra("b")
    arrastrar(mp_celda(*c1), mp_celda(*c2), 0.8)


def mp_lapiz(tile_accion, celdas):
    mp_boton(tile_accion); time.sleep(0.3)
    letra("p")
    for c in celdas:
        uno(*mp_celda(*c), 0.35)


def nivel_fondo():
    """La capa 0: hierba con la caja, la tierra con el relleno, una plataforma y una pared de ladrillo."""
    mp_boton(5000); time.sleep(0.6)
    mp_caja(1001, (0, 12), (21, 12))
    mp_boton(1002); time.sleep(0.3)
    letra("f")
    uno(*mp_celda(6, 14), 0.6); time.sleep(1.5)
    mp_caja(1003, (7, 8), (10, 8))
    mp_caja(1003, (15, 10), (16, 11))


def nivel_delante():
    """Una capa nueva delante: nubes y monedas."""
    mp_boton(5001); time.sleep(0.6)
    mp_boton(6200); time.sleep(1.0)
    mp_boton(5000); time.sleep(0.6)
    mp_lapiz(1005, [(3, 3), (12, 2), (18, 4)])
    mp_lapiz(1006, [(8, 6), (9, 6), (10, 6)])


def nivel_choques():
    """Otra capa, de choques: el suelo y la pared sólidos, la plataforma."""
    mp_boton(5001); time.sleep(0.6)
    mp_boton(6200); time.sleep(1.0)
    mp_boton(6204); time.sleep(1.0)
    mp_boton(5000); time.sleep(0.6)
    mp_caja(2001, (0, 12), (21, 15))
    mp_caja(2001, (15, 10), (16, 11))
    mp_caja(2002, (7, 8), (10, 8))


def nivel_objetos():
    """El jugador y un enemigo."""
    mp_boton(5003); time.sleep(0.6)
    mp_boton(7000); time.sleep(0.4)
    uno(*mp_celda(1, 10), 0.6); time.sleep(0.8)
    mp_boton(7001); time.sleep(0.4)
    uno(*mp_celda(19, 10), 0.6); time.sleep(0.8)


def antena_torcida():
    """En el segundo fotograma, la antena se tuerce: se borra (color 0) y se pinta inclinada. Así la piel de cebolla
    tiene algo que enseñar: la antena de antes, en puntos."""
    letra("0"); letra("l")
    arrastrar(sp_celda(15, 7), sp_celda(15, 3), 0.4)
    letra("p")
    for x, y in ((14, 2), (15, 2), (16, 2), (15, 1)):
        uno(*sp_celda(x, y), 0.2)
    letra("6"); letra("l")
    arrastrar(sp_celda(15, 7), sp_celda(18, 4), 0.5)
    letra("8"); letra("p")
    for x, y in ((18, 3), (19, 3), (20, 3), (19, 2)):
        uno(*sp_celda(x, y), 0.2)


def prefs():
    """La ventana de preferencias de Forja (su título cambia con el idioma; es pequeña y lleva "Forja")."""
    for w in amiga.ventanas():
        if "Forja" in w[1] and w[1] != "Forja" and w[4] < 500:
            return w[1:]
    return None
