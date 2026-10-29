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
| [Compilar] [Ejecutar] [Depurar] [Paso] [Entrar] [Salir] [Seguir] [Inferencia]  |
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
  - Para el resto de la ventana se instalan unas preferencias de MUI propias del programa, con tema oscuro.
    MUI las guarda por aplicación.
- **Editor de código**: hecho sobre el canvas, porque Dash no tiene campo de varias líneas.
  - Colores según la sintaxis de Dash, números de línea y puntos de parada.
  - Buscar y reemplazar, deshacer y pestañas.
  - Es la pieza más grande.
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

Ahora el depurador de Dash solo funciona en el emulador (`--debug`, `debug_break`, por uaelib). En un Amiga de
verdad hace falta otro:
- El IDE lanza el programa como proceso propio y recoge sus excepciones con `tc_TrapCode`, como ya hace el runtime
  de Dash.
- Los puntos de parada ponen una instrucción `TRAP` en la dirección de la línea.
- El paso a paso usa el bit de traza del 68k.
- dashc tiene que dar una tabla de líneas y direcciones y la posición de cada variable.

## ARexx

Puerto propio, para Inferencia y para quien quiera:
- `ABRIR fichero [línea]`
- `SELECCION`: devuelve el texto elegido, el fichero y las líneas.
- `CAMBIAR fichero desde hasta "texto"`: el cambio entra en el deshacer.
- `COMPILAR`: devuelve los errores.
- `EJECUTAR`

## Piezas que faltan en Dash

- Información de depuración en dashc y una librería de depuración: lanzar un proceso hijo, puntos de parada,
  paso a paso, leer memoria y registros.
- Construir una ventana MUI desde un `.dashui` en tiempo de ejecución.
- ARexx como servidor en MUI (la misma pieza que necesita Inferencia).

## Fases

- **F1**: la ventana oscura, el editor con colores, abrir, guardar, compilar, ejecutar y saltar a los errores.
- **F2**: el puerto ARexx y el botón de Inferencia.
- **F3**: el editor de `.dashui` con MUI de verdad.
- **F4**: el depurador.
- **F5**: proyectos, catálogos, el paquete y la publicación.
