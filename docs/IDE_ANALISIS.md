# Forja: dónde está y qué le falta para ser el mejor IDE del Amiga

Fecha: 2026-11-16. Análisis, sin tocar ningún repositorio.

Cómo leerlo: lo que digo de Forja, Dash, dashgit e Inferencia lo he mirado en el código, los docs y `git log`.
Lo que digo de otros IDE (StormC, GoldED, AsmPro...) es de memoria: no lo he comprobado aquí. Va marcado.

Tres cosas que no coinciden con el encargo:

- Las ramas de Forja (arbol-variables, clic-depurar, git, mapas, mapas3, pintar-rapido, sprites, video) **no traen
  nada sin fusionar**: `git log main..rama` da 0 commits en todas. Solo sobran las ramas y dos worktrees
  (`~/Projects/forja-sprites` y `.worktrees/arbol`), limpios.
- En `forja/docs` no hay `DISENO.md` ni `ARREGLOS_LOOP.md`. Esos dos son de dashgit. El plan de Forja es `PLAN.md`.
- Lo que sí está a medias no está en ramas: está en diseños sin código (sección 1.3).

---

## 1. Dónde estamos

### 1.1 Forja 0.6.5, lo que hay de verdad

Tamaño: 13.700 líneas de Dash en 12 ficheros, 115 commits, 41 pruebas con el emulador (`tests/*.sh`).

| Pieza | Qué hay (visto en `src/`) | Dónde |
|---|---|---|
| Editor | Dibujado a mano en un lienzo. Colores, números de línea, selección con teclado y ratón, deshacer y rehacer, portapapeles, sangría automática, pestañas, sesión | `editor.dash` |
| Buscar | Buscar y cambiar en el fichero, con o sin mayúsculas. Ir a la línea | `editor.dash`, `ventana.dashui` |
| Código | Autocompletado (palabras, 1011 builtins, símbolos del proyecto y de los imports, campos tras el punto), ayuda de argumentos, Help/F1, ir a la definición, volver, dónde se usa | `codigo.dash` (2.139 líneas) |
| Compilar | Compilar, ejecutar, parar. Errores con clic. Errores del programa en rojo con clic. Cajón de ejecutables | `main.dash`, `paneles.dash` |
| Depurador | Puntos de parada, seguir, paso, entrar, salir. Pila y variables en árbol | `main.dash`, `paneles.dash` |
| Ventanas | Editor de `.dashui`: árbol, propiedades y vista previa con MUI de verdad | `diseno.dash` |
| Sprites | Editor de sprites y BOBs: herramientas, paleta, fotogramas, piel de cebolla, animación | `sprites.dash` (2.128 líneas) |
| Mapas | Editor de `.fmap`: capas, choques, objetos, deshacer | `mapas.dash` (1.803 líneas) |
| Git | Menú con 7 órdenes de dashgit. La salida va al panel de abajo | `main.dash` (`git()`) |
| ARexx | Puerto `FORJA.1` con 16 órdenes | `main.dash` (`orden_rexx`) |
| Inferencia | Botón que le manda el fichero o la selección. Inferencia edita dentro del editor de Forja | `main.dash`, e `inferencia/src/herramientas.dash` |
| Actualizar | Busca Dash nuevo en GitHub y lo instala | `actualizar.dash` |
| Idiomas | Castellano e inglés por catálogo | `catalogos/` |

### 1.2 Lo flojo o incómodo

Editor:

- **El resaltado no conoce el lenguaje entero.** `sintaxis.dash` tiene 29 palabras clave y 9 tipos a mano. Va línea
  a línea. Faltan cosas como `interface`, `weak` o `Double` (no las vi en la lista).
- **No hay plegado, ni marcadores, ni comentar o duplicar línea, ni mover línea.** No encontré nada de eso en
  `editor.dash`.
- **No resalta el paréntesis o el `end` que casa.** Tampoco cierra solo comillas ni paréntesis.
- **Buscar es solo en el fichero abierto y sin expresiones regulares.** Dash ya tiene `regex_*` (grupo
  "Expresiones regulares y comodines"). No hay "buscar en el proyecto".
- **No hay renombrar, ni esquema del fichero, ni formatear.** La extensión de VS Code sí los tiene.
- **No hay errores mientras escribes.** Solo al compilar. Compilar 1.505 líneas tarda 9,9 s a velocidad de A1200
  (`docs/PRUEBAS_LOOP.md`).
- **Una sola vista.** No se puede partir la ventana para ver dos ficheros.
- **El teclado va al editor solo con el puntero encima** (lo dice el README). Es raro para quien llega.
- **Escribir una línea cuesta 48 ms** en un A1200 con Fast (misma bitácora). Se nota al teclear rápido.
- Opciones de compilar: no hay sitio para `--cpu`, `--fpu`, `--memcheck` ni `--profile`. No encontré esas palabras
  en `main.dash`.

Proyecto:

- **No hay fichero de proyecto.** El `.forja` está decidido (2026-11-02) pero no hay código (`grep` no da nada).
  Desde un sprite, Forja busca `main.dash` a ciegas.
- El menú "Nuevo" solo crea un fichero vacío, un sprite o un mapa. No hay plantillas.

