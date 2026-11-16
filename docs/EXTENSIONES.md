# Extensiones de Forja

Una extensión es un programa aparte que añade algo a Forja: opciones de menú, teclas, marcas en el código, un texto
en la barra, un editor para un tipo de fichero. Habla con Forja por su puerto ARexx, `FORJA.1`. Si cae o se cuelga,
Forja sigue en pie.

Se escriben en Dash con `lib/forja.dash`, pero valen en cualquier lenguaje que hable ARexx (también un script).

La de ejemplo es `extensiones/Contar`: cuenta las líneas y las palabras del fichero, lo pone en la barra y mete la
fecha en el cursor con Ctrl Alt D.

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
| `menu` | Una opción del menú Extensiones: `título \| tecla \| orden`. La tecla y la orden pueden faltar; sin orden, es el título. Puede haber varias. |
| `tipos` | Los ficheros que abre ella, por su final: `.spr .bob`. Forja no los abre: se los pasa con `EDITAR`. Los `.dash` y `.dashui` son siempre de Forja. |

Teclas: `ctrl`, `alt`, `shift`, `amiga` y una letra, una cifra o `f1` a `f10`. Por ejemplo `ctrl alt d` o `f3`.
Funcionan con el puntero sobre el editor. Las de Forja van antes: `amiga s` nunca llega a una extensión. Libres hoy:
F2, F3, F4 y F8, y Amiga con M, T o Y.

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
| `EDITAR ruta` | Se abrió un fichero de sus `tipos`. | No |
| `SALIR` | Forja se cierra, o la desactivan en el gestor. Debe acabar. | No |
| `ABIERTO ruta` | Se abrió un fichero en una pestaña nueva. | `abierto` |
| `GUARDADO ruta` | Se guardó. | `guardado` |
| `CERRADO ruta` | Se cerró su pestaña (sin ruta: el nombre). | `cerrado` |
| `ACTIVO ruta` | Cambió el fichero de delante (vacío: ninguno). Llega también al arrancar. | `activo` |
| `CAMBIADO ruta` | Se escribió en el editor y lleva 1,2 s sin escribir. | `cambiado` |
| `COMPILADO n` | Acabó de compilar: n errores (0 si compiló). Sus líneas, con `ERRORES`. | `compilado` |
| `PROYECTO cajón` | Cambió el cajón del panel del proyecto. Llega también al arrancar. | `proyecto` |
| `MARCA ruta línea` | Un clic en una marca suya del margen. | `marca` |
| `VUELTA` | La ventana de Forja vuelve a ser la activa (quizá cambió algo fuera: git mira el estado). Se mira cada 1,5 s, solo si alguna lo pide. | `vuelta` |

Un fichero sin guardar no tiene ruta: va su nombre ("sin nombre.dash").

## Órdenes

Al puerto `FORJA.1`. Las líneas y columnas cuentan desde 1. Un fichero entre comillas si lleva espacios. RC 0 bien,
5 si no había nada que hacer, 10 si la orden está mal o no se puede.

Las de "el fichero activo" valen solo con un fichero de texto delante (no con un sprite o un mapa): si no, RC 10.

### La extensión

| Orden | Respuesta |
|-------|-----------|
| `HOLA nombre` | La versión de la API y la de Forja: `1 0.6.5`. |
| `SUCESOS nombre` | Sus sucesos, uno por línea, y la cola queda vacía. |
| `ADIOS nombre` | Se va. Forja quita sus marcas y su texto. |
| `MENU nombre título\|tecla\|orden` | Una opción más en el menú Extensiones, mientras Forja siga abierto. Su número; RC 5 si no caben (hay 12 entre todas). |

### Leer

| Orden | Respuesta |
|-------|-----------|
| `ACTIVO` | Del fichero de delante, una cosa por línea: ruta (vacía si no se ha guardado), nombre, cambiado (0 o 1), tipo (`texto`, `dashui`, `sprite` o `mapa`) y número de líneas. RC 5 si no hay ninguno. |
| `TEXTO [fichero]` | Todo el texto, guardado o no. Sin fichero, el activo. El fichero tiene que estar abierto. |
| `LINEAS desde hasta [fichero]` | Esas líneas, las dos incluidas. |
| `LINEA n [fichero]` | Una línea. |
| `CURSOR` | `línea columna`. |
| `ELEGIDO` | `l1 c1 l2 c2` en la primera línea y lo elegido tal cual en las siguientes. Sin nada elegido, el cursor dos veces. |
| `SELECCION` | La ruta, la primera y la última línea elegidas y su texto (las líneas enteras). |
| `ABIERTO fichero` | `1` o `0`. |
| `ABIERTOS` | Las rutas de las pestañas, una por línea. |
| `PROYECTO` | El cajón del panel del proyecto en la primera línea; después, lo que enseña (los cajones acaban en `/`). |
| `ESTADO` | `libre`, `compilando`, `ejecutando`, `depurando` o `git`. |
| `ERRORES` | Las líneas de error de la última compilación. |
| `SALIDA` | El texto de la salida. |
| `BARRA` | Lo que enseña la barra. |

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
| `COMPILAR`, `EJECUTAR` | Sin esperar: `ESTADO` dice cuándo acaba; también el suceso `COMPILADO`. |

### La ventana

| Orden | Qué hace |
|-------|----------|
| `AVISO tipo texto` | Una línea en la salida: tipo 0 normal, 1 error (en rojo), 2 bien (en verde). |
| `BARRA nombre texto` | Su texto en la barra, a la derecha del título de la salida. Sin texto, lo quita. |
| `MARCAS nombre fichero`, y una marca por línea: `línea símbolo` | Sus marcas en el margen de ese fichero. Sustituyen las suyas de antes; sin líneas, las quita. |
| `MARCASPROYECTO nombre`, y una por línea: `letras ruta` | Sus letras junto a los ficheros y cajones del panel del proyecto (rutas enteras; un cajón, sin `/` al final). Sustituyen las suyas. El color sale de la última letra: `A` verde; `D`, `U` y `!` rojo; `?` gris; las demás, azul. |

Las marcas del margen van en una columna entre los números y el texto, que solo aparece si el fichero tiene alguna.
Se distinguen por el símbolo, también con los 4 colores del Workbench. El color sale del símbolo: `+` verde
(añadida), `-` y `!` rojo (quitada, error), `~` y `*` azul (cambiada); los demás, del color del texto.

Las marcas no se mueven al escribir: la extensión las vuelve a poner cuando le parezca (git, con `GUARDADO`).

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
| `forja_menu(título, tecla, orden)` | Una opción más en el menú. |

El `import "lib/forja.dash"` lo encuentra `./dash` subiendo de cajón en cajón desde el fichero que importa: una
extensión en `extensiones/X/` del repositorio de Forja (o en `Forja/Extensiones/X/`, con `Forja/lib/forja.dash`)
compila sin más. Si algún día pasa a la `lib/` de Dash, el `import` no cambia.

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

- Teclas de las extensiones fuera del editor (con el puntero en el proyecto o la salida).
- El menú tiene 12 opciones para todas las extensiones. Las libres quedan vacías y apagadas: Dash no puede
  añadir ni quitar opciones de un menú ya hecho (se pidió `mui_menu_add` / `mui_menu_remove`).
- Paneles propios dentro de la ventana de Forja: hoy cada extensión pinta sus ventanas.
- Que las marcas sigan a las líneas al escribir.
- Probar la instalación desde un `.lha` en el emulador (no tiene `C:LhA`).
