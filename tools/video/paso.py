"""paso.py x y nombre [veces]: clic relativo a la ventana Instalar (o absoluto si x<0) y captura recortada."""
import sys, time, amiga, piloto as p
from amiberry import orden
from PIL import Image
x, y, nombre = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
tit = sys.argv[4] if len(sys.argv) > 4 else "Instalar"
v = amiga.ventana(tit)
p.mover_a(v[2] + x, v[3] + y); p.clic(); time.sleep(2.5)
for w in amiga.ventanas(): print(w[1:])
f = f"/home/freemem/.cache/video-forja/ver/{nombre}.png"
orden("SCREENSHOT", f)
w = amiga.ventana(tit)
if w: Image.open(f).crop((w[2] - 10, w[3] - 10, w[2] + w[4] + 10, w[3] + w[5] + 10)).save(f.replace(".png", "c.png"))
