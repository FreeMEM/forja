# Forja: el bucle hacia el mejor IDE del Amiga

Plan y bitácora del bucle que empezó el 2026-11-16. El análisis de partida está en `docs/IDE_ANALISIS.md`.

## Decisiones del usuario (2026-11-16)

- Forja es para el Amiga. En Linux y en DashOS, el "Forja" es la extensión de VS Code de Dash. Forja no tendrá
  versión para DashOS.
- Forja tendrá un **sistema de extensiones**. Serán extensiones:
  - dashgit (git);
  - los editores de sprites y de mapas;
  - Inferencia, como un copiloto: lee el código y los ficheros del proyecto y escribe en el editor.
- Dash tendrá **ensamblador en línea**, para demos.
- La memoria mínima la fija esta sesión (ver más abajo).

## Cómo son las extensiones (diseño de partida)

- **Una extensión es un programa aparte**, en `Forja/Extensiones/<nombre>/`, con un manifiesto. Así:
  - cada una tiene su licencia (dashgit es GPLv2 y Forja es MIT);
  - se cargan solo cuando hacen falta;
  - si una cae, Forja sigue en pie en lo posible.
- **El manifiesto** dice:
  - nombre, versión, autor y descripción;
  - qué añade: menús, teclas, tipos de fichero que abre, paneles;
  - cuándo se arranca: al abrir Forja, con su menú o con un tipo de fichero.
- **Habla con Forja por su puerto ARexx**, con una API documentada y un módulo de Dash para usarla. La API cubre:
  - leer y escribir el texto del editor;
  - el cursor y la selección;
  - los ficheros del proyecto;
  - la barra de estado;
  - marcas en el proyecto y en el margen;
  - avisos de "guardado", "abierto" y "cerrado";
  - añadir entradas de menú.
- **La extensión pinta sus propias ventanas** (MUI).
- **Gestor de extensiones en Forja:** lista, activar y desactivar, e instalar desde un .lha.

## Memoria mínima

- **Mínimo:** 68020, 2 MB de chip y 4 MB de fast, con AmigaOS 3.1 y MUI 3.8. Es un A1200 con una ampliación
  pequeña.
- **Recomendado:** 8 MB de fast o más, para usar git e Inferencia a la vez que se compila.
- **Por qué:**
  - las extensiones se cargan solo al usarlas;
  - la ayuda se lee del disco a trozos, sin cargarla entera;
  - hay que medir cuánta memoria usa Forja hoy y dejar un tope en las pruebas (paso 0.3).
- **Medido** (2026-11-17, paso 0.3, `tests/memoria.sh`; A1200 emulado con AmigaOS 3.1 y MUI 5, 2 MB de chip y 8 de
  fast; el proyecto `tests/prueba/juego` abierto). Chip: 75 KB en todos los casos. Fast:

  | Forja | Quieta | Compilando (lo más alto) |
  |-------|--------|--------------------------|
  | sin extensiones | 2,5 MB | 4,4 MB |
  | con Git (y el servidor de dashgit) | 3,3 MB | 5,2 MB |
  | con todas (Git, el copiloto, Sprites y Mapas) | 3,0-3,6 MB | 4,9-5,5 MB |
  | con todas, y un sprite y un mapa abiertos | 4,2 MB | |

  - De los 2,5 MB, unos 0,9 se quedan al salir: MUI, sus clases y las fuentes, que el sistema guarda cargadas.
    Forja sola son 1,6 MB. Antes de sacar los editores, Forja sin extensiones usaba 2,7 MB (170 KB más).
  - Compilar (dash para el Amiga, `main.dash` con dos módulos) suma 1,9 MB mientras dura.
  - Sprites y Mapas, solo al abrir uno de sus ficheros: 0,3 MB cada una.
  - Inferencia (la aplicación, con AmiSSL) no cuenta: el copiloto no la arranca hasta usarlo.
  - Con MUI 3.8 en la máquina de CoffinOS (68040, RTG): 4,5 MB quieta, 5,3 con Git, 8,6 con todo abierto (las
    ventanas en una pantalla de tarjeta gráfica gastan más; esas máquinas tienen memoria de sobra). Compilar allí dura
    0,2 s y la prueba no llega a ver el pico.
  - **Conclusión**: con 2 MB de chip y 4 de fast quedan unos 5,8 MB libres tras arrancar el sistema. Caben Forja y
    compilar (4,4 MB), y justo con Git (5,2 MB). Con todas las extensiones y compilando (5,5 MB) se queda sin
    margen, y sin contar Inferencia. Se queda el mínimo de 2 + 4 MB para Forja con Git, y 8 MB de fast recomendados
    para el copiloto, los editores e Inferencia.

## Plan

Cada paso dice de quién es: **[F]** Forja, **[D]** Dash, **[G]** dashgit, **[I]** Inferencia, **[V]** extensión de
VS Code.

### Fase 0. Base
- 0.1 [F] Probar Forja en la máquina CoffinOS emulada y apuntar lo que falle.
- 0.2 [F] Borrar las ramas ya fusionadas (`git log main..rama` vacío) y sus worktrees.
- 0.3 [F] Medir la memoria de Forja con un proyecto mediano y fijar el tope. Medido (ver "Memoria mínima"); falta
  el tope en las pruebas.

### Fase 1. Sistema de extensiones
- 1.1 [F] Manifiesto, carga, ciclo de vida y gestor de extensiones.
- 1.2 [F] API por ARexx (la lista de arriba) y su documentación, `docs/EXTENSIONES.md`.
- 1.3 [F] Un módulo de Dash para escribir extensiones, más una extensión de ejemplo con su prueba.
- 1.4 [G][F] Git como extensión: las salidas para máquinas de dashgit, la rama en la barra, marcas, panel de
  cambios y diferencias. Ya está empezado, en módulos que luego pasan a la extensión.
- 1.5 [F] Editores de sprites y de mapas como extensiones (hecho en la rama `ext-editores`, ver la bitácora).
- 1.6 [I][F] Inferencia como copiloto (hecho en la rama `copiloto`, ver la bitácora):
  - pregunta sobre la selección o el fichero;
  - escribe o cambia código en el editor, con vista previa y "aceptar";
  - lee los ficheros del proyecto;
  - explica un error de compilación.

### Fase 2. Editor cómodo
- 2.1 Resaltado sacado de la gramática de Dash.
- 2.2 Comentar, duplicar, mover y borrar líneas; resaltar el paréntesis o el bloque que hace pareja; cerrar solos
  los paréntesis y el `end`.
- 2.3 Buscar con expresiones regulares y en todo el proyecto.
- 2.4 Esquema del fichero y abrir un fichero por su nombre.
- 2.5 Marcadores y saltar al siguiente error con una tecla.
- 2.6 Renombrar.
- 2.7 Plegado.
- 2.8 Teclas, colores y fuente a elegir.

### Fase 3. Proyecto y documentación
- 3.1 [F] Fichero de proyecto `.forja` con opciones y argumentos. Hecho (rama `proyecto`).
- 3.2 [F] Plantillas de proyecto: orden, MUI, juego y demo. Hecho, también commodity y 3D (rama `proyecto`).
- 3.3 [D] Ayuda generada desde Dash: un fichero con índice, más AmigaGuide, metida en el paquete del Amiga.
- 3.4 [F] Panel de ayuda: la ficha entera, búsqueda, enlaces y un botón "Probar".
- 3.5 [D] Opción "solo comprobar", y [F] errores marcados en el código al guardar.

### Fase 4. Depurar y medir
- 4.1 Puntos de parada con condición, vigilar variables y ver el valor bajo el ratón. Hecho (rama `proyecto`).
- 4.2 Perfil y memcheck con vista propia. Hecho (rama `proyecto`).
- 4.3 Medir y acelerar lo que tarda en compilar en el Amiga.

### Fase 5. Demos, juegos y 3D
- 5.1 [D] Ensamblador en línea, por los dos caminos de Dash.
- 5.2 [F] Herramientas de demos: pistas de sincronía, visor de MOD, editor de copper y medidor de rasterlines. Hecho
  (rama `demos`, extensión Demos; ver la bitácora).
- 5.3 [D] Prueba de MiniGL en el emulador y, si va, funciones `gl_*`.

### Fase 6. VS Code
- 6.1 [V] Lo que la extensión de VS Code necesita para ser "el Forja" de Linux y DashOS: compilar con
  `--dashos` y probar en QEMU, depurar, la ayuda, los editores de `.dashui`.

## Bitácora

- 2026-11-16: análisis hecho (`docs/IDE_ANALISIS.md`) y decisiones del usuario. En marcha el 1.4 (ramas `salidas`
  de dashgit y `git-panel` de Forja).
