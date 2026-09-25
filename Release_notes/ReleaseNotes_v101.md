## Release notes v1.0.1 (September 2026)

### New features
- The "distortion" post-processing shader (barrel distortion of the whole stimulus, `QDSpy_useDistort` in `QDSpy_global.py`) now actually works end-to-end; it had been present but effectively untested/unused before this release.

### Fixed issues
- Shader parameters that change while a stimulus is running (e.g., moving-grating properties) stopped updating after the first scene and appeared frozen. Caused by a `pyglet` 2.x `Group`-identity quirk: `pyglet` compares/hashes rendering groups by `(class, order, parent)`, not by object identity, so the fresh group QDSpy creates for each scene could get silently aliased to the previous scene's (not yet pruned) group, whose shader/uniform state was never updated again.
- Parts of the previous stimulus remained visible for a while when starting the next one while using the distortion shader. Each stimulus run opens its window in a fresh process; the first presented frame could be delayed enough (extra shader compilation and frame-buffer setup for distortion) that the OS kept showing the previous process's last frame in the meantime. A blank frame is now presented immediately after window creation, before the slower stimulus/shader setup runs.
- Startup crash (`TypeError: can only concatenate str (not "tuple") to str`) logging the OpenGL version, from a `pyglet` 2.x API change (`GLInfo.get_version()` now returns a `(major, minor)` tuple; use `get_version_string()` instead).
- The distortion frame buffer's texture was being reallocated every single frame, right before the `glClear()` meant to zero it, briefly leaving its content undefined each frame.
- All stimulus shaders (`Shader/*.cl`) failed to compile (e.g., `syntax error, unexpected '('`, `undefined variable "position"`, `round requires "#version 130"`). The `#version` directive is on the first line of each `.cl` file, outside the `ShaderVertexStart/End` and `ShaderFragmentStart/End` blocks, so the shader file parser (`QDSpy_core_shader.py`) discarded it and the driver fell back to GLSL 1.10. The parser now places a file-level `#version` line at the start of both the vertex and the fragment shader source.
- `SquareWaveGratingMix2.cl` declared `#version 300`, which is not a valid desktop GLSL version; changed to `#version 400`, like the other desktop shaders.
- The GLSL ES (`#version 310 es`) shaders (`SQUARE_WAVE_GRATING_MIX4`, `SQUARE_WAVE_GRATING_MIX_RP5`, `SINE_WAVE_GRATING_MIX_RP5`) failed to compile (`OpenGL/ES requires precision specifier on this float type`), because GLSL ES has no default float precision in fragment shaders. For `es` versions, the parser now adds `precision highp float;` to the fragment shader source, unless the fragment block already declares a float precision.

### Changes:
- `pyglet` upgraded from the legacy `1.5.x` line to `pyglet>=2.1,<3.0`. `pyglet` 2.x dropped the legacy fixed-function OpenGL pipeline (matrix stack, immediate-mode drawing), so `Graphics/renderer_opengl.py` now computes the stage transform explicitly as a `pyglet.math.Mat4` and feeds it as an `mvp` uniform to the shared flat-color batch shader and to every bound per-object (`.cl`) shader.
- All built-in stimulus shaders (`Shader/*.cl`) and the distortion shaders (`Graphics/distort_*`) rewritten from legacy GLSL (`ftransform()`, `gl_Color`, `gl_FragColor`, `gl_ModelViewProjectionMatrix`) to explicit, core-profile-compatible `in`/`out` attributes and uniforms.
- `Graphics/shader_opengl.py`: fixed a pre-existing bug in `uniform_matrixf()` (wrong attribute name) so it works, since it is now used every frame for the per-shader `mvp` uniform.
- `QDSpy_stim_movie.py`, `QDSpy_stim_video.py`: adapted to `pyglet` 2.x's `Sprite.position`, which now requires a 3rd (z) component.
- This is on the `pyglet2` branch (`requires pyglet>=2.1,<3.0`); the `main` branch continues to use the legacy, clamped `pyglet<1.5.6`.

### Open issues:
- The RPi5/GLES variants of the stimulus and distortion shaders were updated for consistency but not verified on actual RPi5 hardware as part of this migration; they compile and link correctly against a desktop OpenGL driver (NVIDIA).
- `QDSpy_useDistort` remains a source-level constant in `QDSpy_global.py` rather than a config-file or GUI option.