Depurador:

- No hay puntos de parada con condición, ni vigilar una expresión, ni ver el valor al pasar el ratón. La extensión
  de VS Code sí, y lo calcula ella con `dbg_value`.
- No se pueden cambiar variables. No hay vista de registros ni de memoria, aunque Dash tiene `dbg_reg` y `dbg_peek`.
- Un error de ejecución acaba el programa: no se queda parado en la línea.
- Un programa parado en `mui_wait_event` no pausa hasta que vuelve a su código (límite apuntado en `PLAN.md`).

Documentación:

- La ayuda es una línea por builtin: firma y descripción (`builtins.dash`, generado). No hay ejemplos, ni el
  manual, ni búsqueda por tema.
- En `tools/paquete_amiga.py` no vi que el paquete del Amiga lleve la documentación. Lleva `examples/` y `lib/`.

General:

- **No se ha probado en un Amiga de verdad** (lo dice el README). Es el mayor riesgo de calidad.
- Git: se explica en la sección 1.5.

### 1.3 Lo que está diseñado y sin código

| Diseño | Estado |
|---|---|
| `docs/HERRAMIENTAS_DISENO.md`: `.forja`, plantillas, perfil, memcheck, traducciones, iconos, instalador, pistas de sincronía, copper, medidores | Decidido por ti. Sin código |
| `docs/JUEGOS_DISENO.md`: Fragua (biblioteca de juegos) y editor de escenas | Fragua tiene la fase 1 (un commit en `~/Projects/fragua`). Editor de escenas: nada |
| `docs/3D_DISENO.md`: MiniGL, builtins `gl_*`, Fragua 3D, visor de modelos | Sin código. La fase 1 (probar MiniGL en el emulador) no está hecha. Dos preguntas tuyas sin responder |
| `docs/MAPAS_DISENO.md` | Hecho y fusionado |

Un dato: el diseño de herramientas dice que falta un puerto ARexx para programas sin MUI. Ya existe en Dash
(`rexx_port`, `rexx_get`, `rexx_signal`, `rexx_reply`). Las pistas de sincronía ya no esperan por eso.

### 1.4 dashgit 0.2 alfa

5.800 líneas de Dash. Formato igual al de git, comprobado contra el git del PC en las pruebas.

- **Tiene:** `init`, `add`, `rm`, `status` (también `-s`/`--porcelain`), `commit` (`-a`, `-m`), `log` (`--oneline`,
  `-n`), `branch` (`-d`), `checkout` (rama, `-b`, `-- fichero`), `diff` y `diff --cached`, `merge` de tres vías con
  conflictos y `--abort`, `clone`, `fetch`, `pull`, `push` por http y https, `.gitignore` completo, `config`.
- **No tiene** (no aparece en `src/`): `stash`, `reset`, `restore`, `show`, `tag`, `blame`, `rebase`,
  `cherry-pick`, `commit --amend`, `remote` (se hace con `config`), `log` de un fichero, `diff` entre dos commits,
  ssh, deltas al subir.
- **Sin probar:** push a GitHub de verdad con token (tarea T11, abierta). Velocidad en un Amiga real.
- **Límites apuntados:** la respuesta de la red va entera a memoria. Un clon de 373 objetos tardó unos 3 minutos
  con el emulador a tope. Necesita un disco con nombres largos (no FFS).

### 1.5 dashgit dentro de Forja hoy

Es lo mínimo. `git()` lanza `dashgit -C cajón orden` con `run_start` y vuelca el texto en la salida.

- Siete entradas de menú: estado, diferencias, historial (30 líneas), añadir todo, confirmar todo, pull, push.
- No hay marcas en el panel del proyecto (apuntado como pendiente en el diseño de dashgit).
- No hay marcas en el margen del editor. No hay vista de diferencias: es texto plano en la salida.
- No se elige qué ficheros entran en el commit: siempre `commit -a`.
- No hay ramas en el menú. No se ve en qué rama estás.
- Un conflicto solo se ve como texto. No hay ayuda para resolverlo.
- Las credenciales se ponen a mano con `SetEnv`.

### 1.6 Inferencia

Habla con modelos por red y tiene herramientas (leer, escribir, orden, arexx...). Con Forja abierto, lee y cambia
el texto dentro del editor, con deshacer. Pide MUI 5 (Forja admite 3.8). Desde Forja solo hay un botón: mandar el
fichero o la selección. No hay "explica este error", ni "arregla esto", ni completar con IA.

---

## 2. Comparación

Aviso: esta sección es de memoria. Sirve para orientar, no como dato comprobado.

