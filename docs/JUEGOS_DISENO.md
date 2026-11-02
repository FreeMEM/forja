# Biblioteca de juegos y editor de escenas: diseño

Estado: propuesta para revisar (2026-11-02). Aún no hay código. Las decisiones que son del usuario están al final.

Lo pedido: una biblioteca de Dash para hacer juegos, como pygame. Va aparte de Forja y de Dash, con el bucle de
juego, las físicas y las luces. Y en Forja, un editor de escenas con jerarquía de nodos, como Godot.

## 1. Lo que se copia de cada uno

**De pygame, la base.** pygame no impone una forma de hacer el juego. Da piezas sueltas:
- una pantalla;
- imágenes (`Surface`) y rectángulos (`Rect`);
- eventos de teclado y ratón;
- un reloj que marca el ritmo (`Clock`);
- sonido (`mixer`) y fuentes.

Encima van `Sprite` y `Group`. Un sprite tiene imagen, rectángulo y un `update()` propio. Un grupo actualiza y
dibuja a todos sus sprites a la vez, y comprueba choques: `spritecollide`, `groupcollide`, por rectángulo, por
círculo o por máscara de píxeles. `LayeredUpdates` dibuja por capas. Los "dirty rects" redibujan solo lo que
cambió.

Se copia todo eso, porque es pequeño, se entiende en una tarde y sirve para cualquier juego.

**De Godot, la estructura.** Según su documentación, los nodos son las piezas básicas de un juego. Funciona así:
- Una **escena** es un árbol de nodos con una raíz. Guardada, se usa como un nodo más dentro de otra escena, y se
  puede instanciar muchas veces: el enemigo es una escena, y el nivel tiene diez.
- Cada nodo hace una cosa: `Sprite2D` dibuja, `CollisionShape2D` da la forma de choque, `CharacterBody2D` se mueve
  y choca, `Camera2D` sigue a alguien.
- Un personaje es un nodo con hijos.
- Cada nodo recibe llamadas: `_ready` al entrar en el árbol, `_process(delta)` en cada fotograma, y
  `_physics_process(delta)` a ritmo fijo (60 por segundo por defecto), para que las físicas no dependan de los
  fotogramas.
- Las **señales** avisan entre nodos sin que se conozcan: "me han dado", "he llegado".
- El **inspector** enseña las propiedades del nodo elegido.

Se copian el árbol, las escenas que se instancian, las tres llamadas, el paso fijo, las señales y el inspector.

**Lo que no se copia:**
- **El intérprete (GDScript):** Dash compila. Los scripts son código de Dash compilado con el juego.
- **El 3D, los shaders y la física general de cuerpos que giran:** no caben en un Amiga.
- **Los cientos de tipos de nodo:** pocos, los que de verdad usa un juego 2D del Amiga.
- **Un editor que corra el juego dentro:** la vista previa es el juego compilado, como la vista previa de ventanas
  MUI de Forja enseña la ventana de verdad.

## 2. Lo que manda el Amiga

**Cuánto cabe en un fotograma.** A 50 Hz (PAL) hay 20 ms por fotograma. Medido con Dash
(`docs/COMPARATIVA.md` de Dash, y la tarea 4 de este loop):

| | A500 (68000, 7 MHz) | A1200 (68020, 14 MHz) |
|---|---:|---:|
| Una vuelta de bucle sencilla | ~9,5 µs | ~2,1 µs |
| Una llamada a función de Dash | ~9,6 µs | ~2,2 µs |
| Un rectángulo relleno del sistema (RectFill) | no medido | ~0,22 ms |
| Vueltas sencillas en 20 ms | ~2.000 | ~9.000 |

**Lo que sale de esas cifras:**
- **La lógica es barata y el dibujo es caro.** Cincuenta nodos con tres llamadas cada uno son 150 llamadas: unos
  0,3 ms en un A1200 y 1,5 ms en un A500. En cambio, cada cosa dibujada con las funciones del sistema cuesta
  décimas de milisegundo.
