# Extensiones de Forja

Una extensión es un programa aparte que añade algo a Forja: opciones de menú (sueltas o en un menú suyo), teclas,
marcas y rayas en el margen del código, letras en el proyecto, una zona en la barra de botones, un texto en la barra,
pestañas de solo lectura con colores y teclas propias, paneles dentro de la ventana de Forja (junto al proyecto o junto
a la salida), un editor para un tipo de fichero con su ventana. Habla con
Forja por su puerto ARexx, `FORJA.1`. Si cae o se cuelga, Forja sigue en pie.

Se escriben en Dash con `lib/forja.dash`, pero valen en cualquier lenguaje que hable ARexx (también un script).

La de ejemplo es `extensiones/Contar`: cuenta las líneas y las palabras del fichero, lo pone en la barra y mete la
fecha en el cursor con Ctrl Alt D. `extensiones/Git` (git con dashgit) usa casi todo lo demás, también un panel (Cambios,
junto al proyecto). `extensiones/Inferencia` (el copiloto, que habla con Inferencia) usa las vistas para enseñar un
cambio antes de aceptarlo, `SUGERENCIA` y un panel abajo con el resultado de la prueba que escribe.
`extensiones/Sprites` y `extensiones/Mapas` (los editores de sprites y de mapas de tiles) abren sus tipos de fichero en
una ventana suya y hacen ficheros nuevos (`tipos`, `nuevo`, `GUARDADO`, `SINGUARDAR`, `COMPILAR fichero`).
`extensiones/Demos` (copper, MOD, pistas de sincronía y medidor) escribe en el código del editor (`TEXTO`, `CAMBIAR`,
`INSERTAR`) y habla además con otro programa, la demo en marcha.

## Dónde van

En el cajón `Extensiones` junto a Forja, una por cajón:

    Forja/
      Forja
      Extensiones/
        Contar/
          manifiesto.txt
          Contar           (el programa)

`ENV:Forja/extensiones` cambia ese cajón (las pruebas lo usan).

## El manifiesto

`manifiesto.txt`, una línea por dato, `clave = valor`. `#` empieza una nota. En Latin-1 o en UTF-8.

    # Contar: la extensión de ejemplo de Forja
    nombre = Contar
    version = 1.0
    autor = FreeMEM
    licencia = MIT
    descripcion = Cuenta las líneas y las palabras del fichero activo y lo pone en la barra.
    programa = Contar
    arranque = inicio
    sucesos = activo guardado cambiado
    menu = Contar las palabras | | contar
    menu = Insertar la fecha | ctrl alt d | fecha

| Clave | Qué es |
|-------|--------|
| `nombre`, `version`, `autor`, `licencia`, `descripcion` | Lo que enseña el gestor. |
| `programa` | El programa, dentro de su cajón. Por defecto, el nombre del cajón. |
| `arranque` | `inicio`: arranca con Forja. `menu` (por defecto): la primera vez que se elige su menú, se pulsa su tecla o se abre uno de sus tipos de fichero. |
| `sucesos` | Los avisos que quiere (ver Sucesos). Los demás no se le guardan. |
| `menu` | Una opción del menú: `título \| tecla \| orden`. La tecla y la orden pueden faltar; sin orden, es el título. Puede haber varias. |
| `submenu` | El título de su menú propio (`submenu = Git`): un menú más en la barra de menús, tras Extensiones, con sus opciones (12 como mucho). Hay 3 entre todas; si no quedan, van sueltas en Extensiones. |
| `pausa` | Cuántos milisegundos sin escribir antes de `CAMBIADO` (por defecto 1200; 300 como poco). |
| `tipos` | Los ficheros que abre ella, por su final: `.spr .bob`. Forja no los abre: se los pasa con `EDITAR` (desde el panel del proyecto, Abrir, la sesión o ARexx). El panel del proyecto los lista y la petición de Abrir los deja elegir. Los `.dash` y `.dashui` son siempre de Forja. |
| `nuevo` | Un fichero nuevo que hace ella: `título \| orden \| descripción` (`nuevo = _BOB \| bob \| Un BOB: del tamaño...`). Proyecto > Nuevo de extensión... (Amiga-B) enseña la descripción de cada uno y un botón con su título (el `_` marca su tecla); el elegido le llega como `NUEVO orden`. Puede haber varios. |

