# Editor de sprites de Forja (para `/loop`)

Arranque:

```
/loop Sigue las instrucciones de docs/SPRITES_LOOP.md (en ~/Projects/forja-sprites; si aún no existe, el de ~/Projects/forja): haz UNA tarea y actualiza la bitácora. No hagas pausas entre vuelta y vuelta
```

## Objetivo

Pedido por el usuario (2026-11-02): "una herramienta para dibujar/animar sprites" en Forja, dentro del plan de
hacer de Forja el mejor IDE del Amiga también para juegos y demos. Después, con las mismas piezas, un editor de
mapas de tiles (el usuario preguntó por él; bloque F).

Lo que tiene que salir:
- Una pestaña más del editor, como la del editor de ventanas: dibujar con zoom, paleta, fotogramas y la
  animación en marcha.
- Lo que se guarda lo cargan **tal cual** `sprite_load` y `bob_load` de Dash, y también DPaint y PPaint.
- Lo que le falte a Dash para usar bien esos ficheros sale como builtins nuevos (bloque E).

## Datos de partida (comprobados el 2026-11-02)

**Forja** (main, 4d6fb20): F1 a F9 hechas; `PLAN.md` y `docs/PUBLICAR.md`. Escrito en Dash 2.0.1; se compila
con `~/Projects/FreeMEMLang/dash src/main.dash -o Forja` (Dash en main, b2cc3ba; tarda menos de un segundo).

Por dónde se engancha (el editor de ventanas `diseno.dash` es el modelo a seguir):
- `struct Documento` en `src/editor.dash:49`. Se crea solo en `ed_abrir_texto` (`editor.dash:118`).
- Dibujo: `ed_dibujar` (`editor.dash:1174`) desvía a `dv_dibujar` si `d.diseno`. Para dibujar una parte usa
  `mui_canvas_updating()` con `ed_solo_linea` y `mui_canvas_update_area` (`main.dash:698`).
- Ratón y teclas: `en_editor` (`main.dash:821`). El arrastre llega como `EV_ARRASTRE` al bucle principal
  (`main.dash`, al final). El menú Edición va por `edicion` (`main.dash:729`) y los atajos por `atajo`
  (`main.dash:806`).
- Ficheros: `abrir` (`main.dash:164`, lee texto), `guardar_en` / `guardar_como` (`main.dash:179`), menú Proyecto
  en `proyecto()` (`main.dash:220`, eventos 30 a 34). El panel del proyecto solo lista `.dash` y `.dashui`
  (`proyecto_leer`, `paneles.dash:50`). La sesión guarda las rutas (`main.dash:1006`).
- Compilar (`main.dash:326`) compila el documento activo: desde una pestaña de sprite no debe compilar el IFF.
- Hay **un solo temporizador** de MUI: todo pasa por `armar_tic` / `tic()` (`main.dash:366`). La bienvenida
  parpadea con él mirando `time_ms()`; la animación debe hacer lo mismo.
- El lienzo del editor ya está con `mui_canvas_buffered` (`main.dash:1268`).
- Colores: `tema.dash`, con `color_pen(r, g, b)`.
- Textos: `tr(n, "...")`. En los `.dash` se usan hasta el 77; en `ventana.dashui` hasta el 351; del 400 al 442
  son de lib/red. `tools/catalogos.py cd|ct|catalog` rehace `catalogos/Forja.cd` y `english.ct`.
- Menús de `ventana.dashui`: Amiga + N O S W Q K E G I Z R X C V A F L D P ya están cogidas; libres B, H, J, M,
  T, U, Y.

**Dash** (lo que leen y escriben sus builtins, en `compiler/codegen.py`):
- `sprite_load(id, fichero)` (`_dash_sprite_load_file`): lee con datatypes; fotogramas de **16 píxeles** uno al
  lado del otro, tan altos como la imagen; usa los lápices 0-3 (uno mayor cuenta por sus dos bits bajos). **No
  lee el CMAP**: los colores se ponen con `sprite_color(id, i, r, g, b)`, con componentes de **4 bits** (SetRGB4,
  colores 17-19 para la pareja 0) y solo en una pantalla propia del programa.
- `bob_load(id, fichero)` (`_dash_bitmap_load` y `_dash_bob_setup`): lector propio de ILBM (BMHD, CMAP, BODY sin
  comprimir o ByteRun1, de 1 a 8 planos). No admite masking 1 (un plano de máscara de más). Solo ve varios
  fotogramas si **ancho > alto y ancho % alto == 0**, es decir, con fotogramas cuadrados. El color 0 es
  transparente.