- **Hay que dibujar poco y con el hardware.** Los sprites de hardware no cuestan nada de CPU. El scroll de
  hardware y el copper tampoco. Los BOBs sí cuestan, y hay que contarlos. Cuánto cuesta un BOB (borrar, copiar con
  máscara) se mide en la fase 1 antes de prometer cifras.
- **Las físicas, en coma fija** (`Fixed` 16.16, que Dash ya tiene con `fx_sin` y `fx_sqrt`). `Float` cuesta mucho
  en un 68000 sin FPU.
- **El paso fijo es el fotograma de 50 Hz** (60 en NTSC), con `wait_vblank`. Si un fotograma se pasa de tiempo, el
  juego hace dos pasos de física y dibuja una vez: se pierde suavidad, no se rompe la física.
- **Memoria chip:** las imágenes que dibuja el hardware van ahí. Un A500 tiene 512 KB; un A1200, 2 MB. La
  biblioteca tiene que decir cuánta usa.

**Luces, sin mezclar colores píxel a píxel** (eso solo se puede en RTG con color verdadero). En una pantalla de
paleta hay tres caminos, de más barato a más caro:
1. **Paleta y copper:** oscurecer toda la pantalla, fundidos, o un degradado por líneas (niebla, agua, noche). No
   cuesta CPU. Ya hay `gfx_rgb8` y `copper_*`.
2. **Luz por tiles:** cada tile del mapa se dibuja en uno de N niveles de luz, precalculados al cargar. Con AGA
   caben 32 colores por 8 niveles en 256 colores: el nivel 3 del color 5 es otro índice de la paleta. Cada luz
   (antorcha, jugador) ilumina los tiles cercanos según la distancia. Cuesta memoria (N copias del tileset) y
   CPU solo al cambiar el nivel de un tile.
3. **RTG con color verdadero:** mezcla de verdad, con la CPU. Lento salvo en máquinas rápidas: opcional.

Las físicas también se quedan en lo que cabe:
- cajas alineadas (AABB) contra el mapa de tiles, para plataformas y vista cenital;
- cajas y círculos entre sí, con una rejilla para no comparar todos contra todos;
- cuerpos con velocidad, gravedad y rebote.

Nada de giros ni de pilas de cajas que se apoyan unas en otras.

## 3. La biblioteca (aparte de Forja y de Dash)

Va en dos capas. Se puede usar solo la de abajo, como pygame, o las dos, como Godot.

### Capa 1: piezas sueltas (como pygame)

| Pieza | Qué hace | Sobre qué builtins |
|---|---|---|
| Pantalla | Abre la pantalla del juego (modo, colores, doble búfer) y la presenta en cada fotograma | `screen_open_custom`, `rtg_open_screen`; doble búfer: falta (25) |
| Imagen | Carga IFF de Forja, recorta fotogramas, dibuja con o sin máscara | `bitmap_*`, `bob_*` |
| Rect | Rectángulo con choques, unión e intersección, en Dash puro | ninguno |
| Reloj | Espera al siguiente fotograma y cuenta los que se perdieron | `wait_vblank`, `time_ms` |
| Entrada | Teclado, ratón, joystick (y pad CD32) como estado y como eventos | `key_*`, `joy_*`, `mouse_*`; pad CD32: falta |
| Sonido | Efectos en un canal libre y música MOD a la vez | `sound_*`, `music_*`; reservar canales: falta |
| Sprite y Grupo | Imagen, posición, `actualizar()`; los grupos dibujan por capas y miran choques | Dash puro sobre lo de arriba |
| Mapa | Tiles de un tileset de Forja, scroll y choques con el mapa | `tilemap_draw`: falta (F) |

Ejemplo (los nombres son una propuesta, ver decisiones al final):

```
import "juego/juego.dash"

Main
    p = pantalla_abrir(320, 256, 5, "Pong")
    pala = Sprite(imagen_cargar("pala.iff"), Rect(10, 100, 8, 32))
    reloj = Reloj(50)
    while not tecla_pulsada(TECLA_ESC)
        if joy_up(1)
            pala.rect.y = pala.rect.y - 3
        end
        pantalla_borrar(p, 0)
        pala.dibujar(p)
        pantalla_mostrar(p)
        reloj.esperar()
    end
end
```