| IDE | Lo que hace mejor que Forja hoy (de memoria) | Lo que Forja ya hace mejor |
|---|---|---|
| **StormC** | Gestor de proyectos de verdad. Depurador a nivel de fuente con inspección y cambio de variables. Todo integrado y rápido | Autocompletado, ayuda de builtins, editores de gráficos |
| **SAS/C (SE + CPR)** | CPR: depurador muy completo, con vigilancias, memoria y registros. Mensajes de error con ayuda larga | Editor moderno, todo en una ventana |
| **GoldED / Cubic IDE** | El editor más cómodo del Amiga: plegado, macros, ARexx para todo, menús y teclas configurables, plantillas, muchos lenguajes, API de plugins | Depurador propio, entender el código (definición, usos) |
| **CygnusEd** | Velocidad. Scroll instantáneo con ficheros enormes. Macros. Bloques en columna | Todo lo que no es editar texto |
| **AmiBlitz3 / Blitz Basic** | Ayuda en línea de cada orden con un toque. Compila y ejecuta casi al instante. Muchas bibliotecas y ejemplos de juegos | Depurador con árbol, git, editores de sprites y mapas |
| **AMOS Pro** | Todo dentro: editor de sprites, de sonido, de menús, y ayuda con ejemplos que se ejecutan. Modo directo para probar una línea | Lenguaje compilado, ventanas del sistema, depurador |
| **Devpac** | Ensamblar y depurar (MonAm) sin salir. Muy ligero: va en un A500 | Nivel alto |
| **ASM-One / AsmPro** | El ciclo más corto que existe: ensamblar y ejecutar en un segundo. Monitor, desensamblador, ver memoria. Es lo que usa la demoscene | Nada para demos todavía |
| **Annotate** | Editor ligero con plegado y resaltado, muy configurable | Es un IDE, no solo editor |
| **CodeBench (OS4)** | Proyectos, integración con el SDK y sus autodocs, ayuda contextual de la API | Depurador integrado |
| **VS Code (con la extensión de Dash)** | Errores al escribir, renombrar, esquema, formatear, arreglos rápidos, plegado, condiciones y vigilancias al depurar, perfil y memcheck con vista, plantillas de proyecto, elegir máquina | La vista previa es MUI de verdad. Corre en el Amiga |
| **JetBrains** | Refactorizar con seguridad, buscar en todo, historial local, vista de diferencias de git de tres paneles | — |
| **Xcode** | Instrumentos (perfil con línea de tiempo), editor de interfaces unido al código | — |

Lo que sale de la tabla:

1. **Nadie en el Amiga juntó todo.** Hay buen editor (GoldED, CygnusEd), buen depurador (CPR, StormC), buenas
   herramientas de juego (AMOS) y ciclo rápido (AsmPro), pero en programas distintos. Forja ya tiene un poco de
   todo. Le falta hondura en cada cosa.
2. **Forja pierde sobre todo como editor.** Es justo lo que pides primero: "potente y cómodo".
3. **Ya gana en entender el código** (definición, usos, autocompletado con tipos). Ningún IDE clásico lo hacía,
   que yo recuerde.
4. **El ciclo corto es lo que más quieren juegos y demos.** 10 segundos para compilar 1.500 líneas es mucho frente
   a AsmPro o Blitz.

---

## 3. Qué le falta, por áreas

### 3.1 Editor

| Falta | Coste | Nota |
|---|---|---|
| Resaltado generado desde la gramática (como hace `tools/gen_tmgrammar.py` para VS Code) | Bajo | Ya se genera `builtins.dash`; añadir las palabras clave |
| Comentar, duplicar, mover y borrar línea | Bajo | |
| Resaltar el par (paréntesis, `if`/`end`) y saltar a él | Bajo | |
| Cerrar solo comillas y paréntesis; `end` automático (VS Code lo tiene: `dash.editor.autoEnd`) | Bajo | |
| Marcadores | Bajo | |
| Buscar con expresiones regulares | Bajo | Con `regex_*` de Dash |
| Buscar en el proyecto, con resultados clicables | Medio | La salida ya admite clic a un sitio |
| Esquema del fichero (funciones, structs) en el panel | Medio | `codigo.dash` ya tiene los símbolos |
| Abrir rápido: fichero o símbolo por nombre (Ctrl+P, Ctrl+T) | Medio | Usa el mismo índice |
| Renombrar en todo el proyecto | Medio | Sobre `cx_referencias`. Enseñar la lista antes de cambiar |
| Plegado de bloques y `# region` | Medio-alto | Toca el dibujo y el paso de línea a fila |
| Formatear documento | Medio | Las reglas de sangría ya están |
| Dos vistas (partir en dos) | Alto | El editor es un solo lienzo |
| Multicursor | Alto | Empezar por selección en columna, que da el 80 % del uso |
| Macros de teclado (grabar y repetir) | Medio | Y dejarlas como script ARexx |
| Teclas y colores configurables | Medio | Un fichero en `ENVARC:Forja/` |
| El teclado en el editor sin el puntero encima | Bajo-medio | Depende de cómo da MUI el foco al lienzo |
| Fragmentos (`func`, `struct`, `mui`...) | Bajo | Los de la extensión sirven |
| Fuente elegible y tamaño | Bajo | |

### 3.2 Compilar y errores

- **Opciones por proyecto:** CPU, FPU, pila, `--memcheck`, `--profile`, `--gcc`. Van en el `.forja`.
- **Comprobar sin compilar.** Una opción del compilador que solo analice y dé errores (no la he visto en
  `./dash --help`). Con ella, Forja marca errores al guardar o tras una pausa. Es de Dash.
- **Compilar más rápido en el Amiga.** Medir dónde se van los 9,9 s. Si es el análisis, una caché por módulo. Es de
  Dash, y es lo que más cambia la sensación de uso.