**En otro idioma**: `clave.idioma = valor` vale en lugar de `clave` cuando el catálogo de Forja es de ese idioma
(`descripcion.english = Counts the lines...`, `menu.english = Count the words | | contar`). Sirve para `nombre`,
`descripcion`, `submenu`, `menu` y `nuevo`; las de `menu` y `nuevo` van todas a la vez: si hay alguna en su idioma, las
otras no cuentan (la orden, la tercera parte, tiene que ser la misma). Sin catálogo (en castellano), no cuentan.

Teclas: `ctrl`, `alt`, `shift`, `amiga` y una letra, una cifra o `f1` a `f10`. Por ejemplo `ctrl alt d` o `f3`.
Funcionan en toda la ventana de Forja: con el puntero sobre el editor, el proyecto, la salida o la barra de botones,
con un panel de una extensión con el teclado y sin ningún fichero abierto (desde la API 6; antes, solo sobre el editor
con un fichero). Las de Forja van antes: `amiga s` nunca llega a una extensión. Libres hoy: Amiga con M, T o Y, y Ctrl
Alt con casi todas las letras (Amiga-I es de Inferencia; F1 a F10 son de Forja).

## Cómo arranca y cómo habla

Forja arranca el programa con dos argumentos: el puerto de Forja y el nombre de su cajón.

    Extensiones/Contar/Contar FORJA.1 Contar

La extensión:

1. Abre un puerto ARexx `FORJAEXT.<NOMBRE>` (en mayúsculas). Solo sirve para que Forja sepa que sigue viva: se cierra
   solo al acabar, también si el programa falla. Si ya existe, la extensión ya estaba en marcha y no debe seguir.
2. Vigila el fichero `ENV:Forja/Avisos/<nombre>` (`file_notify`).
3. Manda `HOLA <nombre>` a Forja.
4. Cada vez que cambia ese fichero, manda `SUCESOS <nombre>` y atiende lo que le llega.
5. Al acabar por su cuenta, `ADIOS <nombre>`: Forja quita sus marcas y su texto de la barra. Tras `SALIR` no hay que
   mandar nada: Forja ya no la cuenta y, si se está cerrando, solo atiende 2 s más para que las extensiones recojan
   su `SALIR`.

`lib/forja.dash` hace todo eso. Una extensión mínima:

    import "lib/forja.dash"

    Main
        if forja_empezar("Contar")
            while forja_suceso(0) != "SALIR"
                if forja_tipo == "MENU" and forja_dato == "fecha"
                    forja_insertar(date_text("%d-%m-%Y"))
                end
            end
            forja_acabar()
        end
    end

Con ventanas MUI propias, se espera a la vez a la ventana y a Forja:

    ev = mui_wait_event_signals(forja_senal())
    if ev == 0
        s = forja_suceso(-1)      # -1: no espera
        while s != ""
            ...
            s = forja_suceso(-1)
        end
    end

### Por qué así: Forja no espera nunca a una extensión

Forja no le manda órdenes ARexx a la extensión: si lo hiciera y la extensión estuviera colgada, Forja se quedaría
esperando su respuesta (`rexx_send` no tiene tiempo de espera). En su lugar:

- Los sucesos esperan en una cola de Forja, de 64 como mucho. Si se llena, se pierden los más viejos y Forja lo dice
  una vez en la salida.
- Forja avisa escribiendo un número en `ENV:Forja/Avisos/<nombre>`, en RAM. No espera a nadie.
- Si una extensión pasa 15 segundos sin recoger sus sucesos, Forja mira si su puerto sigue. Si no está, dice en la
  salida que se ha cerrado, quita sus marcas y la vuelve a arrancar la próxima vez que se elija su menú.
- Las órdenes de la extensión a Forja sí esperan respuesta, pero Forja contesta enseguida: ninguna orden espera a
  otro programa.

`lib/forja.dash` baja la prioridad de la extensión a -1, para que un trabajo largo suyo no frene a Forja.

## Sucesos

Cada uno es una línea: el tipo, un espacio y el dato.

