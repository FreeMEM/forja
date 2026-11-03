# Forja

*English | [Castellano](README.md)*

A development environment for [Dash](https://github.com/FreeMEM/FreeMEMLang) that runs on the Amiga itself, with a
black background: code editor with colours, build and run, step-by-step debugger and a `.dashui` window editor with
real MUI. It talks over ARexx with [Inferencia](https://github.com/FreeMEM/inferencia), the AI for the Amiga.

This is a test version: it works in the emulator, but it has not been tried on a real Amiga yet. It speaks
English or Spanish, following the Locale preferences (the English catalog is in `Catalogs/`).

## Requirements

- AmigaOS 3.0 or later, with a 68020 or better, and MUI 5.
- dashc, the Dash 2.0 compiler for the Amiga (`make amiga` in Dash's `dashc/`), with its `.drt` files next to it.
  Forja looks for it in `ENV:Forja/dashc`, or as `dashc` in the command path.
- For the Inferencia button, [Inferencia](https://github.com/FreeMEM/inferencia) (`ENV:Forja/inferencia`).
- Syntax colours look better with more than 4 colours on the screen.

## Use

`Forja [file]`, or double-click its icon. Without a file, it opens what was open last time (this can be turned off
in the preferences).

The preferences can also make Forja start on a screen of its own: a public copy of the Workbench's, named `FORJA`.
While Forja is open it is the default public screen, so the programs it runs open there. On quitting, the old
default comes back. It needs a Dash with `screen_make_default`.

- **Editor**: the keyboard goes to the editor when the pointer is over it. Arrows; with Shift they select; Alt: start
  and end of line, page up and down; Ctrl: word by word, start and end of the text. Tab and Shift+Tab indent. Undo
  (Amiga-Z), redo (Amiga-R), cut, copy and paste with the system clipboard.
- **Files**: tabs; Amiga-N, Amiga-O, Amiga-S, Amiga-W. The left panel opens the files of the drawer with a click. It
  asks when closing with unsaved changes.
- **Find and replace** (Amiga-F) and **go to line** (Amiga-L).
- **Build** (Amiga-K) and **run** (Amiga-E): errors show at the bottom, and a click takes you to the line.
- **Debug** (Amiga-G or F5): breakpoints with F9 or a click in the margin; F5 continue, F10 step over, F6 step into,
  F7 step out. On the left, the call stack and the variables.
- **`.dashui` windows** open in the window editor (Amiga-D switches to text). The object tree and its properties;
  "+" adds, Del removes, Alt+arrows moves. Amiga-P opens the preview with real MUI. It saves the same way as the VS
  Code extension.
- **Inferencia** (Amiga-I): sends it the file, or the selected lines.
- **Sprites and BOBs**: IFF ILBM pictures (DPaint brushes too) open in their own editor, and Amiga-B makes a
  hardware sprite (16 wide, 3 colours and the transparent one) or a BOB (any size and colours). They are saved as
  IFF, and Dash's `sprite_load` and `bob_load` load them as they are.
  - Drawing: P pencil, L line, B box (filled with Shift when you start), F fill, K eyedropper, A handle point.
    Alt + click erases; Ctrl + click picks the colour. Up, down and the digits choose a colour; the R G B bars
    change it.
  - Frames: the arrows go from one to another, N new, D duplicate, Del remove, Backspace clear, H and V mirror,
    Alt + arrows move, Shift + arrows scroll the drawing, Amiga-C/X/V copy, cut and paste. O turns the onion skin
    on.
  - Animation: Space starts the animated preview; + and - change the speed.
  - Size: Ctrl + arrows, or the Size tab (width, height, colours); T turns a hardware sprite into a BOB.
  - C copies to the clipboard the Dash lines that load it, with its colours and how to animate it.

  ![The sprite editor with a 4-frame ship](docs/img/sprites-en.png)
- **Tile maps**: `.fmap` files (IFF `FORM FMAP`) open in the map editor, and Amiga-B also makes a new map. The
  tileset is a BOB from the sprite editor, with one frame a tile of 8, 16 or 32; the map keeps its name. Dash's
  `tilemap_load` and `tilemap_draw` load and draw them.
  - Tools: P pencil, B box, F fill, K pick, E erase. Alt + click erases; Ctrl + click picks the tile. H and V
    mirror the tile; comma and full stop change the tile. In the panel, the Tiles page chooses the tile.
  - Layers (Layers page): choose, show or hide, new, remove, back and front. Map (Map page): width, height, zoom,
    grid (G) and tileset.
  - The arrows and the wheel move the view (with Shift, a screen at a time); + and - change the zoom.
  - Collisions: on the Layers page a layer becomes a collision layer; on it you paint solid, platform, ladder or
    harm, shown on top as a pattern of colours. The game reads it with `tilemap_get`.
  - Objects (Objects page): a click puts one of the chosen kind (player, enemy, coin, door, other) or chooses the
    one there; dragging moves it and Del removes it. They can have a sprite. The game finds them with
    `tilemap_object_find`.
  - Amiga-Z and Amiga-R undo and redo; C copies the Dash lines that load and draw it.

  ![The map editor with a 40 x 20 level](docs/img/mapas.png)

### ARexx

Port `FORJA.1`: `ABRIR file [line]` (open), `ABIERTO file` (is it open), `TEXTO file` (text), `SELECCION`
(selection), `CAMBIAR file from to text` (change lines), `GUARDAR [file]` (save), `COMPILAR` (build), `EJECUTAR`
(run), `ESTADO` (state), `ERRORES` (errors), `BUSCAR text` (find), `CAMBIARTODO find replace`, `IRA line` (go to).

## Build

With Dash 2.0: `./dash src/main.dash -o Forja`. The package: `python3 tools/paquete.py 0.1`. The tests run in the
emulator: [tests/LEEME.md](tests/LEEME.md) (in Spanish).

Written in Dash. MIT license.
