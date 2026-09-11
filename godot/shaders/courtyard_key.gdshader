shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){
 vec4 s=texture(TEXTURE,UV);
 float key=min(s.r,s.b)-s.g;
 if(key>0.12 || s.a<0.5)discard;
 COLOR=vec4(s.rgb*tint.rgb,s.a*tint.a);
}
