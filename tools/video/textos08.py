"""Los textos del montaje del vídeo de Forja 0.8 (los mismos recursos que textos.py: Topaz solo tiene Latin-1)."""
from textos import MUSICA, TEXTOS as ANTIGUOS

CAP = {
    "en": {
        "intro": ("What is new in Forja", "Forja 0.8, with Dash 2.17"),
        "instalar": ("Install it", "It comes inside the Dash package"),
        "proyecto": ("Projects", "From a template"),
        "editor": ("The editor", "Colours, pairs, lines, outline, search, folding"),
        "ayuda": ("Dash help", "F1, search and Try"),
        "errores": ("Errors and running", "Marked on save, F8, build and run"),
        "depurar": ("The debugger", "Condition, watch, hover and change a value"),
        "git": ("Git", "Branch, stripes, Changes panel and commit"),
        "inferencia": ("The Inferencia copilot", "Change code, write the test, explain and fix errors"),
        "sprites": ("Sprites and maps", "Two extensions, in short"),
        "demos": ("Demos", "Sync tracks, MOD viewer, copper, raster, parts"),
        "tresd": ("3D with MiniGL", "A cube from the 3D template"),
        "cierre": ("Extensions", "Free, on GitHub"),
    },
    "es": {
        "intro": ("Lo nuevo de Forja", "Forja 0.8, con Dash 2.17"),
        "instalar": ("Instalarlo", "Viene dentro del paquete de Dash"),
        "proyecto": ("Proyectos", "Desde una plantilla"),
        "editor": ("El editor", "Colores, pares, líneas, esquema, buscar y plegar"),
        "ayuda": ("La ayuda de Dash", "F1, buscar y Probar"),
        "errores": ("Errores y ejecutar", "Marcados al guardar, F8, compilar y ejecutar"),
        "depurar": ("El depurador", "Condición, vigilar, valor bajo el ratón y cambiarlo"),
        "git": ("Git", "Rama, rayas, panel Cambios y commit"),
        "inferencia": ("El copiloto Inferencia", "Cambiar código, escribir la prueba, explicar y arreglar errores"),
        "sprites": ("Sprites y mapas", "Dos extensiones, en breve"),
        "demos": ("Demos", "Pistas de sincronía, visor de MOD, copper, raster y partes"),
        "tresd": ("3D con MiniGL", "Un cubo de la plantilla 3D"),
        "cierre": ("Extensiones", "Libre, en GitHub"),
    },
}
RAS = {
    "en": {
        "coffin": "CoffinOS R65, RTG", "paquete": "Dash 2.17 package", "instalador": "Classic Installer",
        "cajon": "Forja in the Dash drawer", "plantilla": "Project templates", "colores": "Syntax colours",
        "pares": "Auto-closing pairs and end", "lineas": "Comment, duplicate, move", "esquema": "File outline",
        "simbolo": "Go to a name", "buscar": "Search the project", "plegar": "Folding",
        "f1": "F1: the Dash help", "buscaayuda": "Search the help", "probar": "Try the example",
        "errores": "Errors marked on save", "f8": "F8: next error", "compilar": "Amiga-K, Amiga-E",
        "juego": "The template game", "punto": "Breakpoint", "condicion": "Breakpoint condition",
        "pila": "Stack and variables", "vigilar": "Watch an expression", "raton": "Value under the pointer",
        "cambiar": "Change a value", "rama": "Branch in the bar", "rayas": "Stripes in the margin",
        "cambios": "Changes panel", "diferencias": "Differences", "commit": "Commit",
        "copiloto": "AI copilot (test server)", "cambiarcod": "Change the code", "aceptar": "Preview and accept",
        "prueba": "Write the test", "explicar": "Explain the error", "arreglar": "Fix the error",
        "bob": "Sprites and BOBs", "mapa": "Tile maps", "demo": "Demo template", "asm": "asm ... end block",
        "pistas": "Sync tracks, live", "claves": "Keys reach the demo", "mod": "MOD viewer",
        "copper": "Copper editor", "raster": "Raster meter", "partes": "Parts timeline", "cubo": "MiniGL cube",
        "gestor": "Extension manager", "libre": "Free & open source",
    },
    "es": {
        "coffin": "CoffinOS R65, RTG", "paquete": "Paquete de Dash 2.17", "instalador": "Instalador clásico",
        "cajon": "Forja en el cajón Dash", "plantilla": "Plantillas de proyecto", "colores": "Colores de sintaxis",
        "pares": "Cierre de pares y end", "lineas": "Comentar, duplicar, mover", "esquema": "Esquema del fichero",
        "simbolo": "Ir a un nombre", "buscar": "Buscar en el proyecto", "plegar": "Plegar",
        "f1": "F1: la ayuda de Dash", "buscaayuda": "Buscar en la ayuda", "probar": "Probar el ejemplo",
        "errores": "Errores marcados al guardar", "f8": "F8: siguiente error", "compilar": "Amiga-K, Amiga-E",
        "juego": "El juego de la plantilla", "punto": "Punto de parada", "condicion": "Condición del punto",
        "pila": "Pila y variables", "vigilar": "Vigilar una expresión", "raton": "Valor bajo el ratón",
        "cambiar": "Cambiar un valor", "rama": "La rama en la barra", "rayas": "Rayas en el margen",
        "cambios": "Panel Cambios", "diferencias": "Diferencias", "commit": "Confirmar",
        "copiloto": "Copiloto con IA (servidor de pruebas)", "cambiarcod": "Cambiar el código",
        "aceptar": "Vista previa y aceptar", "prueba": "Escribir la prueba", "explicar": "Explicar el error",
        "arreglar": "Arreglar el error", "bob": "Sprites y BOBs", "mapa": "Mapas de tiles",
        "demo": "Plantilla Demo", "asm": "Bloque asm ... end", "pistas": "Pistas de sincronía, en vivo",
        "claves": "Las claves llegan a la demo", "mod": "Visor de MOD", "copper": "Editor de copper",
        "raster": "Medidor de raster", "partes": "Línea de tiempo de partes", "cubo": "Un cubo con MiniGL",
        "gestor": "Gestor de extensiones", "libre": "Libre y de código abierto",
    },
}
SCROLL = {
    "en": {
        "paquete": "FORJA 0.8 COMES INSIDE THE DASH 2.17 PACKAGE... ONE LHA FILE, AND THE INSTALLER DOES THE REST...",
        "plantilla": "SIX TEMPLATES: SHELL COMMAND, COMMODITY, MUI APP, GAME, DEMO AND 3D... EACH ONE BUILDS AND RUNS...",
        "pares": "TYPE A PARENTHESIS OR QUOTES AND THE CLOSING ONE APPEARS... A FUNC BRINGS ITS END...",
        "f1": "THE WHOLE DASH HELP, WITH MORE THAN A THOUSAND FUNCTIONS, ONE KEY AWAY...",
        "errores": "ERRORS ARE CHECKED IN THE BACKGROUND WHEN YOU SAVE: THE LINE TURNS RED...",
        "condicion": "STOP ONLY WHEN YOU WANT: A CONDITION ON EVERY BREAKPOINT...",
        "cambiar": "CHANGE A VARIABLE WHILE THE PROGRAM IS STOPPED, AND CARRY ON...",
        "rayas": "THE MARGIN SHOWS WHAT CHANGED SINCE THE LAST COMMIT, AS YOU TYPE...",
        "copiloto": "THE ANSWERS IN THIS SECTION COME FROM A TEST SERVER, WRITTEN IN ADVANCE...",
        "pistas": "SYNC TRACKS LIKE ROCKET, INSIDE FORJA: EDIT A KEY AND THE DEMO GETS IT AT ONCE...",
        "raster": "HOW MANY RASTER LINES EACH FRAME USES: GREEN, YELLOW, RED...",
        "cubo": "A SPINNING CUBE WITH GL_ CALLS, ON MINIGL...",
        "libre": "FREE AND OPEN SOURCE: GITHUB.COM/FREEMEM/FORJA *** FORJA.FREEMEM.SPACE",
    },
    "es": {
        "paquete": "FORJA 0.8 VIENE EN EL PAQUETE DE DASH 2.17... UN FICHERO LHA Y EL INSTALADOR HACE EL RESTO...",
        "plantilla": "SEIS PLANTILLAS: ORDEN DE SHELL, COMMODITY, APLICACION MUI, JUEGO, DEMO Y 3D... CADA UNA COMPILA Y ARRANCA...",
        "pares": "ESCRIBES UN PARENTESIS O UNAS COMILLAS Y SALE EL CIERRE... UN FUNC TRAE SU END...",
        "f1": "TODA LA AYUDA DE DASH, CON MAS DE MIL FUNCIONES, A UNA TECLA...",
        "errores": "LOS ERRORES SE COMPRUEBAN EN SEGUNDO PLANO AL GUARDAR: LA LINEA SE PONE EN ROJO...",
        "condicion": "PARA SOLO CUANDO QUIERES: UNA CONDICION EN CADA PUNTO DE PARADA...",
        "cambiar": "CAMBIA UNA VARIABLE CON EL PROGRAMA PARADO Y SIGUE...",
        "rayas": "EL MARGEN ENSENA LO CAMBIADO DESDE EL ULTIMO COMMIT, MIENTRAS ESCRIBES...",
        "copiloto": "LAS RESPUESTAS DE ESTE TRAMO SON DE UN SERVIDOR DE PRUEBAS, ESCRITAS DE ANTEMANO...",
        "pistas": "PISTAS DE SINCRONIA COMO ROCKET, DENTRO DE FORJA: CAMBIAS UNA CLAVE Y LA DEMO LA RECIBE AL MOMENTO...",
        "raster": "CUANTAS LINEAS DE RASTER GASTA CADA IMAGEN: VERDE, AMARILLO, ROJO...",
        "cubo": "UN CUBO QUE GIRA CON LLAMADAS GL_, SOBRE MINIGL...",
        "libre": "LIBRE Y DE CODIGO ABIERTO: GITHUB.COM/FREEMEM/FORJA *** FORJA.FREEMEM.SPACE",
    },
}


