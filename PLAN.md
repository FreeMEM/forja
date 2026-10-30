# Forja: plan

Forja es un entorno de desarrollo para Dash que corre en el propio Amiga:
- MUI 5, moderno y con fondo negro.
- Editor de código con colores.
- Compilar con dashc y ejecutar.
- Depurador paso a paso.
- Editor visual de ventanas `.dashui`, con MUI de verdad.

Se integra con [Inferencia](https://github.com/FreeMEM/inferencia) por ARexx.

Escrito en Dash 2.0 (dashc), sin `@native` y con licencia MIT.

## La ventana

```
+--------------------------------------------------------------------------------+
| Forja: Work:juego                                                        [][]  |
+--------------------------------------------------------------------------------+
| [Compilar] [Ejecutar] [Depurar]                                   [Inferencia]  |
+--------------+-----------------------------------------------------------------+
| Proyecto     | main.dash | ventana.dashui | red.dash                            |
|  main.dash   |  45   total = lista.count                                       |
|  red.dash    |  46   j = 0                                                     |
|  ventana.ui  |  47 ● while j < total                                           |
|              |  48 >     procesar(lista[j])                                    |
| Variables    |  49       j = j + 1                                             |
|  j      3    |  50   end                                                       |
|  total  10   |                                                                 |
+--------------+-----------------------------------------------------------------+
| Salida: compilado en 1,2 segundos, 0 avisos                                    |
+--------------------------------------------------------------------------------+
```

- **Fondo negro**:
  - El editor y la salida se dibujan sobre `mui_canvas`, con colores propios.
  - El resto de la ventana se pone oscuro con `"background"` y `"color"` del `.dashui` (`mui_set_background`,
    `mui_set_text_pen`). Unas preferencias de MUI propias no se pueden escribir a mano.
- **Editor de código**: hecho sobre el canvas, porque Dash no tiene campo de varias líneas.
  - Colores según la sintaxis de Dash, números de línea y puntos de parada.
  - Buscar y reemplazar, deshacer y pestañas.
  - Es la pieza más grande.
- **Botones**: los del depurador (Paso, Entrar, Salir, Seguir) solo salen al depurar; todos a la vez no caben en
  una pantalla de 640 píxeles.
- **Proyecto**: los ficheros. Al depurar, también las variables y la pila de llamadas.
- **Salida**: los errores de dashc. Con un clic se salta a la línea.
- **Botón Inferencia**: manda a Inferencia el fichero y la selección. Si no está abierta, la arranca.

## Editor de `.dashui` con MUI de verdad

En Linux, la extensión de VS Code simula MUI con HTML. Aquí la vista previa es la ventana MUI real, construida a
partir del JSON mientras se edita. Lo que se ve es exactamente lo que saldrá.

Una pestaña con tres partes:
- El árbol de objetos.
- La ventana real.
- Las propiedades del objeto elegido.

Usa el mismo formato `.dashui` que la extensión (`docs/MUI_EDITOR.md`), y los dos tienen que poder abrir los
ficheros del otro.

## Depurador

En un Amiga de verdad, no solo en el emulador. Las piezas ya están en Dash 2.0 (rama `ide-piezas`, sin fusionar):
- Se compila el programa con `./dash --debug`. Eso pone un NOP en cada línea y una tabla de líneas y
  variables (HUNK_DEBUG).
- Forja lo controla con los builtins `dbg_*`:
  - Arrancar en pausa, poner y quitar puntos de parada.
  - Seguir, paso, entrar, salir y pausa.
  - La pila, las variables locales y globales, y el valor de una expresión como `p.hijos[0].x`.
  - Registros, memoria y la salida del programa.
- Los puntos de parada son un `TRAP` en el NOP de la línea, sin el bit de traza, así que funciona también
  en Emu68 (PiStorm).
- La espera entra en el bucle de MUI con `dbg_signal()`, así que la ventana no se congela.
- Límites de ahora:
  - Una tarea de `task_start` que pase por una línea con `TRAP` se cae.
  - Un programa parado en `mui_wait_event` no acaba con `dbg_end` hasta que vuelve a su código.

## ARexx

Puerto propio, para Inferencia y para quien quiera:
- `ABRIR fichero [línea]`
- `SELECCION`: devuelve el texto elegido, el fichero y las líneas.
- `CAMBIAR fichero desde hasta "texto"`: el cambio entra en el deshacer.
- `COMPILAR`: devuelve los errores.
- `EJECUTAR`

## Piezas de Dash

Hechas en la rama `ide-piezas` de Dash, todavía sin fusionar:
- El depurador (`dbg_*`, `./dash --debug`).
- La ventana de un `.dashui` construida en tiempo de ejecución: `lib/dashui.dash`, con `dashui_window` y
  `dashui_object`.
- Órdenes ARexx propias en una aplicación MUI: `mui_app_rexx`.
- Ejecutar dashc y recoger sus errores: `run_capture` o `run_start`, sin bloquear la ventana.

## Fases

- **F1**: la ventana oscura, el editor con colores, abrir, guardar, compilar, ejecutar y saltar a los errores.
- **F2**: el puerto ARexx y el botón de Inferencia.
- **F3**: el editor de `.dashui` con MUI de verdad.
- **F4**: el depurador.
- **F5**: proyectos, catálogos, el paquete y la publicación.
