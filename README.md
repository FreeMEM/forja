# Forja

*[English](README.en.md) | Castellano*

Un entorno de desarrollo para [Dash](https://github.com/FreeMEM/FreeMEMLang) que corre en el propio Amiga, con
fondo negro: editor con colores, compilar y ejecutar, depurador paso a paso y editor de ventanas `.dashui` con MUI
de verdad. Se entiende por ARexx con [Inferencia](https://github.com/FreeMEM/inferencia), la IA para el Amiga.

Es una versión de prueba: funciona en el emulador, pero aún no se ha probado en un Amiga de verdad. Habla en
castellano o en inglés, según el idioma de las Preferencias de Locale (el catálogo inglés va en `Catalogs/`).

## Qué necesita

- AmigaOS 3.0 o mejor, con un 68020 o mejor, y MUI 5.
- dashc, el compilador de Dash 2.0 para el Amiga (`make amiga` en `dashc/` de Dash), con sus ficheros `.drt` al
  lado. Forja lo busca en `ENV:Forja/dashc`, o como `dashc` en el camino de órdenes.
- Para el botón Inferencia, [Inferencia](https://github.com/FreeMEM/inferencia) (`ENV:Forja/inferencia`).
- Los colores de la sintaxis se ven mejor con más de 4 colores en la pantalla.

## Uso

`Forja [fichero]`, o un doble clic en su icono. Sin fichero, abre lo de la última vez (se puede quitar en
Preferencias).

- **Editor**: el teclado va al editor con el puntero encima. Flechas; con Mayúsculas eligen; Alt: principio y final
  de línea, página arriba y abajo; Ctrl: de palabra en palabra, principio y final del texto. Tab y Mayúsculas+Tab
  sangran. Deshacer (Amiga-Z), rehacer (Amiga-R), cortar, copiar y pegar con el portapapeles del sistema.
- **Ficheros**: pestañas; Amiga-N, Amiga-O, Amiga-S, Amiga-W. El panel de la izquierda abre los ficheros del cajón
  con un clic. Al cerrar con cambios, pregunta.
- **Buscar y cambiar** (Amiga-F) e **ir a la línea** (Amiga-L).
- **Compilar** (Amiga-K) y **ejecutar** (Amiga-E): los errores salen abajo, y un clic lleva a su línea.
- **Depurar** (Amiga-G o F5): puntos de parada con F9 o un clic en el margen; F5 seguir, F10 paso, F6 entrar, F7
  salir. A la izquierda, la pila y las variables.
- **Ventanas `.dashui`**: se abren en el editor de ventanas (Amiga-D cambia a texto). El árbol de objetos y sus
  propiedades; "+" añade, Supr quita, Alt+flechas mueve. Amiga-P abre la vista previa con MUI de verdad. Se guarda
  igual que la extensión de VS Code.
- **Inferencia** (Amiga-I): le manda el fichero, o las líneas elegidas.
- **Sprites y BOBs**: las imágenes IFF ILBM (también los pinceles de DPaint) se abren en su propio editor, y
  Amiga-B crea un sprite de hardware (16 de ancho, 3 colores y el transparente) o un BOB (del tamaño y los
  colores que quieras). Se guardan como IFF, y `sprite_load` y `bob_load` de Dash los cargan tal cual.
  - Dibujar: P lápiz, L línea, B caja (con Mayúsculas al empezar, rellena), F relleno, K cuentagotas, A punto
    de agarre. Alt + clic borra; Ctrl + clic coge el color. Arriba, abajo y las cifras eligen color; las barras
    R G B lo cambian.
  - Fotogramas: flechas para ir de uno a otro, N nuevo, D duplicar, Supr quitar, Retroceso vaciar, H y V espejo,
    Alt + flechas mover, Mayúsculas + flechas desplazar el dibujo, Amiga-C/X/V copiar, cortar y pegar. O enciende
    la piel de cebolla.
  - Animar: Espacio pone en marcha la vista animada; + y - cambian la velocidad.
  - Tamaño: Ctrl + flechas, o la pestaña Tamaño (ancho, alto, colores); T pasa de sprite de hardware a BOB.
  - C copia al portapapeles las líneas de Dash que lo cargan, con sus colores y cómo animarlo.

  ![El editor de sprites con una nave de 4 fotogramas](docs/img/sprites.png)

### ARexx

Puerto `FORJA.1`: `ABRIR fichero [línea]`, `ABIERTO fichero`, `TEXTO fichero`, `SELECCION`,
`CAMBIAR fichero desde hasta texto`, `GUARDAR [fichero]`, `COMPILAR`, `EJECUTAR`, `ESTADO`, `ERRORES`,
`BUSCAR texto`, `CAMBIARTODO buscar cambiar`, `IRA línea`.

## Compilar

Con Dash 2.0: `./dash src/main.dash -o Forja`. El paquete: `python3 tools/paquete.py 0.1`. Las pruebas, en el
emulador: [tests/LEEME.md](tests/LEEME.md).

Escrito en Dash. Licencia MIT.