### Capa 2: árbol de nodos y escenas (como Godot)

Dash ya tiene lo necesario:
- `interface`, para que cada tipo de nodo tenga sus propios métodos;
- `weak` para el puntero al padre, para no hacer ciclos;
- listas de nodos.

Los nodos:
- **Nodo:** nombre, hijos, padre (`weak`), y `listo()`, `proceso()`, `fisica()` y `dibujar()`.
- **Nodo2D:** posición, escala entera y capa.
- **Sprite y SpriteAnimado:** imagen de Forja; las animaciones salen de la velocidad guardada en el IFF.
- **SpriteHardware:** usa un sprite de hardware en vez de un BOB. Es lo que hay que usar para el jugador y las
  balas.
- **Mapa:** tiles y capas, del editor de mapas (F).
- **Camara:** sigue a un nodo con límites. Mueve el scroll de hardware si hay, o el mapa si no.
- **Cuerpo:** se mueve y choca con el mapa y con otros cuerpos. Lleva `mover_y_deslizar()`, como `move_and_slide`
  de Godot.
- **Area:** detecta quién entra y quién sale. No empuja.
- **Forma:** caja o círculo, hija de un Cuerpo o de un Area.
- **Luz:** punto con radio e intensidad, para el camino 2 de las luces.
- **Sonido2D:** un efecto que suena cuando se le pide.
- **Temporizador:** avisa al cabo de un tiempo.

Cómo corre:
- **El bucle:** en cada fotograma, entrada, luego `fisica()` a paso fijo (una o dos veces si se va con retraso),
  luego `proceso()`, luego `dibujar()` de atrás adelante por capas, y luego presentar.
- **Las señales:** en lugar de conectar funciones (las lambdas de Dash no ven variables locales), cada nodo
  recibe `senal(nombre, quien, dato)`. Al conectar se dice qué nodo escucha a cuál, y la cola de señales se
  reparte una vez por fotograma.
- **Lo que hace el usuario:** un `struct` suyo que cumple `Nodo` (o envuelve un Cuerpo). Ejemplo:

```
struct Jugador: Nodo
    cuerpo: Cuerpo
    func fisica()
        if joy_left(1)
            self.cuerpo.vx = Fixed(-2)
        end
        self.cuerpo.mover_y_deslizar()
    end
    func senal(nombre: String, quien: Nodo, dato: Int)
        if nombre == "moneda"
            puntos = puntos + 1
        end
    end
end
```

## 4. Escenas en fichero

- **Formato:** JSON, como `.dashui`, con extensión propia (propuesta: `.escena`). Cada nodo lleva tipo, nombre,
  propiedades, hijos y, si quiere, su script (un `struct` de Dash). Una escena puede meter otra: es un nodo cuyo
  tipo es la ruta de su fichero.
- **Sin intérprete:** igual que `import "ventana.dashui"` crea la ventana, `import "nivel1.escena"` crearía una
  función que monta el árbol, con los structs del usuario donde la escena los pide. Eso es una pieza del
  compilador de Dash, en los dos caminos (directo a hunk y `--gcc`), como ya se hizo con `.dashui`. Hasta
  entonces, Forja puede escribir esa función como un `.dash` generado.
- **Lo que no cambia en el fichero** (rutas de imágenes, mapas) se carga al empezar. Lo que se edita en el
  inspector son las propiedades iniciales.

## 5. En Forja

- **El editor de escenas,** una pestaña como el editor de ventanas: a la izquierda el árbol de nodos (añadir,
  quitar, mover, instanciar otra escena), a la derecha el inspector con las pestañas que ya tiene el editor de
  sprites, y en medio la vista.
- **La vista:** la escena colocada con el render de verdad del Amiga (sprites, mapa, luces) y sin la lógica. Se
  mueven los nodos con el ratón. Ejecutar (Amiga-E) compila y corre el juego de verdad.
