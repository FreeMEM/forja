"""Captura la pantalla del Amiga: python3 ver.py nombre  ->  ~/.cache/video-forja/ver/nombre.png"""
import os, sys
from amiberry import orden
d = os.path.expanduser("~/.cache/video-forja/ver"); os.makedirs(d, exist_ok=True)
f = os.path.join(d, sys.argv[1] + ".png"); print(orden("SCREENSHOT", f))
