#version 120

uniform sampler2D texture;
uniform vec2 resolution;

void main() {
    vec2 uv = gl_TexCoord[0].xy;
    vec2 center = resolution * 0.5;
    vec2 toCenter = (uv * resolution - center) / resolution;
    float dist = length(toCenter);
    float theta = atan(toCenter.y, toCenter.x);
    float radius = dist * dist; // Distortion effect
    vec2 distortedUV = center + radius * vec2(cos(theta), sin(theta)) / resolution;
    gl_FragColor = texture2D(texture, distortedUV);
    //gl_FragColor = texture2D(texture, uv);
}