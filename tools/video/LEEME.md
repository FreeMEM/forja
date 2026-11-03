# El vídeo de Forja

El vídeo tutorial de Forja, en castellano y en inglés, grabado en Coffin R65 (Amiberry, RTG a 1280x1024) con la
voz del usuario clonada en pegaso. Las herramientas salen de las del vídeo de Trasfondo y de Tachyon
(`~/Projects/trasfondo/tools/video`): socket de Amiberry, agente dentro del Amiga, piloto del ratón, `Rodaje`.

- `preparar.py es|en`: una copia de Coffin con reflink en `~/.local/share/video-forja` (tiene que ir en el disco
  del original: `~/.cache` está en otro), un Traspaso propio en `~/.cache/video-forja/traspaso` con el paquete de
  Dash publicado (que trae Forja), el idioma de Locale de la toma, Amiberry en Xvfb `:80` y el agente.
  `preparar.py mirar` dice qué tiene ese Coffin de Dash y de Forja.
- `locuciones_es.json`, `locuciones_en.json`: lo que dice la voz, por claves. `locutar.py` (en pegaso, con
  OmniVoice y el perfil "FreeMEM voz" de VoiceStudio) hace un WAV por clave y `duraciones.json`.
- `pasos.py`: los pasos medidos (instalar, abrir Forja, teclear código, guardar...). `guion.py`: la toma.
  `rodaje.py` apunta subtítulos, voces, capítulos, clics y acercamientos con su hora; `montar.py` hace el vídeo.

Lo aprendido:
- LhA escrito en una Shell: el salto de línea va como tecla Return aparte (`agente.tecla`), no dentro del texto.
- El editor de Forja deja en cada línea nueva la sangría de la anterior, y su Retroceso quita un nivel entero.
- El Path que el instalador pone en S:User-Startup no llega al Workbench en marcha: por eso el instalador de Dash
  escribe `ENV:Forja/dashc`. El cajón instalado se abre con el ARexx del Workbench (`WINDOW ... OPEN`).
- La petición de guardar de ASL: con la ruta entera en File, el primer Return la reparte en Drawer y File; el
  segundo guarda.
