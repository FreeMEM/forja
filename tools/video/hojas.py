"""Hojas de contacto de una toma, para revisarla: python3 hojas.py <toma> <cada_n_segundos> <ancho> -> /tmp/.../hoja_N.png"""
import glob, os, subprocess, sys
from PIL import Image
toma, cada, ancho = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
d = f"/tmp/claude-1000/hojas_{os.path.basename(toma.rstrip('/'))}"
os.makedirs(d, exist_ok=True)
for f in glob.glob(d + "/f*.png"):
    os.remove(f)
subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(toma, "toma.mkv"), "-vf", f"fps=1/{cada},scale={ancho}:-1", d + "/f%03d.png"], check=True)
fs = sorted(glob.glob(d + "/f*.png"))
cols, por = 3, 9
for h in range(0, len(fs), por):
    ims = [Image.open(f) for f in fs[h:h + por]]
    w, hh = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGB", (w * cols, hh * rows))
    for i, im in enumerate(ims):
        S.paste(im, ((i % cols) * w, (i // cols) * hh))
    S.save(f"{d}/hoja_{h // por}.png")
print(len(fs), "cuadros;", (len(fs) + por - 1) // por, "hojas en", d)
