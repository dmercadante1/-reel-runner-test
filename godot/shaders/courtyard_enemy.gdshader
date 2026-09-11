shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){
 vec4 s=texture(TEXTURE,UV);
 if(min(s.r,s.b)-s.g>0.025 && s.b>s.r*0.65)discard;
 COLOR=tint.r<0.0?vec4(0.15,0.8,1.0,s.a*tint.a):s*tint;
}
