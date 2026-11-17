#!/usr/bin/env python3
"""Las plantillas de "Nuevo proyecto..." (paso 3.2 de docs/FORJA_LOOP.md) dentro de Forja.

    python3 tools/plantillas.py              # escribe src/plantillas_datos.dash desde plantillas/
    python3 tools/plantillas.py --comprobar  # sale con 1 si no está al día

Cada cajón de plantillas/ es una plantilla (orden, commodity, mui, juego, demo, 3d) con sus ficheros tal cual: se
compilan y se prueban como cualquier programa (tests/plantillas.sh). plantillas.en/ tiene los mismos ficheros con el
código en inglés (todos menos los de la demo, cuyo código lee la extensión Demos): Forja los usa con su catálogo inglés. %NOMBRE% es el nombre del proyecto. Van dentro
del ejecutable (unos 20 KB) para que "Nuevo proyecto..." no dependa de ficheros sueltos.
"""
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
ORDEN = ["orden", "commodity", "mui", "juego", "demo", "3d"]


def literal(texto: str) -> str:
    """El texto como literal de Dash: "#{" se parte en dos (si no, sería una interpolación)"""
    s = texto.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "    ")
    # "a#{b" -> "a#" + "{b"
    return '"' + '#" + "{'.join(s.split("#{")) + '"'


def literal_partido(texto: str) -> str:
    """Un literal por línea del fichero, unidos con +, para que el .dash generado se lea"""
    lineas = texto.splitlines(keepends=True)
    return " +\n        ".join(literal(l) for l in lineas) if lineas else '""'


def icono_proyecto() -> bytes:
    """El icono de un .forja: un documento con el yunque de Forja (sin herramienta: la pone Forja, su ruta, con
    icon_save). tools/paquete.py lo pone en Forja/Iconos/proyecto.info"""
    sys.path.insert(0, str(raiz / "tools"))
    from iconos_wb import Lienzo, info, NEGRO, BLANCO, AZUL, WBPROJECT
    l = Lienzo(30, 22)
    l.rect(4, 1, 25, 20, BLANCO)
    l.marco(4, 1, 25, 20, NEGRO)
    l.rect(20, 1, 25, 6, 0)
    l.linea(20, 1, 25, 6, NEGRO)
    l.linea(20, 1, 20, 6, NEGRO)
    l.linea(20, 6, 25, 6, NEGRO)
    l.rect(8, 10, 21, 11, AZUL)          # el yunque
    l.rect(6, 10, 8, 10, AZUL)
    l.rect(12, 12, 17, 14, AZUL)
    l.rect(10, 15, 19, 16, AZUL)
    for x, y in ((14, 6), (16, 5), (12, 5)):
        l.punto(x, y, AZUL)
    return info(l, WBPROJECT)


def generar() -> str:
    out = ["# Las plantillas de Nuevo proyecto... (plantillas/). Lo escribe tools/plantillas.py: no se toca a mano.",
           "",
           "# Los ficheros de una plantilla, separados por |",
           "func pl_ficheros(tipo: String) -> String"]
    tipos = [t for t in ORDEN if (raiz / "plantillas" / t).is_dir()]
    for i, t in enumerate(tipos):
        nombres = sorted(p.name for p in (raiz / "plantillas" / t).iterdir() if p.is_file())
        out.append(f'    {"if" if i == 0 else "elif"} tipo == "{t}"')
        out.append(f'        return "{"|".join(nombres)}"')
    out += ["    end", '    return ""', "end", "",
            "# El texto de un fichero de una plantilla (con %NOMBRE% sin cambiar)",
            "func pl_texto(tipo: String, fichero: String) -> String"]
    primero = True
    for t in tipos:
        for p in sorted((raiz / "plantillas" / t).iterdir()):
            if not p.is_file():
                continue
            texto = p.read_text(encoding="utf-8")
            out.append(f'    {"if" if primero else "elif"} tipo == "{t}" and fichero == "{p.name}"')
            out.append("        return " + literal_partido(texto))
            primero = False
    out += ["    end", '    return ""', "end", ""]
    # las de plantillas.en/: el mismo fichero con el código en inglés (Forja las usa con su catálogo inglés)
    out += ["# El mismo fichero en inglés (plantillas.en/), o \"\" si no lo hay: con el catálogo inglés de Forja",
            "func pl_texto_en(tipo: String, fichero: String) -> String"]
    primero = True
    for t in tipos:
        d = raiz / "plantillas.en" / t
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if not p.is_file() or not (raiz / "plantillas" / t / p.name).is_file():
                continue
            out.append(f'    {"if" if primero else "elif"} tipo == "{t}" and fichero == "{p.name}"')
            out.append("        return " + literal_partido(p.read_text(encoding="utf-8")))
            primero = False
    if not primero:
        out.append("    end")
    out += ['    return ""', "end", ""]
    return "\n".join(out)


def main():
    destino = raiz / "src" / "plantillas_datos.dash"
    nuevo = generar()
    if "--comprobar" in sys.argv:
        if not destino.exists() or destino.read_text(encoding="utf-8") != nuevo:
            print("src/plantillas_datos.dash no está al día: python3 tools/plantillas.py")
            sys.exit(1)
        return
    destino.write_text(nuevo, encoding="utf-8")
    print(f"{destino.relative_to(raiz)}: {len(nuevo)} bytes")


if __name__ == "__main__":
    main()
