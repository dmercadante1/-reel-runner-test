shader_type canvas_item;
render_mode unshaded;
varying vec4 tint;
void vertex(){tint=COLOR;}
void fragment(){
 vec4 source=texture(TEXTURE,UV);
 // Key only the magenta hue; retain dark burgundy vampire clothing.
 // Include blue-purple key spill while preserving red-dominant cloth.
 if(min(source.r,source.b)-source.g>0.025 && source.b>source.r*0.65)discard;
 COLOR=source*tint;
}