- **Lista de errores** con filtro y "siguiente error" (una tecla). Hoy solo hay clic.
- **Arreglos rápidos:** "crear la función", "importar de...", "quizá querías...". La extensión los tiene.
- **Marcar el error en el código** (línea subrayada o margen rojo), no solo en la salida.

### 3.3 Depurador

- Condiciones y contador en los puntos de parada. Forja las evalúa con `dbg_value`, como la extensión.
- Vigilar expresiones. Valor al parar el ratón sobre un nombre.
- Pararse en el error de ejecución, no acabar. Pide un cambio en Dash.
- Cambiar una variable. Pide `dbg_set` en Dash (no existe).
- Vistas de registros, memoria y desensamblado. `dbg_reg` y `dbg_peek` ya están. Para programas de sistema y
  demos es importante.
- "Ejecutar hasta aquí". Puntos de parada que se guardan con el proyecto.
- Depurar por red un Amiga real desde otro (la extensión ya usa `tools/amiga/dbgserver.dash` por TCP).

### 3.4 Perfilador y memoria

- `--profile` existe en Dash (lo documenta el manual). No he comprobado que la orden `dash` del Amiga lo admita.
- En Forja: "Ejecutar con perfil" y una tabla ordenable con clic a la función. "Ejecutar con memcheck" con los
  avisos como errores clicables.
- Medidor en vivo: memoria chip y fast, y tiempo de fotograma, mientras el programa corre. El programa se lo
  cuenta a Forja por ARexx (`rexx_port` ya está).

### 3.5 Documentación integrada

Es de lo que más pides y hoy es lo más corto. Propuesta:

1. **Un fichero de ayuda generado desde Dash** (`docs/BUILTINS.md`, `SINTAXIS.md`, el manual), con índice por
   nombre, por grupo (los 40 grupos de `BUILTINS.md`) y por palabra. Va en el paquete del Amiga. Es de Dash
   (una herramienta como `tools/gen_builtins_doc.py`).
2. **Panel de ayuda en Forja:** Help sobre un nombre abre su ficha entera, con ejemplo. Enlaces entre fichas.
   Buscar en todo el manual.
3. **Ejemplos que se ejecutan:** cada ficha con un botón "Probar": abre el ejemplo en una pestaña sin nombre y lo
   ejecuta. `docs/builtins` ya se prueba en el runner de Dash, así que los ejemplos compilan.
4. **También en AmigaGuide,** para quien no use Forja. Sale del mismo generador.
5. **Ayuda de los errores:** cada error del compilador con una explicación larga y un ejemplo (lo hacía SAS/C, de
   memoria).
6. **Explorador de ejemplos** por tipo (sistema, ventanas, juego, demo), que hoy son 34 y casi todos `test_*`.

### 3.6 Proyectos y plantillas

- El `.forja` ya decidido: tipo, principal, ejecutable, opciones, versión, icono.
- "Nuevo proyecto..." con plantillas: orden del Shell, commodity, aplicación MUI, aplicación de DashOS, juego,
  demo, 3D. La extensión de VS Code ya tiene dos (`newProject.js`).
- Panel del proyecto agrupado por clase y con árbol de cajones.
- Abrir un proyecto desde su icono del Workbench (apuntado como sin probar).

### 3.7 Plugins

Cómo lo haría, de menos a más:

1. **Nivel 1, ARexx (ya casi está).** Un plugin es un script o un programa que habla con `FORJA.1`. Faltan
   órdenes: posición del cursor, insertar en el cursor, abrir un panel de texto, añadir una entrada de menú, poner
   marcas en el margen, registrar un tipo de fichero.
2. **Nivel 2, menú Herramientas configurable.** Un fichero en `ENVARC:Forja/herramientas` con nombre, orden y
   tecla. Con variables: fichero, cajón, selección, línea. Es lo que hacía GoldED (de memoria) y da mucho por poco.
3. **Nivel 3, plugins con manifiesto.** Un cajón en `PROGDIR:Plugins/nombre/` con un `plugin.json`: nombre,
   versión, qué menús añade, qué extensiones de fichero abre, qué eventos escucha (al guardar, al compilar, al
   abrir). El plugin es un programa de Dash aparte, que Forja arranca y con el que habla por ARexx.
4. **Nivel 4, biblioteca `lib/forja.dash`** en Dash: funciones para escribir un plugin sin saber ARexx
   (`forja_text()`, `forja_insert()`, `forja_menu()`...).

- **Seguridad:** el plugin corre como proceso aparte, así que un fallo suyo no tira Forja. Pero AmigaOS no tiene
  permisos: un plugin puede hacer cualquier cosa. Lo honrado es decirlo, pedir confirmación al instalar, enseñar
  qué órdenes va a poder mandar y no arrancar nada sin que el usuario lo haya activado.
- **No hacer:** plugins cargados dentro de Forja como código. Dash no carga módulos en ejecución, y un fallo se
  llevaría el IDE.
- **Distribución:** un `.lha` que se suelta en `Plugins/`, y una lista dentro de Forja que los baja de GitHub,
  igual que `actualizar.dash` baja Dash.