- 2026-11-16, rama `extensiones`: **1.1 a 1.3 hechos** (sistema de extensiones). Diseño final y API en
  `docs/EXTENSIONES.md`. Lo que cambia frente al diseño de partida:
  - **Forja no manda órdenes ARexx a las extensiones.** `rexx_send` espera la respuesta sin límite: una extensión
    colgada colgaría Forja. Los sucesos esperan en una cola por extensión (64 como mucho) y Forja avisa escribiendo
    `ENV:Forja/Avisos/<nombre>`; la extensión lo vigila con `file_notify` y los recoge con `SUCESOS`. Sin gastar
    nada mientras espera y sin consultas periódicas.
  - Una extensión está viva si tiene su puerto `FORJAEXT.<NOMBRE>` (se cierra solo al acabar, también si falla).
    Si en 15 s no recoge sus sucesos y no está su puerto, Forja dice que se ha cerrado y la vuelve a arrancar con su
    menú.
  - Manifiesto `manifiesto.txt` (`clave = valor`), no JSON: más fácil de escribir en el Amiga.
  - El menú es "Extensiones", con 12 opciones para todas (Dash no añade opciones a un menú ya hecho).
  - La "barra de estado" es la derecha del título de la salida.
  - Órdenes por lotes: `LOTE`. Medido en el emulador a velocidad de A1200: una orden 5 ms, tres sueltas 17 ms, tres
    en un lote 11 ms. Con una extensión colgada, Forja sigue contestando (lo peor, 0,3 s guardando 70 veces).
  - Piezas: `src/extensiones.dash` (manifiestos, cola, menú, teclas, tipos, gestor, instalar),
    `src/marcas.dash` (marcas del margen y del proyecto, la barra), en `src/main.dash` las órdenes ARexx y los
    sucesos; `lib/forja.dash` para escribirlas; `extensiones/Contar` de ejemplo.
  - Pruebas: `tests/extensiones_base.sh` (sin ventana) y `tests/extensiones.sh` (con Contar y `tests/extensiones/Eco`),
    en MUI 5 (A1200, 3.1) y MUI 3.8 (`SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`).
  - Lo que pide git-panel (`docs/GIT_LOOP.md` de su rama) y queda cubierto: guardado, abierto, cajón del proyecto
    (`PROYECTO`), letras en el proyecto, marcas en el margen, leer el fichero, abrir en una línea, la salida, sus
    ventanas. También `VUELTA` (Forja vuelve a ser la ventana activa: se mira cada 1,5 s, como hace git, porque Dash no tiene ese
    evento). **Falta**: una zona propia
    en la barra de botones con clic, un menú propio (hoy, opciones en Extensiones), y una pestaña de solo lectura con
    colores por línea y teclas propias (la vista de diferencias). Las marcas son letras (`+ ~ - !`), no rayas.
  - Unida `main` (git-panel): las letras de las extensiones van a la izquierda de la de git y su columna del margen
    delante de la raya de git. `tests/git_panel.sh` y `git_panel_coffin.sh` siguen dando TODO BIEN.
  - Todas las pruebas de Forja pasan en la rama (rexx, buscar, sesion, compilar, salir, salida, depurar, clic,
    proyecto, errores, parar, botones, git_panel, git_panel_coffin, ficheros, teclas, sprites_forja, completar,
    mapas_forja, pantalla y las de base) salvo `tests/diseno.sh` ("cambiar label"), que falla igual en `main`
    (e01544c): no es de esta rama.
  - Visto en la prueba con MUI 3.8: el gestor no se abrió hasta el tercer intento (el evento llegó; la ventana no
    estaba). La prueba reintenta; falta saber por qué.
  - **Falta en Forja**: teclas de extensión fuera del editor; paneles dentro de la ventana; que las marcas sigan a las
    líneas al escribir; el catálogo inglés de los textos nuevos (tr 600 a 634); probar instalar un `.lha` (el
    emulador no tiene `C:LhA`).
  - **Falta en Dash** (apuntado, sin rodeos): `rexx_send` con tiempo de espera o sin esperar; añadir y quitar opciones
    de un menú MUI ya hecho (las libres quedan vacías y apagadas); `input_menu` no llega a los menús de MUI (la prueba
    usa `ENV:FORJA_EVENTO` con la sonda); un evento de ventana activada. Y quizá `lib/forja.dash` en la `lib/` de
    Dash (el `import "lib/forja.dash"` no cambiaría).
