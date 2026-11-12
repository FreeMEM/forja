# Pruebas a fondo de Forja (loop)

Encargo del usuario (2026-11-10): probar Forja a tope, con programas de varios ficheros y todo lo que usa la gente,
y arreglar cada fallo hasta que no salgan más. Para que nadie se eche atrás al usarla. Nada se publica sin el usuario.

Empezó por dos fallos de David Martínez con la 0.6.0 (Dash Amiga #1094 y #1095, con vídeo #1093).

Rama: `clic-depurar`.

## Cómo se prueba

- Cada prueba es `tests/X.sh ~/Projects/FreeMEMLang ~/Projects/FreeMEMLang/dashc/build`, con `scratchpad/env.sh`.
- Las pruebas de Forja no usan red, así que no hace falta el cerrojo del emulador. Van de dos en dos, como mucho, para
  no ahogar la CPU.
- Un fallo que coincida con otra tanda pesada se repite a solas antes de darlo por bueno o por malo.
- Cada arreglo lleva su prueba, y la prueba se pasa antes con el Forja viejo para ver que falla (`FORJA=cajón`).

## Plan

1. [x] Los dos de David: clic en el editor depurando (`tests/clic.sh`) y clic en el panel de las variables.
2. [x] Proyecto de varios ficheros en un cajón con espacio (`tests/proyecto.sh`): ejecutar desde un módulo, guardar
   al ejecutar, error en otro fichero, depurar entre ficheros.
3. [x] Todas las pruebas que ya había, con lo nuevo.
4. [x] Más casos de uso:
   - ficheros largos (más de 1000 líneas): escribir, rueda, barra, buscar;
   - cerrar pestañas con cambios y depurando;
   - error de ejecución en un módulo (código 20, el sitio);
   - programa que no acaba: Parar;
   - abrir lo de la última vez (la sesión) con varios ficheros;
   - Workbench de pocos colores y 640x256;
   - MUI de 3.2 (sys32mui);
   - puntos de parada en dos ficheros;
   - cambiar un fichero mientras se depura;
   - seleccionar con el ratón y arrastrar;
   - deshacer muchas veces.
5. [x] Lo que salga de mirar con capturas (lo que una prueba no ve: parpadeos, cosas mal pintadas).

## Bitácora

- 2026-11-10:
  - Causa del salto, vista en el vídeo de David: tras el clic, el editor pinta un momento desde la línea 12.
  - El tic del depurador (cada 0,3 s) volvía a atender la misma parada. Con el ancla del clic puesta (`d.al`),
    `ed_ir_a_quieto` lo tomaba por una selección y centraba la línea. También se llevaba el cursor a la línea de la
    parada.
  - Arreglo: la parada se atiende una sola vez (`parada_atendida`), y solo una selección de verdad cuenta.
  - Clic en las variables: `en_proyecto` no miraba si el panel enseñaba la depuración. Ahora no hace nada.
  - Visto al leer el código:
    - Ejecutar desde un módulo compilaba el módulo solo. Ahora `programa_de` busca el programa del proyecto.
    - La lista del proyecto salía en el orden del disco. Ahora salen los cajones y luego los ficheros, por orden
      alfabético.
  - Sonda nueva: `RAM:forja-vistas.txt` (la primera línea de cada dibujo entero) y `ENV:FORJA_FICHEROS`.
  - `tests/proyecto.sh` y `tests/depurar.sh` pasan enteras. `tests/clic.sh` falla con el Forja viejo (el código pasa
    de la línea 13 a la 16 y el cursor se va a la parada) y pasa con el nuevo.
  - En 640x256 el editor enseña 8 líneas. Cada paso del depurador cerca del borde centraba la línea, y el código
    saltaba 4 líneas (también en la 0.5.2 y la 0.6.0). Ahora, si la parada cae cerca, el código se mueve lo justo
    (`ed_ir_a_quieto`).
  - La salida pesa 25 en vez de 60. En 640x256 no cambia nada, porque ya está en su mínimo, pero en pantallas más
    altas el editor gana sitio.
  - Fallo de Dash, pasado a la sesión freememlang-af: el compilador directo no comprueba el tipo al reasignar
    (`s = "a"`, luego `s = [1]` compila).
  - `tests/salir.sh`: salir de Forja con un programa en marcha cierra la ventana, pero Forja sigue viva hasta que el
    programa acaba, y el programa sigue corriendo. La causa es que un programa de Dash solo atiende Ctrl-C si llama a
    `break_check()`. Lo comprueba `tests/parar.sh`: si Parar no puede con un bucle sin fin, no hay forma de pararlo
    sin reiniciar.
  - `tests/parar.sh` lo confirma: Parar no para `while true / i = i + 1 / end`, y Forja no puede ni salir.
  - El usuario eligió arreglarlo en Dash (rama `ctrl-c` de FreeMEMLang, sin subir): cada vuelta de un `while` o un
    `for` mira el Ctrl-C de la tarea, en los dos compiladores.
    - Si llega, el programa escribe `***Break` y acaba con código 5.
    - No se pone en los programas que atienden Ctrl-C por su cuenta: `break_check`, `single_instance`, la espera de
      MUI y los `cx_`.
    - Pruebas `tests/test_ctrl_c*.dash` y `dashc/tests/ctrl_c*.dash`: pasan en A1200 y A500, y los dos compiladores
      dan lo mismo.
    - Un fallo por el camino: sin `volatile`, gcc sacaba la lectura fuera de un bucle sin llamadas.
  - Forja:
    - Si Parar no lo para en 4 s, lo dice en la salida (un programa que espera a su ventana no lo ve).
    - Al salir, para antes lo que esté en marcha: `dbg_end`, o Ctrl-C y 3 s. Si sigue, pregunta.
  - `tests/grande.sh` (1505 líneas):
    - Bien: ir al final, Amiga-L, buscar, ejecutar, deshacer y rehacer.
    - El dibujo entero tarda 71 ms en el emulador rápido.
    - Compilar y ejecutar tarda 12,6 s: es lo que tarda dashc en el Amiga, y queda por mirar aparte.
    - Escribir tras buscar falla. Se está mirando si las teclas van a la ventana de Buscar.
  - Con el Dash de la rama `ctrl-c`:
    - `tests/parar.sh`: Parar corta el bucle sin fin en 1,3 s.
    - `tests/salir.sh`: al salir de Forja no queda nada vivo, ni ejecutando ni depurando.
  - `tests/grande.sh` pasa. Escribir no repinta todo. Las dos veces que sí repinta son la flecha (quita lo elegido
    por buscar) y la primera tecla (el "*" de la pestaña).
  - `tests/errores.sh` (nuevo):
    - Un error de ejecución en un módulo ("Error: campo de nil (en ruta:línea)") no se podía pulsar. Ahora sale en
      rojo y con su sitio (`salida_error_programa`).
    - En 640x256 la salida enseña dos líneas, y "exe failed returncode 20" del Shell empujaba el error fuera de la
      vista. Esa línea ya no se pone, y el primer error queda a la vista.
  - `tests/sesion.sh` (nuevo): abrir lo de la última vez y cerrar con cambios (Descartar).
    - Con un fichero de la sesión en un disco que no está, Forja se quedaba esperando en "Inserta el volumen" al
      arrancar. Ahora `sesion_abrir` lo hace sin esos requesters (`dos_requesters(false)`) y salta lo que no está.
- 2026-11-11:
  - `tests/sprites_cebolla.sh` fallaba también con la 0.6.0: la celda del sprite mide 4 píxeles en 640x256, y el punto
    de la cebolla no cae en el píxel del centro. La prueba ahora busca en toda la celda.
  - `tests/sprites_forja.sh`: desde un sprite se compila main.dash, el programa de red.dash, que es un módulo.
  - `tests/clic.sh` también prueba arrastrar para elegir: de la línea 2 a la 3, comprobado con ARexx SELECCION.
  - Las 25 pruebas de Forja pasan con el Dash de `ctrl-c`. Repaso a ojo en 3.2 con RTG: bien.
  - Ctrl-C en Dash, coste medido con 300.000 vueltas:
    - En cada vuelta de todo bucle, un `while` que cuenta pasaba de 232 a 825 ms en A1200 (3,5x).
    - Ahora solo lo miran los `while` que pueden no acabar. Los `for` y los `while` que cuentan no pagan nada.
    - El peor caso es un `while` que no cuenta y sin llamadas: de 522 a 1173 ms en A1200 sin memoria Fast, y de 2168 a
      4155 ms en A500. Con alguna llamada dentro no se nota.
  - Batería de Dash: 97 "timeout" seguidos a partir de `test_string_memory`, que sola pasa. Cada máquina tiene un tope
    de tiempo por arranque (360 s en A1200, 700 s en A500), y el coste de antes lo sobrepasaba. Se repite con el
    cambio.
  - Topes de tiempo del runner de Dash: con main también fallaban las 30 últimas del A1200 por tiempo. Se suben en
    la rama `ctrl-c` (A1200 540 s, A500 1100 s, OS 3.2 600 s), en un commit aparte.
  - `tests/nuevo.sh` (nuevo): lo primero de alguien que empieza. Forja sin fichero, Amiga-N, escribir un programa
    con if y else, Ejecutar, el requester de guardar (ASL: el primer Return reparte la ruta en Drawer y File, el
    segundo acepta), compilar y ejecutar. Pasa.
  - Sangría automática nueva, con las reglas de la extensión de VS Code:
    - Return tras Main, func, if, else, while... entra un nivel.
    - end, else y elif vuelven a la altura de su bloque, al escribir su última letra o al pulsar Return.
    - `tests/teclas.sh` ahora escribe sin poner la sangría a mano.
  - Fallo serio de Dash encontrado así: compilado con `./dash`, la sangría fallaba, y con `--gcc` iba bien.
    - Una función con un bucle, copiada en línea a la izquierda de una resta, pisa el registro de la variable de la
      derecha (`espacios(b) - v` da 0).
    - Caso mínimo en scratchpad/repro/min.dash, pasado a freememlang-af, que lo arregla.
    - En Forja se esquiva guardando antes la llamada en una variable.
  - El título del requester de guardar ("Guardar ") ya se puede traducir.
  - Con el Dash de `ctrl-c`, las 26 pruebas de Forja pasan menos `salir`.
    - El programa de esa prueba es un `for` con `time_delay`, y ya no miraba Ctrl-C.
    - Arreglo: un bucle que llama a algo (función, builtin, Print) siempre lo mira. Al lado de la llamada no cuesta
      nada.
    - Un `for` o un `while` que cuenta, sin llamadas, sigue sin mirarlo. El bucle de prueba sigue en 231 ms.
    - `test_ctrl_c` tiene un hijo "lento", un `for` con `time_delay`.
  - freememlang-af arregló el fallo de registros en la rama `copia-registros` (c6adf97, sin subir).
  - `REAL=1 tests/grande.sh`, con la CPU a la velocidad de un A1200 (68020 a 14 MHz, 8 MB de Fast) en vez de al
    máximo:
    - Dibujo entero: 58 ms. Una línea al escribir: 48 ms. Compilar y ejecutar 1505 líneas: 9,9 s. Todo bien.
    - El bucle de prueba casi no cambia (232 ms al máximo y 260 ms a velocidad real), así que las medidas de antes
      ya se parecían a un A1200 con Fast.
  - Última vuelta, con el Dash de `ctrl-c`: batería de Dash 1483/1483, `dashc/tests` bien y las 26 pruebas de Forja
    con TODO BIEN. Sin fallos nuevos: el bucle acaba aquí.

## Lo que queda (para el usuario)

- Hecho el 2026-11-12: Dash 2.11.0 (PR #160, Ctrl-C con coste de +16 % en A1200 en el peor bucle) y Forja 0.6.1
  publicadas.
- Sin probar: Forja abierta desde el Workbench con un icono de proyecto, y la actualización contra GitHub desde un
  Amiga de verdad.

## Ideas pedidas

- **Variables del depurador en árbol** (David Martínez, grupo Dash Amiga, 2026-11-12): las listas se despliegan hacia
  abajo, los structs también (campo a campo), y el panel se desplaza en horizontal además de en vertical cuando lo
  desplegado no cabe. Al hacerlo: su nombre en el commit, en las notas de la versión y en "Gracias" de la web.