def _hacer():
    r = {}
    for lg in ("en", "es"):
        t = dict(ANTIGUOS[lg])
        t["capitulos"] = CAP[lg]
        t["rasgos"] = RAS[lg]
        t["scroll"] = SCROLL[lg]
        if lg == "en":
            t["titulo"] = "Forja {ver}: what is new in the Dash IDE for the Amiga"
            t["portada"] = ["What is new in the Dash IDE", "Editor, help, debugger, git, AI copilot, demos and 3D",
                            "AmigaOS 3.x  -  written in Dash"]
            t["scroll_portada"] = "*** FORJA {ver} *** WHAT IS NEW IN THE DASH IDE FOR THE AMIGA *** WITH DASH 2.17 ON COFFINOS R65 ***"
            t["creditos"] = [(k, "What is new in the Dash IDE" if v == "The Dash IDE, on the Amiga itself" else v)
                             for (k, v) in ANTIGUOS[lg]["creditos"]]
        else:
            t["titulo"] = "Forja {ver}: lo nuevo del entorno de Dash para el Amiga"
            t["portada"] = ["Lo nuevo del entorno de Dash", "Editor, ayuda, depurador, git, copiloto con IA, demos y 3D",
                            "AmigaOS 3.x  -  escrito en Dash"]
            t["scroll_portada"] = "*** FORJA {ver} *** LO NUEVO DEL ENTORNO DE DASH PARA EL AMIGA *** CON DASH 2.17 EN COFFINOS R65 ***"
            t["creditos"] = [(k, "Lo nuevo del entorno de Dash" if v == "El entorno de Dash, en el propio Amiga" else v)
                             for (k, v) in ANTIGUOS[lg]["creditos"]]
        r[lg] = t
    return r


TEXTOS = _hacer()
