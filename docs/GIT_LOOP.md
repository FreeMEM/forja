# Git en Forja: bitácora

La fase 3 de `docs/IDE_ANALISIS.md` (sección 5). Rama `git-panel`. Lo de dashgit (las salidas para máquinas) está en
su rama `salidas` (`docs/GIT_FORJA_LOOP.md` de dashgit).

Decisión tomada: Forja llama a dashgit como **proceso aparte** (`run_start`). Forja es MIT y dashgit GPLv2: Forja no
importa ningún módulo de dashgit, solo lee lo que escribe.

Decisión del usuario (2026-11-16): git será una **extensión** de Forja, como los editores de sprites y de mapas e
Inferencia. El sistema de extensiones aún no existe. Por eso todo lo de git va en módulos propios con una interfaz
estrecha (ver "Lo que la extensión necesita de Forja").

## Qué hay

- **La barra**: a la izquierda de Inferencia, un icono de rama, el nombre de la rama y "N cambios" (si no cabe,
  solo el número; si tampoco, nada). Un clic abre el panel Cambios. Se refresca al guardar, al volver a Forja
  (cuando su ventana vuelve a ser la activa), tras cada orden de git y al cambiar de cajón en el panel del proyecto.
- **El panel del proyecto**: una letra a la derecha de cada fichero con cambios: M (cambiado), A (nuevo en el
  índice), D (borrado), U (conflicto), ? (sin seguir). Los cajones llevan la letra que más pesa de lo que tienen
  dentro. Letra y color, no solo color (con 4 colores se distinguen).
- **El margen del editor**: frente a HEAD, del fichero guardado: añadida (raya llena, verde), cambiada (raya a
  trozos, azul), quitadas (un triángulo rojo arriba de la línea siguiente, o abajo de la última). Con cambios sin
  guardar no se enseñan (serían de otro texto). Al llegar las marcas se repintan solo las líneas que cambian.
- **El panel Cambios** (Git > Cambios y confirmar..., o clic en la rama): una fila por fichero con casilla
  (vacía: sin preparar; llena: preparado; media: preparado y con más cambios en el disco), letra y ruta. Clic en la
  casilla: `dashgit add` o `dashgit reset` de ese fichero (la fila cambia ya; el estado de verdad llega después).
  Clic en la ruta la elige; otro clic, o Diferencias, abre sus diferencias. Preparar todo (`add -A`), Quitar todo
  (`reset`), campo de mensaje y Confirmar (`commit -m`, solo lo preparado). Sustituye al `commit -a` ciego.
- **La vista de diferencias**: una pestaña de solo lectura "fichero (cambios)" con `dashgit diff HEAD -- fichero`
  (un fichero sin seguir sale entero como añadido). Colores por línea; `n` y `p` van al trozo siguiente y al
  anterior; Return lleva a esa línea del fichero. Git > Diferencias de este fichero la abre para el activo.
- ARexx: `CAMBIOS` abre el panel; `GITESTADO` da "rama|cambios|letras del panel|marcas del margen del activo".

## Módulos

| Fichero | Qué |
|---|---|
| `src/git_estado.dash` | el estado: busca el repositorio, cola de órdenes de dashgit en segundo plano, lee `status --porcelain -b` y `diff --rangos`, da la rama, las letras y las marcas |
| `src/git_cambios.dash` + `src/git.dashui` | el panel Cambios |
| `src/git_vista.dash` | colores y saltos de la vista de diferencias |
| `src/main.dash`, bloque "Git: el pegamento" | lo que une lo de arriba con Forja (`git_tic`, `git_evento`, `git_al_dia`...) |

## Lo que la extensión necesita de Forja

Es la lista de lo que la API de extensiones tiene que dar para que git salga de Forja:

1. **Avisos**: el cajón del proyecto cambió; se guardó un fichero (ruta); se abrió un fichero (ruta); Forja volvió a
   ser la ventana activa (hoy se mira con `mui_window_active` en un tic cada 1,5 s: Dash no tiene un evento de
   ventana activada); acabó una orden lanzada por la extensión.
2. **Un tic** (o poder esperar a un proceso aparte sin bloquear la ventana).
3. **Lanzar órdenes** en segundo plano y recoger su salida y su código (hoy `run_start` directo), y la salida de
   Forja para mostrar avisos y lo que escriben.
4. **Menú**: entradas propias en un menú propio (Git).
5. **La barra de botones**: una zona propia a la derecha con texto e icono, y un evento al hacer clic.
6. **El panel del proyecto**: una letra (con su color) por entrada, dada la ruta.
7. **El margen del editor**: una marca por línea (unos bits que Forja sabe pintar, o que la extensión pinte en una
   zona de pocos píxeles), y pedir que se repinten solo unas líneas.
