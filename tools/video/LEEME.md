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

## El vídeo de Forja 0.8 (lo nuevo)

Mismas herramientas, con estas diferencias (todo en `*08*` o con un interruptor):
- `preparar.py es|en`: Amiberry 8.5 necesita `env -u WAYLAND_DISPLAY` y `-G` (si no, el Workbench se queda en AGA; la
  tarjeta gráfica con `gfxcard_type` sigue valiendo), el modo RTG 1280x1024 es ahora el 0x50071302 (se pone en
  `ENVARC:Sys/screenmode.prefs`), `sound_output=exact` (sin sonido el reloj de la música no avanza y las pistas de
  sincronía no se mueven; con `SDL_AUDIODRIVER=dummy` no suena nada) y el paquete es `dash-2.17.0-amiga.lha`. El Coffin
  ya tenía Dash: el instalador pregunta "¿Lo pongo al día?". MiniGL se copia a `LIBS:` de la copia del disco.
- `agente.c`: órdenes 4 y 5 (tecla solo pulsada o solo soltada) para mantener Ctrl, Alt o Mayúsculas de verdad
  (`agente.combo`). Amiga-M no cambia de pantalla desde el agente: el botón de profundidad (1267, 10).
- `guion08.py` (`DESDE=capítulo HASTA=capítulo`; cada capítulo sigue aunque falle el anterior), `locuciones08_*.json`,
  `textos08.py` (`VIDEO_TEXTOS=textos08 VIDEO_VOZ=voz08 python3 montar.py ...`), `servidor_inferencia.py` (servidor de
  pruebas de Inferencia con las respuestas escritas de antemano, puerto 40977; sus guiones en
  `~/.cache/video-forja/guiones`), `hojas.py` (hojas de contacto de una toma, para revisarla).
- Los campos de texto de MUI salen con la letra negra sobre negro en este Coffin (se escribe, no se ve): por eso el
  proyecto nuevo se crea por ARexx (`NUEVOPROYECTO`) y las búsquedas de la ayuda se limpian con Amiga-X.
- Los programas con pantalla propia (el juego de la plantilla, el cubo) se acaban con `Break` (`parar_programa`):
  con Esc (que parece llegarle también a Forja) Forja se cerró dos veces; no se ha investigado.
- Inferencia del paquete 2.17 es anterior al copiloto (no entiende `ENCARGO`): se copia la compilada del repositorio.
- Arreglado después (ramas `arreglos-video` de Dash y Forja): el Esc lo convertía en cerrar la ventana una commodity
  de CoffinOS (Dash ya no cierra tras un Esc de una zona con teclas: `tests/esc.sh` con `COFFIN=1`); los campos negros
  eran de `mui_app_field_colors` con MUI 3.8 (ya no se pone ahí); Ctrl / con el mapa castellano (Mayúsculas+6) y
  Arreglar el error en Ctrl Alt G (Ctrl Alt F se la queda una commodity, como Ctrl Alt T, A, flechas y Espacio); los
  sprites sueltos tras Break; el paquete rehace Inferencia.