| Suceso | Cuándo | Hay que pedirlo |
|--------|--------|-----------------|
| `MENU orden` | Se eligió su opción del menú o se pulsó su tecla. | No |
| `EDITAR ruta` | Se abrió un fichero de sus `tipos`. Si ya lo tiene abierto, que ponga delante su ventana. | No |
| `NUEVO orden` | Se eligió uno de sus `nuevo` en Amiga-B. | No |
| `GUARDAR` | Forja se cierra y el usuario eligió Guardar: que guarde los que dijo con `SINGUARDAR` (los que no tienen nombre, con su petición) y lo diga con `SINGUARDAR`. | No |
| `SALIR` | Forja se cierra, o la desactivan en el gestor. Debe acabar. | No |
| `ABIERTO ruta` | Se abrió un fichero en una pestaña nueva. | `abierto` |
| `GUARDADO ruta` | Se guardó. | `guardado` |
| `CERRADO ruta` | Se cerró su pestaña (sin ruta: el nombre). | `cerrado` |
| `ACTIVO ruta` | Cambió el fichero de delante (vacío: ninguno). Llega también al arrancar. | `activo` |
| `CAMBIADO ruta` | Se escribió en el editor (o por ARexx) y lleva su `pausa` sin escribir (1,2 s si no dice). | `cambiado` |
| `COMPILADO n` | Acabó de compilar: n errores (0 si compiló). Sus líneas, con `ERRORES`. | `compilado` |
| `PROYECTO cajón` | Cambió el cajón del panel del proyecto. Llega también al arrancar. | `proyecto` |
| `MARCA ruta línea` | Un clic en una marca suya del margen. | `marca` |
| `VUELTA` | La ventana de Forja vuelve a ser la activa (quizá cambió algo fuera: git mira el estado). Al volver, Forja lee otra vez el cajón del proyecto. | `vuelta` |
| `ZONA` | Un clic en su zona de la barra de botones. | No |
| `TECLA tecla línea nombre` | Una tecla en su pestaña de solo lectura `nombre`, con el cursor en esa línea (desde 1). La tecla es la letra, `return`, `tab`, `borrar` o `espacio`. Las flechas y Esc no llegan: mueven el cursor. | No |
| `PANEL título\|línea\|columna\|otra` | Un clic en una línea de su panel (línea y columna desde 1; `otra` 1 si ya era la elegida: un segundo clic). | No |
| `PANELTECLA título\|tecla\|línea` | Una tecla con su panel con el teclado, con esa línea elegida (0 ninguna). Como en `TECLA`; las flechas mueven la elegida, Esc devuelve el teclado al editor y Tab va a la entrada. | No |
| `PANELBOTON título\|orden` | Un clic en uno de sus botones. | No |
| `PANELTEXTO título\|texto` | Return en la entrada de su panel (el texto se queda: la extensión lo vacía si quiere). | No |

Un fichero sin guardar no tiene ruta: va su nombre ("sin nombre.dash").

## Órdenes

Al puerto `FORJA.1`. Las líneas y columnas cuentan desde 1. Un fichero entre comillas si lleva espacios. RC 0 bien,
5 si no había nada que hacer, 10 si la orden está mal o no se puede.

Las de "el fichero activo" son del fichero de texto de delante en Forja (los de las extensiones, como un sprite, están
en su ventana y Forja no los ve).

### La extensión

| Orden | Respuesta |
|-------|-----------|
| `HOLA nombre` | La versión de la API y la de Forja: `6 0.8.0` (la 2 trae ZONA, VISTA, RAYAS, menú propio, pausa...; la 3, SUGERENCIA y cerrar una VISTA; la 4, `nuevo`, `NUEVO`, `GUARDAR`, `GUARDADO`, `SINGUARDAR`, `DELANTE` y `COMPILAR fichero`; la 5, `EDITANDO` y `SALIR`; la 6, los paneles, las teclas en toda la ventana y `SUGERENCIA` de varias líneas o en medio de una). |
| `SUCESOS nombre` | Sus sucesos, uno por línea, y la cola queda vacía. |
| `ADIOS nombre` | Se va. Forja quita sus marcas y su texto. |
| `MENU nombre título\|tecla\|orden` | Una opción más en su menú (el propio, si tiene `submenu`; si no, suelta en Extensiones), mientras Forja siga abierto. Su número; RC 5 si no caben (12 sueltas entre todas, y 12 en cada menú propio). |

### Leer

