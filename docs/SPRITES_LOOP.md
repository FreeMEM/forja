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
6b. **Capturas al usuario** (lo pidió el 2026-11-03): cuando una vuelta cambia algo que se ve (en Forja o en un
   programa de prueba), saca una captura (`RTG=1`) y mándasela con SendUserFile, con una línea que diga qué es. Si
   la vuelta no tiene nada visible, cada tres o cuatro vueltas, la del estado del editor.
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
- [x] 2. **Leer y escribir ILBM.** `sp_leer(ruta)` y `sp_escribir(s, ruta)`: BMHD, CMAP, GRAB, FRJA, BODY,
      ByteRun1 y masking 1 al leer. Prueba en el emulador: ida y vuelta; un pincel comprimido de `iff.py` sin
      FRJA; `bob_load` y `sprite_load` (en una pantalla propia) cargan lo escrito; `iff.py` compara los píxeles.
- [x] 3. **En Forja.**
      - Abrir por extensión o por contenido, también desde el panel del proyecto y la sesión.
      - Guardar y guardar como (patrón de imágenes).
      - Amiga-B "Nuevo sprite..." con su petición.
      - Compilar desde una pestaña de sprite compila el `.dash` del proyecto (`main.dash` o el primero abierto).
      - Inferencia y Amiga-D avisan.
      - Cerrar y salir con cambios preguntan, como con el texto.

### B. Dibujar
- [x] 4. **Rejilla.** Zoom que llena la zona, tramos, color 0, líneas de rejilla, barra de estado,
      `ENV:FORJA_SPRITE`. Mide el dibujo entero con `REAL=1` (A1200, 68020 a 14 MHz) para 16x16, 32x32 y 64x64,
      y apúntalo aquí. Si 32x32 pasa de 200 ms, busca cómo bajarlo antes de seguir.
- [x] 5. **Lápiz.** Clic y arrastre con líneas entre puntos (sin huecos), Alt + clic con el color 0, Ctrl + clic
      coge el color. Mientras se arrastra, solo las celdas tocadas. Deshacer y rehacer por trazo.
- [x] 6. **Paleta.**
      - Elegir con un clic, con arriba y abajo, o con las cifras.
      - Barras R G B con clic y arrastre, en pasos de 4 bits si es sprite de hardware.
      - Deshacer de la paleta.
      - Comprobar qué pasa con los lápices al mover mucho una barra en 256 colores (ObtainBestPen) y apuntarlo.
- [x] 7. **Herramientas.** Línea, caja, relleno (4 vecinos, sin recursión), cuentagotas y agarre (con su cruz).
      Línea y caja se ven mientras se arrastra. Botones en el panel.
- [x] 8. **Tamaño y tipo.** Ancho, alto y planos (Ctrl + flechas y botones), con recorte o relleno y deshacer.
      T cambia de tipo; a sprite de hardware recorta a 16 de ancho y quita planos.

### H. Biblioteca de juegos y editor de escenas (pedido del usuario el 2026-11-02; va antes que C)
Pedido: "una biblioteca dash en plan pygame", "en el editor algo parecido a como se trabaja en godot, con el
sistema de jerarquías", "una estructura, un bucle de juego, un motor de físicas, un sistema de renderizado de
luces", "todo eso podría ir en una biblioteca aparte para hacer videojuegos". "Hay que diseñarlo bien o tratar de
copiar un poco sus formas de trabajar".
- [?] 26. **Diseño, sin código.** Hecho en `docs/JUEGOS_DISENO.md`. El usuario decidió 1 a 4 (Fragua, A1200, API en inglés, con modo que se adueña del hardware); falta la 5 (cómo se compilan las escenas). Escribe `docs/JUEGOS_DISENO.md` (castellano llano, como los demás docs):
      - **Cómo trabajan pygame y Godot**, de sus docs oficiales (WebFetch): en pygame display, Surface, Rect,
        sprite.Sprite y Group, event, time.Clock, mixer, font, transform y mask. En Godot el árbol de nodos y las
        escenas que se instancian, Node2D, Sprite2D, AnimatedSprite2D, TileMap, Camera2D,
        CharacterBody2D/RigidBody2D/Area2D con CollisionShape2D, señales, `_ready`/`_process`/`_physics_process`,
        AnimationPlayer, PointLight2D y CanvasModulate, y el inspector. Qué se copia y qué no, y por qué.
      - **El Amiga manda:** 68000 a 7 MHz como mínimo o 68020 a 14 MHz (decídelo con números: qué cabe en un
        fotograma de 50 Hz), coma fija (`Fixed`), memoria chip, blitter, copper, sprites de hardware, paleta
        (ECS/AGA) y RTG. Luces en una pantalla de paleta: tablas de sombreado (colormaps precalculadas), colores
        del copper, o mezcla en RTG. Físicas: AABB, tiles, cuerpos simples con pasos fijos; nada que no quepa.
      - **La biblioteca** (aparte de Forja y de Dash): capas (bucle de juego con paso fijo, render, entrada,
        sonido, físicas, luces, escenas), su API en Dash con ejemplos cortos, qué es Dash puro y qué pide
        builtins nuevos (lista, con los que ya salieron en este plan: 15b, 16, 17, 25 doble búfer).
      - **Escenas:** el formato del fichero (JSON como `.dashui`, propuesta), nodos y sus propiedades, scripts en
        Dash enganchados a nodos (cómo, sin intérprete: el compilador genera el código de la escena).
      - **En Forja:** el editor de escenas (árbol de nodos, inspector y la vista con el render de verdad, como
        el editor de ventanas) y cómo encaja con el editor de sprites y el de mapas (F).
      - **Fases** pequeñas, cada una con un juego de ejemplo que funcione.
      - **Decisiones para el usuario,** al final y en una lista: nombre y repo de la biblioteca, máquina mínima,
        y lo que haga falta.
      Déjala `[?]` al acabar: el usuario revisa el diseño antes de que se programe nada. El loop sigue con C.
