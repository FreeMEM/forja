"""El servidor falso de Inferencia (tests/servidor_falso.py de su repositorio) con las respuestas escritas de antemano
para el vídeo: los encargos (cambiar, documentar, prueba, arreglar, completar) salen de guiones/encargo_<tipo>.json y
las preguntas de "Explicar" de guiones/conversacion.json.

    python3 servidor_inferencia.py GUIONES [puerto]      # 40977 por defecto
"""
import json
import os
import sys
from http.server import HTTPServer

sys.path.insert(0, os.path.expanduser("~/Projects/inferencia/tests"))
import servidor_falso as sf

GUIONES = sys.argv[1]
os.environ["INFERENCIA_GUIONES"] = GUIONES
CONV = json.load(open(os.path.join(GUIONES, "conversacion.json"), encoding="utf-8"))


class Video(sf.Falso):
    def _guion(self, mensajes):
        g = super()._guion(mensajes)
        if g:
            return g
        ultima = mensajes[-1]
        if ultima["role"] != "user":
            return None
        t = ultima.get("content") or ""
        if "Explica este error" in t:
            return [{"texto": CONV["explicar_error"]}], 0
        if t.startswith("Explica"):
            return [{"texto": CONV["explicar"]}], 0
        return None


if __name__ == "__main__":
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 40977
    HTTPServer(("127.0.0.1", puerto), Video).serve_forever()