| Orden | Respuesta |
|-------|-----------|
| `ACTIVO` | Del fichero de delante, una cosa por línea: ruta (vacía si no se ha guardado), nombre, cambiado (0 o 1), tipo (`texto`, `dashui` o `vista`, una pestaña de solo lectura) y número de líneas. RC 5 si no hay ninguno. |
| `TEXTO [fichero]` | Todo el texto, guardado o no. Sin fichero, el activo. El fichero tiene que estar abierto. |
| `TEXTODISCO [fichero]` | El texto como se guardaría: en UTF-8 si el fichero lo estaba (`TEXTO` va siempre en Latin-1). Para compararlo con el del disco (git). |
| `VERSION [fichero]` | Cuántos cambios lleva el texto: sube con cada uno. Para `RAYAS` con versión. |
| `LINEAS desde hasta [fichero]` | Esas líneas, las dos incluidas. |
| `LINEA n [fichero]` | Una línea. |
| `CURSOR` | `línea columna`. |
| `ELEGIDO` | `l1 c1 l2 c2` en la primera línea y lo elegido tal cual en las siguientes. Sin nada elegido, el cursor dos veces. |
| `SELECCION` | La ruta, la primera y la última línea elegidas y su texto (las líneas enteras). |
| `ABIERTO fichero` | `1` o `0`. |
| `ABIERTOS` | Las rutas de las pestañas, una por línea. |
| `CAMBIADOS` | Las rutas de los ficheros abiertos con cambios sin guardar, una por línea. |
| `PROYECTO` | El cajón del panel del proyecto en la primera línea; después, lo que enseña (los cajones acaban en `/`). |
| `ESTADO` | `libre`, `compilando`, `ejecutando` o `depurando`. |
| `ERRORES` | Las líneas de error de la última compilación; si no hay, las de los errores marcados al guardar o al escribir (`dash --check`), con la ruta en minúsculas. |
| `SALIDA` | El texto de la salida. |
| `BARRA` | Lo que enseña la barra. |
| `ZONA` | Las zonas de la barra de botones, una por línea: `extensión\|texto\|detalle`. |
| `RAYAS fichero` | Las rayas de ese fichero: `línea:bits` separadas por espacios (1 añadida, 2 cambiada, 4 quitadas encima, 8 quitadas debajo). |
| `SUGERENCIA` | La sugerencia que se ve: `línea columna texto` (vacía si ninguna; el texto puede tener varias líneas). |
| `PANELES` | Los paneles de las extensiones, uno por línea: `extensión\|título\|lado\|delante\|elegida\|líneas\|entrada` (lado `izquierda` o `abajo`; delante 1 si es el que se ve en su lado; la línea elegida desde 1, 0 ninguna; cuántas líneas tiene; el texto de su entrada). |

### Escribir

Todo con deshacer, como si lo hubiera escrito el usuario.

| Orden | Qué hace |
|-------|----------|
| `INSERTAR texto` | Lo escribe en el cursor, en lugar de lo elegido. El texto es todo lo que sigue al primer espacio, con sus espacios y saltos de línea. Amiga-Z lo deshace de una vez. |
| `ESCRIBIR texto` | Cambia todo el texto del fichero activo. |
| `CAMBIAR fichero desde hasta texto` | Cambia esas líneas. Con `hasta = desde - 1` mete el texto antes de la línea `desde`. Abre el fichero si hace falta. |
| `CURSOR línea columna` | Lleva el cursor ahí, a la vista. |
| `ELEGIR l1 c1 l2 c2` | Elige de (l1, c1) a (l2, c2). |
| `ABRIR fichero [línea]` | Lo abre, o va a su pestaña. Si es de un tipo de una extensión, se lo pasa a ella. |
| `GUARDAR [fichero]` | Lo guarda. |
| `IRA línea`, `BUSCAR texto`, `CAMBIARTODO buscar cambiar` | Como en el menú. |
| `COMPILAR [fichero]`, `EJECUTAR [fichero]` | Sin esperar: `ESTADO` dice cuándo acaba; también el suceso `COMPILADO`. Sin fichero, el programa del fichero de delante. Un `.dash` abierto con su `Main` (una prueba) es él mismo: pasa delante y se compila. Con un fichero que no es un programa (un sprite, un mapa, un módulo), el de su cajón: un `.dash` abierto con `Main` de ese cajón o el de encima, si no su `main.dash` o el del proyecto, abierto o no. RC 5 si ya compila o ejecuta; 10 si no hay programa. |

### Los ficheros de una extensión

