"""Una hoja de contacto de un tramo de una toma: python3 tramo.py <toma> <desde> <hasta> <cada> <ancho> [salida.png]"""
import os, subprocess, sys
from PIL import Image
toma, a, b, cada, ancho = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
salida = sys.argv[6] if len(sys.argv) > 6 else "/tmp/claude-1000/tramo.png"
import json
vi = json.load(open(os.path.join(toma, "toma.json")))["video_inicio"]
ims = []
t = a
while t <= b and len(ims) < 12:
    f = f"/tmp/claude-1000/tr_{len(ims)}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(max(0, t - vi)), "-i", os.path.join(toma, "toma.mkv"), "-frames:v", "1", "-vf", f"scale={ancho}:-1", f], check=True)
    ims.append(Image.open(f)); t += cada
w, h = ims[0].size
cols = 3
rows = (len(ims) + cols - 1) // cols
S = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(ims):
    S.paste(im, ((i % cols) * w, (i // cols) * h))
S.save(salida)
print(len(ims))
