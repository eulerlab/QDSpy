#version 400

//#QDS ShaderName          =SQUARE_WAVE_GRATING
//#QDS ShaderParamNames    =perLen_um; perDur_s; minRGB; maxRGB
//#QDS ShaderParamLengths  =1;1;4;4
//#QDS ShaderParamDefaults =0.0; 1.0; (0,0,0,255); (255,255,255,255)
//
//#QDS ShaderVertexStart
// ----------------------------------------------------------------------
void main() 
{
  gl_Position    = ftransform();
}
// ----------------------------------------------------------------------
//#QDS ShaderVertexEnd

//#QDS ShaderFragmentStart
// ----------------------------------------------------------------------
#define pi    3.141592653589
#define pi2   6.283185307179

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
  inten        = ((ceil(sin(((b.x)/perLen_um +time_s/perDur_s) *pi2))+floor(sin(((b.x)/perLen_um +time_s/perDur_s) *pi2)))+1)/2;
  gl_FragColor = mix(minRGB, maxRGB, inten);
}
// ----------------------------------------------------------------------
//#QDS ShaderFragmentEnd
