shader_type canvas_item;
render_mode unshaded, blend_add;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){vec4 s=texture(TEXTURE,UV);COLOR=vec4(s.rgb*tint.rgb,tint.a*s.a);}
