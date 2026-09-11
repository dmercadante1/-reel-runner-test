shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){
 vec4 s=texture(TEXTURE,UV);
 if(min(s.r,s.b)-s.g>0.12 || s.a<0.5)discard;
 // Alpha encodes atmospheric contrast only: physical objects remain opaque.
 COLOR=vec4(mix(vec3(0.11,0.16,0.24),s.rgb*tint.rgb,tint.a),1.0);
}