- `bitmap_save` escribe ILBM sin comprimir, con el CMAP de la pantalla.
- `mui_canvas`: solo da el **botón izquierdo** (`mui_canvas_button` 1). Trae teclas con calificadores, rueda y
  arrastre (`mui_canvas_drag`: 1 moviéndose, 2 al soltar).
- `color_pen` usa ObtainBestPen con PRECISION_IMAGE y guarda los lápices. En el Workbench de 4 colores todos los
  colores del sprite se quedan en esos 4: para verlos hay que usar `RTG=1` (256 colores) en las capturas.
- Probado en el emulador: una lista de `[[Int]]` comparte sus elementos (`p = s.fotos[0]` y cambiar `p` cambia
  `s.fotos`); una porción `l[0:n]` copia. `buffer_alloc`, `file_open/read/write` y los bits (`<< >> & |`)
  funcionan.
- Ya existe `blixel/blixel.dash` en Dash: un editor de píxeles con ReAction y formato propio (BLX). No se
  reutiliza, porque Forja va con MUI y en ILBM, pero se puede mirar.

**Pruebas:** como las demás de `tests/` (`LEEME.md`). Un programa de Dash hace de usuario con `input_key`,
`input_text`, `input_click(x, y, teclas)` (4 = Alt), `input_drag` e `input_menu`, y lee la sonda
(`ENV:FORJA_SONDA`, `RAM:forja-sonda.txt`). Los diálogos ASL no se prueban solos. Emulador:
`~/Projects/FreeMEMLang/tools/emu_run.py`; sistemas en `~/.cache/dash-emu/` (`sys31muisslweb`, `sys32rtg8`).

## Diseño (propuesto; se puede cambiar en la tarea que toque, apuntándolo aquí)

- **Fichero:** IFF ILBM con los fotogramas uno al lado del otro.
  - BMHD con masking 2 (color transparente 0) y CMAP con 2^planos colores.
  - GRAB para el punto de agarre.
  - Un trozo propio `FRJA` en texto: versión, tipo, ancho del fotograma y velocidad. Los demás programas se lo
    saltan.
  - Se escribe sin comprimir. Se lee también ByteRun1 y masking 1.
  - Sin `FRJA` (un pincel de DPaint), los fotogramas se cuentan con la regla de `bob_load`.
  - Extensiones: `.iff`, `.ilbm`, `.lbm`, `.brush`, `.bob` y `.spr`. Al abrir, se mira también si empieza por
    "FORM....ILBM".
- **Dos tipos:**
  - Sprite de hardware: 16 de ancho, 2 planos, color 0 transparente.
  - BOB: de 1 a 256 de ancho y alto, de 1 a 8 planos.
  - Pasar de uno a otro (T) recorta o rellena con deshacer.
- **Código:** `src/sprites.dash`, con el prefijo `sp_`, importado desde `editor.dash` como `diseno.dash`.
  - `Documento` gana `sprite: Sprite` (nil en los de texto) y `lineas = [""]`.
  - `struct Sprite`: ancho y alto del fotograma, planos, si es de hardware, paleta (256 RGB), `fotos: [[Int]]`,
    el fotograma actual, color, herramienta, velocidad (tics de 1/50 s), cebolla, agarre, deshacer y rehacer.
- **Deshacer:** un `Paso` guarda solo el fotograma tocado. Si cambia la estructura (fotogramas, tamaño, planos,
  paleta), guarda todo. Como mucho 50 pasos.
- **Pantalla de la pestaña:**
  - Rejilla con zoom en el centro. El color 0 sale como fondo del tema. Líneas de rejilla con zoom de 6 o más.
    Se dibuja por tramos del mismo color para ir rápido.
  - Panel a la derecha: herramientas, paleta, barras R G B, vista animada, tamaño y botones.
  - Tira de fotogramas abajo, con un "+" al final. Barra de estado con la posición, el tamaño, el fotograma, el
    color y los avisos.
  - Los botones del lienzo se apuntan al dibujar: rectángulo y acción, y un clic los busca.
- **Ratón:**
  - Clic y arrastre con la herramienta: lápiz, línea, caja, relleno, cuentagotas o agarre.
  - Alt + clic pinta con el color 0, porque no hay botón derecho.
  - Ctrl + clic coge el color.
  - Mientras se arrastra, solo se redibujan las celdas tocadas (como `ed_solo_linea`); al soltar, todo.
  - La rueda cambia de fotograma.
