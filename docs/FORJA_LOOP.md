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

## Plan

Cada paso dice de quién es: **[F]** Forja, **[D]** Dash, **[G]** dashgit, **[I]** Inferencia, **[V]** extensión de
VS Code.

### Fase 0. Base
- 0.1 [F] Probar Forja en la máquina CoffinOS emulada y apuntar lo que falle.
- 0.2 [F] Borrar las ramas ya fusionadas (`git log main..rama` vacío) y sus worktrees.
- 0.3 [F] Medir la memoria de Forja con un proyecto mediano y fijar el tope.

### Fase 1. Sistema de extensiones
- 1.1 [F] Manifiesto, carga, ciclo de vida y gestor de extensiones.
- 1.2 [F] API por ARexx (la lista de arriba) y su documentación, `docs/EXTENSIONES.md`.
- 1.3 [F] Un módulo de Dash para escribir extensiones, más una extensión de ejemplo con su prueba.
- 1.4 [G][F] Git como extensión: las salidas para máquinas de dashgit, la rama en la barra, marcas, panel de
  cambios y diferencias. Ya está empezado, en módulos que luego pasan a la extensión.
- 1.5 [F] Editores de sprites y de mapas como extensiones.
- 1.6 [I][F] Inferencia como copiloto:
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
- 3.1 [F] Fichero de proyecto `.forja` con opciones y argumentos.
- 3.2 [F] Plantillas de proyecto: orden, MUI, juego y demo.
- 3.3 [D] Ayuda generada desde Dash: un fichero con índice, más AmigaGuide, metida en el paquete del Amiga.
- 3.4 [F] Panel de ayuda: la ficha entera, búsqueda, enlaces y un botón "Probar".
- 3.5 [D] Opción "solo comprobar", y [F] errores marcados en el código al guardar.

### Fase 4. Depurar y medir
- 4.1 Puntos de parada con condición, vigilar variables y ver el valor bajo el ratón.
- 4.2 Perfil y memcheck con vista propia.
- 4.3 Medir y acelerar lo que tarda en compilar en el Amiga.

### Fase 5. Demos, juegos y 3D
- 5.1 [D] Ensamblador en línea, por los dos caminos de Dash.
- 5.2 [F] Herramientas de demos: pistas de sincronía, visor de MOD, editor de copper y medidor de rasterlines.
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