- **Los editores propios como plugins:** sprites, mapas y `.dashui` podrían ser plugins de nivel 3 más adelante.
  Baja la memoria de Forja para quien solo programa.

### 3.8 Herramientas

| Herramienta | Hay | Falta |
|---|---|---|
| Ventanas `.dashui` | Sí | Arrastrar con el ratón, "ir al código del evento" (la extensión lo tiene) |
| Sprites, BOBs, mapas | Sí | Importar una hoja de sprites, recortar, paleta compartida entre ficheros |
| Iconos `.info` | No | Editor con dos estados y tipos de herramienta; ColorIcons (decidido) |
| Catálogos | No en el Amiga | Tabla de textos `tr()` y sus traducciones; hoy es `tools/catalogo.py` en el PC |
| Paletas | Dentro de sprites | Editor aparte: degradados, cargar de IFF, 12 y 24 bits |
| Copper | No | Editor de degradados y cambios por línea, con vista |
| Sonido 8SVX | No | Recortar, volumen, oír. Dash no escribe 8SVX |
| Música | No | Visor de MOD con fila actual. Un tracker entero no: mejor abrir ProTracker y recargar |
| Fuentes | No | Visor; baja prioridad |
| Empaquetar | En el PC | `.lha`, `.readme` de Aminet e instalador desde el Amiga |
| Probar en otra máquina | No | Lanzar en un segundo Amiga por red, o en UAE desde el PC |
| Terminal | No | Un Shell dentro de un panel, o al menos "ejecutar orden" con salida |

### 3.9 Git e IA

Git: sección 5. IA:

- "Explica este error" y "arregla este error" desde la lista de errores.
- "Explica la selección", "escribe la prueba", "documenta esta función" en el menú del editor.
- Que Inferencia reciba el contexto del proyecto solo: ficheros, símbolos, errores (ya hay `ERRORES` y `SALIDA`).
- Que pueda consultar la ayuda de builtins (el fichero de 3.5), para no inventar funciones.
- Diferencias antes de aceptar un cambio, dentro del editor.
- Inferencia pide MUI 5. Con Forja en MUI 3.8, el botón no sirve: decirlo en el botón.

---

## 4. Por tipo de desarrollo

### 4.1 Programas de sistema (órdenes, commodities, bibliotecas, manejadores)

**Qué necesitan:** argumentos del Shell, código de retorno, ejecutar con argumentos, ver memoria y registros,
controlar fugas, `$VER`, poco tamaño, y probar en 68000 con OS 3.1 pelado.

- **Forja:** un campo "argumentos" al ejecutar y depurar. Entrada estándar en la salida. Memcheck con vista.
  Tamaño del ejecutable tras compilar. Registros y memoria en el depurador. Plantillas "orden" y "commodity".
- **Dash:** ya tiene argumentos, `cx_*`, `rexx_*`, tareas, memoria. No genera bibliotecas ni dispositivos
  (`.library`, `.device`): si entra en "programas de sistema", es un trabajo grande del compilador. Opinión: dejarlo
  fuera por ahora y decirlo.

### 4.2 Programas con ventanas (Workbench y DashOS)

**Qué necesitan:** editor de ventanas, menús, iconos, catálogos, ARexx, instalador, y probar con MUI 3.8 y 5.

- **Forja, Workbench:** ya tiene lo principal (el `.dashui` con MUI de verdad). Falta: iconos, catálogos,
  generador de puerto ARexx, instalador y paquete. Y GadTools y ReAction: Dash los tiene, Forja no tiene editor
  para ellos. Opinión: no hacerlos; MUI es el camino.
