# Diseñador visual de ventanas (para `/loop`)

Arranque:

```
/loop Sigue las instrucciones de docs/DISENADOR_LOOP.md (en ~/Projects/forja-disenador): haz UNA tarea y actualiza la bitácora. No hagas pausas entre vuelta y vuelta
```

## Objetivo

Lo pidió Jose (@Pepillogrillo22) en Dash Amiga #2244 (2026-11-22): "el típico IDE donde tienes un form, añades los
botones, labels, etc... con eventos y demás". El usuario dijo que sí, y que también en la extensión de VS Code.

Hoy el editor de `.dashui` de Forja es un árbol con propiedades ("+" añade, Alt+flechas mueve) y una vista previa
MUI aparte. Falta, como en Visual Basic o Delphi:

1. **Un lienzo con la ventana**: se ve dibujada (aproximada, como MUI) y los objetos se ponen y se mueven con el
   ratón. Paleta de gadgets; arrastrar a un grupo (delante, detrás o dentro); los cambios se ven al momento.
2. **Doble clic en un objeto: a su manejador** en el `.dash` que importa el `.dashui`. Si el objeto no tiene número
   de evento ni nombre, se le ponen; si el `.dash` no trata el evento, se crea la constante y el `if`.
3. **Lo mismo en la extensión de VS Code** (`~/Projects/FreeMEMLang/editor/vscode`), que ya arrastra y tiene el botón
   → de cada evento: le falta el doble clic con número y nombre automáticos.

Commits con "(lo pidió Jose)". Nada hacia fuera: ni push a main de Forja, ni release, ni Telegram. Al acabar, avisar a
`jefe-dash` con commits, pruebas y un borrador para Jose.

## Datos de partida (2026-11-22)

- Forja main fd952d0 (0.8.1). Worktree `~/Projects/forja-disenador`, rama `disenador-visual`.
- Dash main 6ef0d45. Compilar Forja: `~/Projects/FreeMEMLang/dash src/main.dash -o Forja`.
- `src/diseno.dash` (812 líneas): árbol (`dv_filas`), propiedades, `dv_tecla`, `dv_clic`, `dv_dibujar`, vista previa.
  Lo llama `src/editor.dash` (`ed_cargar_diseno`, `ed_aplicar_diseno`, `ed_dibujar`) y `src/main.dash` (clic en
  `en_editor` ~3160, teclas ~3237, `EV_ARRASTRE` ~6571 con `mui_canvas_drag`: 1 moviendo, 2 soltado).
- No hay doble clic en los lienzos de Dash: se mide con `time_ms` en Forja.
- VS Code: `dashuiLinks.js` (`handlers`, `addHandler`, `constantName`, `importsDashui`) y `dashuiCode.js`
  (`dash.gotoEvent`). El código que crea: `const ID_NOMBRE = n` tras los import/const, y
  `if ev == ID_NOMBRE` / `# nombre` / `end` justo después de `ev = mui_wait_event()`. Forja hará lo mismo, igual.
- Pruebas con usuario simulado en FS-UAE: `tests/diseno.sh` + `tests/diseno.dash` (modelo a seguir).
- Traducciones nuevas desde `tr(1100, ...)`.

## Diseño

**Pantalla del editor de ventanas (Forja)**, debajo de las pestañas:

```
| Botón  Texto  Etiqueta  Campo  Casilla  Ciclo ... Grupo H  Grupo V  Marco |  <- paleta
|---------------------------------------------|----------------------------|
|  [x] Título de la ventana                    | label    _Saludar          |
|  +---------------------------------------+   | event    1         (→)     |
|  | Escribe tu nombre                     |   | name     saludar           |
|  | Nombre: [______________]              |   | ...                        |
|  | [ Saludar ] [ Limpiar ]               |   |                            |
|  +---------------------------------------+   |                            |
|---------------------------------------------|----------------------------|
```

- A la izquierda, **Lienzo** o **Árbol** (Amiga-T o un clic en la cabecera cambian). El teclado del árbol vale en
  los dos (flechas, "+", Supr, Alt+flechas). A la derecha, las propiedades, como hoy.
- **Ratón en el lienzo**: clic elige; arrastrar un objeto lo mueve (una raya marca delante o detrás; un marco, dentro
  de un grupo); arrastrar desde la paleta lo crea ahí; doble clic va al manejador.
- **Dibujo aproximado de MUI**: grises, relieves, campos hundidos, marcos con título, pestañas (la primera página o
  la del objeto elegido). Tamaño mínimo de cada objeto y reparto del sobrante por `weight`. Con los colores del
  Workbench (4) sale gris, blanco, negro y azul, como MUI.
- **El evento de cada tipo** (doble clic, igual en Forja y en VS Code): botón e image_button `event`; casilla, ciclo,
  deslizador, barra, pestañas, image_toggle y lista `change` (la lista, `double` si ya lo tiene); campo, combo y
  text_editor `ack` (o `change` si solo tiene ese); elemento de menú `event`; ventana `close` (doble clic en el
  título). Texto, etiqueta, gauge, espacio, imagen y lienzo no dan eventos: se dice.
- **Número nuevo**: el menor desde 1 que no esté en el `.dashui` ni sea el valor de un `const` del `.dash`.
- **Nombre nuevo** (si no tiene): de su texto (`_Saludar` → `saludar`), sin acentos; si no vale o se repite, el tipo
  y un número (`boton1`).

## Tareas

