#version 400

//#QDS ShaderName          =SPHERE
//#QDS ShaderParamNames    =Dummy
//#QDS ShaderParamLengths  =1
//#QDS ShaderParamDefaults =0.0
//
//#QDS ShaderVertexStart
// ----------------------------------------------------------------------
//attribute vec4 position;
//attribute vec2 texcoord;

//varying   vec2 v_texcoord;
varying     vec4 vertex_color;

void main() {
    gl_Position = ftransform();
    vertex_color = gl_Color;
    //gl_Position = position;
    //v_texcoord = texcoord;
}
// ----------------------------------------------------------------------
//#QDS ShaderVertexEnd

//#QDS ShaderFragmentStart
// ----------------------------------------------------------------------
in vec4    vertex_color;

//uniform  sampler2D texture;
uniform    float     dummy;

void main() {
    vec4  a = gl_FragCoord;
    //vec2 uv = gl_TexCoord[0].xy;
    //gl_FragColor = texture2D(texture, uv);
    gl_FragColor = (0,0,0,255);
    gl_FragColor = mix(gl_FragColor, vertex_color, 0.2);
}
// ----------------------------------------------------------------------
//#QDS ShaderFragmentEnd