- **Teclas, sin Amiga:**

  | Teclas | Qué hacen |
  |---|---|
  | P, L, B, F, K, A | Herramientas: lápiz, línea, caja, relleno, cuentagotas, agarre |
  | Izquierda / derecha | Fotograma anterior o siguiente |
  | Alt + izquierda / derecha | Mover el fotograma |
  | Arriba / abajo, 0 a 9 | Elegir color |
  | Mayúsculas + flechas | Desplazar el dibujo, dando la vuelta |
  | Ctrl + flechas | Cambiar ancho y alto |
  | N, D, Supr, Retroceso | Fotograma nuevo, duplicar, quitar y vaciar |
  | H, V | Espejo horizontal y vertical |
  | O | Piel de cebolla |
  | Espacio | Reproducir y parar |
  | + / - | Velocidad |
  | T | Tipo |
  | C | Código |

- **Menús:**
  - Amiga-Z / R: deshacer y rehacer.
  - Amiga-C / X / V: copiar, cortar y pegar fotogramas, dentro de Forja.
  - Amiga-S: guardar.
  - Amiga-B, "Nuevo sprite...": pregunta `_Sprite|_BOB|_Cancelar`.
- **Animación:** `tic()` calcula el fotograma con `time_ms()` y redibuja solo la vista. Si sigue reproduciendo,
  el bucle principal vuelve a armar el tic, igual que con la bienvenida.
- **Código (C):** copia al portapapeles las líneas de Dash para usarlo: `sprite_load` y `sprite_color` (en 4
  bits), o `bob_load` y `gfx_rgb8`, y `sprite_frame` / `bob_frame` con la velocidad. Avisa si un BOB con varios
  fotogramas no los tiene cuadrados.
- **Sonda para las pruebas:**
  - En `RAM:forja-sonda.txt`, la primera línea es "ancho alto planos hardware fotos actual color herramienta
    velocidad". Después, cada fila de cada fotograma en cifras hexadecimales.
  - `ENV:FORJA_SPRITE`: "x y zoom" de la rejilla, desde la esquina de la zona.

## Reglas de cada iteración

0. **Uso.** Lee `~/.claude/state/uso-7d.txt` (el primer número es el % de uso semanal). Con 90 o más: para el loop
   (ScheduleWakeup stop), apunta en la bitácora dónde quedó y avisa al usuario. Excepción: el 2026-11-02 el
   usuario autorizó seguir hasta que se renueve la cuota (hacia las 23:10); hasta las 23:30 de ese día no se para.
1. **Rama.** Trabaja en el worktree `~/Projects/forja-sprites`, rama local `sprites`. No toques `main` ni
   `~/Projects/forja`, salvo en la tarea 1. No hagas push. Para Dash (bloque E): worktree
   `~/Projects/FreeMEMLang/.worktrees/forja-sprites`, rama `forja-sprites` desde main. No toques los demás
   worktrees de Dash (`dashweb`, `ide-piezas`, `optimizar`) ni su main.
2. **Base.** Compila Forja (`~/Projects/FreeMEMLang/dash src/main.dash -o` al scratchpad). Anota si deja de
   compilar.
3. **Tarea.** Coge la primera `[ ]` y márcala `[~]` mientras trabajas. Una por iteración. Si es grande, divídela
   en la lista y haz la primera parte.
4. **Hacer.**
   - Cada cambio con su prueba en el emulador: `tests/sprites*.sh` y `.dash`, con "TODO BIEN" al final.
   - Lo visual se comprueba con capturas `RTG=1` (256 colores) mirándolas con Read. Las capturas van al
     scratchpad.
   - Estilo del código y de los comentarios: el de Forja (castellano llano, comentarios cortos).
5. **Verificar.**
   - Pasan las pruebas nuevas y las de Forja que puedan romperse: `teclas`, `ficheros` y `diseno`. Las que
     necesitan dashc para el Amiga, si está a mano.
   - Antes de una tanda larga en el emulador, mira con ListAgents si otra sesión lo está usando. Mata solo
     procesos tuyos, por PID.
6. **Documentar.** README (es y en), `tests/LEEME.md` y la ayuda de la cabecera de `main.dash` cuando cambie lo
   que ve el usuario.
