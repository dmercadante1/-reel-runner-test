shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){
 vec4 s=texture(TEXTURE,UV);
 if(s.a<0.6 || min(s.r,s.b)-s.g>0.025)discard;
 COLOR=vec4(s.rgb*tint.rgb,1.0);
}
