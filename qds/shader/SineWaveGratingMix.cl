#version 400

//#QDS ShaderName          =SINE_WAVE_GRATING_MIX
//#QDS ShaderParamNames    =perLen_um; perDur_s; minRGB; maxRGB
//#QDS ShaderParamLengths  =1;1;4;4
//#QDS ShaderParamDefaults =0.0; 1.0; (0,0,0,255); (255,255,255,255)
//
//#QDS ShaderVertexStart
// ----------------------------------------------------------------------
varying       vec4   vertex_color;

void main() 
{
  gl_Position    = ftransform();
  vertex_color   = gl_Color;
}
// ----------------------------------------------------------------------
//#QDS ShaderVertexEnd

//#QDS ShaderFragmentStart
// ----------------------------------------------------------------------
#define pi    3.141592653589
#define pi2   6.283185307179

in            vec4   vertex_color;

uniform float time_s;
uniform vec3  obj_xy_rot;
uniform float perLen_um;
uniform float perDur_s;
uniform vec4  minRGB;
uniform vec4  maxRGB;

float         inten;
vec4          b;
      
void main() {
  vec4  a      = gl_FragCoord;
  a.x          = a.x -obj_xy_rot.x;
  a.y          = a.y -obj_xy_rot.y;
  b.x          = a.x*cos(obj_xy_rot[2]) -a.y*sin(obj_xy_rot[2]);
  b.y          = a.y*cos(obj_xy_rot[2]) +a.x*sin(obj_xy_rot[2]);
  inten        = (sin(((b.x)/perLen_um +time_s/perDur_s) *pi2) +1.0)/2.0;
  gl_FragColor = mix(minRGB, maxRGB, inten);
  gl_FragColor = mix(gl_FragColor, vertex_color, 0.5);
}
// ----------------------------------------------------------------------
//#QDS ShaderFragmentEnd
