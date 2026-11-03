"""Deja Coffin listo para una toma del vídeo de Forja, sin tocar el Coffin del usuario: una copia nueva del disco
(reflink), un Traspaso propio con el paquete de Dash publicado (que trae Forja), el idioma de Locale de la toma,
Amiberry en una pantalla virtual (Xvfb, que da los modos RTG) y el agente en marcha.

    python3 preparar.py en|es          # prepara y deja el agente esperando
    python3 preparar.py mirar          # arranca y escribe en Traspaso:mirar.txt lo que hay de Dash y Forja
"""
import glob
import os
import shutil
import subprocess
import sys
import time

import amiga
import agente
import piloto as p
from amiberry import orden

V = os.path.expanduser("~/.cache/video-forja")
IMAGEN = os.path.expanduser("~/.local/share/video-forja/coffin-video.img")   # en el disco del original (reflink)
ORIGINAL = os.path.expanduser("~/Amiberry/HardDrives/coffin_r65_32GB.img")
TRASP = os.path.join(V, "traspaso")
PANTALLA = ":80"
TRASPASO = (38, 250)          # el icono del escritorio de Coffin en RTG


def cerrar_amiberry():
    """Cierra el Amiberry de la toma anterior (por su PID, no por su nombre) y espera a que se vaya del todo."""
    fpid = os.path.join(V, "amiberry.pid")
    if os.path.exists(fpid):
        pid = int(open(fpid).read())
        try:
            orden("QUIT")
        except OSError:
            pass
        for _ in range(60):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.5)
        else:
            try:
                os.kill(pid, 9)
            except ProcessLookupError:
                pass
        os.remove(fpid)
    for f in glob.glob(os.path.join(V, "run", "amiberry*.sock")):
        os.remove(f)


def xvfb():
    """La pantalla virtual, más alta que la de Coffin (1280x1024) para que su ventana quepa entera."""
    if subprocess.run(["pgrep", "-f", f"Xvfb {PANTALLA} "], capture_output=True).returncode:
        subprocess.Popen(["Xvfb", PANTALLA, "-screen", "0", "2560x1600x24"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(2)


def arrancar():
    env = dict(os.environ, DISPLAY=PANTALLA, SDL_VIDEODRIVER="x11", SDL_AUDIODRIVER="dummy",
               XDG_RUNTIME_DIR=os.path.join(V, "run"))
    pr = subprocess.Popen(["amiberry", "-f", os.path.join(V, "video.uae"), "-s", "use_gui=no"], env=env,
                          stdout=open(os.path.join(V, "amiberry.log"), "w"), stderr=subprocess.STDOUT,
                          start_new_session=True)
    open(os.path.join(V, "amiberry.pid"), "w").write(str(pr.pid))
    t = time.time()
    while time.time() - t < 150:                 # hasta que el Workbench esté y quieto
        try:
            amiga._ib = None
            if "Workbench" in amiga.tareas():
                break
        except (OSError, AssertionError, RuntimeError):
            pass
        time.sleep(2)
    time.sleep(20)


def lanzar_agente():
    p.mover_a(*TRASPASO); p.clic(2)
    t = time.time()
    while not amiga.ventana("Traspaso") and time.time() - t < 15:
        time.sleep(0.3)
    time.sleep(1.5)
    v = amiga.ventana("Traspaso")
    time.sleep(2)
    for _ in range(4):
        p.mover_a(v[2] + 141, v[3] + 34); p.clic(2)   # el agente, a la derecha del cajón (medido)
        t = time.time()
        while not hay_agente() and time.time() - t < 8:
            time.sleep(0.5)
        if hay_agente():
            break
    p.cerrar("Traspaso")
    assert hay_agente(), "el agente no arrancó"


def hay_agente():
    """Su buzón (no la lista de tareas: el agente suele ser la tarea en marcha, que no está en ninguna lista)."""
    try:
        agente.buzon()
        return True
    except RuntimeError:
        return False


PAQUETE = "dash-2.2.0-amiga.lha"


def traspaso(lengua):
    shutil.rmtree(TRASP, ignore_errors=True)
    os.makedirs(TRASP)
    shutil.copy(os.path.join(V, "descargas", PAQUETE), TRASP)
    for f in ("agente", "agente.info"):
        shutil.copy(os.path.join(V, "agente", f), TRASP)
    if lengua in ("es", "en"):
        shutil.copy(os.path.join(V, "descargas", f"locale_{'english' if lengua == 'en' else 'espanol'}.prefs"),
                    os.path.join(TRASP, "locale.prefs"))


def mirar():
    """Lo que ya tiene este Coffin de Dash y de Forja (para quitarlo antes de la toma)."""
    cerrar_amiberry()
    xvfb()
    subprocess.run(["cp", "--reflink=always", ORIGINAL, IMAGEN], check=True)
    traspaso("mirar")
    arrancar()
    lanzar_agente()
    agente.lanzar("C:Which dash ALL >Traspaso:mirar.txt")
    agente.lanzar("C:List SYS: SYS:Utilities SYS:Tools SYS:Programs >>Traspaso:mirar.txt")
    agente.lanzar("C:Assign >>Traspaso:mirar.txt")
    agente.lanzar("C:Search SYS:S/User-Startup dash >>Traspaso:mirar.txt")
    time.sleep(6)
    print(open(os.path.join(TRASP, "mirar.txt"), encoding="latin-1").read())


def main(lengua):
    cerrar_amiberry()
    xvfb()
    subprocess.run(["cp", "--reflink=always", ORIGINAL, IMAGEN], check=True)
    traspaso(lengua)
    arrancar()
    lanzar_agente()
    # Lo que no sale en el vídeo: el idioma de la toma (y se arranca otra vez con él)
    agente.lanzar("C:Copy Traspaso:locale.prefs ENVARC:Sys/locale.prefs")
    agente.lanzar("C:Copy Traspaso:locale.prefs ENV:Sys/locale.prefs")
    time.sleep(2)
    agente.lanzar("C:List ENVARC:Sys/locale.prefs >Traspaso:hecho.txt")
    time.sleep(10)                               # que el disco lo escriba antes de cerrar Amiberry
    hecho = open(os.path.join(TRASP, "hecho.txt"), encoding="latin-1").read()
    assert "locale.prefs" in hecho, hecho
    os.remove(os.path.join(TRASP, "hecho.txt"))
    os.remove(os.path.join(TRASP, "locale.prefs"))
    cerrar_amiberry()
    arrancar()
    lanzar_agente()
    for f in ("agente", "agente.info"):
        os.remove(os.path.join(TRASP, f))
    p.mover_a(640, 600)
    print("listo:", lengua, hay_agente())


if __name__ == "__main__":
    if sys.argv[1] == "mirar":
        mirar()
    else:
        main(sys.argv[1])
