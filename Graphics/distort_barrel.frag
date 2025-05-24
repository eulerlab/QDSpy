uniform sampler2D framebuffer_texture;
uniform vec2 resolution;

void main() {
    vec2 uv = gl_TexCoord[0].xy;
    
    // Convert to centered coordinates (-1 to 1)
    vec2 p = (uv * 2.0 - 1.0);
    
    // Calculate distance from center
    float r = length(p);
    
    // Barrel distortion parameters
    float k1 = 0.1;  // Primary distortion
    float k2 = 0.1;  // Secondary distortion
    
    // Apply distortion
    float distortion = 1.0 + k1 * r * r + k2 * r * r * r * r;
    vec2 distorted_uv = p * distortion;
    
    // Convert back to texture coordinates (0 to 1)
    distorted_uv = (distorted_uv + 1.0) * 0.5;
    
    // Sample the texture
    vec4 color = texture2D(framebuffer_texture, distorted_uv);
    
    // Debug: mix with coordinate visualization
    vec4 debugColor = vec4(uv.x, uv.y, 0.0, 1.0);
    float debugMix = 0.0;  // 0.0 for no debug overlay, 0.5 for 50% mix
    
    gl_FragColor = mix(color, debugColor, debugMix);
}