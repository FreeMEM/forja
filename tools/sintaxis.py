#!/usr/bin/env python3
"""Las palabras de los colores de Forja, sacadas de Dash: escribe src/sintaxis_datos.dash (no se edita a mano).

    python3 tools/sintaxis.py [DASH_DIR]        # por defecto ~/Projects/FreeMEMLang
    python3 tools/sintaxis.py --comprobar       # sale con 1 si src/sintaxis_datos.dash no está al día

De Dash salen:
- las palabras clave de compiler/grammar.py, con la clase que les da tools/gen_tmgrammar.py (los colores de VS Code):
  si la gramática tiene una palabra nueva sin clase, gen_tmgrammar.py ya obliga a dársela, y aquí se para igual;
- los tipos (SemanticAnalyzer._TYPE_NAMES);
- las instrucciones y directivas del ensamblador en línea (compiler/asm68k.py: MNEMONICS y DIRECTIVES), para los
  colores de los bloques asm ... end.
"""
import re
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
args = [a for a in sys.argv[1:] if not a.startswith("--")]
dash = Path(args[0]) if args else Path.home() / "Projects/FreeMEMLang"
sys.path.insert(0, str(dash))
sys.path.insert(0, str(dash / "tools"))

from compiler.grammar import dash_grammar_minimal as GRAMATICA  # noqa: E402
from compiler.analyzer import SemanticAnalyzer  # noqa: E402
from compiler import asm68k  # noqa: E402
import gen_tmgrammar  # noqa: E402

# La clase de Forja (src/sintaxis.dash) de cada clase de gen_tmgrammar.py
CLASES = {
    "keyword.control": "S_CLAVE",
    "keyword.other": "S_CLAVE",
    "keyword.operator.logical": "S_CLAVE",
    "storage.type": "S_CLAVE",
    "storage.modifier": "S_CLAVE",
    "keyword.other.event": "S_EVENTO",       # Close, Key...: solo tras On (si no, son nombres corrientes)
    "constant.language": "S_NUMERO",         # true, false, nil
    "variable.language.self": "S_CLAVE",
    "keyword.other.directive": "S_DIRECTIVA",
}
# Palabras que no están en la gramática de Lark (asm, de compiler/asm68k.py, es palabra clave solo al empezar la
# cabecera de un bloque: lo mira src/sintaxis.dash)
EXTRA = {}
# Las de la cabecera de un bloque asm (asm in d0 = a out r = d0 uses d2)
ASM_CABECERA = ["in", "out", "uses"]


def palabras_gramatica():
    texto = "\n".join(linea.split("//", 1)[0] for linea in GRAMATICA.splitlines())
    return set(re.findall(r'"(@?[A-Za-z_][A-Za-z0-9_]*)"', texto))


def texto_dash(s):
    return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\""


def generar():
    tipos = sorted(set(SemanticAnalyzer._TYPE_NAMES) | {"Ptr"})
    clase = {}
    for kind, palabras in gen_tmgrammar.KEYWORDS.items():
        if kind not in CLASES:
            sys.exit(f"tools/sintaxis.py: clase de gen_tmgrammar.py sin color en Forja: {kind} (añádela a CLASES)")
        for p in palabras:
            clase[p] = CLASES[kind]
    for p in tipos:
        clase[p] = "S_TIPO"
    clase.update(EXTRA)
    faltan = sorted(palabras_gramatica() - set(clase))
    if faltan:
        sys.exit(f"tools/sintaxis.py: palabras de compiler/grammar.py sin clase: {faltan}")
    por_clase = {}
    for p, c in clase.items():
        por_clase.setdefault(c, []).append(p)
    instrucciones = sorted(set(asm68k.MNEMONICS) | set(asm68k.DIRECTIVES) | {"equ"})
    largo = max(len(p) for p in clase)
    lineas = [
        "# Generado por tools/sintaxis.py desde Dash (compiler/grammar.py, las clases de tools/gen_tmgrammar.py, los",
        "# tipos del analizador y las instrucciones de compiler/asm68k.py). No editar a mano.",
        "# Cada constante: las palabras de una clase, separadas por espacios.",
        "",
        f"const SXD_LARGO = {largo}          # la palabra más larga",
    ]
    nombres = {"S_CLAVE": "SXD_CLAVES", "S_TIPO": "SXD_TIPOS", "S_NUMERO": "SXD_VALORES", "S_EVENTO": "SXD_EVENTOS",
               "S_DIRECTIVA": "SXD_DIRECTIVAS"}
    for c, nombre in nombres.items():
        lineas.append(f"const {nombre} = {texto_dash(' '.join(sorted(por_clase.get(c, []))))}")
    lineas.append(f"const SXD_ASM_CABECERA = {texto_dash(' '.join(ASM_CABECERA))}")
    lineas.append(f"const SXD_ASM = {texto_dash(' '.join(instrucciones))}")
    lineas.append(f"const SXD_ASM_TOTAL = {len(instrucciones)}")
    return "\n".join(lineas) + "\n"


def main():
    salida = raiz / "src/sintaxis_datos.dash"
    texto = generar()
    if "--comprobar" in sys.argv:
        if not salida.exists() or salida.read_text(encoding="utf-8") != texto:
            print("src/sintaxis_datos.dash no está al día: python3 tools/sintaxis.py")
            sys.exit(1)
        return
    salida.write_text(texto, encoding="utf-8")
    print(f"{salida}: al día")


main()
