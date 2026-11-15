"""Locuciones con la voz clonada del usuario (perfil "FreeMEM voz" de VoiceStudio), con OmniVoice sin la app.

    HF_HUB_CACHE=.../datos/models HF_HUB_OFFLINE=1 python locutar.py frases.json salida/ es|en

frases.json: {"clave": "texto", ...}. Escribe salida/<clave>.wav (24 kHz) y salida/duraciones.json. Se salta las que
ya tienen su WAV con el mismo texto (salida/<clave>.txt).
"""
import json
import os
import sqlite3
import sys

import numpy as np
import soundfile as sf
import torch
from omnivoice import OmniVoice

D = "/home/freemem/1TbSSD/VoiceStudio/datos"
REF = f"{D}/data/voices/d84e5976.wav"

frases = json.load(open(sys.argv[1], encoding="utf-8"))
out, lengua = sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
con = sqlite3.connect(f"{D}/data/omnivoice.db")
ref_text = None
for fila in con.execute("select * from voice_profiles"):
    if any(isinstance(c, str) and "d84e5976" in c for c in fila):
        cols = [d[0] for d in con.execute("select * from voice_profiles").description]
        f = dict(zip(cols, fila))
        ref_text = f.get("ref_text") or f.get("reference_text") or f.get("transcript")
        break
print("texto de referencia:", (ref_text or "")[:80])
pendientes = {k: t for k, t in frases.items()
              if not (os.path.exists(f"{out}/{k}.wav") and os.path.exists(f"{out}/{k}.txt")
                      and open(f"{out}/{k}.txt", encoding="utf-8").read() == t)}
dur = {}
if os.path.exists(f"{out}/duraciones.json"):
    dur = json.load(open(f"{out}/duraciones.json"))
if pendientes:
    modelo = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda", dtype=torch.float16)
    sr = int(getattr(modelo, "sampling_rate", 24000))
    for k, t in pendientes.items():
        a = modelo.generate(text=t, ref_audio=REF, ref_text=ref_text, language=lengua)
        a = a[0] if isinstance(a, (list, tuple)) else a
        x = np.asarray(a.detach().to("cpu").float().numpy()).squeeze()
        sf.write(f"{out}/{k}.wav", x, sr)
        open(f"{out}/{k}.txt", "w", encoding="utf-8").write(t)
        dur[k] = round(len(x) / sr, 2)
        print(k, dur[k], flush=True)
for k in frases:
    if k not in dur and os.path.exists(f"{out}/{k}.wav"):
        i = sf.info(f"{out}/{k}.wav")
        dur[k] = round(i.frames / i.samplerate, 2)
json.dump(dur, open(f"{out}/duraciones.json", "w"), indent=1)
