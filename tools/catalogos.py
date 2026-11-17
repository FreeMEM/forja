#!/usr/bin/env python3
"""Los catálogos de Forja y de sus extensiones, con tools/catalogo.py de Dash.

    python3 tools/catalogos.py [DASH_DIR] cd        # los .cd con los textos (tr y "tr" de los .dashui)
    python3 tools/catalogos.py [DASH_DIR] ct        # pone al día los english.ct (guarda lo traducido)
    python3 tools/catalogos.py [DASH_DIR] catalog   # los .catalog, en build/

Forja: catalogos/Forja.cd y catalogos/english.ct, de src/main.dash; build/Catalogs/english/Forja.catalog.
Cada extensión con @catalog "X.catalog" en su programa (extensiones/<cajón>/): extensiones/<cajón>/catalogos/X.cd y
extensiones/<cajón>/catalogos/english.ct; build/Extensiones/<cajón>/Catalogs/english/X.catalog (en el paquete, junto
a su programa: PROGDIR:Catalogs/english).

DASH_DIR: la carpeta de Dash (por defecto ~/Projects/FreeMEMLang). Los textos de lib/ que se usan (los errores de
red de lib/red, números 400 a 442) también van en el catálogo: el programa no usa esos números.
"""
import re
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
dash = Path(args.pop(0)) if args and args[0] not in ("cd", "ct", "catalog") else Path.home() / "Projects/FreeMEMLang"
orden = args[0] if args else "catalog"
sys.path.insert(0, str(dash / "tools"))
sys.path.insert(0, str(dash))
import os   # noqa: E402
os.environ["DASH_HOME"] = str(dash)
import catalogo   # noqa: E402


def programas():
    """(nombre del catálogo sin .catalog, programa, cajón de su .cd y su .ct, cajón del .catalog)"""
    yield "Forja", raiz / "src/main.dash", raiz / "catalogos", raiz / "build/Catalogs/english"
    for d in sorted((raiz / "extensiones").iterdir()):
        for f in sorted(d.glob("*.dash")):
            m = re.search(r'^@catalog\s+"([^"]+)\.catalog"', f.read_text(), re.M)
            if m:
                yield m.group(1), f, d / "catalogos", raiz / "build/Extensiones" / d.name / "Catalogs/english"


def uno(nombre, programa, cajon, salida):
    cajon.mkdir(exist_ok=True)
    cd = cajon / ("Forja.cd" if nombre == "Forja" else nombre + ".cd")
    ct = cajon / "english.ct"
    if orden == "cd":
        argv = ["cd", str(programa), "-o", str(cd)]
    elif orden == "ct":
        argv = ["ct", str(cd), "--language", "english", "--name", nombre + ".catalog", "--version", "1.0", "-o", str(ct)]
        if ct.exists():
            argv[-2:-2] = ["--update", str(ct)]
    else:
        salida.mkdir(parents=True, exist_ok=True)
        argv = ["catalog", str(ct), "-o", str(salida / (nombre + ".catalog"))]
    sys.argv = ["catalogo.py"] + argv
    catalogo.main()


for p in programas():
    uno(*p)