- 2026-11-16, rama `git-ext`: **1.4, segunda parte: git es una extensión** (`extensiones/Git`, MIT; llama a dashgit
  como programa aparte). Forja ya no tiene nada de git dentro (solo esconde el cajón `.git` en el proyecto): fuera el
  menú Git, las órdenes ARexx `GIT`, `CAMBIOS` y `GITESTADO` (ahora en el puerto de la extensión, `FORJAEXT.GIT`), el
  estado `git` de `ESTADO`, la zona de la rama, las letras, las rayas y la vista de diferencias propias.
  - **La API crece (versión 2)** para que git quepa, de forma general: `ZONA` (una zona con icono, texto y detalle en
    la barra de botones, con clic: suceso `ZONA`); menú propio (`submenu = Git` en el manifiesto: un menú más en la barra de
    menús, hecho en marcha con `mui_menu_add` de Dash PR #182; 3 entre todas, de 10 opciones); `VISTA` (pestaña de solo lectura con un color por línea; sus teclas llegan
    como `TECLA tecla línea nombre`); `RAYAS` (las rayas de git en el margen, con versión del texto para no poner unas
    viejas); `TEXTODISCO`, `VERSION`, `CAMBIADOS`; `pausa` por extensión para `CAMBIADO` (y `CAMBIADO` también tras
    escribir por ARexx). Las marcas y las rayas **siguen a su texto al escribir** (se mueven con las líneas).
  - `VUELTA` sale de `mui_on_activate` (Dash PR #180), sin el tic de 1,5 s; al volver, Forja lee otra vez el cajón del
    proyecto.
  - **Marcas al escribir**: con `dashgit servidor` (rama `servidor` de dashgit), la extensión pide los rangos del texto
    del editor sin guardar tras 0,6 s sin escribir. Se le habla por ficheros, no por `rexx_send` (que espera sin
    límite): un servidor colgado no cuelga la extensión, y a los 20 s sigue sin él.
  - El paquete (`tools/paquete.py`) lleva `Extensiones/Git` y `lib/forja.dash`.
  - Tiempos de las rayas al escribir (repositorio de 4 ficheros, `tests/git_panel.sh`, de la última tecla a ver las
    rayas, con la pausa de 0,6 s dentro): A1200 emulado a velocidad de A1200 (`REAL=1`) 1,2 s (los rangos en el
    servidor, 0,3 s); a toda velocidad 1,3 s; coffin (68040 JIT) 0,7 s. De guardar a ver las letras y las rayas, 1,5 s
    con `REAL=1` (antes, con dashgit aparte, 2,4 s). Teclear no se frena: Forja no espera a nadie y la extensión y el
    servidor van a prioridad -1.
  - Pruebas en la rama: `git_panel.sh` (MUI 5, A1200: normal y `REAL=1`; también `SERVIDOR=no`), `git_panel_coffin.sh`
    (MUI 3.8: con y sin servidor), `extensiones.sh` (MUI 5 y MUI 3.8), `extensiones_base.sh` y el resto
    (botones, teclas, ficheros, rexx, salir, proyecto, clic, buscar, sesion, compilar, errores, parar, salida, depurar,
    completar, pantalla): TODO BIEN.
  - **Falta en Forja**: catálogo inglés de la extensión Git (sus textos van en castellano); las 12 opciones sueltas de
    Extensiones siguen fijas (podrían hacerse en marcha con `mui_menu_extend`); al salir, la extensión espera a que
    acabe su servidor (si se colgara sin atender Ctrl-C, ella se quedaría; Forja no).
  - **Falta en Dash**: `cx_wait` no despierta con el puerto ARexx (el servidor lo mira cada 200 ms).
- 2026-11-17, rama `ayuda`: **3.4 y 3.5 hechos** (ayuda de Dash en Forja y errores marcados al guardar).
  - **Ayuda** (`src/ayuda.dash`): lee `Dash.ayuda` (o `Dash_en.ayuda` si el catálogo de Forja no es el castellano; la
    otra de reserva) a trozos con `lib/ayuda.dash` de Dash, sin cargarla: un registro o una ficha cada vez. Se busca en
    `ENV:Forja/ayuda`, `DASH:Ayuda`, `PROGDIR:/Ayuda` (el paquete de Dash: `Dash/Forja/Forja` y `Dash/Ayuda`),
    `PROGDIR:Ayuda` y el cajón `Ayuda` junto al compilador. Se abre al hacer falta y se cierra con la ventana (y antes de
    poner Dash al día: abierta, no dejaría cambiar `DASH:Ayuda`).
  - Una ventana propia (`VentanaAyuda`, no un panel: en 640x256 no cabe otro): Atrás, Adelante, Índice, Probar y
    "Buscar:"; la lista a la izquierda (lo encontrado o el índice: portada, sintaxis, índice alfabético, los 41 grupos
    y los 27 capítulos; los apartados salen en su capítulo) y la ficha a la derecha en un lienzo con los colores del
    tema: título, subtítulos, el código con su sintaxis, enlaces subrayados. Un clic en un enlace, o en un nombre del
    código (o con `_` en el texto) que tenga ficha, la abre. Rueda, flechas y Mayúsculas+flechas mueven; Retroceso y
    Alt+flechas, atrás y adelante. El texto viene cortado a 76 columnas: si no cabe, se vuelve a cortar.
  - Help/F1 sobre un nombre de Dash abre su ficha; sin nombre, la ayuda; un nombre sin ficha, lo busca. Sobre un
    nombre del proyecto (o sin la ayuda), la ayuda de argumentos de antes. Menú Código: "Ayuda de Dash" y "Buscar en la
    ayuda...".
  - **Probar**: el ejemplo entero de la ficha (un trozo de código con `Main`); en una función, su ejemplo es un trozo
    del de su grupo, así que se abre el del grupo. 226 de las 1277 fichas lo tienen. Se abre en una pestaña sin nombre
    (`ejemplo_<clave>.dash`), se compila desde `T:` y se ejecuta; sus errores llevan a la pestaña.
  - Buscar: las palabras plegadas (sin acentos), todas a la vez, y las que no están por cómo empiezan; la ficha que se
    llama así, primero; 80 como mucho.
  - **Errores** (`src/errores.dash`): al guardar un `.dash`, `dash --check` del programa (el de su proyecto si es un
    módulo) en segundo plano, a prioridad -1 (con `task_priority` alrededor de `run_start`), en el cajón del fichero.
    Tras 1,5 s sin escribir, lo mismo con el texto sin guardar copiado a `T:` (solo un fichero con `Main`: un módulo
    sin guardar no se puede, dash lee del disco lo que importa el programa). Preferencia "Buscar errores al escribir"
    (`ENV:Forja/comprobar`). La línea del error lleva el número en rojo y el nombre subrayado en zigzag; la barra de la
    salida dice el error de la línea del cursor (o cuántos hay); la salida los apunta (con clic) y "Sin errores." al
    quitarse. Siguen a su texto al escribir. F8 y Mayúsculas+F8 (y el menú Código) van al siguiente y al anterior,
    también en otro fichero. Los de compilar se marcan igual. Si la orden dash no sabe `--check`, se dice una vez.
  - Tiempos (A1200 emulado con `REAL=1`, MUI 5): F1 hasta ver la ficha la primera vez 2,3 s (abrir la ventana con
    MUI, 1,2 s; el índice en la lista, 0,5 s; leer la ficha, 0,14 s); con la ventana abierta, una ficha 30-140 ms;
    buscar "sonido" 0,56 s en Forja (la búsqueda 70 ms; el resto, los títulos y llenar la lista de MUI); volver al
    índice tras buscar 0,8 s (llenar la lista); `dash --check` 0,3-0,75 s; de guardar a ver el error marcado 1,1 s; de
    la última tecla a verlo, 3,1 s (con la pausa de 1,5 s). Con MUI 3.8 (68040 JIT), todo por debajo de 0,1 s salvo
    `--check` (0,15 s).
  - Pruebas: `tests/ayuda_base.sh` (sin ventana) y `tests/ayuda.sh` (MUI 5 en A1200 y `REAL=1`; MUI 3.8 con
    `SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`; RTG con MUI 5): TODO BIEN. Siguen bien ficheros, teclas, compilar,
    errores, completar, extensiones (MUI 5 y 3.8), extensiones_base y git_panel.
  - Con MUI 3.8, "Buscar en la ayuda..." no deja el cursor en el campo de buscar (`mui_set_active` no se queda, ni al
    volver a darlo cuando la ventana se activa): hay que hacer clic en él; la prueba lo hace. Con MUI 5 va solo.
  - **Falta en Forja**: la descripción corta del autocompletado sigue en `src/builtins.dash` (sale de
    `docs/BUILTINS.md` de Dash, la misma fuente que la ayuda: no son dos fuentes distintas); el catálogo inglés de los
    textos 600 a 634 (de antes).
  - **Falta en Dash**: `dash --check` da solo el primer error (para en el primero); comprobar un módulo sin `Main`
    ("falta el bloque Main") o el texto sin guardar de un módulo dentro de su programa (algo como
    `--check main.dash --texto red.dash=T:x`); el ejemplo entero de las funciones cuyo `tests/test_doc_*.dash` no es el
    de su grupo (45, como los `sprite_*`: hoy sin Probar); añadir muchas líneas a una lista de MUI de una vez (llenarla
    de una en una cuesta unos 10 ms por línea en un A1200); y el directo acepta una función con el nombre de una
    variable global (`--gcc` da el error).
- 2026-11-17, rama `copiloto` (y `copiloto` de Inferencia): **1.6 hecho, Inferencia como copiloto**
  (`extensiones/Inferencia`, MIT).
  - **Decisión**: la extensión es un programa pequeño (Copiloto, 113 KB) que habla con Inferencia por ARexx, como Git
    con dashgit; no Inferencia en un "modo extensión". Así hay una sola Inferencia (su ventana, su clave, sus
    preferencias, su conversación, su gasto), el copiloto se carga con Forja sin cargar la red, y si Inferencia se
    cuelga, el copiloto no (le habla con `rexx_send_wait`, 5 s como mucho; Forja no espera a ninguno de los dos). Si
    Inferencia no está, la arranca (`ENV:Forja/inferencia`), con su ventana detrás (argumento `DETRAS`).
  - **Acciones**, en su menú Inferencia: preguntar sobre esto (Ctrl Alt I), explicar la selección, cambiar el código
    (Ctrl Alt C, una ventanita MUI para decir qué), documentar la función, escribir la prueba (un `prueba_x.dash`
    nuevo), explicar el error (Ctrl Alt E) y arreglarlo (Ctrl Alt G, antes F; si no hay errores de antes, compila primero),
    aceptar (Ctrl Alt Y), rechazar (Ctrl Alt N) y sugerencias al escribir. Las que cambian código son un `ENCARGO` de
    Inferencia (aparte de la conversación, solo puede leer: ficheros y la ayuda de Dash) y salen en una VISTA con las
    diferencias (subsecuencia común más larga, en Dash); `a` acepta con `CAMBIAR` (deshacer de Forja), `r` rechaza.
    Antes de aplicar, mira que las líneas sigan ahí; si se movieron, las busca. La zona Copiloto de la barra dice
    "pensando", "a / r" o "1 error"; su clic cancela, vuelve al cambio o lo arregla.
  - **Contexto**: el fichero (entero si cabe; si no, 60 líneas alrededor), lo que importa y la lista del proyecto,
    con tope de 16000 caracteres (`ENV:Forja/inferencia_tope`). Por `TEXTO` si está abierto (sin guardar, Latin-1),
    si no del disco (UTF-8 a Latin-1). `TEXTODISCO` no hace falta: Inferencia quiere Latin-1.
  - **Sugerencias al escribir**: apagadas al empezar (`ENVARC:Forja/inferencia_sugerencias`). Tras `CAMBIADO` (pausa
    de 900 ms) con el cursor al final de una línea, un `ENCARGO completar` (80 tokens, sin herramientas); Forja la
    enseña en gris y Tab la mete. Contra el servidor falso (HTTP, en el PC), de la última tecla a verla: 3,7 s en el
    A1200 emulado a toda velocidad (con la pausa de 0,9 s y el flujo SSE en trozos), 1,6 s en el 68040 de MUI 3.8 y 5 s
    con la CPU de un A1200 (`REAL=1`, contando que esa vez arrancaba Inferencia). Contra un
    modelo de verdad por HTTPS en un 68020 no sirve (el saludo de TLS ya tarda más de un minuto): por eso apagadas;
    con Ollama en la red local, o un Amiga rápido, puede valer.
  - **La API, versión 3**: `SUGERENCIA` (texto en gris tras el cursor; Tab lo mete; se va al escribir, al mover el
    cursor o con Esc; si la lista para completar está abierta, Tab es de la lista) y `VISTA` sin líneas cierra la
    pestaña. `forja_sugerencia` y `forja_cerrar_vista` en `lib/forja.dash`.
  - **MUI 3.8**: el copiloto solo usa una ventanita con un campo de una línea (va en 3.8). Inferencia, en 3.8, salía
    sin cuadro para escribir (Textinput no viene con MUI 3.8): ahora, sin Textinput, su ventana va con una línea.
  - **Pruebas** en FS-UAE: `tests/copiloto.sh` (Forja, el copiloto, la Inferencia de verdad, el servidor falso de
    Inferencia con `tests/guiones_copiloto`, la ayuda de Dash y dashc): TODO BIEN en MUI 5 (A1200, 3.1, dos veces) y en
    MUI 3.8 (`SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`, Inferencia con su ventana de una línea). Tras unir main (rama
    `ayuda`) siguen en TODO BIEN: extensiones_base, extensiones (MUI 5 y 3.8), git_panel, teclas, ficheros, rexx y ayuda
    (esta con un dashc.amiga que sabe `--check`); en Inferencia, encargo (nueva), clics, arexx, flujo, juntos (con la
    Forja de la rama) y sistema.
  - Tras unir main: `ERRORES` da también los errores marcados por `dash --check` si no hay de compilar (la ruta en
    minúsculas), así "Explicar el error" y "Arreglar el error" no tienen que compilar si Forja ya los marcó.
  - **Falta**: el botón Inferencia de Forja (Amiga-I) sigue dentro de Forja, aparte del copiloto (hace lo de
    "Preguntar sobre esto"; se podría pasar a la extensión, como pasó con git); los textos del copiloto, sin catálogo
    inglés (como Git); la sugerencia es de una línea y solo al final de la línea; "Escribir la prueba" no compila ni
    ejecuta la prueba; probar contra un modelo de verdad (la prueba usa el servidor falso) y en un Amiga de verdad.
  - **Falta en Dash** (apuntado, sin rodeos): `str_join` (unir una lista de textos; la extensión lleva su `unir`);
    que `mui_text_editor` sin Textinput (MUI 3.8) dé un campo de una línea en vez de nada (Inferencia elige la ventana
    ella misma); una petición de texto sencilla (como `mui_request` pero con un campo), para no hacer una ventana
    para una línea.
- 2026-11-17, rama `editor`: **fase 2 hecha, el editor cómodo** (2.1 a 2.8; lo pidió el usuario: "un editor potente y
  cómodo").
  - **2.1 Colores de la gramática**: `tools/sintaxis.py` escribe `src/sintaxis_datos.dash` desde Dash: las palabras de
    `compiler/grammar.py` con la clase que les da `tools/gen_tmgrammar.py` (los colores de VS Code; si la gramática
    trae una palabra nueva sin clase, para), los tipos del analizador y las instrucciones de `compiler/asm68k.py`.
    `--comprobar` dice si está al día. Nuevos colores: directivas (`@native`...), y en los bloques `asm ... end`
    instrucción (solo las que conoce el ensamblador), registro y etiqueta; la cabecera (`asm in d0 = a out r = d0 uses
    d2`) con `in`/`out`/`uses` y sus registros; `Close`, `Key`... solo tras `On`. Para saber si una línea está dentro
    de un bloque asm se mira hacia arriba solo hasta una línea que lo diga (300 como mucho), sin leer el fichero.
  - **2.2 Comodidades**: menú **Editor** nuevo (hecho en marcha, con las teclas que tenga cada orden): comentar
    (Ctrl /; en asm con `;`), duplicar (Ctrl D), subir y bajar (Ctrl Alt flechas: Alt solo ya es página), borrar
    líneas (Ctrl Mayús K), ir a la pareja (Ctrl M). La pareja (paréntesis, corchete, llave; y `func`/`if`/`while`/
    `asm`.../`end`, `elif`/`else` con su `if`) se ve en un recuadro con el cursor encima; sin pareja, en rojo.
    Cerrar solos `( [ { "` (solo con nada detrás, o algo que cierra; el que cierra pasa por encima; Retroceso entre
    los dos los quita; con selección, la rodea) y el `end` solo al pulsar Return tras abrir un bloque que no lo tiene
    (como `endwise.js` de la extensión de VS Code: un solo paso de deshacer). Las dos se apagan en el menú Editor
    (`ENV:Forja/cerrar_solo`, `ENV:Forja/auto_end`). `tests/teclas.dash` ya no escribe el `end` (lo pone Forja).
  - **Repintar menos**: el cursor que pasa a otra línea sin mover la vista repinta solo esas dos (antes, todo): 21 ms
    frente a 45 del dibujo entero (A1200 emulado con `REAL=1`, MUI 5). Con la pareja, también sus líneas.
  - **2.3 Buscar**: casilla "Expresión regular" (`regex_find` de Dash; `$1`-`$9` en lo que cambia; lo vacío no se
    queda dando vueltas); "Buscar en el proyecto" (Ctrl Mayús F, con lo del cursor) en todos los `.dash` y `.dashui`
    del cajón y los de dentro, con el texto sin guardar de los abiertos, a la salida con clic; "Cambiar en el
    proyecto" (Ctrl Mayús H): una pestaña con cada línea antes y después y una pregunta; los abiertos cambian en el
    editor (un paso de deshacer por fichero), los demás en el disco (en UTF-8 si lo estaban). `src/buscar.dash`.
  - **2.4 Lista rápida** (`src/rapido.dash`): una lista encima del editor que se filtra escribiendo (empieza por, lo
    tiene, sus letras en orden): esquema del fichero (Ctrl O, elegido lo de antes del cursor), abrir un fichero del
    proyecto (Ctrl P) e ir a un nombre de todo el proyecto (Ctrl T). Dibujada en el lienzo, no una ventana de MUI:
    igual en MUI 3.8 y 5.
  - **2.5 Marcadores**: Ctrl F3 pone o quita, F3 y Mayús F3 siguiente y anterior (dan la vuelta); una cinta en el
    margen, también junto a un punto de parada. Siguen a su texto al escribir (también deshacer); comentar o cambiar
    las mismas líneas no los mueve; subir o bajar líneas se los lleva. F8 sigue siendo el error. No se guardan al cerrar.
  - **2.6 Renombrar** (F2): con "dónde se usa" de `codigo.dash` (las locales, solo en su función), pide el nombre
    nuevo en la lista rápida y enseña los cambios como "cambiar en el proyecto". No deja un nombre que no vale, una
    palabra de Dash o uno que ya existe.
  - **2.7 Plegado** (F4 el bloque del cursor, Mayús F4 todo): el bloque enseña su primera línea con " ... end";
    las flechas, la rueda y los clics se saltan lo plegado; ir a una línea oculta la despliega; un clic en " ... end"
    también. Sin nada plegado, el dibujo hace las cuentas de siempre (ninguna más). Con un bloque plegado, el dibujo
    entero 66 ms frente a 64 sin él (A1200 emulado con `REAL=1`).
  - **2.8 Configurable**: `ENVARC:Forja/teclas` (ENV: primero): `orden = teclas` (`duplicar = alt d`,
    `comentar = nada`; letras por su sitio en un teclado inglés, signos por su carácter); `ENVARC:Forja/tema`: los
    colores (`comentario = 255 80 80`) y la fuente del código (`fuente = xen.font 8`, de ancho fijo). Lo que no se
    entiende se dice en la salida. **El teclado va al editor** también con el puntero en el proyecto, la salida o la
    barra de botones (antes esos lienzos se quedaban la tecla).
  - Pruebas: `tests/editor_base.sh` (sin ventana) y `tests/editor.sh` (como un usuario, con capturas): TODO BIEN en
    A1200 con MUI 5 (normal y `REAL=1`), RTG con MUI 5 y MUI 3.8 (`SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`).
    Siguen en TODO BIEN: teclas, ficheros, completar, buscar, errores, compilar, rexx, extensiones (MUI 5 y 3.8),
    extensiones_base, git_panel, ayuda (con el `dashc.amiga` de Dash PR #184) y copiloto (MUI 5, con el servidor
    falso de Inferencia). `tests/proyecto.sh` falla igual en
    `main` (a219701) con el Dash de hoy: el clic en el error de `fisica.dash` (cajón "Mi juego", con espacio) no lleva a
    su línea, y lo que sigue cae detrás. No es de esta rama; queda por mirar.
  - Tiempos (A1200 emulado con la CPU de un A1200, `REAL=1`, MUI 5): dibujo entero 45 ms (64 con el bloque asm a la
    vista, 66 con un bloque plegado); flecha abajo, 21 ms (dos líneas); Ctrl Mayús F hasta ver lo encontrado 0,96 s
    (con abrir la ventana de buscar; la búsqueda en `tests/prueba/editor`, 45 ms); el esquema 19 ms; la pareja de una
    función de 500 líneas 140 ms; partir una línea para los colores, como antes (un 5 % más). Con MUI 3.8 y en RTG
    (68040 JIT), todo por debajo de 10 ms salvo Ctrl Mayús F (0,2 s).
  - **Falta en Forja**: los marcadores y lo plegado no se guardan con la sesión; deshacer un cambio de varias líneas puede juntar sus marcadores en
    la primera; renombrar no cambia en pestañas sin nombre; cambiar en el disco pasa los tabuladores de las líneas
    cambiadas a espacios; la barra del editor no cuenta lo plegado; la lista de cambios es una pestaña que se cierra
    al contestar (no se puede mirar entera antes); las etiquetas del menú Editor salen con las teclas al empezar (si
    se cambia el fichero, hasta la próxima vez); `--gcc` no compila Forja (también en `main`: un `e->activa` sobre un
    entero en `extensiones.dash`, error de Dash), así que `tests/ventana.sh` no va.
  - **Falta en Dash** (apuntado, sin rodeos): **fallo del directo**: en `func color(nombre: String, r: Int, g: Int,
    b: Int) -> Int` que hace `r = Int(p[0])`, `g = ...`, `b = ...` dentro de un `if`, `./dash` deja `b` con su valor
    de antes (con `--gcc`, bien): `color("x", 120, 120, 136)` con "255 80 80" da 255, 80, 136 (la prueba, en
    `tests/editor.sh` con RTG: el color del tema no cambiaba). Forja lo evita sin cambiar los parámetros. `.has` de las listas en el directo ("aún no está"); una función que se
    llame `asm` pasa el análisis y rompe el C con `--gcc` (palabra reservada de C); `C:Copy` no está en el sistema de
    las pruebas (`sys31muisslweb`), la prueba escribe los ficheros ella misma.
  - De Dash PR #184 (llegó a la vez): `mui_request_text` serviría para el nombre nuevo de renombrar, pero la lista
    rápida ya va en MUI 3.8 y 5 sin ventana; `mui_list_add_lines`, para la lista de la ayuda (aquí no hay listas de
    MUI); `--check` con todos los errores, módulos sin Main y `--texto`: para la fase 3.5 (errores en cualquier
    fichero del proyecto); `str_join`, para quitar los "unir" a mano. Quedan para después.
- 2026-11-17, rama `ext-editores`: **1.5 hecho, los editores de sprites y de mapas son extensiones**
  (`extensiones/Sprites` y `extensiones/Mapas`, MIT), como decidió el usuario. Forja ya no tiene nada de sprites ni de
  mapas dentro (fuera `src/sprites.dash` y `src/mapas.dash`, las pestañas de sprite y de mapa, la salida que se ocultaba
  y su sonda): pesa 170 KB menos para quien solo programa.
  - **Cada una, su ventana** (MUI, una pestaña por fichero), con los mismos `sprites.dash` y `mapas.dash` de antes
    (Mapas importa el de Sprites para leer el tileset) y el tema de Forja. Arranca con el primer fichero suyo que se
    abre (`EDITAR`) o se pide nuevo (`NUEVO`), y acaba al cerrar la última pestaña. Menús Proyecto (Nuevo con
    Amiga-B, Abrir, Guardar, Guardar como, Compilar y Ejecutar el programa, Cerrar pestaña), Editar (deshacer,
    rehacer; en Sprites, cortar, copiar y pegar el fotograma; en Mapas, elegir el tileset) y Ventana > Forja. La vista
    animada se para cuando su ventana deja de ser la activa (como antes al cambiar de pestaña).
  - **La API, versión 4** (de forma general, en `docs/EXTENSIONES.md` y `lib/forja.dash`): `nuevo = título | orden |
    descripción` en el manifiesto (Proyecto > Nuevo de extensión..., Amiga-B, enseña los de todas y manda `NUEVO
    orden`); `GUARDADO nombre fichero` (Forja lo dice en la salida, lo pasa a las demás y lee otra vez el proyecto);
    `SINGUARDAR nombre` y sus ficheros con cambios (Forja pregunta por ellos al salir; con Guardar manda `GUARDAR` y
    espera, 20 s como mucho); `COMPILAR fichero` y `EJECUTAR fichero` (el programa del cajón de ese fichero, abierto o
    no: el `main.dash` del cajón de un sprite); `DELANTE` (la ventana de Forja). Abrir y el panel del proyecto ya
    llevaban los `tipos`; la petición de Abrir los deja elegir. Un fichero IFF sin extensión que lo abra no se abre
    como texto: se dice. En `lib/forja.dash`: `forja_guardado`, `forja_sin_guardar`, `forja_compilar`, `forja_delante`.
  - **Pruebas**: las 13 de sprites (`sprites`, `sprites_forja`, `_lapiz`, `_paleta`, `_herramientas`, `_tamano`,
    `_fotogramas`, `_cebolla`, `_animar`, `_codigo`, `_dibujo`, `_base`, `_iff`) y las de mapas (`mapas_base`,
    `mapas_forja`) ponen la extensión en el disco (`tests/extension.sh`) y miran su ventana y su sonda
    (`RAM:forja-sprites-sonda.txt`, `ENV:FORJA_SPRITES_LIENZO`...). Amiga-Q, en la ventana de Forja, pregunta por lo
    que tiene la extensión sin guardar. `sprites_forja` prueba ahora la API nueva: abrir desde el proyecto, guardar
    (Forja lo dice), Amiga-B en Forja y compilar desde el sprite. TODO BIEN en MUI 5 (A1200); `sprites` y
    `mapas_forja`, también en MUI 3.8 (`SISTEMA=~/.cache/dash-emu/sys32rtg38 RTG=1`) y `sprites` en RTG con MUI 5
    (`mapas_forja` ya no pide zoom 1 al empezar: en RTG empieza con 2). Tiempos (A1200 a toda velocidad): un clic en el proyecto hasta ver delante la
    ventana del sprite, 0,25 s; el dibujo entero, como antes (16x16 117 ms, 64x64 227 ms; un mapa, 225 ms).
- 2026-11-17, rama `ext-editores`: **el botón Inferencia pasa a la extensión** (el copiloto), como pasó con git.
  Forja no tiene nada de Inferencia dentro: fuera el botón de la barra, Programa > Preguntar a Inferencia (Amiga-I),
  la preferencia "Inferencia:" y su código (`ADJUNTAR`). El copiloto pone siempre su zona, Inferencia, a la derecha
  de la barra de botones (con el icono de antes); un clic sin nada pendiente es "Preguntar sobre esto", que ahora va
  con Amiga-I. "Dónde está Inferencia..." en su menú guarda `ENVARC:Forja/inferencia`. Sin el botón de la derecha,
  en 640 de ancho los ocho botones cabían con nombre y la zona de git ya no (lo vio `tests/git_panel.sh`): la barra
  cuenta ahora el sitio del texto de las zonas al decidir si los botones en gris llevan nombre.
- 2026-11-17, rama `ext-editores`: **catálogo inglés** de lo que faltaba. Los tr 600 a 634 ya estaban traducidos (la
  bitácora no lo decía); faltaban los nuevos (640 a 646). Las extensiones tienen ahora su catálogo: `@catalog
  "X.catalog"` y `tr()` en Git (28 textos), Inferencia (76, también lo que se le pide al modelo) y en Sprites y Mapas
  (los de antes de Forja, con su traducción, y los de sus ventanas). `tools/catalogos.py` hace los de Forja y los de
  todas las extensiones (`extensiones/X/catalogos/`), y `tools/paquete.py` los pone en `Extensiones/X/Catalogs`. El
  manifiesto, en otro idioma: `descripcion.english`, `menu.english`, `nuevo.english` (con el catálogo de Forja en ese
  idioma; Git, Inferencia, Sprites y Mapas los tienen).
- 2026-11-17, rama `ext-editores`: **`tests/proyecto.sh` arreglado.** No era el espacio de "Mi juego" ni las rutas
  de `dash --check`: con la CPU lenta (`REAL=1`, o el emulador cargado) una comprobación de un guardado anterior
  (`dash --check`, a prioridad -1) acababa después de compilar. Su resultado ("Sin errores.") quitaba los errores
  que acababa de marcar la compilación y añadía una línea a la salida, que se movía: el clic de la prueba caía fuera.
  Ahora, al compilar, la comprobación en marcha se para (lo guardado se comprueba después). TODO BIEN con y sin
  `REAL=1`. La prueba espera un poco más a que el clic llegue y, si falla, dice dónde estaba la salida.
- 2026-11-17, rama `ext-editores`: **paso 0.3, la memoria medida** (`tests/memoria.sh`, ver "Memoria mínima").
- Pruebas tras todo esto (rama `ext-editores`), TODO BIEN: en MUI 5 (A1200, 3.1) teclas, ficheros, completar, buscar,
  errores, compilar, ayuda, editor, editor_base, extensiones, extensiones_base, git_panel, botones, proyecto (también
  `REAL=1`), copiloto (con su servidor falso, bajo `flock`), las 13 de sprites y las 2 de mapas; en MUI 3.8
  (`sys32rtg38`, RTG) editor, ayuda, extensiones, git_panel_coffin, copiloto, sprites y mapas_forja.
  - **Falta en Forja**: los ficheros de una extensión (un sprite, un mapa) no se guardan en la sesión; sus pestañas son
    de su ventana, no de la de Forja; Amiga-Q en la ventana de una extensión no cierra Forja (va a Forja con Ventana >
    Forja); la prueba de memoria no pone aún un tope.
  - **Falta en Dash**: nada nuevo.
- 2026-11-17, rama `proyecto`: **pasos 3.1, 3.2, 4.1 y 4.2** (lo empezó otro agente: el `.forja` en
  `src/proyecto.dash`, seis plantillas en `plantillas/` con `tools/plantillas.py`, el menú Depurar con
  `src/expresion.dash` y Programa > Ejecutar con perfil y con memcheck). Cerrado con sus pruebas:
  - **Los puntos de parada siguen a su línea al escribir**, como los marcadores: el editor los mueve al meter, quitar,
    subir o bajar líneas (`ed_puntos_movidos` dice de dónde a dónde) y Forja mueve con ellos los del proyecto, con su
    condición y su contador. Al `.forja` van al guardar el fichero; al cerrar sin guardar (Descartar) vuelven a la línea
    del disco y se quitan los puestos después (`guardada` en cada punto). Depurando, el depurador sigue con los de antes,
    que son los del programa en marcha.
  - Memcheck pone a la vista su primer aviso al acabar (en 640x256 la salida enseña dos líneas y quedaba arriba).
  - Si Propiedades o Nuevo proyecto no se abren, Forja lo dice (texto 1005).
  - **Las pruebas fallaban por ellas mismas, no por Forja**: el ejecutable de `perfil.sh` se llamaba `Perfil`, como el
    cajón `perfil` (en el Amiga es el mismo nombre) y no arrancaba; activar la ventana ya es un evento y Forja miraba
    `FORJA_EVENTO` con él, y el Esc de después cerraba lo que se acababa de abrir (en MUI 3.8, Propiedades; con el
    depurador, la pregunta de la condición); con el emulador cargado las flechas llegan tarde. Ahora `menu()` pulsa Esc
    solo si hace falta, `a_la_linea` espera al cursor (`CURSOR`) y `responder` espera a ver la pregunta
    (`ENV:FORJA_RAPIDA`). `forja_proyecto.sh` arranca el Workbench con `RTG=1` (`--workbench`), que `wb_open` necesita.
    `plantillas.sh` saca las capturas cuando el programa aún está abierto (la 3D a los 25 s).
  - TODO BIEN: `proyecto_base`, `editor_base` (con los puntos que siguen), `depurar_mas` (también en MUI 3.8, y una
    línea nueva arriba baja el punto con su condición hasta el `.forja`), `plantillas` (las seis; la 3D en la máquina
    de CoffinOS con MiniGL) y `forja_proyecto` (en MUI 5 y en MUI 3.8, con el icono: Forja arranca desde
    `Barras.forja` con `wb_open`). La ventana Nuevo proyecto cabe en 640 de ancho.
  - **`perfil` falla en la parte del perfil por Dash**: dash (el directo, también el del Amiga) copia en línea las
    funciones pequeñas o de un solo sitio también con `--profile`, y la tabla solo tiene Main. La parte de memcheck va
    bien.
  - Las de antes, en esta rama (MUI 5, A1200 con 3.1), TODO BIEN: teclas, ficheros, completar, buscar, errores,
    compilar, depurar, ayuda, editor, editor_base, extensiones, extensiones_base, git_panel, proyecto, botones, sprites,
    mapas_base, mapas_forja y copiloto (con su servidor falso, bajo `flock`). `git_panel` y `copiloto` elegían su menú por su sitio en la barra (`input_menu`), y el
    menú Depurar los corre uno. `editor` falló una vez con el emulador muy cargado (Ctrl T) y pasó al repetirla.
  - Memoria (`tests/memoria.sh`): Forja quieta 2,7 MB de fast (antes 2,5) y compilando 4,6 (antes 4,4). Los 0,2 MB
    son el proyecto, las plantillas y el depurador nuevo.
  - **Falta en Dash**: con `--profile`, no copiar funciones en línea (como con `--debug`: `can_inline` de
    `dashc/src/gen68k.c`, y las de una línea puestas como expresión).
- 2026-11-17, rama `demos`: **paso 5.2, las herramientas de demos** en una extensión, `extensiones/Demos`: menú Demos y
  una ventana con cuatro páginas (Amiga-1 a 4), que también se abre con un `.sync` o un `.mod`. Uso en el README
  (sección Demos).
  - **Pistas de sincronía** tipo Rocket, en `plantillas/demo/sync.dash` (Dash puro, en la plantilla de demo y en
    `Forja/lib` del paquete): claves por fila de la música (posición × 64 + fila), escalón, lineal, suave o rampa, en
    `Fixed`. Fichero `.sync` de texto. La extensión las edita en una tabla con el teclado; Amiga-X las exporta a
    `pistas_datos.dash` (tablas en el programa: con `VIVO = false` la demo no necesita ni el `.sync` ni Forja).
  - **Cómo hablan la demo y Forja** (lo más ligero en un 68000): la demo abre el puerto ARexx `DEMOSYNC` y en cada
    imagen solo hace `rexx_get` (vacío casi siempre); la extensión manda algo solo al cambiar una clave (`CLAVE`,
    `QUITAR`, `PISTA`, `RECARGAR`, `PAUSA`, `SIGUE`, `IR`, `DELANTE`, `DETRAS`, `ACABAR`, y `VALOR` para las
    pruebas). Lo que se lee a menudo (fila, fotograma, líneas, anillo de 64 imágenes, perdidas) lo escribe la demo en
    un bloque de 160 bytes cuya dirección da `HOLA`; la extensión lo lee 5 veces por segundo con `peek_*`. Se descartó
    recargar un fichero en cada cambio (más trabajo en la demo: leerlo y analizarlo entero) y escribir en las listas
    de la demo desde fuera (frágil).
  - **Visor de MOD** (`mod.dash`): cabecera y patrones, la fila que suena resaltada; lo toca la extensión con
    `music_*` o sigue a la demo. Return mete la fila de sincronía en el código.
  - **Editor de copper** (`copper.dash`): paradas (línea y color de 12 bits), degradado o cambios secos, cualquier
    registro de color. Genera `copper_*` o una tabla de 256 colores para un bloque `asm`, entre `# copper: nombre` y
    `# fin copper: nombre`, con una línea `# paradas:` para volver a leerlo; si el bloque ya está en el fichero, lo
    cambia allí (`CAMBIAR`), si no lo mete en el cursor. `p` lo enseña en una pantalla propia con el copper de verdad.
  - **Medidor**: la demo mide con VPOSR/VHPOSR (`peek_word($DFF004/6)`) entre `sync_fotograma()` y `sync_fin()`; las
    64 últimas en barras, media, máximo, perdidas (por `time_ms`). También en la barra de Forja mientras corre.
  - La plantilla de demo usa todo esto: `sync.dash`, `demo.sync` (pistas "velocidad" y "subida" que mueven las
    barras), `pistas_datos.dash`, `musica.mod` si está, y `sync_fin` alrededor del bloque asm (unas 190 líneas por
    imagen, porque espera línea a línea).
  - Pruebas nuevas: `tests/demos_base.sh` (sin ventana; con la demo de verdad por DEMOSYNC; compila en el PC el código
    de copper que escribe) y `tests/demos_forja.sh` (con Forja y la demo en marcha; compila en el PC la demo con el
    copper y la versión final con lo exportado). `tests/mod_ejemplo.py` hace el MOD de prueba.
  - **Falta en Forja**: catálogo inglés de Demos (sus textos van sin `tr`); deshacer en las pistas; renombrar, quitar y
    ordenar pistas; una sola `.sync` abierta; el copper solo se elige con clic (no se arrastra) y solo cambia un
    registro por bloque; el copper no llega en vivo a la demo; el medidor no separa partes (lógica, dibujo); tamaño del
    ejecutable con tope de 4K/64K y Shrinkler (`HERRAMIENTAS_DISENO.md`); línea de tiempo de partes.
  - **Falta en Dash** (no se ha rodeado con `@native`):
    - `music_seek(pos, fila)`: hoy `music_position` salta al principio del patrón, así que `IR` y `g` van de patrón en
      patrón.
    - `music_tick()` y `music_speed()`: la fracción de la fila para interpolar dentro de ella; `sync.dash` la estima
      con los fotogramas que duró la fila anterior.
    - `music_playing()`: `sync.dash` lleva su propia variable (`sync_tocar`).
    - `beam_line()` (VPOSR y VHPOSR leídos a la vez, sin carrera) y `vblank_count()` (un contador de la interrupción de
      VBlank): hoy `peek_word` dos veces y las imágenes perdidas se calculan con `time_ms`. También saber si la
      pantalla es PAL o NTSC (313 o 263 líneas): hoy se supone PAL.
    - Listas de copper que se cambian ya instaladas (doble búfer): para mandar el copper a la demo en vivo.
    - `screen_save_png` (y `tools/amiga/shot.c`) leen el bitmap: el copper y los colores cambiados por la CPU no salen
      en las capturas; para probarlo haría falta una captura de la imagen de FS-UAE.
    - Esperar un clic en una pantalla sin ventana: `probar` mira el botón en el CIA (`$BFE001`), que no ve los clics
      de `input_click`.
  - Pruebas (rama `demos`), TODO BIEN: `demos_base` y `demos_forja` en MUI 5 (A1200 con chipset, 3.1) y `demos_forja`
    en MUI 3.8 (`sys32rtg38`, RTG); la plantilla de demo arranca y acaba (RC 0). Las de antes, en MUI 5: teclas,
    ficheros, compilar, extensiones, extensiones_base, editor_base, proyecto_base, sprites y mapas_base; en MUI 3.8:
    extensiones, sprites y mapas_forja.
  - **Lento**: un dibujo entero de la ventana de Demos tarda unos 0,8 s en los dos emuladores (lo apunta la sonda,
    `dibujo`). Con la demo en marcha se repinta como mucho 2,5 veces por segundo, con búfer. Una raya por línea en la
    vista del copper tardaba 10 s con MUI 3.8 y tarjeta: ahora va por franjas y con 4 niveles por color. Falta medirlo
    con `REAL=1` y pintar solo lo que cambia (la fila que suena, la columna de la pista).

- 2026-11-17, rama `pulido`: **lo que quedaba pendiente en las listas de "falta", para que Forja sea redonda**, y el
  paso 0.1 (Forja de punta a punta en la máquina CoffinOS).
  - **Demos, pintar solo lo que cambia.** La tabla de pistas y el visor de MOD van de página en página, como un
    tracker (antes se centraban en el cursor y en cada fila nueva se movía todo): al sonar, cambian dos filas. Con
    `mui_canvas_update_area` se dibujan solo esas filas, la línea de arriba y el estado de la demo (a la derecha de
    las pestañas, ahora al día con la tabla en cada lectura). El medidor barre como un osciloscopio: cada imagen en su
    sitio del anillo (la de ahora, vacía) y en cada lectura solo las barras nuevas, con dos cajas cada una (las rayas
    del 25 al 100 %, a la izquierda). Moverse por la tabla y escribir en una celda, igual. Si hace falta el dibujo
    entero y no toca (2,5 por segundo como mucho), queda pendiente para la siguiente lectura.
    - Medido con `REAL=1` (A1200 emulado, MUI 5): sin la demo, un dibujo entero 110-120 ms y una fila 4-5 ms; con la
      demo en marcha (que gasta la CPU esperando línea a línea) un dibujo entero 500-600 ms y lo que se dibuja ahora en
      cada fila nueva, unos 20 ms. En la máquina CoffinOS (68040 JIT, MUI 3.8) 40 ms y menos de 1 ms. Con la demo, de
      cada 100 dibujos unos 60 son ya de una parte.
  - **Demos, lo demás**: deshacer y rehacer en las pistas (Amiga-Z, Amiga-R; el texto de todas antes de cada cambio,
    64 pasos), cambiar el nombre de una pista (`r`, en la tabla, con el nombre de ahora), quitarla (Mayúsculas+Supr) y
    moverla (Alt+flechas), también en un menú Pistas; a la demo le llega todo con `RECARGAR`. Sus textos van con `tr`
    y tienen catálogo inglés (`extensiones/Demos/catalogos`), como las demás.
  - **Sesión**: `ENVARC:Forja/sesion_estado` guarda de cada fichero el cursor, la primera línea que se ve, los
    marcadores y lo plegado, y cuál estaba delante (con el carácter 30 entre ficheros: `env_get` lee una línea). Los
    ficheros de las extensiones (un sprite, un mapa, las pistas y el MOD de Demos) van en la sesión: la API 5 trae
    `EDITANDO` (`forja_editando`), y al empezar se abren con su extensión como desde Abrir.
  - **Depurador**: al "Guardar como", los puntos de parada (con su condición y su contador) pasan a la ruta nueva, y el
    `.forja` se escribe (también si el fichero sale del proyecto). Los de un fichero sin nombre pasan a los del proyecto.
  - **Editor**: deshacer y rehacer un cambio de varias líneas deja los marcadores en sus líneas (cada cambio que quita
    varias líneas apunta los marcadores y lo plegado que había en ellas, y al volver a meterlas se ponen como estaban;
    antes se juntaban en la primera); renombrar cambia también en las pestañas sin nombre; cambiar en el disco no pasa
    los tabuladores a espacios (lo cambiado se pone en la línea con sus tabuladores: `bp_con_tabs`); la barra del
    editor va en filas de las que se ven (lo plegado no cuenta); Forja vigila `ENV:Forja/teclas` y `ENVARC:Forja/teclas`
    (`file_notify`) y al cambiar las lee otra vez y pone al día las etiquetas del menú Editor (`mui_set_text`).
  - **Extensiones**: Amiga-Q en la ventana de Sprites, Mapas o Demos cierra Forja como en la suya (orden `SALIR`,
    `forja_salir`: Forja pregunta por lo que haya sin guardar); las opciones sueltas del menú Extensiones se ponen en
    marcha con `mui_menu_extend` (solo las que hay; antes 12 vacías y apagadas en `ventana.dashui`); probado instalar
    desde un cajón con el gestor (la ruta por `ENV:FORJA_INSTALAR` con la sonda, sin la petición de ASL); la prueba de
    memoria tiene topes que la hacen fallar (paso 0.3).
  - **MUI 3.8**: "Buscar en la ayuda..." deja el cursor en el campo: al activarse la ventana se le da, y otra vez
    150 ms después (algo de MUI 3.8 se lo quitaba justo después). La prueba ya no necesita el clic.
  - **De punta a punta en CoffinOS** (`tests/coffin.sh`, la máquina `coffin` de Dash: el disco de CoffinOS, 68040 con
    JIT, RTG de 1280x1024, MUI 3.8): un proyecto de cada plantilla y compilarlo (0,3 s; la demo 1,1 s), ejecutar la
    orden con los argumentos del proyecto, un error marcado al guardar y quitado al arreglarlo (0,5 s), depurar con un
    punto de parada (0,3 s hasta parar), git (init, commit y la rama), F1, un sprite con Amiga-B y la demo con Demos (se
    conecta en 1,3 s). Lo que se vio y se arregló:
    - las pestañas de dos ficheros que se llaman igual (el `main.dash` de cada proyecto) no se distinguían: ahora
      llevan delante su cajón (`Cueva/main.dash`);
    - en Demos, el estado de arriba ("demo: fila 31") iba detrás de la tabla ("suena la fila 38"): se pone al día con
      cada fila.
  - Memoria (`tests/memoria.sh`, A1200 con MUI 5, fast): sin extensiones 2,8 MB quieta y 4,8 compilando; con todas
    (Git, el copiloto, Sprites y Mapas) 3,2-3,8 MB quieta, 5,2-5,8 compilando y 4,4 con un sprite y un mapa. Tras
    salir quedan 1 MB (MUI y las fuentes), igual la segunda vez.
  - **Lo que encontraron las pruebas de siempre** al pasarlas todas (y que fallaba igual en `main`):
    - el panel de las variables ya no se movía con las flechas (desde que el teclado va al editor con el puntero en
      el panel, rama `editor`): depurando, las flechas sobre el panel vuelven a ser suyas (`tests/arbol.sh`);
    - Amiga-Z de más (sin nada que deshacer) repintaba todo: en un fichero de 1500 líneas cada una tardaba medio
      segundo y se quedaban en cola, y el Amiga-R de después llegaba tarde (`tests/grande.sh`); ahora no dibujan nada;
    - Git por su puerto ARexx usaba el proyecto de antes si el suceso PROYECTO aún no le había llegado (un guion que
      abre un proyecto y manda `GIT init` enseguida): ahora pregunta antes a Forja (`tests/coffin.sh`);
    - las pruebas: `salida.sh` y `nuevo.sh` escribían los `end` que ya pone Forja (fase 2) y van sin el end solo;
      `nuevo.sh` y `diseno.sh` miraban el texto antes de que Forja acabara con las teclas y ahora esperan (hasta 5 s).
  - **Pruebas** (todas en FS-UAE): en MUI 5 (A1200, 3.1) TODO BIEN teclas, ficheros, completar, codigo_base, compilar,
    salida, botones, clic, proyecto, grande, errores, parar, salir, sesion, rexx, diseno, depurar, arbol,
    depurar_ventana, buscar, pantalla, git, actualizar, extensiones_base, extensiones, ayuda_base, ayuda, editor_base,
    editor, memoria (nada, git y todas), proyecto_base, forja_proyecto, plantillas, depurar_mas, perfil (con el Dash de
    hoy ya pasa entero), demos_base, demos_forja (también `REAL=1`), git_panel, git_panel_coffin, sprites_todas (las
    13), mapas_base, mapas_forja y nuevo; en MUI 3.8 (`sys32rtg38`, RTG) extensiones, editor, ayuda (sin el clic en el
    campo), sprites, mapas_forja, demos_forja, forja_proyecto, depurar_mas y perfil; el copiloto con el servidor falso
    de Inferencia (bajo `flock`) en MUI 5 y en MUI 3.8; y `coffin.sh` en la máquina CoffinOS. `ventana.sh` sigue sin ir (necesita `--gcc`, ver abajo).
  - **Falta en Forja**: las pestañas que no caben se salen por la derecha (no hay desplazamiento; con el cajón delante
    de los nombres repetidos se llenan antes); los puntos de parada no vuelven a su línea al deshacer un cambio de
    varias líneas (los marcadores sí); la lista de cambios de "cambiar en el proyecto" y renombrar es una pestaña que
    se cierra al contestar; teclas de las extensiones fuera del editor; paneles dentro de la ventana; probar instalar
    un `.lha` (el emulador no tiene `C:LhA`). En Demos: una sola `.sync` abierta; el copper solo se elige con clic y
    cambia un registro por bloque, y no llega en vivo a la demo; el medidor no separa partes; tamaño con tope de
    4K/64K y Shrinkler; línea de tiempo de partes. En el copiloto: la sugerencia es de una línea; "Escribir la prueba"
    no la compila; probarlo contra un modelo de verdad y en un Amiga de verdad (aquí, el servidor falso).
  - **Falta en Dash** (apuntado, sin rodeos con `@native`):
    - `mui_menu_separator` no devuelve un objeto: la raya de encima de las opciones sueltas de Extensiones no se
      puede quitar cuando no queda ninguna (`mui_menu_remove`).
    - Un solo `mui_timer` por programa y ninguna forma de mandarse un evento a sí mismo: `SALIR` de una extensión
      llega por el reloj y se pierde el tic que hubiera (Forja lo vuelve a armar). Algo como `mui_post_event(id)`.
    - `env_get` lee una sola línea (la sesión separa los ficheros con el carácter 30).
    - El Dash de Python (`--gcc`) no puede con Forja: "maximum recursion depth exceeded" al transpilar (con
      `sys.setrecursionlimit(20000)` transpila), y su gramática no acepta `f().campo = x` (el directo sí; Forja ya no
      lo usa). Por eso `tests/ventana.sh` no va.
    - Los de antes (no se ha mirado si ya están): `music_seek`, `music_tick`/`music_speed`, `music_playing`, `beam_line` y `vblank_count`,
      PAL/NTSC, listas de copper cambiables ya instaladas, capturas con el copper, esperar un clic sin ventana; `.has`
      de las listas en el directo; `cx_wait` con el puerto ARexx; `rexx_send` con tiempo de espera.

- 2026-11-17, rama `remate`: **los últimos pendientes de Forja** de las listas de "falta".
  - **Pestañas que no caben** (`src/editor.dash`): la de delante siempre se ve (si cambia, las pestañas se mueven
    hasta ella) y a la derecha salen tres botones: mover a la izquierda, a la derecha y la lista de todas. La rueda
    sobre las pestañas también las mueve. Órdenes nuevas del editor (y en el menú Editor, cambiables en
    `ENVARC:Forja/teclas`): `pestana_siguiente` (Ctrl Tab), `pestana_anterior` (Ctrl Mayús Tab) y `pestanas` (Ctrl
    E, la lista: la lista rápida con las abiertas, que se filtra escribiendo). Probado en 640 de ancho con 12 ficheros
    de nombre largo (`tests/pestanas.sh`).
  - La lista rápida usaba `LR_FILAS` (12) para saber si la elegida se veía y un ancho que no cabía en un editor
    estrecho: en 640x256 el nombre y el detalle se pisaban y la elegida quedaba fuera. Ahora, con las filas y el ancho
    que caben de verdad (el detalle se corta por delante: `../pestanas/`).
  - **La lista de cambios** de cambiar en el proyecto y renombrar ya no es una pregunta modal (no dejaba mirar la
    lista): la pestaña Cambios (`*cambios`) se queda abierta y se contesta en ella, Return hace los cambios y Esc no
    (o se cierra). Se puede ir a otras pestañas y volver. Antes de cambiar, mira que las líneas sigan como en la lista
    (`bp_al_dia`); si no, no cambia nada y lo dice.
  - **Los puntos de parada vuelven a su línea al deshacer** un cambio de varias líneas, como los marcadores: el
    `Cambio` apunta los puntos de las líneas quitadas (`puntos`, y cuál pasó a la primera, `punto_junto`). Al volver a
    meterlas, el que se quedó vuelve a su sitio (main le lleva la condición) y los que se fueron vuelven como nuevos
    (`puntos_antes` -1): main los saca de su papelera (`puntos_papelera`, los que se fueron con su línea, 64 como
    mucho) con su condición y su contador.
  - **Demos**: varios `.sync` abiertos a la vez (`SyncFichero`: el de delante vive en `sync_pistas`, los demás en
    texto con su cursor y su deshacer). Tab y Mayúsculas+Tab pasan de uno a otro, Proyecto > Cerrar estas pistas
    cierra el de delante, al salir pregunta por cada uno con cambios, y la sesión y Forja (`SINGUARDAR`, `EDITANDO`)
    los saben todos. A la demo solo le llegan los cambios de su `.sync` (`mandar_pistas`); si se conecta con uno que no
    está abierto, se abre detrás. El copper: un clic en la lista elige la parada, arrastrar en la vista la mueve, y Tab
    lee el bloque de copper siguiente del fichero (Mayúsculas+Tab, el anterior).
  - **Un fichero con su `Main` dentro de un proyecto** (una prueba, una herramienta) se compila y se ejecuta él mismo
    (con las opciones de compilar del proyecto, sin su ejecutable ni sus argumentos); antes, Compilar y Ejecutar iban
    siempre al principal. Con eso, **el copiloto ejecuta la prueba que escribe** al aceptarla (su salida, en la de
    Forja).
  - **Tope de tamaño** del ejecutable en el proyecto (`tope` en el `.forja`, en Propiedades > Compilar): al compilar,
    Forja dice lo que pesa el ejecutable y avisa si pasa del tope (para intros de 4 y 64 KB).
  - README en castellano e inglés como es Forja 0.7 (el inglés no tenía la ayuda de Dash, los errores marcados ni
    Demos). Forja no tiene otra ayuda propia: el paquete lleva los README como `LEEME` y `README`.
  - De Dash PR #190 (llegó durante el remate): **Depurar > Cambiar valor...** con `dbg_set` (la variable del último
    clic en el panel, también lo vigilado, o la del cursor; "nombre = valor" en la pregunta de la lista rápida; lo que
    no se puede cambiar se dice con el porqué de Dash), y **el icono de los `.forja` con `icon_save`** en lugar del
    `.info` escrito a mano en hexadecimal: la imagen del yunque va en el paquete (`Forja/Iconos/proyecto.info`, de
    `tools/plantillas.py`), y Forja le pone su ruta como herramienta; sin ella, el icono de proyecto del sistema.
  - **Pruebas** (FS-UAE). En MUI 5 (A1200, 3.1), TODO BIEN: teclas, ficheros, completar, codigo_base, compilar,
    salida, botones, clic, proyecto, grande, errores, parar, salir, sesion, rexx, diseno, depurar, arbol,
    depurar_ventana, buscar, pantalla, extensiones_base, extensiones, ayuda_base, ayuda, editor_base, editor, pestanas
    (nueva), memoria (nada y todas), proyecto_base, forja_proyecto, plantillas, depurar_mas, perfil, demos_base,
    demos_forja, git_panel, git_panel_coffin, sprites_todas (las 13), mapas_base, mapas_forja, nuevo; bajo `flock`, git,
    actualizar y copiloto. En MUI 3.8 (`sys32rtg38`, RTG), TODO BIEN: extensiones, editor, pestanas, ayuda, sprites,
    mapas_forja, demos_forja, forja_proyecto, depurar_mas, perfil y copiloto. `tests/coffin.sh` en la máquina CoffinOS: TODO BIEN.
  - **`memoria.sh` con git falla** por poco: compilando, 5,7 MB de fast con un tope de 5,6. Falla igual con la Forja
    de `main` (5,69 MB) y el Dash de hoy (PR #190, compiladores rehechos): no es del remate. Hace falta mirar si el
    dash del Amiga gasta más al compilar (unos 2,07 MB frente a 1,9) o subir el tope.
  - Las pruebas que cambian de pestaña con un clic (`proyecto`, `sesion`) usan la flecha de los botones si la
    pestaña no se ve; `sesion` ya no cuenta "botones:" como una pestaña.
  - **El arrastre del copper** solo se ha visto en MUI 3.8 (la parada se mueve con el primer movimiento; el suceso
    de soltar no llega). En MUI 5, `input_drag` no da ningún suceso de arrastre en el lienzo de Demos (con búfer): la
    prueba lo dice y no lo mira. Falta probarlo con el ratón de verdad.
  - **Falta en Forja**: teclas de las extensiones fuera del editor; paneles dentro de la ventana; probar instalar un
    `.lha` (el emulador no tiene `C:LhA`). En Demos: el copper cambia un registro por bloque y no llega en vivo a la
    demo; el medidor no separa partes (lógica, dibujo); Shrinkler; línea de tiempo de partes. En el copiloto: la
    sugerencia es de una línea; probarlo contra un modelo de verdad y en un Amiga de verdad.
  - **Falta en Dash** (apuntado, sin rodeos con `@native`):
    - `input_drag` sobre un lienzo con `mui_canvas_buffered` (el de Demos): en MUI 5 no llega ningún suceso de
      arrastre; en MUI 3.8, solo el primer movimiento, sin el de soltar. En Sprites (sin búfer) sí llegan. Por mirar si
      es del directo (`dashc/runtime`) o de `input_drag`.
    - `tools/paquete_amiga.py` de Dash mete Forja en el paquete: debería llevar también `Forja/Iconos/proyecto.info`
      (de `tools/plantillas.py` de Forja); sin él, los `.forja` nuevos salen con el icono de proyecto del sistema.
    - Los de la lista de `pulido` siguen: `music_seek`, `music_tick`/`music_speed`, `music_playing`, `beam_line`,
      `vblank_count`, `mui_post_event`, `env_get` de varias líneas, `mui_menu_separator` que devuelva su objeto.


- 2026-11-17, rama `cierre`: **lo que quedaba de Forja para cerrar el plan.**
  - **API 6 de las extensiones: paneles dentro de la ventana de Forja** (`src/paneles_ext.dash`). Un panel es una
    pestaña más junto al panel del proyecto (lado `izquierda`) o junto a la salida (`abajo`): con un panel en un lado,
    la fila del título de ese lado son pestañas (la de Forja y las de los paneles). Forja lo pinta con lo que manda la
    extensión (líneas con un color, la elegida, botones abajo y una entrada de una línea), así que no hace falta otra
    ventana ni que la extensión esté despierta para repintar. Órdenes `PANEL`, `PANELVER` (con `entrada`, el teclado a
    la entrada), `PANELCERRAR`, `PANELBOTONES` (`texto|orden|corto`: los cortos si los largos no caben en una fila),
    `PANELENTRADA`, `PANELCURSOR` y `PANELES`; sucesos `PANEL título|línea|columna|otra`, `PANELTECLA`, `PANELBOTON` y
    `PANELTEXTO`. Un clic en el panel le da el teclado (flechas, Return, letras, Tab a la entrada, Esc vuelve); un clic
    en el editor, `VISTA` o `ABRIR` lo devuelven al editor. La barra y la rueda de su lado lo mueven. 8 como mucho; se
    van con su extensión. En `lib/forja.dash`: `forja_panel`, `forja_panel_ver`, `forja_panel_cerrar`,
    `forja_panel_botones`, `forja_panel_entrada`, `forja_panel_entrada_texto`, `forja_panel_cursor`,
    `forja_panel_estado` y `forja_campo`. Documentado en `docs/EXTENSIONES.md` (Paneles).
  - **Teclas de las extensiones en toda la ventana**: con el puntero en el proyecto, la salida o la barra de botones,
    con un panel con el teclado y sin ningún fichero abierto (antes, solo sobre el editor con un fichero).
  - **Git usa un panel**: el panel Cambios ya no es una ventana suya (fuera `git.dashui`): pestaña Cambios junto al
    proyecto, `[x] M ruta` por fichero, el mensaje en la entrada, Diferencias, Preparar todo, Quitar todo y Confirmar
    (Dif, Todo, Nada y OK si no caben). Casilla o Espacio, add/reset; segundo clic o Return, diferencias; Return en el
    mensaje, commit.
  - **El copiloto usa dos**: Cambiar el código... pide qué cambiar en el panel Inferencia de abajo (fuera
    `copiloto.dashui`), que dice cuándo Inferencia está con ello y, al llegar el cambio, tiene Aceptar y Rechazar.
    **Escribir la prueba** la ejecuta al aceptarla y enseña el resultado en el panel Prueba (cuántas "bien:" y cuántas
    "FALLO", cada línea en su color, Otra vez y Abrir la prueba), y la cuenta en la salida.
  - **Sugerencias de varias líneas y en medio de una**: `SUGERENCIA` acepta varias líneas y el cursor en medio de una
    línea. La primera se ve desde el cursor; las demás, encima de las de debajo como una capa (con una raya a la
    izquierda), y lo que había tras el cursor, detrás de la última, como quedará. Tab la mete de una vez. El copiloto la
    pide al final de una línea, en medio (con lo de antes y lo de después) o en una línea vacía tras un `func`, `if`,
    `while`... (el cuerpo), 8 líneas como mucho, y quita lo que repita de antes o de después del cursor.
  - **Arreglos**: `EJECUTAR fichero` con un `.dash` abierto con su `Main` lo ejecuta a él (el copiloto ejecutaba
    `main.dash` en lugar de la prueba); los menús propios de las extensiones llevan 12 opciones (al del copiloto, con 11,
    le faltaba Dónde está Inferencia, y Forja lo decía en la salida al arrancar).
  - **Instalar desde un `.lha`, probado**: `tests/extensiones.sh` pone en el emulador un LhA del Amiga (`LHA_AMIGA`; por
    defecto el de `~/.cache/caffeine-prueba`, no va al repositorio), la prueba hace con él `Hola.lha` y lo instala con
    el gestor.
  - **Demos** (`extensiones/Demos`, `plantillas/demo/sync.dash`):
    - **El copper cambia varios registros por bloque**: cada registro con sus paradas (COLOR00 a COLOR31, BPLCON0/1/2,
      BPL1MOD, BPL2MOD, DIWSTRT/STOP, DDFSTRT/STOP); los colores en degradado o secos, los demás secos o lineales. El
      código pone una espera por línea con cambios y en ella los `copper_color` o `copper_move` de todos; en modo
      tabla, una tabla por registro. Una línea `# registro: NOMBRE modo l:v ...` por registro (los bloques viejos con
      `# paradas:` se leen). Teclas: izquierda/derecha otro registro, `a` añade, Mayúsculas+Supr quita, `c`/`C` lo
      cambian, `d` el modo, `+ - < >` el valor.
    - **El medidor separa partes**: `sync_medir(nombre)` en la demo (4 como mucho; lo de antes de la primera, "otro").
      El bloque de memoria pasa a la versión 2 (868 bytes: nombres en +164, lo de cada parte por imagen en +228; la
      extensión sigue leyendo la 1). Barras apiladas en colores con la media de cada parte. La plantilla mide "lógica"
      y "barras".
    - **Línea de tiempo de partes** (página 5, Amiga-5, `extensiones/Demos/partes.dash`): una barra con una caja por
      parte y la fila que suena, y la lista editable (cifras, `+ - < >`, `n`, `r`, Supr, `g` lleva la demo al
      principio de la parte; con el deshacer de las pistas; avisa si dos se pisan). Van en el `.sync` (`parte nombre
      desde hasta`; `sync.dash` las lee en `sync_partes` y da `sync_parte_de(fila)`). `c` mete o cambia el bloque
      `# partes:` (una constante `PARTE_X` por parte, `parte_de(fila)` y `parte_cambio(fila)` con `parte_actual` y
      `parte_primera`); `l` lo vuelve a leer. La plantilla trae "entrada" y "barras" con su bloque.
    - **Dónde se enchufa lo de Dash cuando llegue** (otra tarea lo añade): `music_seek(pos, fila)` en `sync_ir` de
      `sync.dash` (hoy `music_position(fila / 64)`) y en la tecla `g` de `sync_tecla`, `partes_tecla` y `musica_tecla`
      de `demos.dash`; `music_tick()`/`music_speed()` en `sync_parte()` y en la cuenta de `_sync_por_fila` y
      `_sync_cuenta` de `sync_fotograma`; `music_playing()` en `sync_musica`/`sync_tocar` y en `suena` (`tocar()`) de
      `demos.dash`; `beam_line()` en `sync_linea()` (hoy dos `peek_word`); `vblank_count()` en `sync_fotograma`, para
      las imágenes perdidas (hoy por `time_ms`); PAL/NTSC en `SYNC_LINEAS_PAL` (`sync_fin`, `_sync_apuntar`) con un
      campo nuevo en el bloque para que `medidor_barra` y `medidor_texto` escalen a 263 o 313 líneas; el copper en vivo,
      una orden nueva de DEMOSYNC (`COPPER fichero`) en `_sync_orden` que rehaga la lista con doble búfer con la lógica
      de `cu_instalar` de `copper.dash`, mandada desde `copper_tecla` o `al_codigo` con la demo conectada.
  - **Las pruebas**: `tests/extensiones.dash` con las teclas de Eco en la salida, el proyecto y la barra, sus dos
    paneles (Lista y Charla), la sugerencia de dos líneas en medio de una y el `.lha`; `tests/git_panel.dash` con el
    panel en Forja (clics por `ENV:FORJA_PANELES`); `tests/copiloto.dash` con el panel Inferencia, el panel Prueba y una
    sugerencia de dos líneas (`tests/guiones_copiloto/encargo_completar.json`). `ENV:FORJA_PANELES` va en una sola línea
    (separada con el carácter 30): `env_get` lee una línea, y la prueba hacía clic en (0, 9), el botón de cerrar de la
    ventana.
  - **Contra un modelo de verdad**: el copiloto con Inferencia y qwen3-coder:30b (Ollama en la red de casa) en el
    emulador. Pedida como "el cursor está al final de la línea 14", el modelo repetía la línea ("Print sal"); ahora la
    sugerencia se pide con el código y una marca `<<CURSOR>>` donde va (como un "rellenar en medio"), y da `udo("Amiga")`
    en unos 9,5 s. La prueba con el servidor falso sigue dando las dos líneas de su guion.
  - **Con Dash PR #193** (llegó durante esta rama): `SALIR` de una extensión llega con `mui_post_event` (antes, por el
    reloj, y se perdía el tic); la raya de encima de las opciones sueltas de Extensiones es de `mui_menu_separator` y se
    va con ellas; `tests/ventana.sh` va otra vez (Forja compila por `--gcc`). Los de demos (`music_seek`, `beam_line`,
    `vblank_count`, `video_pal`, `copper_set`...) los enchufa en Demos otra tarea de esta rama (ver abajo).
  - `tests/proyecto.dash` fallaba igual en `main` (la pestaña cambiaba tarde con la comprobación en marcha): espera
    hasta 1,5 s. `tests/proyecto_base.dash` no compilaba en `main` (usaba `pl_icono_hex`, que se fue con `icon_save`).
  - Instalar un `.lha` borraba su cajón temporal con `C:Delete`, que el sistema de pruebas no tiene: ahora lo borra Forja.
  - **Demos con los builtins de Dash PR #193** (c90b619; ya no son "dónde se enchufará"): `sync_linea` es `beam_line`;
    las imágenes perdidas, con `vblank_count`; `sync_parte` con `music_tick`/`music_speed`; `sync_ir` con `music_seek` a
    la fila exacta (también `g` en Sincronía y Partes y las flechas del visor de MOD); `suena` es `music_playing()`; el
    bloque pasa a la versión 3 (en +868 las líneas de una imagen, `beam_lines`) y el medidor escala con 313 o 263.
    **El copper llega en vivo a la demo**: la orden `COPPER` de DEMOSYNC lleva la lista (la demo la rehace y contesta
    `copper_count`); si solo cambian valores, `COPPERSET i:valor` y la demo usa `copper_set`. **El arrastre del copper**
    se prueba: al elegir y arrastrar una parada se pinta solo la columna de marcas y la lista (antes, el lienzo entero,
    1,1 s con la demo en marcha, y el soltar llegaba tarde); la vista entera, al soltar. demos_base (64 bien) y
    demos_forja en MUI 5 y 3.8 (62 bien), TODO BIEN.

  - **Pruebas** (rama `cierre`, FS-UAE). En MUI 5 (A1200, 3.1), TODO BIEN: teclas, ficheros, completar, codigo_base,
    compilar, salida, botones, clic, proyecto, grande, errores, parar, salir, sesion, rexx, diseno, depurar, arbol,
    depurar_ventana, buscar, pantalla, extensiones_base, extensiones (con paneles, teclas, sugerencia y `.lha`),
    ayuda_base, ayuda, editor_base, editor, pestanas, memoria (nada y todas), proyecto_base, forja_proyecto, plantillas,
    depurar_mas, perfil, git_panel (el panel en Forja), git_panel_coffin, sprites_todas, mapas_base, mapas_forja, nuevo,
    demos_base y demos_forja; el copiloto con el servidor falso (bajo `flock`). En MUI 3.8 (`sys32rtg38`, RTG), TODO
    BIEN: extensiones, editor, pestanas, ayuda, sprites, mapas_forja, forja_proyecto, depurar_mas, perfil, demos_forja
    y el copiloto. `tests/coffin.sh` en la máquina CoffinOS: TODO BIEN. `tests/ventana.sh` va. El copiloto contra
    qwen3-coder de verdad: la sugerencia correcta en 9,5 s (la prueba espera la del guion falso, así que "falla").
  - **Falta en Forja**: Shrinkler (el tope de 4K/64K ya está); NTSC sin probar en una máquina NTSC; el copiloto en un
    Amiga de verdad; los paneles son de texto (una extensión que dibuje sigue con su ventana); con MUI 3.8, un menú
    propio añadido con la ventana abierta la cierra y la abre.
  - **Falta en Dash**: nada nuevo (lo de la lista de `remate` llegó en PR #193; `env_get_text` aún no se usa: la sesión y
    `ENV:FORJA_PANELES` siguen con el carácter 30).