Para las que abren sus propios tipos de fichero (`tipos`, `nuevo`) en una ventana suya.

| Orden | Qué hace |
|-------|----------|
| `GUARDADO nombre fichero` | Guardó un fichero suyo: Forja dice "Guardado: fichero" en la salida, lo cuenta a las extensiones que piden `guardado` y, si es del cajón del proyecto, lee otra vez el panel (sale el fichero nuevo). |
| `SINGUARDAR nombre`, y un fichero por línea | Sus ficheros con cambios sin guardar (los nombres; sin líneas, ninguno). Sustituye la lista de antes. Al salir, Forja los cuenta con los suyos en "Cambios sin guardar": con Guardar le manda `GUARDAR` y espera (20 s como mucho) a que la lista quede vacía; si no, Forja sigue abierta. Con Descartar, se pierden. |
| `DELANTE` | La ventana de Forja, delante y activa (Ventana > Forja en la de la extensión). |
| `EDITANDO nombre`, y una ruta entera por línea | Los ficheros suyos que tiene abiertos (sin líneas, ninguno). Sustituye la lista de antes. Al salir, Forja los guarda en su sesión y la próxima vez los vuelve a abrir (con `EDITAR`, como al abrirlos desde Forja). |
| `SALIR` | Que Forja se cierre, como con Amiga-Q en su ventana (para Amiga-Q en la de la extensión): pregunta por lo que haya sin guardar, también lo de las extensiones, y manda `SALIR` a todas. |

### La ventana

| Orden | Qué hace |
|-------|----------|
| `AVISO tipo texto` | Una línea en la salida: tipo 0 normal, 1 error (en rojo), 2 bien (en verde). |
| `BARRA nombre texto` | Su texto en la barra, a la derecha del título de la salida. Sin texto, lo quita. |
| `MARCAS nombre fichero`, y una marca por línea: `línea símbolo` | Sus marcas en el margen de ese fichero. Sustituyen las suyas de antes; sin líneas, las quita. |
| `MARCASPROYECTO nombre`, y una por línea: `letras ruta` | Sus letras junto a los ficheros y cajones del panel del proyecto (rutas enteras; un cajón, sin `/` al final), a la derecha. Sustituyen las suyas. El color sale de la última letra: `A` verde; `D`, `U` y `!` rojo; `?` gris; las demás, azul. |
| `RAYAS nombre fichero [versión]`, y una por línea: `línea símbolos` | Sus rayas en el margen de ese fichero, pegadas al texto: `+` añadida (raya llena, verde), `~` cambiada (raya a trozos, azul), `-` se quitaron líneas justo encima (un triángulo rojo arriba), `_` se quitaron justo debajo (abajo; para lo quitado tras la última). Se juntan: `~-`. Sustituyen las suyas; sin líneas, las quita. Con versión (la de `VERSION`), solo si el texto sigue en esa: si no, RC 5 y nada cambia. |
| `ZONA nombre icono\|texto\|detalle\|corto` | Su zona en la barra de botones, a la derecha: un icono (uno de Forja, como `rama` o `inferencia`, o uno propio: 12 filas de 12 separadas por `/`, con `#` los píxeles), un texto y un detalle en otro color. Si no cabe el detalle, va el corto; si tampoco, solo el texto; si tampoco, no se ve. Un clic da `ZONA`. Sin texto ni detalle, la quita. |
| `VISTA nombre "título"`, y una por línea: el color (un carácter) y el texto | Una pestaña de solo lectura, delante; si ya tiene una con ese título, la vuelve a llenar. El color de cada línea: `+` verde, `-` rojo, `@` azul, `#` gris, `!` amarillo; otro (un espacio), el del texto. Sus teclas llegan con `TECLA`; el cursor se mueve con `CURSOR`. No se guarda ni se escribe en ella. Sin ninguna línea detrás, cierra esa pestaña suya (RC 5 si no la hay). |
| `SUGERENCIA nombre línea columna versión`, y el texto en las líneas siguientes | Una sugerencia en gris en el cursor del fichero activo, como la de un copiloto: Tab la mete (con deshacer, de una vez), Esc la quita y se va sola al escribir o al mover el cursor. Solo si el cursor está en esa línea y columna, sin nada elegido, y el texto sigue en esa versión (`VERSION`): si no, RC 5 y no sale. Puede tener varias líneas y el cursor puede estar en medio de una (API 6): la primera se ve desde el cursor, las demás encima de las líneas de debajo (con una raya a la izquierda) y lo que había tras el cursor, detrás de la última, como quedará. Si a la vez está la lista para completar, Tab es de la lista. `SUGERENCIA nombre` sin más quita la suya. |

