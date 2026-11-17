# Para las pruebas: pone una extensión de Forja, compilada, en el disco del emulador (DH0:Prueba/Extensiones/<nombre>)
# y le dice a Forja que las busque ahí (ENV:Forja/extensiones). Se usa desde los .sh, con $dash, $aqui y $tmp:
#
#   . "$aqui/tests/extension.sh"
#   extension Sprites editor_sprites        # extensiones/Sprites/editor_sprites.dash -> Extensiones/Sprites/Sprites
#   extension Inferencia copiloto Copiloto  # el programa con otro nombre (programa = en su manifiesto)
extension() {
  mkdir -p "$tmp/sys/Prueba/Extensiones/$1"
  cp "$aqui/extensiones/$1/manifiesto.txt" "$tmp/sys/Prueba/Extensiones/$1/"
  "$dash/dash" "$aqui/extensiones/$1/$2.dash" -o "$tmp/sys/Prueba/Extensiones/$1/${3:-$1}"
  if ! grep -q "Forja/extensiones " "$tmp/sys/S/Startup-Extra" 2>/dev/null; then
    { echo "C:MakeDir >NIL: ENV:Forja"; echo "SetEnv Forja/extensiones DH0:Prueba/Extensiones"; } >> "$tmp/sys/S/Startup-Extra"
  fi
}
