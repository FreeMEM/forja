#!/usr/bin/env python3
"""Las palabras que Forja sabe completar: las palabras clave y los tipos de Dash y sus builtins, con su firma y su
descripción corta. Escribe src/builtins.dash (no se edita a mano).

    python3 tools/builtins.py [DASH_DIR]     # por defecto ~/Projects/FreeMEMLang

Las palabras clave salen de compiler/grammar.py y los builtins de docs/BUILTINS.md de Dash. En src/builtins.dash
van los nombres en el orden de las minúsculas (para buscar a medias), cada uno en BI_ANCHO letras, y BI_INFO con
"clase|firma|descripción" de cada uno (clase: 0 palabra clave, 1 tipo, 2 builtin) y dónde empieza cada línea (BI_POS).
"""
import re
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
dash = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Projects/FreeMEMLang"

# Lo que devuelve un builtin en C, como tipo de Dash
C_A_DASH = {"LONG": "Int", "ULONG": "Int", "WORD": "Int", "UWORD": "Int", "BYTE": "Int", "UBYTE": "Int",
            "int": "Int", "STRPTR": "String", "BOOL": "Bool", "void": "", "APTR": "Pointer", "float": "Float",
            "FLOAT": "Float", "DashFixed": "Fixed", "double": "Float", "DashArrayLong *": "Array"}

TIPOS = ["Int", "Float", "String", "Bool", "Pointer", "Func", "Fixed", "Array", "Void", "Ptr"]

# Palabras de la gramática que no son del lenguaje (sale de expresiones regulares o de nombres de reglas)
NO_SON = {"clave", "b", "k"}

# Una descripción corta de algunas palabras clave
CLAVES = {
    "func": "func nombre(a: Int) -> Int ... end", "struct": "struct Nombre campo: Int ... end",
    "enum": "enum Nombre A, B end", "const": "const NOMBRE = valor", "var": "var nombre: Tipo = valor",
    "import": "import \"modulo.dash\"", "if": "if condición ... elif ... else ... end",
    "while": "while condición ... end", "for": "for i in (1..10) ... end / for x in lista ... end",
    "return": "return valor", "Main": "Main ... end: donde empieza el programa", "Print": "Print valor",
    "EventLoop": "EventLoop On Close ... end end", "Window": "Window Nombre title \"...\" end",
    "fn": "fn(x) -> expresión", "interface": "interface Nombre func m() end",
}


def texto_dash(s):
    """Un literal de texto de Dash"""
    s = s.replace("\\", "\\\\").replace("\"", "\\\"").replace("#{", "\\x23{").replace("\n", "\\n")
    return "\"" + s + "\""


def palabras_clave():
    g = (dash / "compiler/grammar.py").read_text(encoding="utf-8")
    g = "\n".join(linea.split("//", 1)[0] for linea in g.splitlines())
    return sorted(set(re.findall(r'"(@?[A-Za-z_][A-Za-z0-9_]*)"', g)) - set(TIPOS) - NO_SON)


def builtins():
    fila = re.compile(r"^\| `([A-Za-z_][A-Za-z0-9_]*)\((.*?)\)` \| `(.*?)` \| (.*?) \|")
    vistos = {}
    for linea in (dash / "docs/BUILTINS.md").read_text(encoding="utf-8").splitlines():
        m = fila.match(linea)
        if not m:
            continue
        nombre, params, ret, desc = m.groups()
        ret = C_A_DASH.get(ret.strip(), ret.strip())
        firma = f"{nombre}({params})" + (f" -> {ret}" if ret else "")
        desc = desc.replace("\\|", "|").replace("`", "").strip()
        vistos.setdefault(nombre, (firma, desc))
    return vistos


def main():
    entradas = {}
    for p in palabras_clave():
        entradas[p] = (0, CLAVES.get(p, p), "")
    for t in TIPOS:
        entradas[t] = (1, t, "")
    for nombre, (firma, desc) in builtins().items():
        entradas.setdefault(nombre, (2, firma, desc))
    orden = sorted(entradas, key=lambda n: (n.lower(), n))
    for n in orden:
        if "\n" in n or "|" in n:
            raise SystemExit(f"nombre raro: {n!r}")
    ancho = max(len(n) for n in orden)
    nombres = "".join(n.ljust(ancho) for n in orden)
    lineas = [f"{entradas[n][0]}|{entradas[n][1]}|{entradas[n][2]}".replace("\n", " ") for n in orden]
    info = "\n".join(lineas)
    # dónde empieza cada línea de BI_INFO, en bytes de Latin-1 (como lo verá el Amiga), seis cifras hexadecimales
    pos, p = [], 0
    for l in lineas:
        pos.append(p)
        p += len(l.encode("latin-1", "replace")) + 1
    pos.append(p)
    posiciones = "".join(f"{x:06x}" for x in pos)
    n_bi = sum(1 for e in entradas.values() if e[0] == 2)
    salida = raiz / "src/builtins.dash"
    salida.write_text(
        "# Generado por tools/builtins.py desde Dash (compiler/grammar.py y docs/BUILTINS.md). No editar a mano.\n"
        f"# {len(orden)} entradas: {n_bi} builtins, palabras clave y tipos, en el orden de las minúsculas. BI_NOMBRES:\n"
        "# los nombres, cada uno en BI_ANCHO letras (con espacios detrás); BI_INFO: \"clase|firma|descripción\" por línea\n"
        "# (clase 0 palabra clave, 1 tipo, 2 builtin); BI_POS: dónde empieza cada línea de BI_INFO (6 cifras hexadecimales\n"
        "# cada una, y una más al final). Así no hay que partir nada al empezar.\n\n"
        f"const BI_TOTAL = {len(orden)}\n"
        f"const BI_ANCHO = {ancho}\n\n"
        f"const BI_NOMBRES = {texto_dash(nombres)}\n\n"
        f"const BI_POS = {texto_dash(posiciones)}\n\n"
        f"const BI_INFO = {texto_dash(info)}\n", encoding="utf-8")
    print(f"{salida}: {len(orden)} entradas ({n_bi} builtins)")


main()