- **Forja, DashOS.** Aquí hay un problema de fondo: `./dash --dashos` genera AArch64 y enlaza con `ld.lld` en el PC
  (`./dash --help`). No vi que la orden `dash` del Amiga lo haga. Tres caminos:
  1. **Corto:** Forja compila para Amiga y enseña qué `mui_*` no están en DashOS (el compilador ya da "mui_x aún no
     está en DashOS"). Una tabla "disponible en" en la ayuda de cada builtin. Solo pide datos en `builtins.dash`.
  2. **Medio:** un servidor de compilación en el PC. Forja le manda el proyecto por red, el PC compila con
     `--dashos` y lo prueba en QEMU (`tools/dashos_run.py`), y devuelve errores y una captura. Sirve también para
     probar en FS-UAE desde el Amiga.
  3. **Largo y el bueno:** Forja compilado para DashOS. Forja es Dash con `mui_*` y lienzo. Cuando DashOS tenga el
     lienzo y lo que le falte de `mui_*`, Forja corre allí y compila en nativo. Hay que listar qué `mui_*` usa
     Forja que no están en `DASHOS_MUI`.
- **Dash:** la vista previa de `.dashui` con el aspecto de DashOS (Material 3) no existe en el Amiga. Con el
  camino 2, se pide la captura al PC.

### 4.3 Videojuegos

**Qué necesitan:** ciclo corto, sprites, mapas, escenas, sonido, medidor de fotograma, vista de choques, y probar
en A500 y A1200.

- **Forja:** tiene sprites y mapas, que es mucho. Falta: editor de escenas, efectos de sonido, medidor de
  fotograma, vista de depuración sobre el juego, plantilla de juego, y "ejecutar" que vuelva a Forja al salir sin
  dejar la pantalla rota.
- **Fragua:** solo la fase 1. Es la pieza que más frena los juegos. Sin ella, cada juego reescribe bucle, choques
  y cámara.
- **Dash:** faltan `music_seek`, `frame_lines`, escribir 8SVX, copper a doble búfer y los efectos de MOD que
  faltan (todo apuntado en `HERRAMIENTAS_DISENO.md`; comprobado que `music_seek` y `frame_lines` no están en
  `BUILTINS.md`). Faltan ejemplos de juegos completos: los 34 ejemplos son casi todos pruebas.

### 4.4 Demos

**Qué necesitan (opinión, por cómo trabaja la demoscene):** ciclo de un segundo, control exacto del hardware,
sincronía con la música, medir rasterlines, tamaño (4K, 64K), y tomar el sistema.

- **Forja:** nada específico hoy. Falta: pistas de sincronía en vivo (tipo Rocket), visor de MOD, editor de
  copper, medidor de rasterlines, tamaño con tope y compresor, plantilla de demo.
- **Dash:** un modo "tomar el sistema" (apagar multitarea e interrupciones, y devolverlo bien). No lo he buscado
  a fondo: comprobar si existe. Ensamblador en línea sin gcc: hoy `@native` es C y obliga a ir por gcc. Para demos,
  poder meter 68k directo en el compilador propio sería un argumento fuerte. Incluir binarios (`incbin`). Tablas
  precalculadas al compilar.
- **Realismo:** las demos punteras se hacen en ensamblador o C cruzado. Dash no va a ganarles en velocidad. Sí
  puede ser el camino más cómodo para una primera demo o una intro con efectos del sistema. Conviene decirlo así.

### 4.5 MiniGL y 3D

Hoy no hay nada: `grep` de `gl_`, MiniGL y Warp3D en `BUILTINS.md` y `amiga_builtins.py` da cero.

**En Dash, por orden:**

1. **Comprobar la base** (fase 1 del diseño, sin hacer): MiniGL con Wazp3D en FS-UAE, y un triángulo en C. Sin
   esto todo lo demás es a ciegas.
2. **Builtins `gl_*`:** contexto (`gl_open`, `gl_close`, `gl_swap`), estado, matrices, `gl_begin`/`gl_vertex`/
   `gl_end`, arrays de vértices, texturas (`gl_texture_load` desde datatypes o PNG), luces, niebla, mezcla. En
   los dos caminos de `./dash`. Si falta la biblioteca, `gl_open()` da falso.
3. **Decidir los números:** MiniGL usa coma flotante. Sin FPU es muy lento. Opinión: los programas `gl_*` piden
   `--fpu` y 68040 o más, y el compilador lo dice.
4. **`lib/gl3d.dash`:** vectores, matrices, cámara, cargar `.obj` y `.lwo`.
5. **Ejemplos:** triángulo, cubo con textura, modelo cargado, un pasillo.
6. **Un sistema de pruebas con MiniGL** para el runner (`# emu-needs: minigl.library`).
7. **DashOS:** si los mismos `gl_*` van sobre Vulkan o GL en DashOS, el mismo programa 3D corre en los dos. Vale
   la pena pensarlo antes de fijar los nombres.

**En Forja:**

- Visor de modelos en una pestaña. Visor de texturas.
- Plantilla "3D".
- Vista 3D del editor de escenas, más adelante.
- Si la máquina no tiene MiniGL, todo eso se apaga solo y Forja sigue igual.

**Pendiente de ti** (del diseño): los mensajes de Santi y si tienes un PiStorm32 con Pi 4.

---

## 5. dashgit y Forja

### 5.1 Lo que le falta a dashgit para el día a día

Por orden de uso real:

1. **Salida para máquinas.** `status --porcelain` ya está. Faltan `diff` con formato fijo por fichero, `log` con
   formato (`--format`), `branch` con la rama actual marcada. Forja no debería leer texto pensado para personas.
2. **`diff` de un fichero y entre dos commits.** `show <commit>`. `log -- fichero`.
3. **`restore` / `checkout -- fichero`** (este ya está) y **`reset`** (quitar del índice, volver atrás).
4. **`commit --amend`.**
5. **`stash`** (guardar y recuperar). Sin esto, cambiar de rama con cambios es incómodo.
6. **`tag`** y **`remote`** (`add`, `-v`).
7. **Push a GitHub con token, probado** (T11). Es el paso que da confianza.
8. **Progreso y cancelar** en clone, fetch y push. Y no cargar la respuesta entera en memoria.
9. **Velocidad:** medir `status` en un repositorio de 500 ficheros a velocidad de A1200. Si tarda, caché de fechas.
10. `blame`, `cherry-pick`, `rebase`: después. `rebase` puede esperar mucho.
11. ssh: opinión, no hacerlo. https con token basta.

### 5.2 Cómo integrarlo en Forja, en pasos

1. **Rama y estado en la barra.** Nombre de la rama y número de ficheros cambiados. Se refresca al guardar y al
   volver a Forja. Comprobable: una prueba que cambia un fichero y lee la barra.
2. **Marcas en el panel del proyecto:** M, A, ?, U junto a cada fichero. Con `status --porcelain`.
3. **Marcas en el margen del editor:** líneas añadidas, cambiadas y quitadas frente a HEAD. Clic en la marca:
   enseña lo de antes y deja deshacer ese trozo. Aquí conviene una orden de dashgit que dé solo los rangos.
4. **Panel "Cambios":** lista de ficheros con casilla (preparado o no), campo de mensaje y botón Confirmar. Sustituye
   al `commit -a` ciego.
5. **Vista de diferencias:** dos columnas o una con colores, en una pestaña. Con saltar al cambio siguiente.
6. **Historial:** lista de commits (autor, fecha, mensaje). Clic: sus ficheros y sus diferencias. Historial de un
   fichero.
7. **Ramas:** menú con las ramas, cambiar, crear, borrar, fusionar.
8. **Traer y subir** con progreso y botón de cancelar. Aviso claro si falta AmiSSL, red o token.
9. **Conflictos:** los ficheros en conflicto marcados. En el editor, sobre cada bloque `<<<<<<<`, tres botones:
   lo mío, lo suyo, los dos. Al acabar, "marcar resuelto" (`add`).
10. **Credenciales:** una ventana que pide usuario, token y servidor, y los guarda en `ENVARC:dashgit/credenciales`.
    Sin enseñar el token.
11. **Clonar** desde Proyecto > Clonar repositorio...
12. **Quitar "(alfa)"** cuando T11 y la prueba en un Amiga real estén hechas.

Una decisión técnica: hoy cada orden arranca el programa `dashgit`. Para las marcas del margen se llamará mucho.
Dos salidas: una orden `dashgit servidor` que se queda abierta y responde por ARexx, o meter los módulos de
dashgit dentro de Forja con `import`. Ojo con la segunda: dashgit es GPLv2 y Forja es MIT. Importarlo haría que el
binario de Forja fuera GPL. El proceso aparte evita el problema. Es decisión tuya.

---

## 6. Plan

Cada paso dice de quién es: **[F]** Forja, **[D]** Dash, **[G]** dashgit, **[I]** Inferencia, **[Fr]** Fragua.

### Fase 0. Base (antes de añadir nada)

- **[F] Probar Forja en un Amiga de verdad** (o en la máquina CoffinOS emulada como mínimo) y apuntar lo que salga.
- **[F] Borrar las ramas ya fusionadas y los dos worktrees.**
- **[D] Medir por qué compilar 1.505 líneas tarda 9,9 s en el Amiga** y fijar un objetivo.

### Fase 1. Editor cómodo (impacto alto, coste bajo-medio)

1. **[F] Resaltado generado desde la gramática de Dash.** Prueba: un fichero con todas las palabras clave.
2. **[F] Comentar, duplicar, mover y borrar línea; par resaltado; cierre automático; `end` automático.**
3. **[F] Buscar con regex y buscar en el proyecto.**
4. **[F] Esquema del fichero y abrir rápido por nombre.**
5. **[F] Marcadores y "siguiente error" con una tecla.**
6. **[F] Renombrar.**
7. **[F] Plegado.**
8. **[F] Teclas, colores y fuente configurables. Foco del teclado sin el puntero.**

### Fase 2. Proyecto y documentación (impacto alto, coste medio)

1. **[F] El `.forja`, con opciones de compilar, argumentos y tipo.**
2. **[F] Plantillas de proyecto** (orden, MUI, juego, demo).
3. **[D] Generador de la ayuda** (fichero con índice + AmigaGuide) y meterla en el paquete del Amiga.
4. **[F] Panel de ayuda:** ficha entera, búsqueda, enlaces, botón "Probar".
5. **[D] Ejemplos de verdad** por tipo, y revisar los que hay.
6. **[D] Opción "solo comprobar"** y **[F] errores al guardar**, marcados en el código.

### Fase 3. Git (impacto alto para quien colabora, coste medio)

1. **[G] Salidas para máquinas, `diff` de fichero, `show`, `log -- fichero`.**
2. **[F] Rama en la barra, marcas en el proyecto y en el margen.**
3. **[F] Panel de cambios y vista de diferencias.**
4. **[G] `reset`, `--amend`, `stash`, `tag`, `remote`. T11 (push real).**
5. **[F] Historial, ramas, conflictos, credenciales, clonar.**
6. **[G] Progreso, cancelar y memoria en la red.**

### Fase 4. Depurar y medir (impacto medio-alto, coste medio)

1. **[F] Condiciones, vigilancias y valor bajo el ratón.**
2. **[F] Perfil y memcheck con vista.** **[D]** comprobar que la orden del Amiga los admite.
3. **[D] Parar en el error de ejecución; `dbg_set`.** **[F]** registros y memoria.
4. **[F] Medidor en vivo** (memoria, fotograma) por ARexx.

### Fase 5. Plugins y herramientas de escritorio (impacto medio, coste medio)

1. **[F] Menú Herramientas configurable** y las órdenes ARexx que faltan.
2. **[F] Catálogos, iconos, instalador y paquete desde el Amiga.**
3. **[F] Plugins con manifiesto** y **[D] `lib/forja.dash`**.
4. **[I] Acciones de IA en errores y selección; la ayuda de builtins como herramienta.**

### Fase 6. Juegos y demos (impacto alto para ese público, coste alto)

1. **[Fr] Fragua fases 2 a 4.**
2. **[D] `music_seek`, `frame_lines`, 8SVX, copper a doble búfer.**
3. **[F] Pistas de sincronía, visor de MOD, editor de copper, medidor de rasterlines.**
4. **[F] Editor de escenas.**
5. **[D] Ensamblador en línea e `incbin`** en el compilador propio (decidir si se hace).

### Fase 7. 3D y DashOS (coste alto, depende de fuera)

1. **[D] Prueba de MiniGL en el emulador** (pequeña: se puede adelantar a cualquier fase).
2. **[D] `gl_*`, `lib/gl3d.dash`, ejemplos.** **[F]** visor de modelos y plantilla.
3. **[F] "Disponible en DashOS"** en la ayuda de cada builtin (pequeña: adelantar a la fase 2).
4. **[F][D] Servidor de compilación en el PC** para `--dashos` y QEMU.
5. **[F] Forja en DashOS.**

### Los primeros pasos que daría ya

1. **[F] Probar en un Amiga real o en CoffinOS emulado y limpiar ramas.** Medio día. Quita el mayor riesgo.
2. **[F] Resaltado generado + comentar/duplicar/mover línea + par resaltado + cierre automático.** Es lo que más
   se nota al escribir y es barato.
3. **[F] Buscar con regex y en el proyecto.**
4. **[F] El `.forja` con opciones y argumentos, y dos plantillas.** Desbloquea perfil, memcheck, tipos y git.
5. **[D] Generador de ayuda y [F] panel de ayuda con "Probar".** Es tu petición de "integración perfecta con la
   documentación".
6. **[G] Salidas para máquinas y [F] rama en la barra + marcas en el proyecto.** El empujón visible a git.
7. **[D] Medir el tiempo de compilar en el Amiga.** Decide cuánto se puede acercar al ciclo de AsmPro o Blitz.
8. **[D] La prueba de MiniGL en el emulador.** Pequeña, y dice si el 3D es posible sin un PiStorm.

---

## 7. Límites del Amiga

- **CPU.** En un 68020 a 14 MHz, pintar una línea cuesta 48 ms y la pantalla entera 58 ms (medido). Todo lo
  nuevo del editor (plegado, marcas de git, par resaltado) tiene que pintar solo lo que cambia. El índice de
  símbolos ya se hace a trozos en reposo: seguir así con todo lo que sea lento.
- **Memoria.** Forja crece con cada editor. Un A1200 con 2 MB de chip y 4-8 de fast es el suelo razonable.
  No he medido cuánta usa Forja hoy: hay que medirlo y poner un tope. Los editores como procesos aparte (plugins)
  ayudan. La ayuda entera no puede cargarse en memoria: fichero con índice y `file_seek`.
- **Pantalla.** En 640x256 el editor enseña 8 líneas (bitácora). Dos vistas, paneles de git y ayuda no caben ahí:
  tienen que ser pestañas o ventanas aparte, no más paneles fijos. Con 4 colores los estados de git tienen que
  distinguirse por letra, no solo por color.
- **MUI 3.8 frente a 5.** Forja admite los dos; Inferencia solo MUI 5. Cada cosa nueva de interfaz se prueba en
  3.8. Como el editor es un lienzo propio, casi todo lo del editor no depende de MUI. Lo que sí: listas con muchas
  filas, pestañas, arrastrar.
- **RTG o no.** El 3D pide RTG y MiniGL. El resto tiene que ir en AGA y, a ser posible, en ECS con 4-8 colores.
- **OS 3.1 frente a 3.2 y 3.9.** ReAction solo se prueba en 3.2. Los iconos de color son de 3.5 en adelante.
  3.9 con ROM Update ya dio un fallo (arreglado en 2.15.0): meter 3.9 en las máquinas de prueba.
- **Disco.** dashgit necesita nombres de más de 30 letras: no vale FFS. Forja debe avisar al iniciar git en un
  disco así.
- **Red.** Git por https, actualizar e Inferencia piden pila TCP/IP, AmiSSL y el reloj en hora. Todo eso tiene
  que fallar con un mensaje claro y no bloquear la ventana.
- **Sin protección de memoria.** Un programa depurado que escribe donde no debe puede tirar Forja. Guardar todo
  antes de ejecutar (ya se hace) y una copia de recuperación de lo no guardado.
- **Compilar DashOS desde el Amiga** no es posible hoy (el enlazado es en el PC). Hay que contar con ello en
  cualquier promesa sobre DashOS.

## Decisiones que te tocan

1. dashgit dentro de Forja como proceso aparte (Forja sigue MIT) o importado (Forja pasa a GPL).
2. DashOS: servidor de compilación en el PC, o esperar a Forja nativo en DashOS.
3. Bibliotecas y dispositivos del sistema en Dash: dentro o fuera.
4. Ensamblador en línea en el compilador propio, para demos.
5. 3D: los mensajes de Santi y si hay un PiStorm32 con Pi 4.
6. Suelo de máquina de Forja: memoria mínima que se promete.
