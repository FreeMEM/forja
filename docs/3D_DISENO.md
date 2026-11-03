# Juegos en 3D con MiniGL: diseño

Estado: propuesta para revisar (2026-11-03). Aún no hay código. Las decisiones que son del usuario están al final.
Lo pedido: "también vamos a crear juegos en 3D con minigl".

## 1. Qué es MiniGL hoy en el Amiga clásico

MiniGL es una parte de OpenGL para el Amiga, pensada para portar juegos 3D. En 2026 se ha movido mucho:

- **minigl.library compartida**, de Steffen "MagicSN" Häuser. Está basada en MiniGL 1.2, con extensiones, y va con
  la licencia Hyperion MiniGL Open Source License. Trae un SDK para programas nuevos: las cabeceras `mgl/gl.h` y
  `libraries/minigl_dispatch.h`, `libminigl.a` y `<proto/minigl.h>`, con `MiniGLOpen()` y `MiniGLClose()`. Antes
  era estática; los juegos viejos hay que recompilarlos. [1]
- **PiStorm3D**, de Dennis Boon: MiniGL acelerada con la GPU de la Raspberry Pi (VideoCore V3D), en el PiStorm32
  con una Pi 4, una CM4 o una 4B. No necesita Warp3D. Se entregó en septiembre de 2026 y está en Aminet desde
  octubre. Pide AmigaOS 3.x y RTG (Picasso96 o CyberGraphX). El PiStorm3 no vale; hay versiones para Pi3 y para
  Radeon 9200 en desarrollo, fuera del proyecto. [1][2]
- **MiniGL Classic**, también de Häuser, para las tarjetas 3D clásicas (CyberVision 64/3D, tarjetas PCI) y para
  QuarkTex, un Warp3D para WinUAE. Serkan Dursun hace QuarkTex NG, más rápido. [2]
- **Wazp3D**, de Alain Thellier: un Warp3D por software, sin hardware 3D, para 68020-40, y lento. Hay una versión
  para el 68080 de Vampire. [3][4]
- **WarpMiniGL**, de arczi84: el camino al revés, Warp3D encima de MiniGL, para que corran los juegos de Warp3D en
  el PiStorm. LGPL-3.0. [5]

**Juegos ya portados** (según amiga-news.de): Quake 1, 2 y 3, Return to Castle Wolfenstein, Unreal, Doom64,
Carmageddon, WipeOut, Heretic 2, Jedi Knight II, Jazz Jackrabbit 2 y OpenLara. Hay más en camino. El autor da
Quake 1 a unos 188 fotogramas por segundo en 640x480 en el PiStorm; son sus cifras, sin comprobar. [2]

**LightWave:** en 2026 también salió LightwaveRTG, una versión de LightWave 5 para el Amiga con RTG y 24 bits,
hecha con ingeniería inversa por 70lk13n. Los iconos nuevos son de SantiDarkG. Lo que haga Santi con MiniGL y su
modeler no sale en las fuentes públicas: hacen falta sus mensajes. [6]

## 2. Lo que eso significa para Dash y Fragua

- **El 3D de verdad pide una máquina con aceleración:** PiStorm32 con una Pi 4, una tarjeta 3D clásica o un
  Vampire. En un A1200 con 68020 y sin tarjeta, solo hay Wazp3D por software, que es lento. Así que el 3D va
  **aparte de la base de Fragua** (A1200): "Fragua 3D", que pide RTG y MiniGL.
- **Los números:** MiniGL trabaja con coma flotante. En un PiStorm con Emu68 la FPU es rápida; en un 68020 sin FPU
  es lentísima. Fragua 3D usa `Float`, a diferencia de la 2D, que usa `Fixed`.
- **Probar en el emulador:** MiniGL Classic encima de un Warp3D (Wazp3D en FS-UAE, QuarkTex en WinUAE) debería
  dejar probar sin PiStorm, aunque lento. Está sin comprobar: es lo primero que hay que hacer.

## 3. Cómo lo usaría Dash