7. **Cerrar.** Marca `[x]`, escribe la entrada en la bitácora y haz un commit local `sprites: <tarea> - <resumen>`
   (`dash: ...` en el worktree de Dash).
8. **Fin.** Sin tareas `[ ]`: resumen final, para el loop y avisa con PushNotification.

## Límites

- Sin `@native` en Forja: solo Dash y sus builtins. Lo que falte se pide a Dash en el bloque E.
- No instales paquetes del sistema. Python solo para herramientas de prueba (`tests/iff.py`), sin dependencias.
- Nada de ficheros binarios en el repo: las imágenes de prueba las crea `tests/iff.py`.
- Los ficheros que guarda Forja tienen que cargarse con `bob_load` y `sprite_load` de Dash. Se comprueba en las
  pruebas, no se supone.
- No cambies el formato `.dashui` ni lo que ya hacen las otras pestañas.
- Los builtins nuevos de Dash, con sus tests y `docs/BUILTINS.md` al día (`tools/gen_builtins_doc.py`), en los
  dos caminos de `./dash` (directo a hunk y `--gcc`), según `AGENTS.md` de Dash. Fusionarlos en main de Dash lo
  decide el usuario: déjalo `[?]`.
- Si una tarea exige una decisión del usuario, déjala `[?]` con la pregunta y pasa a la siguiente.

## Tareas

### A. Base
- [x] 1. **Arranque.** Crea el worktree `~/Projects/forja-sprites` (rama `sprites` desde main) y mueve allí este
      fichero, quitándolo de `~/Projects/forja`; commit. `src/sprites.dash` con `struct Sprite`, `struct Paso`,
      `sp_nuevo(hardware)`, paletas por defecto y acceso a píxeles. `Documento.sprite` y `ed_abrir_sprite`.
      `tests/iff.py`: escribe y lee ILBM (con ByteRun1 y sin él) para crear y comprobar ficheros de prueba.
- [ ] 2. **Leer y escribir ILBM.** `sp_leer(ruta)` y `sp_escribir(s, ruta)`: BMHD, CMAP, GRAB, FRJA, BODY,
      ByteRun1 y masking 1 al leer. Prueba en el emulador: ida y vuelta; un pincel comprimido de `iff.py` sin
      FRJA; `bob_load` y `sprite_load` (en una pantalla propia) cargan lo escrito; `iff.py` compara los píxeles.
- [ ] 3. **En Forja.**
      - Abrir por extensión o por contenido, también desde el panel del proyecto y la sesión.
      - Guardar y guardar como (patrón de imágenes).
      - Amiga-B "Nuevo sprite..." con su petición.
      - Compilar desde una pestaña de sprite compila el `.dash` del proyecto (`main.dash` o el primero abierto).
      - Inferencia y Amiga-D avisan.
      - Cerrar y salir con cambios preguntan, como con el texto.

### B. Dibujar
- [ ] 4. **Rejilla.** Zoom que llena la zona, tramos, color 0, líneas de rejilla, barra de estado,
      `ENV:FORJA_SPRITE`. Mide el dibujo entero con `REAL=1` (A1200, 68020 a 14 MHz) para 16x16, 32x32 y 64x64,
      y apúntalo aquí. Si 32x32 pasa de 200 ms, busca cómo bajarlo antes de seguir.
- [ ] 5. **Lápiz.** Clic y arrastre con líneas entre puntos (sin huecos), Alt + clic con el color 0, Ctrl + clic
      coge el color. Mientras se arrastra, solo las celdas tocadas. Deshacer y rehacer por trazo.
- [ ] 6. **Paleta.**
      - Elegir con un clic, con arriba y abajo, o con las cifras.
      - Barras R G B con clic y arrastre, en pasos de 4 bits si es sprite de hardware.
      - Deshacer de la paleta.
      - Comprobar qué pasa con los lápices al mover mucho una barra en 256 colores (ObtainBestPen) y apuntarlo.
- [ ] 7. **Herramientas.** Línea, caja, relleno (4 vecinos, sin recursión), cuentagotas y agarre (con su cruz).
      Línea y caja se ven mientras se arrastra. Botones en el panel.
- [ ] 8. **Tamaño y tipo.** Ancho, alto y planos (Ctrl + flechas y botones), con recorte o relleno y deshacer.
      T cambia de tipo; a sprite de hardware recorta a 16 de ancho y quita planos.

