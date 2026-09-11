shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex() { tint = COLOR; }
void fragment() {
 vec4 source = texture(TEXTURE, UV);
 if (min(source.r, source.b) - source.g > 0.02) discard;
 COLOR = source * tint;
}