- **Encaje con lo demás:**
  - el editor de sprites da las imágenes y animaciones de Sprite y SpriteAnimado;
  - el de mapas (F) da Mapa;
  - la vista de depuración de juegos (tarea 27) enseña las formas de choque y las velocidades mientras corre;
  - un doble clic en un nodo con script abre su `.dash`, como ya hace la extensión de VS Code de un evento del
    `.dashui` a su código.

## 6. Fases (cada una acaba con un juego de ejemplo que funciona)

1. **Capa 1 mínima:** pantalla, imagen, rect, reloj, entrada y sprite. Se mide lo que cuesta cada cosa en A500 y
   A1200 y se apunta. Ejemplo: Pong.
2. **Mapas y cámara:** el editor de mapas de Forja (F), `tilemap_draw` y el scroll. Ejemplo: un nivel que se
   recorre.
3. **Capa 2:** nodos, bucle con paso fijo, Cuerpo, Area y señales, escritos en Dash. Ejemplo: plataformas con
   enemigos y monedas.
4. **Escenas en fichero** y el editor de escenas en Forja (primero Forja genera el `.dash`; luego el `import` del
   compilador).
5. **Luces:** paleta y copper, y luego luz por tiles. Ejemplo: una cueva con antorchas.
6. **Sonido y pulido:** efectos sobre la música, partículas sencillas y un AnimationPlayer pequeño (mover y
   cambiar propiedades a lo largo del tiempo).

**Builtins que pide, con los que ya salieron en el plan:**
- doble búfer de pantalla (25);
- pintar una imagen de lápices de golpe (15b);
- soltar lápices (15c);
- colores de 8 bits para sprites (16);
- colores del fichero (17);
- `tilemap_draw` (F);
- scroll de hardware;
- reservar canales de sonido para efectos con la música sonando;
- pad CD32 (`lowlevel.library`);
- `import` de `.escena` en el compilador.

## 7. Decisiones del usuario (2026-11-02)

1. **Nombre: Fragua.** Biblioteca aparte (repo propio, propuesta), que se instala junto a Dash.
2. **Máquina mínima: el A1200**; el A500 funciona con menos cosas en pantalla.
3. **API en inglés**, como pygame, Godot y los builtins de Dash. Los ejemplos de este documento, escritos en
   castellano, se pasan al inglés cuando empiece la fase 1.
4. **Con modo que se adueña del hardware**, además del modo amigable con el sistema. Si falla, cuelga el Amiga:
   ese modo necesita salir siempre limpio (devolver el sistema) y probarse en el emulador antes de nada.
5. **Pendiente:** cómo se compilan las escenas. Explicado al usuario el 2026-11-02; falta su respuesta.

## Preguntas que se hicieron

1. **Nombre y sitio de la biblioteca.** Un repo propio de FreeMEM (propuestas: Yunque, Fragua, Brasa; van con
   Forja) o una carpeta de `lib/` dentro de Dash. Lo pedido fue "aparte": la propuesta es un repo propio, que se
   instala junto a Dash.
2. **Máquina mínima.** Propuesta: A1200 (68020 y AGA) como base, a 50 Hz; el A500 funciona con menos cosas en
   pantalla, a 25 Hz si hace falta. ¿O el A500 como base de verdad?
3. **Idioma de la API.** Los builtins de Dash están en inglés (`sprite_load`) y Forja está escrita en castellano.
   ¿La biblioteca en castellano, como en los ejemplos de arriba, en inglés como pygame y Godot, o en los dos?
4. **Amigable con el sistema o sin él.** Propuesta: siempre con el sistema (ventana o pantalla propia, el
   Workbench sigue vivo), con un modo opcional que se queda con el hardware para lo más exigente. Ese modo es
   arriesgado: si falla, se cuelga el Amiga.
5. **Escenas compiladas:** ¿se pide ya a Dash el `import` de `.escena`, o se empieza con el `.dash` que genera
   Forja?
