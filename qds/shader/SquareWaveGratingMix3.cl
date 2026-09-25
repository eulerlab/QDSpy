#version 400

//#QDS ShaderName          =SQUARE_WAVE_GRATING_MIX3
//#QDS ShaderParamNames    =perLen_um; perDur_s; minRGB; maxRGB; mixA
//#QDS ShaderParamLengths  =1;1;4;4;1
//#QDS ShaderParamDefaults =0.0; 1.0; (0,0,0,255); (255,255,255,255); 0.5
//
//#QDS ShaderVertexStart
// ----------------------------------------------------------------------
layout(location = 0) in vec2 position;
layout(location = 1) in vec4 colors;

out vec4 vertex_color;

uniform mat4 mvp;

void main()
{
  gl_Position    = mvp * vec4(position, 0.0, 1.0);
  vertex_color   = colors;
}
// ----------------------------------------------------------------------
//#QDS ShaderVertexEnd

//#QDS ShaderFragmentStart
// ----------------------------------------------------------------------
#define pi    3.141592653589
#define pi2   6.283185307179
// aspect ratio y/x
#define ar_xy 2.0

in            vec4   vertex_color;
out           vec4   fragColor;

uniform float time_s;
uniform vec3  obj_xy_rot;
uniform float perLen_um;
uniform float perDur_s;
uniform vec4  minRGB;
uniform vec4  maxRGB;
uniform float mixA;

float         inten;
float         l, rot_deg;
vec4          b;

void main() {
  vec4  a      = gl_FragCoord;
  a.x          = a.x -obj_xy_rot.x;
  a.y          = a.y -obj_xy_rot.y;
  b.x          = a.x *cos(obj_xy_rot[2]) -a.y*sin(obj_xy_rot[2]);
  b.y          = a.y *cos(obj_xy_rot[2]) +a.x*sin(obj_xy_rot[2]);
  rot_deg      = obj_xy_rot[2] /pi2 *360;
  l            = perLen_um *(ar_xy +(1.-ar_xy) *abs(mod(rot_deg, 180.) -90.) /90.);
  inten        = round((sin(((b.x)/l +time_s/perDur_s) *pi2) +1.0)/2.0);
  fragColor = mix(minRGB, maxRGB, inten);
  fragColor = mix(fragColor, vertex_color, mixA);
}
// ----------------------------------------------------------------------
//#QDS ShaderFragmentEnd
