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

### ARexx

Port `FORJA.1`: `ABRIR file [line]` (open), `ABIERTO file` (is it open), `TEXTO file` (text), `SELECCION`
(selection), `CAMBIAR file from to text` (change lines), `GUARDAR [file]` (save), `COMPILAR` (build), `EJECUTAR`
(run), `ESTADO` (state), `ERRORES` (errors), `BUSCAR text` (find), `CAMBIARTODO find replace`, `IRA line` (go to).

## Build

With Dash 2.0: `./dash src/main.dash -o Forja`. The package: `python3 tools/paquete.py 0.1`. The tests run in the
emulator: [tests/LEEME.md](tests/LEEME.md) (in Spanish).

Written in Dash. MIT license.