### C. Animar
- [ ] 9. **Fotogramas.** Tira de miniaturas (con zoom 2, 1 o muestreo si son altas) y "+". Nuevo, duplicar,
      quitar, mover, vaciar, espejo H y V, desplazar con Mayúsculas + flechas, y copiar, cortar y pegar fotogramas.
- [ ] 10. **Piel de cebolla.** Los píxeles del fotograma anterior como un punto en el centro de la celda vacía.
- [ ] 11. **Vista animada.** A tamaño real (y al doble si cabe), con velocidad, Espacio y botones, por `tic()`
      sin estorbar a compilar ni a la bienvenida. Al cambiar de pestaña se para sola.
- [ ] 12. **Código.** C y el botón: las líneas de Dash al portapapeles y un aviso en la salida. Prueba: compilar
      y ejecutar ese código con dashc carga el fichero.

### D. Pruebas y acabado
- [ ] 13. **Usuario de prueba completo.** `tests/sprites.sh` y `tests/sprites.dash`: abrir el pincel de
      `iff.py`, dibujar, rellenar, deshacer, fotogramas, guardar con Amiga-S, comprobar con `bob_load` y
      `iff.py`. Después, nuevo BOB con Amiga-B y salir descartando. Capturas `RTG=1` para el README.
- [ ] 14. **Acabado.** Catálogo (`tools/catalogos.py cd` y `ct`, con las traducciones al inglés), README es y en,
      `tests/LEEME.md`, `PLAN.md` (fase nueva) y el paquete (`tools/paquete.py`) si hace falta.

### E. Piezas de Dash (builtins nuevos, en el worktree de Dash)
- [ ] 15. **BOB con fotogramas de cualquier ancho:** `bob_frame_width(id, ancho)`, o que `bob_load` lea el ancho
      de `FRJA`. Decide cuál, con su test y su doc. Forja deja de avisar por los fotogramas no cuadrados.
- [ ] 16. **Colores de 8 bits para sprites en AGA:** `sprite_rgb8(id, i, r, g, b)` (SetRGB32).
- [ ] 17. **Colores del fichero:** `sprite_load_colors(id, fichero)` y `bob_load_colors(fichero, desde)` toman el
      CMAP. Así el código que genera Forja se queda en una línea.
- [ ] 18. **Sprites acoplados** (15 colores, parejas de sprites): `[?]` antes de empezar. Pregunta al usuario si
      lo quiere ya, porque cambia el formato y la herramienta.
- [ ] 19. Forja usa las piezas que se fusionen (`[?]` hasta que el usuario las lleve a main de Dash).

### F. Mapas de tiles (después de los sprites)
- [ ] 20. **Diseño.** Los tiles son un BOB de esta herramienta: fotogramas cuadrados, uno por tile. Formato del
      mapa (propuesta: texto con cabecera y filas de números, que se lee en Dash sin builtins), capas, tiles
      de 8, 16 o 32, y el builtin que pinta un trozo del mapa rápido (`tilemap_draw`). Escribe aquí el diseño
      y déjalo `[?]` para que el usuario lo vea antes de programar.

## Bitácora

### 2026-11-02 — Plan
- Pedido por el usuario: "Vamos a añadir a Forja una herramienta para dibujar/animar sprites", "sería interesante
  alguna herramienta en forja para mapas de juegos?" y "hay que elaborar prompt para loop".
- Investigado en esta sesión (ver "Datos de partida"). En Dash no hay AHI ni printer.device.

### 2026-11-02 — Tarea 1 (arranque)
- Worktree `~/Projects/forja-sprites`, rama `sprites` desde 4d6fb20. Forja compila con Dash main (b2cc3ba).
- `src/sprites.dash`: `Sprite`, `SpPaso` (el nombre `Paso` era muy corto para un módulo que se importa en todo
  Forja), `sp_nuevo`, `sp_paleta_inicial` (32 colores, cubo 6x6x6 y grises), `sp_px`/`sp_poner`, `sp_apuntar`,
  `sp_deshacer`, `sp_rehacer`. La lista de colores es `var` porque `const` solo admite números.
- `Documento.sprite` (nil en los de texto) y `ed_abrir_sprite` en `editor.dash`.
- `tests/sprites_base.sh`: TODO BIEN en FS-UAE (13 comprobaciones). `tests/iff.py prueba`: TODO BIEN (con y sin
  ByteRun1, con y sin plano de máscara, FRJA y GRAB).