- [x] T1. Disposición: calcular el tamaño y el sitio de cada objeto (función pura, con prueba en el PC con dash).
- [x] T2. Dibujo del lienzo con la ventana, la paleta arriba y Lienzo/Árbol; clic elige (sincroniza el árbol).
- [x] T3. Arrastrar objetos (mover) y desde la paleta (crear), con la marca de dónde cae.
- [x] T4. Doble clic: evento y nombre automáticos; buscar o crear el manejador en el `.dash` (abrirlo y saltar).
- [x] T5. Prueba con usuario simulado en FS-UAE (`tests/disenador.sh`), capturas al usuario.
- [x] T6. Lo que falte a Dash (si falta algo), en los dos caminos (`./dash` y `./dash --gcc`).
- [x] T7. VS Code: doble clic en la vista y en el árbol (número y nombre automáticos, `gotoEvent` sin preguntar);
  pruebas de la extensión; captura.
- [x] T8. Documentación (ayuda de Forja, README, CHANGELOG, `docs/MUI_EDITOR.md` de Dash) con "(lo pidió Jose)".
- [x] T9. Aviso a jefe-dash: commits, qué se probó, borrador para Jose.
- [ ] T10. (Lo pidió el usuario, 22/11) Un vídeo demostrativo nuevo de Forja con todas sus características, el
  diseñador incluido. Con `tools/video` y lo de la memoria "Vídeo de Forja" (voz del usuario en pegaso). Sin
  publicarlo: se le manda al usuario.

## Bitácora

- 2026-11-22: plan escrito. Worktree creado; Forja compila con Dash main.
- 2026-11-22 T1: `src/lienzo.dash` (disposición, dibujo, `lz_en`, `lz_destino`) y `tests/lienzo_base.dash` (22 bien, con
  `tests/emu_prueba.sh`, unos 11 s). El dibujo aún sin probar en pantalla.
- 2026-11-22 T2-T3: lienzo en `src/diseno.dash`: paleta de iconos en una fila (el nombre al pasar el puntero),
  ventana a la izquierda, propiedades a la derecha, Tab o el botón "Árbol" cambian al árbol. Clic elige, arrastrar
  mueve, paleta + arrastre o paleta + clic crean; rueda sube y baja la ventana, lo elegido se sigue. Prueba
  `RTG=1 tests/disenador.sh` (TODO BIEN). En 640x256 (sin RTG) la zona del editor mide unos 85 px: la ventana no cabe
  y la prueba falla los clics; se baja con la rueda. ESPERA=300 para las capturas (cada paso para 6 s).
- 2026-11-22 T4: doble clic (o Amiga-J en el editor de ventanas) va al código del evento: `src/eventos_ui.dash`
  (como `dashuiLinks.js`, pero sin pararse en `@version`: VS Code pone la constante al principio del fichero si
  hay un `@version` antes de los import) y `ir_evento_diseno` en `main.dash`. Número libre y nombre automáticos
  (`dv_evento`). Pruebas: `tests/eventos_base.dash` (14 bien) y `RTG=1 tests/disenador.sh` (11 bien, TODO BIEN).
  Al escribir en una propiedad solo se redibuja su fila. `tests/diseno.sh` (la vieja) falla 3 pasos (cambiar label,
  vista previa, rehacer y guardar) igual en main fd952d0: no es de esta rama.
- 2026-11-22 T5: capturas (RTG, ESPERA=300) mandadas al usuario: casilla arrastrada, paleta + botón, árbol y el
  código creado con doble clic.
- 2026-11-22 T6: a Dash no le falta nada para esto. Forja compila con `./dash` y con `./dash --gcc` (22 s).
- 2026-11-22 T7: VS Code, worktree `~/Projects/FreeMEMLang/.worktrees/disenador`, rama `disenador`, d567dc8: doble
  clic en el árbol, la vista, el título o una opción de menú -> `dash.openEvent` (número y nombre como Forja, luego
  `gotoEvent` sin preguntar). La constante ya no va al principio si hay `@version`. Pruebas: `node test/run.js`
  (bien las nuevas; falla "new project" porque el worktree no tiene `dashc` compilado) y la de integración en VS Code
  (`DASH_IT_FLAGS=--ozone-platform=headless sh test/integration/run.sh`: la nueva bien; fallan las de compilar,
  depurar y DashOS por lo mismo). `node_modules` es un enlace al de la copia principal (en info/exclude).
- 2026-11-22 T8: README (es/en) de Forja; CHANGELOG de la extensión y `docs/MUI_EDITOR.md` (es/en) de Dash, con
  Jose. La web ("Gracias") y las notas de la versión, al publicar (no se publica aquí).
- 2026-11-22 T9: aviso a jefe-dash con commits, pruebas, avisos y el borrador para Jose. Siguiente: T10 (el vídeo).
- 2026-11-22 T10: paquete Dash 2.20 con esta Forja (worktree de Dash), guion09 con el capítulo del diseñador, voces
  nuevas en pegaso (comprobadas con Whisper), toma es09a entera (13,5 min, sin fallos), música Overload (la eligió el
  usuario). Montando la versión en castellano.
- 2026-11-22 T10: montado en castellano, ~/.cache/video-forja/salida09/forja-es.mp4 (12:32; acercamiento del
  diseñador a 900x720; saludos del scroller con Overload, Jose y JaviTecH; OCR sin datos privados). Recorte del
  capítulo mandado al usuario (el entero pasa del límite de 30 MB). Rodando y montando la versión inglesa (en09a).
  Pendiente: el número de versión de los rótulos (0.9 provisional), que decide el usuario.