- [?] 27. **Diseño de las herramientas de Forja por tipo de proyecto, sin código** Hecho en `docs/HERRAMIENTAS_DISENO.md`. Decidido por el usuario: `.forja` sí, el orden propuesto, iconos de 3.5 (ColorIcons) y Shrinkler si está instalado (recomendado por Claude). (pedido: "herramientas en forja
      específicas para hacer videojuegos, otras para demos y otras para aplicaciones de escritorio"). En
      `docs/HERRAMIENTAS_DISENO.md`:
      - **Proyecto con tipo:** un fichero de proyecto (`.forja`, ya en el plan) dice si es juego, demo o
        aplicación, y Forja enseña las herramientas de ese tipo, con una plantilla para empezar cada uno.
      - **Juegos:** sprites (este loop), mapas (F), escenas (26), y además vista de depuración (cajas de choque,
        velocidades), efectos de sonido, y memoria chip y fast mientras corre.
      - **Demos:** pistas de sincronía con la música (E8x, filas, línea de tiempo de escenas, editadas mientras la
        demo corre), editor de copper y degradados, medidor del coste por fotograma, vista del MOD, compresión del
        ejecutable (Shrinkler) y tamaño de 4K/64K a la vista.
      - **Aplicaciones de escritorio:** el editor de ventanas `.dashui` (ya está), catálogos de idiomas (editar
        `.cd`/`.ct`), iconos `.info`, guía AmigaGuide, puerto ARexx, script de Installer y el paquete para Aminet
        (`.readme`).
      - Qué hay ya en Forja y en Dash, qué es nuevo, qué builtins pide, y en qué orden (fases con algo que funcione
        en cada una). Decisiones para el usuario al final. `[?]` al acabar, como la 26.

### I. Juegos en 3D con MiniGL (pedido del usuario el 2026-11-02; va antes que lo que queda de C)
Pedido: "también vamos a crear juegos en 3D con minigl". Hay movimiento en el grupo de Amiga de Telegram: Santi
(DarkG) hace cosas con MiniGL y un modeler. Claude no puede leer Telegram: si el usuario pasa los mensajes
(exportados desde Telegram Desktop o pegados), se leen antes de escribir el diseño.
- [?] 28. **Diseño 3D, sin código.** Hecho en `docs/3D_DISENO.md`; falta que el usuario lo revise, decida lo de su sección 6 y pase los mensajes de Santi. En `docs/3D_DISENO.md`:
      - **Qué es MiniGL hoy en el Amiga clásico** (fuentes públicas, WebFetch/WebSearch, citadas): sobre qué va
        (Warp3D, Wazp3D por software, tarjetas 3D como Permedia2, Voodoo o Virge, Vampire, PiStorm/Emu68), qué
        versión, licencia, qué parte de OpenGL tiene y qué rinde en cada máquina. No afirmar nada sin fuente.
      - **Cómo lo usaría Dash:** builtins (`@extern` sobre minigl.library, como se hizo con otras bibliotecas) o
        una capa en Fragua; con qué formato de modelos (los que use el modeler de Santi, si se sabe; si es LightWave,
        su formato `.lwo` es público).
      - **Encaje con Fragua y Forja:** nodos 3D en las escenas (cámara, malla, luz) y una vista 3D en el editor.
      - **Lo que no se sabe** y lo que haría falta probar (en el emulador hay Wazp3D o no; en una máquina real).
      - Decisiones para el usuario al final. `[?]` al acabar.

### C. Animar
- [x] 9. **Fotogramas.** Tira de miniaturas (con zoom 2, 1 o muestreo si son altas) y "+". Nuevo, duplicar,
      quitar, mover, vaciar, espejo H y V, desplazar con Mayúsculas + flechas, y copiar, cortar y pegar fotogramas.
- [x] 10. **Piel de cebolla.** Los píxeles del fotograma anterior como un punto en el centro de la celda vacía.
- [x] 11. **Vista animada.** A tamaño real (y al doble si cabe), con velocidad, Espacio y botones, por `tic()`
      sin estorbar a compilar ni a la bienvenida. Al cambiar de pestaña se para sola.
- [x] 12. **Código.** C y el botón: las líneas de Dash al portapapeles y un aviso en la salida. Prueba: compilar
      y ejecutar ese código con dashc carga el fichero.

### D. Pruebas y acabado
- [x] 13. **Usuario de prueba completo.** `tests/sprites.sh` y `tests/sprites.dash`: abrir el pincel de
      `iff.py`, dibujar, rellenar, deshacer, fotogramas, guardar con Amiga-S, comprobar con `bob_load` y
      `iff.py`. Después, nuevo BOB con Amiga-B y salir descartando. Capturas `RTG=1` para el README.
- [x] 14. **Acabado.** Catálogo (`tools/catalogos.py cd` y `ct`, con las traducciones al inglés), README es y en,
      `tests/LEEME.md`, `PLAN.md` (fase nueva) y el paquete (`tools/paquete.py`) si hace falta.

### E. Piezas de Dash (builtins nuevos, en el worktree de Dash)
- [x] 15. **BOB con fotogramas de cualquier ancho:** `bob_frame_width(id, ancho)`, o que `bob_load` lea el ancho
      de `FRJA`. Decide cuál, con su test y su doc. Forja deja de avisar por los fotogramas no cuadrados.
- [x] 15b. **Pintar una imagen de lápices de golpe:** `gfx_pens_draw(buffer, ancho, alto, x, y, zoom)` (un byte por
      píxel con el lápiz; WriteChunkyPixels o WritePixelArray8, con zoom). La rejilla de 32x32 con píxeles al azar
      tarda 240 ms en un A1200 porque son unos 1000 RectFill desde Dash (tarea 4). Forja lo usaría sin zoom de
      rejilla y en las miniaturas.
- [x] 15c. **Soltar lápices:** `color_pen` guarda 128 lápices y, pasado el tope, devuelve uno que suelta en seguida
      (otro ObtainBestPen puede cambiarle el color en la pantalla). Un BOB de 256 colores ya pasa del tope, y mover
      una barra R G B pide un lápiz por cada valor. Pedir `color_pen_free(pen)` o `color_pens_reset()` para soltar
      los que ya no se usan (tarea 6).
- [x] 15d. **`gfx_rgb8` sin ventana cuelga el programa:** su C es `SetRGB32(&_dash_win->WScreen->ViewPort, ...)`
      (`compiler/amiga_builtins.py`). Con `screen_open_custom` y sin ventana, `_dash_win` es NULL. Usar la pantalla
      del programa (`_dash_screen`) si la hay, y no hacer nada si no hay ni ventana ni pantalla. Test con
      `screen_open_custom` + `gfx_rgb8` sin ventana. Mirar si otros builtins tienen el mismo `_dash_win->`.
- [x] 16. **Colores de 8 bits para sprites en AGA:** `sprite_rgb8(id, i, r, g, b)` (SetRGB32).
- [x] 17. **Colores del fichero:** `sprite_load_colors(id, fichero)` y `bob_load_colors(fichero, desde)` toman el
      CMAP. Así el código que genera Forja se queda en una línea.
- [x] 18. **Sprites acoplados** (15 colores, parejas de sprites). El usuario lo quiso ya (2026-11-03).
- [ ] 19. Forja usa las piezas que se fusionen. El usuario mandó fusionar el 2026-11-03.

### F. Mapas de tiles (después de los sprites)
- [x] 20. **Diseño** (hecho en `docs/MAPAS_DISENO.md`; el usuario aceptó las propuestas de su sección 6 el 2026-11-03). Los tiles son un BOB de esta herramienta: fotogramas cuadrados, uno por tile. Formato del
      mapa (propuesta: texto con cabecera y filas de números, que se lee en Dash sin builtins), capas, tiles
      de 8, 16 o 32, y el builtin que pinta un trozo del mapa rápido (`tilemap_draw`). Escribe aquí el diseño
      y déjalo `[?]` para que el usuario lo vea antes de programar.

### G. Pantallas propias (pedido del usuario el 2026-11-02, en el worktree de Dash)
Hoy hay `screen_open` (modo del Workbench con `SA_LikeWorkbench`, solo para ventanas de Intuition),
`screen_open_custom`, `rtg_open_screen` y `mui_window_own_screen` (copia la pública, pero solo para una ventana MUI
a pantalla completa). Lo que falta:
- [x] 21. **Clon del Workbench, público.** Una pantalla igual que la del Workbench (modo, tamaño, profundidad,
      colores, lápices y fuente), pública y con nombre. `screen_clone_wb(nombre)` o con opciones; que Intuition
      la cierre bien cuando aún tiene ventanas de otros (esperar o avisar). Test y doc.
- [x] 22. **Ventanas MUI normales en una pantalla pública:** `mui_window_screen(win, nombre)` (o
      `mui_app_screen(nombre)` para toda la aplicación). Prueba: una aplicación MUI con dos ventanas en el clon.
- [x] 23. **Elegir el modo:** la petición de modo de pantalla de ASL (`dialog_screen_mode`: modo, ancho, alto y
      profundidad) y `screen_open_mode(modo, ancho, alto, planos, título)` con un modo exacto (PAL 320x256 a 32
      colores, AGA, RTG).
- [ ] 24. **Forja en su pantalla:** preferencia para abrir Forja en un clon público del Workbench, y que los
      programas que ejecuta salgan ahí (`[?]` si depende de piezas sin fusionar).
- [ ] 25. **Doble búfer de pantalla** para juegos y demos (`AllocScreenBuffer`/`ChangeScreenBuffer`). Decidido el
      2026-11-03: va en Dash, y Fragua lo usa.

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

### 2026-11-02 — Tarea 2 (leer y escribir ILBM)
- `sp_escribir` y `sp_leer` en `src/sprites.dash`, con `sp_error` y los textos 80 a 86. Se escribe sin comprimir
  con masking 2, CMAP, GRAB y FRJA ("1 tipo ancho velocidad"). Se lee BMHD, CMAP, GRAB, FRJA y BODY, sin comprimir
  o ByteRun1, con el plano de máscara (masking 1) saltado; sin FRJA, la regla de `bob_load`.
- `tests/sprites_iff.sh`: TODO BIEN (14 en el Amiga y 3 de `iff.py` sobre lo escrito), con `bob_load` y
  `sprite_load` cargando el fichero de Forja.
- **Ojo:** las pruebas necesitan `DASH_KICKSTART="/home/freemem/Descargas/Telegram Desktop/ks31a1200.rom"`. Sin
  ella `emu_run.py` usa la ROM de AROS y `sprite_load` (datatypes) se queda colgado. No es de Forja; no se ha
  mirado más.
- El usuario pidió en esta vuelta soporte de pantallas propias, también clonadas del Workbench: añadido el bloque G.

### 2026-11-02 — Tarea 3 (en Forja)
- Abrir: un fichero que no es `.dash`/`.dashui` y empieza por FORM....ILBM va al editor de sprites
  (`sp_es_ilbm`); el panel del proyecto lista también las imágenes (`sp_extension`). Guardar y guardar como, con
  `SP_PATRON`. Amiga-B "Nuevo sprite..." (evento 36, `tr` 352) con la petición `_Sprite|_BOB|_Cancelar`.
- Compilar desde un sprite compila `main.dash` si está abierto, si no el primer `.dash` (`programa_abierto`).
  Inferencia, Amiga-D y Amiga-P avisan. Deshacer y rehacer van a `sp_deshacer`/`sp_rehacer`. La pestaña dibuja de
  momento una línea con el tipo y el tamaño (`sp_dibujar`, la rejilla es la tarea 4).
- La sonda se escribe también al arrancar (antes, solo al redibujar), y con un sprite lleva `sp_sonda`.
- Textos nuevos: 87 a 92 en `.dash` y 352 en `ventana.dashui` (al catálogo en la tarea 14).
- `tests/sprites_forja.sh`: TODO BIEN (8 en el Amiga y `iff.py` sobre lo guardado). `teclas.sh` y `ficheros.sh`
  siguen dando TODO BIEN. `diseno`, `compilar`, `depurar`, `rexx` y `buscar` no se pasaron: necesitan dashc para el
  Amiga (`make amiga`), que no está construido.
- Visto de paso, no es de esta tarea: si no se encuentra el compilador, la salida dice "No compila: 0 errores" en
  vez de que no se puede ejecutar.
- Aparte del loop, el usuario pidió los registros A de forja e inferencia.freemem.space: puestos en OVH
  (37.187.75.28, comprobado con dig en dns15/ns15.ovh.net). Las webs las hace otro agente en `webs-freemem`.

### 2026-11-02 — Tarea 4 (rejilla)
- `sp_dibujar`: la rejilla con el mayor zoom que cabe (hasta 32). Cada fila se pinta por tramos del mismo color y
  el lápiz solo se cambia si cambia el color. Con zoom de 6 o más, separación de 1 píxel. El color 0 se pinta con un
  gris del tema (`fondo_linea`), distinto del negro. Barra de estado (tipo, tamaño, fotograma, color,
  herramienta, o el último aviso). `ENV:FORJA_SPRITE` "x y zoom".
- **Sitio:** en 640x256 el editor deja unos 90 píxeles de alto y 32x32 cabía con zoom 2. Ahora, con un sprite
  delante, se ocultan la salida, su divisor (`balance_salida`) y la barra (`ajustar_paneles` en `main.dash`), y
  los avisos van a la barra de estado del sprite. La tira de fotogramas solo sale si con ella la rejilla tiene
  zoom 4 o más. Así, en 640x256, 16x16 sale con zoom 5, 32x32 con zoom 4 y 64x64 con zoom 2. En RTG de 1024x768,
  64x64 sale con zoom 8 y la bola de 32x32 con zoom 16.
- **Tiempos** (`tests/sprites_dibujo.sh`, `REAL=1`, A1200 a 14 MHz, Workbench de 640x256): 16x16 al azar 75 ms;
  32x32 al azar 239 ms; 64x64 al azar 890 ms; bola de 32x32 (como un sprite de verdad) 65 ms. Quitar las llamadas
  de sobra no bajó nada (237 a 239): cada tramo es un RectFill que cuesta unos 0,22 ms. Pasa de 200 ms solo con
  ruido, que no es lo normal. Mientras se pinta, la tarea 5 redibuja solo las celdas tocadas. Lo que lo arregla
  es un builtin que pinte la imagen de golpe: tarea 15b. Se sigue adelante.
- Captura RTG (scratchpad `rtg-14.png`): bien.
- Webs (fuera del loop): el agente terminó `forja` e `inferencia` en `webs-freemem`, rama `forja-inferencia`, sin
  publicar.

### 2026-11-02 — Tarea 5 (lápiz)
- `sp_clic` y `sp_arrastrar` devuelven `SP_CAMBIO`, `SP_TODO` y `SP_CELDAS`. `sp_resultado` (en `main.dash`)
  marca el documento y redibuja todo, o solo las celdas de `sp_tocados` (`mui_canvas_update_area` con
  `sp_celda_sola`, como `ed_solo_linea`).
- Trazo con líneas de Bresenham entre los puntos del arrastre. El paso de deshacer se guarda antes del primer
  píxel que cambia, así que un clic que no cambia nada no deja paso. Alt + clic pinta con el 0; Ctrl + clic (o
  el cuentagotas) coge el color. Al soltar también se pinta hasta donde se soltó: el último movimiento llegaba
  antes del final y la diagonal quedaba sin su último píxel (la prueba lo cazó).
- `tests/sprites_lapiz.sh`: TODO BIEN (10). `tests/sprites_forja.sh` sigue en TODO BIEN.
- Webs (fuera del loop, lo pidió el usuario): publicadas forja e inferencia.freemem.space (haproxy del CT 101 con
  copia, `main` subido con la cuenta FreeMEM, `desplegar.py --certificado`). Comprobado desde fuera.

### 2026-11-02 — Tarea 6 (paleta)
- Panel de la derecha con la paleta: cuadrícula de 8 columnas (16 con más de 32 colores), el color 0 con una raya
  (es el transparente), el elegido enmarcado y su valor "#RRGGBB". Debajo, barras R G B: clic o arrastre. En un
  sprite de hardware van en pasos de 17, porque `sprite_color` usa 4 bits. Un clic en una barra guarda un paso de
  deshacer de todo (la paleta va en el paso completo).
- Botones del lienzo: cada dibujo apunta rectángulo y acción (`_sp_boton`); `sp_clic` los busca fuera de la
  rejilla. Teclado sin Amiga: `sp_tecla` (arriba y abajo dan la vuelta; las cifras eligen color).
- La sonda acaba con "paleta RRGGBB ..."; `ENV:FORJA_SPRITE_PANEL` "x y lado columnas" de la paleta y "x y ancho
  paso" de las barras.
- `tests/sprites_paleta.sh`: TODO BIEN (10), también con `RTG=1`. `sprites_lapiz` y `sprites_forja` siguen en
  TODO BIEN.
- Lápices en 256 colores: tras arrastrar la barra G de punta a punta, la captura RTG no mostró colores cambiados.
  Pero Dash guarda 128 lápices y, pasado el tope, suelta cada uno en seguida, así que un BOB de 256 colores o
  mucho arrastre pueden cambiar colores en pantalla. No visto, no descartado: tarea 15c.
- La cuota semanal se renovó (0 %) a las 23:08: la excepción de la regla 0 ya no hace falta.

### 2026-11-02 — Tarea 7 (herramientas)
- Botones de las seis herramientas en el panel, encima de la paleta. Teclas P L B F K A.
- Línea y caja: mientras se arrastra, la figura se dibuja encima de la rejilla y solo se redibuja la rejilla
  (`SP_REJILLA`, `sp_zona_rejilla`, `sp_solo_rejilla`). Al soltar pasa al dibujo, con un paso de deshacer si cambia
  algo. Mayúsculas al empezar rellena la caja.
- Relleno de 4 vecinos con una pila (sin recursión), un paso de deshacer. Agarre: un clic lo pone; con esa
  herramienta se ve una cruz en el punto.
- La sonda lleva también el agarre: "... velocidad agarre_x agarre_y". `ENV:FORJA_SPRITE_PANEL` añade
  "x y paso_x paso_y" de los botones de herramientas.
- `tests/sprites_herramientas.sh`: TODO BIEN (14), también con `RTG=1`. `paleta`, `lapiz` y `forja` siguen en TODO
  BIEN. **Sin probar:** la caja rellena con Mayúsculas (`input_drag` no lleva teclas).
- Visto con las capturas: una captura puede salir a medias mientras MUI copia el búfer del lienzo a la pantalla
  (arriba lo viejo, abajo lo nuevo). Otra captura un segundo después sale bien; no es un fallo de Forja.
- Pulsar una tecla y arrastrar en seguida (la prueba, sin esperar) puede llegar antes de que Forja procese la
  tecla. A mano no pasa; la prueba espera a la sonda entre los dos.

### 2026-11-02 — Tarea 8 (tamaño y tipo)
- Ancho y alto (Ctrl + flechas, botones - y +), colores (planos de 1 a 8, botones) y tipo (T o su botón), con
  deshacer completo. Cambiar de tamaño corta o rellena con el 0. Quitar planos deja los bits bajos, como
  `sprite_load`. Pasar a sprite de hardware corta a 16 de ancho y 2 planos. Un sprite de hardware no cambia de
  ancho ni de colores: un aviso dice que T lo pasa a BOB.
- **Panel en pestañas** ("Dibujo" y "Tamaño", luego "Animar"), como el inspector de Godot: en 640x256 no cabían
  herramientas, paleta y tamaño juntos, y los botones de tamaño quedaban fuera del lienzo. La página Dibujo se
  compactó (sin el título de herramientas; el color elegido va en la línea del título de la paleta).
- `ENV:FORJA_SPRITE_BOTONES`: "acción,x,y" del centro de cada botón, para que las pruebas pulsen por acción.
- `tests/sprites_tamano.sh`: TODO BIEN (11). `paleta`, `lapiz` y `herramientas` siguen en TODO BIEN.
- **Intermitente:** una de tres veces, `sprites_herramientas` dejó el agarre en 5,1 en vez de 5,6. Las otras dos
  pasaron. La prueba ahora espera a la sonda entre la tecla A y el clic. No está explicado: si se repite, mirarlo.
- El usuario pidió en esta vuelta la biblioteca de juegos tipo pygame y el editor de escenas tipo Godot, y las
  herramientas de Forja por tipo de proyecto: bloque H (tareas 26 y 27, de diseño), antes del bloque C.

### 2026-11-02 — Tarea 26 (diseño de la biblioteca de juegos y el editor de escenas)
- `docs/JUEGOS_DISENO.md`: qué se copia de pygame (piezas sueltas, Sprite y Group, choques, capas) y de Godot
  (árbol de nodos, escenas que se instancian, `_ready`/`_process`/`_physics_process` con paso fijo, señales,
  inspector), sacado de sus docs oficiales; lo que no se copia y por qué. Cuentas del fotograma de 50 Hz con las
  medidas de Dash (A500 ~2.000 vueltas sencillas por fotograma, A1200 ~9.000; dibujar con el sistema es lo
  caro). Luces en tres caminos (paleta/copper, luz por tiles precalculada, RTG). Físicas AABB y círculos en
  coma fija. La biblioteca en dos capas (pygame y Godot), escenas `.escena` en JSON compiladas con un `import`
  como `.dashui`, el editor de escenas en Forja, seis fases con un juego cada una y la lista de builtins.
- Queda `[?]`: el usuario decide nombre y repo, máquina mínima, idioma de la API, si hay modo sin sistema y cómo
  se compilan las escenas.

### 2026-11-02 — Tarea 27 (diseño de las herramientas por tipo de proyecto)
- `docs/HERRAMIENTAS_DISENO.md`: un `.forja` con tipo (juego, demo, aplicación) que cambia el menú
  Herramientas, la plantilla y el panel; lo común (perfil, memcheck y memoria con vistas en Forja); juegos (vista
  de depuración, efectos 8SVX, medidor); demos (pistas de sincronía en vivo, vista del MOD, línea de tiempo,
  editor de copper, medidor de líneas, tamaño y Shrinkler); escritorio (traducciones, iconos `.info`,
  AmigaGuide, puerto ARexx, instalador y paquete para Aminet, que hoy solo existen en Python en el PC).
- Comprobado en Dash: no hay forma de que un programa sin MUI reciba órdenes ARexx (solo `rexx_send` y
  `mui_app_rexx`); las pistas en vivo de las demos lo necesitan (`rexx_port_*`). No comprobado: si Shrinkler
  tiene versión de Amiga.
- Queda `[?]`: el usuario decide el `.forja`, el orden, los iconos y Shrinkler. El loop sigue con el bloque C.

### 2026-11-02 — Tarea 9 (fotogramas)
- Tira de miniaturas: al doble si el sprite mide hasta 24 de alto, a tamaño real hasta 64, y tomando uno de cada
  k píxeles si es más alto. El actual va enmarcado, hay un "+" al final, y la tira se desplaza para que el actual
  se vea. Un clic elige el fotograma. Sin sitio para la tira (pantallas bajas), las teclas siguen valiendo.
- Teclas: flechas (con vuelta), Alt + flechas mueve, Mayúsculas + flechas desplaza el dibujo dando la vuelta, N
  nuevo, D duplicar, Supr quitar (nunca el último), Retroceso vaciar, H y V espejo. La rueda del ratón cambia de
  fotograma. Amiga-C, X y V copian, cortan (vacía) y pegan fotogramas dentro de Forja; pegar mete uno nuevo detrás
  del actual, cortado al tamaño y a los colores. Todo con deshacer.
- `tests/sprites_fotogramas.sh`: TODO BIEN (14), y la captura RTG se ve bien. `lapiz`, `herramientas` y `tamano`
  siguen en TODO BIEN.
- El usuario decidió el diseño de los bloques H: Fragua, A1200, API en inglés y modo que se adueña del hardware
  (falta la 5, cómo se compilan las escenas); y para las herramientas, `.forja`, el orden propuesto, iconos de
  3.5 y Shrinkler si está instalado.

### 2026-11-02 — Tarea 10 (piel de cebolla)
- O la enciende y la apaga. Las celdas vacías del fotograma actual enseñan un punto, de un tercio del lado, con
  el color que tiene esa celda en el fotograma anterior (el último si el actual es el primero, porque las
  animaciones dan la vuelta). Solo con zoom de 3 o más. Las celdas sueltas que se repintan también lo llevan. La
  barra de estado dice "cebolla", y la sonda la lleva al final de la cabecera.
- `tests/sprites_cebolla.sh`: TODO BIEN dos veces seguidas, mirando píxeles reales con `screen_pixel`.
  `sprites_forja` sigue en TODO BIEN.
- La primera versión de la prueba leía la pantalla antes de que Forja hubiera pintado. Ahora espera a la sonda
  antes de leer.
- **Corrección:** el primer commit de esta tarea dio por buena `sprites_forja`, y tenía un FALLO; el "TODO BIEN"
  que se vio era solo el de `iff.py`. Repetida, fallaba siempre al cambiar entre la pestaña del sprite y una de
  texto desde el panel del proyecto. Esperando a la sonda (hasta 5 s) pasa: era lentitud. Al pasar de sprite a
  texto se enseña o se oculta la salida, y MUI recoloca toda la ventana. **Pendiente:** medir con `REAL=1` cuánto
  tarda ese cambio de pestaña en un A1200. Si se nota, ocultar la salida solo si la ventana es baja.

### 2026-11-02 — Tarea 11 (vista animada)
- Tercera pestaña del panel, "Animar": la vista (al doble si cabe; si no, a tamaño real, o tomando uno de cada
  k), con el color 0 transparente. Botón Reproducir/Parar (Espacio), "Tics" por fotograma con - y + (y las teclas
  - y +, de 1 a 50 tics; se guarda en FRJA) y la cebolla (O). Al reproducir se va a esa pestaña.
- `tic()` avanza la vista por el reloj (`sp_avanzar`) y redibuja solo su zona (`sp_solo_vista`). El bucle
  principal vuelve a armar el tic con el intervalo de la animación, como hace la bienvenida. Cambiar de pestaña
  para las animaciones de los demás sprites (`ajustar_paneles`).
- Error de la primera prueba: los botones nuevos (7000 en adelante) caían en la comprobación de las miniaturas
  (6000 en adelante) y elegían el fotograma 1000. Arreglado con el rango de 6000 a 6999.
- `tests/sprites_animar.sh`: TODO BIEN tres veces (una con `RTG=1`, captura bien). `forja`, `fotogramas` y
  `cebolla` siguen en TODO BIEN. Una vez, antes del arreglo, la segunda pulsación de Espacio no se vio en 5 s;
  no se repitió en las tres siguientes.
- El usuario pidió en esta vuelta juegos en 3D con MiniGL (bloque I).

### 2026-11-03 — Tarea 28 (diseño 3D con MiniGL)
- `docs/3D_DISENO.md`, con fuentes: en 2026 hay una minigl.library compartida de Steffen Häuser (licencia
  Hyperion MiniGL Open Source, SDK para programas nuevos). Hay PiStorm3D (aceleración con la GPU de la Pi 4 en el
  PiStorm32), MiniGL Classic (tarjetas 3D clásicas y QuarkTex para WinUAE), Wazp3D (Warp3D por software) y
  WarpMiniGL, y muchos juegos portados.
- Consecuencia: el 3D de verdad pide aceleración (PiStorm32 con Pi 4, tarjeta 3D o Vampire). Va como "Fragua 3D",
  aparte de la base A1200, con `Float`. Propuesta: builtins `gl_*` en Dash, nodos 3D como Godot, modelos `.lwo`
  (formato público) y `.obj`, visor de modelos y vista 3D en Forja, en cinco fases.
- Lo de Santi: las fuentes públicas solo lo nombran como autor de los iconos de LightwaveRTG. Lo de su modeler con
  MiniGL no aparece: hacen falta sus mensajes.
- Sin comprobar: si MiniGL Classic con Wazp3D funciona en FS-UAE (es la fase 1).

### 2026-11-03 — Tarea 12 (código)
- C, o el botón "Copiar el código (C)" de la pestaña Tamaño, copia al portapapeles las líneas de Dash para usar el
  sprite. Un sprite de hardware lleva `sprite_load` con aviso si falla, `sprite_color` de los colores 1-3 (en 4
  bits, índices 0-2 como en el runtime) y cómo animarlo con `sprite_frame`. Un BOB lleva `bob_load`, `gfx_rgb8` de
  sus colores, y `bob_frame`/`bob_pos`/`bob_draw`; si sus fotogramas no son cuadrados, avisa en un comentario.
  Sin guardar, pide guardar antes (el código lleva el nombre del fichero).
- `tests/sprites_codigo.sh`: TODO BIEN. Forja copia el código y luego se compila de verdad dentro de un programa y
  carga el sprite y el BOB en el emulador.
- **Fallo de Dash encontrado:** `gfx_rgb8` sin ventana cuelga el programa (`_dash_win` NULL). Aislado con 9
  programas pequeños en el emulador. Tarea 15d. La prueba abre una ventana en la pantalla, como un juego de verdad.

### 2026-11-03 — Tarea 13 (usuario de prueba completo)
- `tests/sprites.sh`: de principio a fin. Abre un pincel con ByteRun1 sin FRJA, dibuja, hace línea, rellena y
  deshace, duplica y voltea, pasa a sprite de hardware, guarda (Amiga-S) y lee lo guardado con `bob_load` y con
  `iff.py`, que lo compara con lo que enseñaba el editor. Mide el cambio de pestaña, crea un BOB, lo toca y sale
  descartando. TODO BIEN dos veces seguidas.
- `tests/sprites_todas.sh`: las 13 pruebas de sprites con un resumen. Todas en TODO BIEN, tras arreglar
  `sprites_base` (con Kickstart 3.1 le faltaba `locale.library`: ahora lleva sistema) y `sprites_codigo` (leía la
  salida antes de que Forja la escribiera).
- **Lo que parecían eventos perdidos no lo era.** Con un registro de eventos en la sonda (`RAM:forja-eventos.txt`)
  se vio que todas las teclas y el soltar del arrastre llegaban. Lo que fallaba era la escritura de la sonda: si
  la prueba tenía el fichero abierto, AmigaDOS no dejaba escribirlo, y la prueba leía el estado viejo. Ahora Forja
  reintenta (`sonda_fichero`), y la sonda del sprite solo se publica si cambia. Probablemente explica también los
  fallos intermitentes de las tareas 7 y 11 y parte de la "lentitud" de la tarea 10.
- **Pendiente:** medir el cambio de pestaña dentro de Forja. Medido desde la prueba (inflado por sus lecturas
  constantes de la sonda): 0,9 s a un texto, 2,7 s a un sprite, sin `REAL=1`.

### 2026-11-03 — Tarea 14 (acabado)
- Catálogo: `tools/catalogos.py cd` falló con el texto 104 repetido ("TAMAÑO" y "Tamaño"): la pestaña pasa al 137.
  El trozo "BOB de %1 x %2" del código copiado pasa a ser traducible (138). Los 60 textos nuevos traducidos en
  `catalogos/english.ct` (80 a 138 y 352); `catalog` construye `build/Catalogs/english/Forja.catalog`. Con
  `CATALOGOS=1` el editor sale en inglés (captura).
- `tests/ventana.sh` con `SPRITE=1`: abre una nave de ejemplo (BOB de 32x32, 16 colores, 4 fotogramas, de
  `iff.py`). Capturas RTG en castellano e inglés en `docs/img/sprites.png` y `sprites-en.png` (14 KB cada una),
  enlazadas desde los README. Los README describen el editor entero con sus teclas; `PLAN.md` gana la fase F10 y
  los diseños por revisar.
- El paquete (`tools/paquete.py`) no necesita nada: el editor va dentro del ejecutable y el catálogo ya se
  empaqueta.

### 2026-11-03 — Tarea 15 (Dash: BOB con fotogramas de cualquier ancho)
- Worktree de Dash `~/Projects/FreeMEMLang/.worktrees/forja-sprites`, rama `forja-sprites` desde main 67770c1 (Dash
  2.0.2). **Ojo:** el main de Dash tiene cambios sin commit de otra sesión (`compiler/codegen.py`, `main.py`, los
  `dashrt*.o`...). No se tocaron.
- Decidido: las dos cosas. `bob_load` lee el trozo FRJA ("1 tipo ancho velocidad") y toma el ancho del fotograma;
  así los ficheros de Forja funcionan sin código de más. `bob_frame_width(id, ancho)` sirve para cualquier otra
  imagen (borra el BOB si estaba dibujado y vuelve al fotograma 0 si ya no existe).
  `_dash_bitmap_fw[]`, a 0 en `_dash_bitmap_create`.
- Test `tests/test_bob_frame_width.dash`: un IFF escrito a mano con FRJA (3 fotogramas de 8x4, que con la regla de
  los cuadrados serían 6 de 4x4), el mismo sin FRJA, y con `bob_frame_width`. Pasa con `--emu` (y `test_bobs`
  sigue bien), y también compilado con `./dash` directo a hunk tras `make -C dashc runtime` (runtime de dashc
  rehecho, `builtins_tab.c` al día). `docs/BUILTINS*.md` y la gramática de VS Code regenerados. Batería sin
  emulador: 522/522.
- Commit 47b5b6f en `forja-sprites` de Dash. Fusionar en main de Dash lo decide el usuario (tarea 19). Hasta
  entonces, Forja sigue avisando de los fotogramas no cuadrados en el código que copia.

### 2026-11-03 — Tarea 15b (Dash: `gfx_pens_draw`)
- `gfx_pens_draw(buffer, ancho, alto, x, y, zoom)`: un byte por píxel con el lápiz, cada píxel de zoom x zoom.
- **Primera versión, más lenta:** `WriteChunkyPixels` por fila. En un A1200 con pantalla de planos fue más lenta
  que los tramos de Forja (16x16 zoom 5: 179 ms frente a 44; 32x32 zoom 4: 363 frente a 172). El sistema pasa a
  planos píxel a píxel.
- **Versión buena:** en un bitmap de planos (ECS/AGA), cada fila de la imagen se pasa a planos en C, en una banda
  de `zoom` líneas, y el blitter la copia (`BltBitMapRastPort`, recortado por la ventana). En RTG,
  `WriteChunkyPixels`, que ahí es rápido. Sin ninguno de los dos, tramos de RectFill. Sin capa (el RastPort de una
  pantalla) no escribe fuera del bitmap.
- **Medido en A1200 (REAL=1, Workbench de 4 colores)**, con píxeles al azar y contando el llenado del búfer desde
  Dash: 16x16 zoom 5, 21 ms frente a 43; 32x32 zoom 4, 56 frente a 172; 64x64 zoom 2, 117 frente a 662.
- Test `tests/test_gfx_pens_draw.dash` (zoom 1 y 4, y que no pinte de más): pasa con `--emu`, y directo a hunk en
  la máquina RTG. Batería sin emulador: 523/523. Commit 29f780a en `forja-sprites` de Dash.
- **Sin probar:** el camino de RectFill (gráficos anteriores a V40) y pantallas de más de 4 planos en ECS/AGA.
- Forja lo usará en la rejilla (sin las líneas, que van encima) y en las miniaturas cuando se fusione (tarea 19).

### 2026-11-03 — Tarea 15c (Dash: soltar lápices)
- `color_pen` cuenta cuántas veces da cada lápiz. `color_pen_free(pen)` resta uno y, al llegar a 0, lo devuelve a
  la pantalla (ReleasePen). Así el tema de Forja no pierde un color que también use un sprite. El tope de la
  lista sube de 128 a 512.
- **Fallo de Dash encontrado y arreglado:** con `color_pen` en una pantalla propia, `screen_close` la cerraba sin
  soltar sus lápices; al salir, `ReleasePen` iba sobre el ColorMap ya liberado y el programa se colgaba (a veces).
  Ahora `screen_close` (y abrir otra pantalla RTG encima) los suelta antes, con un enganche
  (`_dash_screen_closing`) que pone el código de los lápices: va en otra plantilla del runtime, que se emite
  después.
- Test `tests/test_color_pen_free.dash`: mismo lápiz para el mismo color, sigue pedido tras soltar una vez, y salir
  con lápices pedidos en una pantalla cerrada ya no cuelga. **Sin prueba directa:** que el lápiz vuelva a estar
  libre. Con `PRECISION_IMAGE` la pantalla da antes un lápiz parecido que ya tiene que uno libre, y desde Dash no
  se ve qué lápices están libres; dos intentos de probarlo llenando la paleta no lo demostraban.
- Pruebas de pantallas, colores, fuentes, mezclas y RTG con `--emu`: todas bien. Batería sin emulador 524/524. Runtime
  de dashc rehecho. Commit en `forja-sprites` de Dash.
- Forja (tarea 19): `_sp_preparar_pens` soltará los lápices de la paleta anterior antes de pedir los nuevos.

### 2026-11-03 — Tarea 15d (Dash: pantalla propia sin ventana)
- Buscando `_dash_win->` en los builtins salieron `gfx_rgb8`, `mouse_x` y `mouse_y`. `gfx_rgb8` pasa a
  `_dash_set_color8`, hermana de `_dash_set_color` (`gfx_rgb`): pantalla propia, si no la de la ventana.
  `mouse_x`/`mouse_y` sin ventana dan 0.
- El test destapó dos fallos más, aislados con programas pequeños en el emulador:
  - Dibujar (`gfx_pen`, `gfx_pixel`...) en una pantalla propia sin ventana colgaba, porque `_dash_rp` era NULL.
    Ahora, al abrir una pantalla propia sin ventana (los cuatro sitios que la abren), `_dash_rp` es su RastPort, y
    al cerrarla vuelve a NULL si apuntaba ahí.
  - `gfx_pixel_rgb` y `color_pen` miraban la paleta del Workbench, no la de esa pantalla (`_dash_pen_screen`).
- Test `tests/test_gfx_rgb8_sin_ventana.dash` (rojo exacto con `gfx_pixel_rgb`, ratón 0, y acaba). Batería entera
  de Dash en el emulador A1200: 783/783; sin emulador 525/525. Runtime de dashc rehecho. Commit 066239f.
- Captura mandada al usuario: degradado de 32 colores en una pantalla propia sin ventana. Sale corrida unos
  píxeles a la izquierda (el título se corta); parece el encuadre del emulador, sin comprobar.

### 2026-11-03 — Tarea 16 (Dash: `sprite_rgb8`)
- `sprite_rgb8(id, i, r, g, b)`: como `sprite_color` (índice 0-2, los registros 17-31 según el sprite de hardware
  que le tocó), con `SetRGB32` y componentes de 0 a 255. Exacto en AGA; en ECS el sistema se queda con 4 bits. Las
  descripciones de los dos dicen ya el índice y el rango.
- **Sin comprobar el color en el emulador:** `screen_open` no da más de 4 planos en esta máquina (5, 6 y 8 fallan),
  y `screen_open_custom` con más planos elige un modo RTG, donde no hay sprites de hardware. Con 16 colores no se
  pueden pintar y leer los colores 17-31. Dos intentos de test con `gfx_pixel_rgb` lo enseñaron. El test se queda
  en: corre en una pantalla nativa con un sprite y no hace nada con un sprite que no existe.
- Batería sin emulador 526/526; tests de sprites con `--emu` bien; runtime de dashc rehecho. Commit de53d5d.
- Forja (tarea 19): el código que copia con C usará `sprite_rgb8` con los colores de 8 bits del editor (y en
  `sprite_color`, los de 4 bits para ECS).

### 2026-11-03 — Tarea 17 (Dash: colores del fichero)
- `sprite_load_colors(id, fichero)`: los colores 1-3 del CMAP como colores del sprite, con 8 bits (como
  `sprite_rgb8`); falso si el fichero no tiene CMAP o el sprite no existe. `bob_load_colors(fichero, desde)`: todos
  los colores del CMAP en la paleta de la pantalla (la propia, o la de la ventana) desde el color `desde`; da
  cuántos puso (0 si no es un IFF). Con un lector de CMAP propio (`_dash_cmap_read`), en `GRAPHICS_RUNTIME`, sin
  depender del runtime de bitmaps.
- Test `tests/test_load_colors.dash`: un IFF escrito a mano con 4 colores; los colores 1 y 11 (con `desde` 8) se
  leen con `gfx_pixel_rgb`; un fichero que no es IFF da 0 y falso. Del sprite solo se ve que corre (los colores
  17-31 no se leen en el emulador, como en la tarea 16). Batería sin emulador bien; runtime de dashc rehecho.
- Con esto, el código que copia Forja (C) queda en dos líneas por sprite: `sprite_load` y `sprite_load_colors`
  (o `bob_load` y `bob_load_colors`), cuando se fusione (tarea 19).

### 2026-11-03 — Tareas 18, 19 y 20
- 18 (sprites acoplados) y 19 (que Forja use las piezas de Dash) quedan `[?]`: la 18 pide decidir si se quieren ya;
  la 19, que el usuario fusione la rama `forja-sprites` de Dash.
- 20: `docs/MAPAS_DISENO.md`.
  - El tileset es un BOB del editor de sprites (fotogramas cuadrados; `bob_load` ya sabe su ancho).
  - El mapa, en un IFF propio `FORM FMAP` (MHDR, TSET, LAYR, OBJS). No en texto: 32.768 números con `str_split`
    tardan segundos en un 68000. Tiled por JSON, más adelante.
  - El editor, como el de sprites: zoom, desplazamiento, panel en páginas (tiles, capas, mapa, objetos), lápiz,
    caja, relleno, cuentagotas, borrar, selección, espejo, capas de choques y de objetos, tiles animados,
    deshacer y "Código".
  - En el juego: scroll por hardware pintando solo las tiras nuevas, y `tilemap_draw` en C con el blitter. Las
    cifras del coste son estimaciones a medir en la fase 1.
  - Seis fases y cuatro decisiones para el usuario. Queda `[?]`.
- Lo que queda sin `[?]` es el bloque G (pantallas propias).

### 2026-11-03 — Tarea 21 (Dash: clon público del Workbench)
- `screen_clone_wb(nombre)`: `SA_LikeWorkbench` (modo, tamaño, profundidad, lápices y fuente), `SA_PubName`,
  lápices compartidos y `PubScreenStatus(scr, 0)`: pública. Falso si no se abre, si el nombre ya existe o si el
  programa ya tiene pantalla. Sin ventana, se dibuja en ella (como en la tarea 15d). `screen_visitors()`: las
  ventanas de otros programas en ella (`psn_VisitorCount`).
- `screen_close` con una pantalla pública: primero la hace privada (para que no entren más), esperando a que se
  cierren las ventanas de otros. Si al cabo de un minuto siguen abiertas, la deja abierta: cerrarla debajo de ellas
  colgaría el Amiga.
- Test `tests/test_screen_clone_wb.dash`: el clon mide lo mismo que el Workbench; una consola `CON:.../SCREEN
  nombre` abierta por nombre cuenta como visita y, al cerrarla, la pantalla se cierra. Lo de "nombre ya usado" no
  queda probado aparte: la segunda llamada da falso porque el programa ya tiene pantalla. Captura mandada al
  usuario. Batería sin emulador y tests de pantallas bien; runtime de dashc rehecho.

### 2026-11-03 — Tarea 22 (Dash: ventanas MUI en una pantalla pública)
- `mui_window_screen(ventana, nombre)`: `MUIA_Window_PublicScreen` antes de abrir. MUI guarda el puntero al
  nombre, así que se guarda una copia (8 nombres). Falso si no hay pantalla pública con ese nombre: la ventana se
  queda en la de siempre. No se hizo `mui_app_screen`: con una por ventana basta, y Forja pondrá la suya.
- `screen_visitors()` cuenta lo que cuenta Intuition: ventanas y bloqueos (MUI bloquea la pantalla además de
  abrir la ventana: dos ventanas dieron 4). Descripciones corregidas.
- Test `tests/test_mui_window_screen.dash` (con MUI): dos ventanas en el clon, en la misma pantalla, con visitas
  mientras están abiertas y 0 al cerrarlas; un nombre sin pantalla da falso. Las 11 pruebas de pantallas con
  `--emu` y la batería sin emulador, bien. Captura mandada al usuario.
- **Visto en la captura, sin mirar:** el botón "_Aceptar" de la primera ventana sale sin texto en el clon. Puede
  ser de los lápices del clon con MUI o de MUI sin preferencias en este sistema. Pendiente para la tarea 24, que
  pondrá Forja (MUI) en su pantalla.

### 2026-11-03 — Tarea 23 (Dash: elegir el modo de pantalla)
- `dialog_screen_mode(título)`: la petición de modo de pantalla de ASL, empezando en el modo del Workbench, con
  ancho, alto y profundidad. Cierto si se eligió. `screen_mode_id()`, `_width()`, `_height()` y `_depth()` dan lo
  elegido (una función `_dash_screen_mode_get`, porque el analizador no admite builtins que sean solo una
  variable). `screen_open_mode(modo, ancho, alto, planos, título)`: `SA_DisplayID` exacto; falso si
  `ModeNotAvailable` o si no se abre.
- **Error mío corregido:** escribí que 0x29000 era PAL de baja resolución. Es la de alta (`PAL_MONITOR_ID` 0x21000
  + `HIRES_KEY` 0x8000); la de baja es 0x21000. Con 0x29000 y 5 planos no abría y parecía un fallo.
- Test `tests/test_screen_mode.dash`: PAL baja resolución 320x256 con 5 planos abre (y mide eso); un modo que no
  existe da falso. **La petición no está en el runner:** espera al usuario. Las teclas de una tarea de
  `task_start` no le llegan, y Return no es su OK. Comprobada a mano con otro programa (por Startup-Extra) que hace
  clic en OK: cierto, modo 0x29000, 640x200x2. Captura de la petición mandada al usuario.
- **Pregunta abierta:** esta máquina A1200 del emulador no da más de 4 planos en alta resolución. AGA da 8, así
  que puede que el emulador esté en ECS. Si es así, lo de "exacto en AGA" de `sprite_rgb8` (tarea 16) tampoco se
  ha visto.
- Batería sin emulador bien; runtime de dashc rehecho.

### 2026-11-03 — Fin del loop (no quedan tareas sin `[?]`)
- **24** queda `[?]`: Forja en un clon público necesita `screen_clone_wb` y `mui_window_screen`, que solo están en
  la rama `forja-sprites` de Dash. Forja se compila con main de Dash. Al hacerla, mirar el botón sin texto de MUI
  en el clon (tarea 22).
- **25** queda `[?]`: preguntar si el doble búfer va aquí o con las piezas de juegos (Fragua).

**Resumen.**
- **Forja, rama `sprites`** (worktree `~/Projects/forja-sprites`): el editor de sprites y BOBs entero (tareas 1 a
  14). Abre y guarda IFF ILBM (también pinceles de DPaint con ByteRun1); rejilla con zoom; lápiz, línea, caja,
  relleno, cuentagotas y agarre; paleta con barras R G B; tamaño, colores y tipo; fotogramas con tira, copiar y
  pegar, espejos y desplazar; piel de cebolla; vista animada; código para usarlo; catálogo inglés, README con
  capturas. 13 pruebas en el emulador (`tests/sprites_todas.sh`), todas bien. Sin fusionar en main.
- **Dash, rama `forja-sprites`** (worktree `.worktrees/forja-sprites`): `bob_frame_width` y FRJA en `bob_load`,
  `gfx_pens_draw`, `color_pen_free`, `sprite_rgb8`, `sprite_load_colors`, `bob_load_colors`, `screen_clone_wb`,
  `screen_visitors`, `mui_window_screen`, `dialog_screen_mode` y `screen_open_mode`. Fallos arreglados:
  `gfx_rgb8`, dibujar y los colores en una pantalla propia sin ventana, y `screen_close` con lápices pedidos.
  Batería 530/530 sin emulador y 783/783 en el emulador (antes de las tres últimas tareas, que pasaron sus pruebas).
  Sin fusionar en main (que tiene cambios sin commit de otra sesión).
- **Diseños para revisar:** `docs/JUEGOS_DISENO.md` (Fragua; decididas 1 a 4, falta la 5), `HERRAMIENTAS_DISENO.md`
  (decidido), `3D_DISENO.md` y `MAPAS_DISENO.md`.
- **Pendiente del usuario:** fusionar las dos ramas; sprites acoplados (18); escenas forma B; las preguntas del 3D y
  de los mapas; doble búfer (25).

### 2026-11-03: decisiones del usuario
- Fusionar las dos ramas (`sprites` en Forja y `forja-sprites` en Dash).
- 18 (sprites acoplados): sí, ya.
- Escenas: forma B (Forja genera un `.dash`).
- 3D: PiStorm32 con Pi 4 primero; Fragua 3D aparte. Siguen sin respuesta si tiene un PiStorm32 y los mensajes de Santi.
- Mapas: IFF `FORM FMAP`, Tiled en la fase 6, tiles cuadrados de 8, 16 y 32, hasta 1.024x1.024 por capa.
- 25 (doble búfer): en Dash.

### 2026-11-03: tarea 18, sprites acoplados
- Dash (rama `sprites-acoplados`, d77eb04): `sprite_load_attached(id, fichero)`. Una pareja par e impar de sprites
  de hardware; los planos 0-1 al par, los 2-3 al impar con el bit de acoplado. Las demás órdenes de sprites tratan
  la pareja; colores 17-31. Prueba `test_sprite_attached` (datos y bit de acoplado; lo que se ve no se puede
  comprobar en el emulador: sus capturas copian el bitmap de la pantalla, sin sprites).
- Forja: un sprite de hardware con 4 planos es acoplado (`sp_acoplado`). T pasa de BOB a sprite, a acoplado y a
  BOB. FRJA sigue con tipo 1. El código copiado usa `sprite_load_attached` y `sprite_load_colors`. Textos 139-144.
  `ventana.sh` con ACOPLADO=1 abre uno de ejemplo. Pruebas: sprites_iff y sprites_tamano bien.