8. **Leer el fichero abierto**: su ruta, si tiene cambios sin guardar, su número de líneas, sus líneas.
9. **Una pestaña de solo lectura** con un color por línea que da la extensión, y teclas propias en ella (n, p,
   Return).
10. **Abrir un fichero en una línea** (ir de las diferencias al código).
11. **Una ventana propia** (el panel Cambios), con su .dashui y sus eventos.
12. **La sonda** para las pruebas.

## Pruebas

`tests/git_panel.sh DASH_DIR [DASHGIT_DIR [captura.png segundos...]]` (FS-UAE, MUI 5, `DASH_KICKSTART`; DASHGIT_DIR
por defecto `~/Projects/dashgit`, necesita la rama `salidas`). `tests/git_panel.dash` hace init y commit por ARexx;
mira la barra (rama, 0 cambios); cambia dos líneas y guarda: 1 cambio, M en el panel y las marcas 1 (añadida) y 5
(cambiada); escribe un fichero desde fuera, pone otra ventana delante y vuelve a Forja: sale con ?; abre el panel
Cambios, marca con el ratón las casillas (add, add, reset), abre las diferencias con dos clics (con lo añadido y lo
quitado), salta con n, va al código con Return, y confirma escribiendo el mensaje (Confirmar sin mensaje pone el
cursor en el campo). El git del PC comprueba los commits y el estado. `SISTEMA=...` usa otro sistema de
`~/.cache/dash-emu`.

## Bitácora

- 2026-11-16: todo lo de arriba. `tests/git_panel.sh`: TODO BIEN en el A1200 emulado con OS 3.1 y MUI 5
  (`sys31muisslweb`). `tests/git_panel_coffin.sh` (la misma prueba en la máquina coffin de Dash: 68040, RTG, MUI
  3.8, lanzada por `tests/git_panel_coffin.dash`): TODO BIEN. Siguen bien `tests/ficheros.sh` y `tests/teclas.sh`.
- La prueba fallaba al azar por leer `ENV:FORJA_GIT_CAMBIOS` mientras Forja la escribía (salía vacía): la sonda
  ahora solo la escribe cuando cambia.
- En la prueba, un `Window` de Dash abierto desde el programa de prueba (lanzado con `Run >NIL:` junto a Forja) se
  quedaba colgado al abrirse; solo, en otro arranque, abre bien. No lo he investigado: para "otra ventana delante"
  se usa la de buscar de Forja (Amiga-F). Así no se prueba la vuelta desde otro programa, aunque el mecanismo es el
  mismo (`mui_window_active` de la ventana principal).
- Tiempos (repositorio de 4 ficheros, medidos por Forja con su reloj): A1200 emulado a toda velocidad,
  `status --porcelain -b` 1,1 s y `diff --rangos` 1,1 s, de guardar a ver las marcas 2,6 s; con `REAL=1` (68020 a
  la velocidad de un A1200) 1,1 s, 0,8 s y 2,4 s; en coffin (68040 JIT), 1,5 s de guardar a las marcas. Casi todo es
  arrancar dashgit (390 KB) y leer el índice. No probado en un Amiga de verdad.
- Decisión pendiente (para el usuario): para el margen basta con el proceso aparte, porque solo se pide al guardar,
  al abrir y al volver a Forja, en segundo plano, y la ventana no se para. Si se quiere que las marcas sigan al
  escribir (sin guardar), 1-2 s por llamada es demasiado: entonces conviene el modo servidor (`dashgit servidor`
  que se queda abierto y contesta por ARexx, sin arrancar ni leer el índice cada vez). No está hecho.
- Con los 4 colores del Workbench 3.1 la vista de diferencias sale toda del mismo color (se distingue por el + y el
  -); con más colores (coffin) va en verde, rojo y azul. Las letras del panel y las formas del margen sí se
  distinguen con 4 colores.
- Sin probar: `tests/git.sh` (la prueba vieja del menú Git con un servidor del PC): el cerrojo de red
  (`/run/user/1000/dash-emu-red.lock`) lo tenían otras sesiones con baterías largas. No cambia lo que prueba
  (órdenes GIT por ARexx), salvo que la ventana vieja de "Confirmar los cambios" ya no existe.

## Falta

- Clic en una marca del margen: enseñar lo de antes y deshacer ese trozo.
- Historial, ramas (cambiar, crear, borrar, fusionar), conflictos, credenciales, clonar (pasos 6 a 11 del análisis).
- Que las marcas sigan las líneas mientras se escribe (hoy se esconden hasta guardar).
- Aviso al iniciar git en un disco sin nombres largos (FFS).
- Un evento de Dash para "la ventana se activó" (hoy se mira cada 1,5 s con un tic, solo si hay repositorio).
