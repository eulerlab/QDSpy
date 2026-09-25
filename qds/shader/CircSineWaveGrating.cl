#version 400

//#QDS ShaderName          =CIRC_SINE_WAVE_GRATING
//#QDS ShaderParamNames    =perLen_um; perDur_s; minRGB; maxRGB
//#QDS ShaderParamLengths  =1;1;4;4
//#QDS ShaderParamDefaults =0.0; 1.0; (0,0,0,255); (255,255,255,255)
//
//#QDS ShaderVertexStart
// ----------------------------------------------------------------------
layout(location = 0) in vec2 position;

uniform mat4 mvp;

void main()
{
  gl_Position    = mvp * vec4(position, 0.0, 1.0);
}
// ----------------------------------------------------------------------
//#QDS ShaderVertexEnd

//#QDS ShaderFragmentStart
// ----------------------------------------------------------------------
#define pi    3.141592653589
#define pi2   6.283185307179

out vec4 fragColor;

uniform float time_s;
uniform vec3  obj_xy_rot;
uniform float perLen_um;
uniform float perDur_s;
uniform vec4  minRGB;
uniform vec4  maxRGB;

float         inten, r;
vec4          b;
      
void main() {
  vec4  a      = gl_FragCoord;
  a.x          = a.x -obj_xy_rot.x;
  a.y          = a.y -obj_xy_rot.y;
  r            = sqrt(a.x*a.x +a.y*a.y);
  inten        = (sin((r/perLen_um +time_s/perDur_s) *pi2) +1.0)/2.0;
  fragColor = mix(minRGB, maxRGB, inten);
}
// ----------------------------------------------------------------------
//#QDS ShaderFragmentEnd
