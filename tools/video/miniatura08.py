"""La miniatura del vídeo de Forja 0.8: la de miniatura.py con su lema y su pie.

    python3 miniatura08.py <captura.png> en|es <salida.jpg> [x0,y0,x1,y1]"""
import sys

import miniatura as m

m.LEMA = {"en": ["WHAT IS NEW", "IN FORJA 0.8"], "es": ["LO NUEVO", "DE FORJA 0.8"]}
m.PIE = {"en": "Editor, git, AI copilot, demos, 3D", "es": "Editor, git, copiloto con IA, demos, 3D"}

if __name__ == "__main__":
    zona = tuple(int(v) for v in sys.argv[4].split(",")) if len(sys.argv) > 4 else (400, 200, 700, 440)
    m.miniatura(sys.argv[1], sys.argv[2], "0.8", zona).save(sys.argv[3], quality=92)
