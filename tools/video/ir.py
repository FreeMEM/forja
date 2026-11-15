"""Prueba: ir.py URL nombre segundos -> capturas cada 2 s en ver/nombre_N.png; dice cuándo deja de cambiar."""
import sys, time, hashlib
import piloto as p, agente
from amiberry import orden
url, nombre, tope = sys.argv[1], sys.argv[2], float(sys.argv[3])
agente.tecla(0x28, 0x80); time.sleep(0.3); agente.tecla(0x32, 0x80)   # Amiga-L y Amiga-X: la dirección, vacía
time.sleep(0.4)
agente.escribir(url); agente.tecla(0x44)
t0 = time.time(); prev = None; n = 0
while time.time() - t0 < tope:
    time.sleep(2)
    f = f"/home/freemem/.cache/video-forja/ver/{nombre}_{n}.png"
    orden("SCREENSHOT", f)
    h = hashlib.md5(open(f, "rb").read()).hexdigest()
    print(round(time.time() - t0, 1), "igual" if h == prev else "cambia")
    prev = h; n += 1