- **Builtins `gl_*` en el runtime de Dash** (en inglés, como los demás): abrir el contexto de MiniGL en una
  pantalla o ventana RTG y las llamadas de OpenGL que trae MiniGL 1.2, en los dos caminos de `./dash`. Así lo
  usan Fragua 3D y cualquier programa de Dash. Si la biblioteca no está, `gl_open()` da falso y el programa lo
  dice; nunca un cuelgue.
- **Fragua 3D encima,** en inglés (decisión del usuario):
  - nodos `Camera3D`, `MeshInstance3D`, `Light3D` y `Node3D`, como en Godot;
  - carga de modelos;
  - el mismo bucle con paso fijo que la 2D;
  - choques sencillos (esferas y cajas) para empezar.
- **Modelos:** el formato de LightWave (`.lwo`, LWOB y LWO2) es público y se puede leer en Dash. También OBJ, que
  es texto. Si el modeler de Santi guarda en otro formato, se añade cuando se sepa cuál.

## 4. En Forja

- **Vista 3D** en el editor de escenas (`docs/JUEGOS_DISENO.md`): la escena con MiniGL en una ventana o pantalla
  RTG, con la cámara movida con el ratón. Si la máquina no tiene MiniGL, Forja enseña el árbol y el inspector, sin
  la vista.
- **Visor de modelos:** abrir un `.lwo` u `.obj` en una pestaña para verlo girar. Es la primera herramienta 3D, y la
  más útil para el modeler de Santi.

## 5. Fases

1. **Comprobar la base:** MiniGL Classic con Wazp3D en FS-UAE. Si funciona, un programa de C mínimo que pinte un
   triángulo. Si no funciona, se prueba en un PiStorm de verdad o en WinUAE con QuarkTex, y se apunta.
2. **Builtins `gl_*` en Dash.** Ejemplo: un cubo que gira.
3. **Cargar `.lwo` y `.obj`.** Ejemplo y visor en Forja.
4. **Fragua 3D:** nodos, cámara, luces y bucle. Ejemplo: un pasillo para recorrer.
5. **Vista 3D** en el editor de escenas de Forja.

## 6. Decisiones para el usuario

**Decidido el 2026-11-03:** 1 (PiStorm32 con Pi 4 primero) y 2 (Fragua 3D aparte). Sin respuesta todavía: 3 (los mensajes de Santi) y 4 (si tiene un PiStorm32).

1. **Máquina para el 3D:** ¿primero el PiStorm32 con Pi 4 (donde está la aceleración y los juegos de 2026), y
   luego las tarjetas clásicas y Vampire?
2. **¿Fragua 3D como parte aparte de Fragua** (propuesta), o dentro desde el principio?
3. **Los mensajes de Santi:** para saber qué formato usa su modeler y si se puede colaborar (por ejemplo, que
   Forja y Fragua lean sus modelos). Hace falta que el usuario los pase.
4. **¿Tienes un PiStorm32 con Pi 4** para probar? El emulador no da la aceleración: sin máquina real, el 3D se
   prueba solo por software.

## Fuentes

1. [MiniGL_Library_68k (Steffen Häuser): README](https://github.com/SteffenHaeuser/MiniGL_Library_68k)
2. [amiga-news.de, 8/10/2026: 3D hardware acceleration: Pistorm 3D, MiniGL Classic, new game ports](https://www.amiga-news.de/en/news/AN-2026-10-00035-EN.html)
3. [Aminet: driver/video/Wazp3D](https://aminet.net/package/driver/video/Wazp3D)
4. [Aminet: driver/video/VampireWazp3D](https://aminet.net/package/driver/video/VampireWazp3D)
5. [WarpMiniGL (arczi84)](https://github.com/arczi84/WarpMiniGL)
6. [Generation Amiga, 29/8/2026: LightWave 3D getting native RTG support](https://www.generationamiga.com/2026/08/29/the-amiga-lightwave-3d-that-helped-make-babylon-5-is-getting-native-rtg-support/)
   y [The Oasis BBS: Amiga LightWaveRTG](https://theoasisbbs.com/amiga-lightwavertg-brings-24-bit-graphics-to-the-classic-3d-package/)