### Paneles

Desde la API 6. Un panel es una pestaña más en la ventana de Forja: junto al panel del proyecto (lado `izquierda`) o
junto a la salida (`abajo`). Con un panel en un lado, la fila del título de ese lado son pestañas: la de Forja (el
proyecto o la salida) y las de los paneles; un clic en una la pone delante. Forja lo pinta con lo que manda la
extensión, así que no cuesta una ventana más ni que la extensión esté despierta para repintarlo:

- líneas con un color cada una (los de `VISTA`), y una elegida (resaltada);
- botones abajo (los que no caben en una fila pasan a otra);
- una entrada de texto de una línea sobre los botones, con su etiqueta, si se pide.

Un clic en el panel le da el teclado: las flechas mueven la elegida y las demás teclas llegan con `PANELTECLA`; Tab va
a la entrada y vuelve; en la entrada se escribe (Return da `PANELTEXTO`); Esc devuelve el teclado al editor, como un
clic en el editor. Las teclas con Amiga, las de las extensiones y las del depurador valen igual. Al depurar, el lado
izquierdo enseña las variables, como siempre. La barra de su lado (la del proyecto o la de la salida) mueve el panel
de delante, y la rueda también. Hay 8 paneles como mucho entre todas; se van con su extensión.

| Orden | Qué hace |
|-------|----------|
| `PANEL nombre "título" [izquierda\|abajo]`, y una línea por fila: el color (un carácter) y el texto | Lo pone o lo vuelve a llenar (la elegida y lo desplazado se quedan). No lo pone delante. RC 5 si ya no caben. |
| `PANELVER nombre "título" [entrada]` | Delante en su lado; con `entrada`, su entrada toma el teclado. |
| `PANELCERRAR nombre "título"` | Lo quita. |
| `PANELBOTONES nombre "título"`, y una línea por botón: `texto\|orden` | Sus botones (sin líneas, ninguno). |
| `PANELENTRADA nombre "título" etiqueta`, y quizá el texto en la línea siguiente | Una entrada con esa etiqueta; con la línea siguiente cambia su texto (vacía, la vacía). Sin etiqueta, la quita. |
| `PANELCURSOR nombre "título" línea` | La línea elegida (desde 1; 0 ninguna), a la vista. |

Así lo usa Git: `PANEL Git "Cambios" izquierda` con una fila por fichero (`[x] M main.dash`), la entrada "Mensaje:" y
los botones Diferencias, Preparar todo, Quitar todo y Confirmar. Un clic en la casilla (las columnas 1 a 3) o Espacio
prepara el fichero; un segundo clic en la elegida o Return abre sus diferencias; Return en el mensaje confirma.

### Las marcas y las rayas

Las marcas del margen van en una columna entre los números y el texto, que solo aparece si el fichero tiene alguna.
Se distinguen por el símbolo, también con los 4 colores del Workbench. El color sale del símbolo: `+` verde
(añadida), `-` y `!` rojo (quitada, error), `~` y `*` azul (cambiada); los demás, del color del texto. Las rayas van
a la derecha de los números, pegadas al texto, y se distinguen por la forma.

Al escribir (también por ARexx), las marcas y las rayas siguen a su línea: si se meten o se quitan líneas, las de
después se mueven, y las de las líneas quitadas se van. La extensión las vuelve a poner cuando le parezca (git, con
`CAMBIADO`: del texto que hay en el editor, sin guardar).

Ejemplo, desde ARexx:

    ADDRESS FORJA.1
    'MARCAS Git "Work:juego/main.dash"' || '0a'x || '3 +' || '0a'x || '7 ~'

### Por lotes

Cada orden ARexx cuesta (en un 68020 a 14 MHz, unos milisegundos). Para leer varias cosas de una vez:

    LOTE
    ACTIVO
    CURSOR
    LINEA 12

