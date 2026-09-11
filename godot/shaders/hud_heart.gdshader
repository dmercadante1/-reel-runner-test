shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){vec4 s=texture(TEXTURE,UV);if(s.r<0.25 || s.r<s.g*1.35)discard;COLOR=s*tint;}