La palabra `LOTE` y, en cada línea siguiente, una orden de una sola línea. Las respuestas van en el mismo orden,
separadas por el carácter 30, con RC 0: ARexx no deja dar respuesta con otro RC, así que la de una orden que falla
va vacía. En `lib/forja.dash`: `forja_lote(["ACTIVO", "CURSOR"])`.

Para leer el fichero entero, `TEXTO` de una vez es mucho más rápido que línea a línea.

## Un editor para un tipo de fichero

Así van `extensiones/Sprites` y `extensiones/Mapas`:

    tipos = .iff .ilbm .lbm .brush .bob .spr
    nuevo = _Sprite | sprite | Un sprite de hardware: 16 píxeles de ancho, 3 colores y el transparente.
    arranque = menu

- Arranca la primera vez que se abre uno de sus ficheros (`EDITAR`) o se pide uno nuevo (`NUEVO`), y abre su ventana
  MUI con una pestaña por fichero. Si ya lo tiene abierto, pone delante su ventana.
- Guarda ella, con Amiga-S en su ventana, y lo dice con `GUARDADO`; los que tienen cambios, con `SINGUARDAR`, para que
  Forja pregunte por ellos al salir. Si le llega `GUARDAR`, los guarda.
- Compilar y Ejecutar (Amiga-K y Amiga-E en su ventana) son `COMPILAR fichero` y `EJECUTAR fichero`: Forja compila el
  programa del cajón del sprite, aunque no esté abierto.
- Cuando se cierra su última pestaña, acaba (y suelta su memoria). Forja la vuelve a arrancar con el siguiente.

## lib/forja.dash

| Función | Qué hace |
|---------|----------|
| `forja_empezar(nombre)` | Lee los argumentos, abre su puerto, vigila su aviso y saluda. `false` si Forja no está o ya estaba en marcha. |
| `forja_suceso(ms)` | El siguiente suceso, también en `forja_tipo` y `forja_dato`. Si no hay, espera hasta `ms` (0: lo que haga falta; -1: no espera) y da `""`. `SALIR` si Forja se cierra o con Ctrl-C. |
| `forja_senal()` | La señal del aviso, para `mui_wait_event_signals`. |
| `forja_acabar()` | `ADIOS`. |
| `forja_orden(orden)` | Cualquier orden: su respuesta; el RC en `forja_rc` (-1 si Forja no está). |
| `forja_lote(ordenes)` | Varias en un viaje. |
| `forja_activo()`, `forja_fichero()` | `ACTIVO`, y solo su ruta. |
| `forja_texto(ruta)`, `forja_lineas(a, b)`, `forja_linea(n)` | Leer (ruta `""`: el activo). |
| `forja_cursor()` | Lee el cursor en `forja_cursor_linea` y `forja_cursor_columna`. |
| `forja_seleccion()` | Lo elegido. |
| `forja_proyecto()` | El cajón del proyecto y sus ficheros. |
| `forja_insertar(texto)`, `forja_escribir(texto)`, `forja_cambiar(ruta, a, b, texto)` | Escribir. |
| `forja_ir(l, c)`, `forja_elegir(l1, c1, l2, c2)`, `forja_abrir(ruta, línea)` | Mover el cursor, elegir, abrir. |
| `forja_aviso(texto)`, `forja_aviso_tipo(texto, tipo)` | Una línea en la salida. |
| `forja_barra(texto)` | Su texto en la barra. |
| `forja_marcas(ruta, líneas, símbolos)`, `forja_marcas_proyecto(rutas, letras)` | Sus marcas. |
| `forja_menu(título, tecla, orden)` | Una opción más en su menú. |
| `forja_zona(icono, texto, detalle, corto)` | Su zona en la barra de botones. |
| `forja_vista(nombre, líneas, colores)` | Una pestaña de solo lectura con un color por línea (`colores`: un carácter por línea). |
| `forja_rayas(ruta, líneas, símbolos, versión)` | Sus rayas en el margen (versión -1: sin mirarla). |
| `forja_texto_disco(ruta)`, `forja_version_texto(ruta)` | `TEXTODISCO` y `VERSION`. |
| `forja_cerrar_vista(nombre)` | Cierra su pestaña de solo lectura. |
| `forja_sugerencia(línea, columna, versión, texto)` | `SUGERENCIA` (texto `""`: la quita). |
| `forja_guardado(ruta)` | `GUARDADO`: guardó un fichero suyo. |
| `forja_sin_guardar(nombres)` | `SINGUARDAR`: los suyos con cambios sin guardar (`[]`: ninguno). |
| `forja_compilar(ruta, ejecutar)` | `COMPILAR` o `EJECUTAR` el programa de ese fichero (ruta `""`: el de delante en Forja). |
| `forja_delante()` | `DELANTE`. |
| `forja_editando(rutas)` | `EDITANDO`: los suyos abiertos, para la sesión (`[]`: ninguno). |
| `forja_salir()` | `SALIR`: Forja se cierra (Amiga-Q en su ventana). |
| `forja_panel(título, lado, líneas, colores)` | `PANEL` (lado `"izquierda"` o `"abajo"`). |
| `forja_panel_ver(título, entrada)`, `forja_panel_cerrar(título)` | `PANELVER` (con `entrada` true, el teclado a su entrada) y `PANELCERRAR`. |
| `forja_panel_botones(título, botones)` | `PANELBOTONES` (`"texto\|orden"` cada uno). |
| `forja_panel_entrada(título, etiqueta)`, `forja_panel_entrada_texto(título, etiqueta, texto)` | `PANELENTRADA` (la segunda cambia también el texto). |
| `forja_panel_cursor(título, línea)` | `PANELCURSOR`. |
| `forja_panel_estado(título)` | Su línea de `PANELES` en partes (la última, el texto de la entrada); `[]` si no lo tiene. |
| `forja_campo(n)` | La parte n (desde 0, separadas por `\|`) del dato del último suceso: en los de los paneles, la 0 es el título. |

El `import "lib/forja.dash"` lo encuentra `./dash` subiendo de cajón en cajón desde el fichero que importa: una
extensión en `extensiones/X/` del repositorio de Forja (o en `Forja/Extensiones/X/`, con `Forja/lib/forja.dash`)
compila sin más. Si algún día pasa a la `lib/` de Dash, el `import` no cambia.

## Su catálogo

Los textos de la extensión, como los de Forja: `@catalog "X.catalog" 1 "español"` en su programa y `tr(número,
"texto")`. El catálogo va en `Catalogs/<idioma>/X.catalog` dentro de su cajón (su `PROGDIR:`). En el repositorio de
Forja, `python3 tools/catalogos.py cd`, `ct` y `catalog` hacen también los de las extensiones
(`extensiones/X/catalogos/X.cd` y `english.ct`; el `.catalog`, en `build/Extensiones/X/Catalogs/english`), y
`tools/paquete.py` los pone junto a cada una. Git, Inferencia, Sprites y Mapas tienen el inglés.

## El gestor

Extensiones > Gestor de extensiones... Lista las que hay, con su estado: apagada, en marcha o el error que tenga (por
ejemplo, que falta su programa). Debajo, su descripción, autor, licencia y cuándo arranca.

- **Activar / Desactivar** (o doble clic): se guarda en `ENVARC:Forja/extensiones_apagadas`. Desactivarla le manda
  `SALIR` y quita sus opciones del menú, sus marcas y su texto. Activarla vuelve a poner sus opciones y, si es de
  `arranque = inicio`, la arranca.
- **Instalar...**: se elige el `manifiesto.txt` de un cajón o un `.lha` (hace falta `C:LhA`). Forja enseña qué es y
  avisa de que una extensión es un programa y puede hacer cualquier cosa en el Amiga. Con "Instalar y activar" queda
  lista; con "Instalar", apagada. Se copia a `Extensiones/<nombre de su cajón>`; si ya estaba, la sustituye.

Las que se copian a mano en `Extensiones/` están activas al arrancar Forja.

## Lo que falta

- Con MUI 3.8, añadir o quitar un menú propio con la ventana abierta la cierra y la abre (los del arranque se hacen
  antes de abrirla). Las opciones sueltas de Extensiones se ponen y se quitan con `mui_menu_extend` y
  `mui_menu_remove` (12 como mucho, solo las que hay); la raya de encima se queda (`mui_menu_separator` de Dash no da
  un objeto que se pueda quitar).
- Los paneles son de texto (líneas, botones y una entrada): una extensión que necesite dibujar (un lienzo) sigue
  abriendo su ventana.
- Instalar desde un `.lha` está probado con un LhA del Amiga puesto en el emulador para la prueba (`LHA_AMIGA`); el
  sistema de pruebas no lo trae.
