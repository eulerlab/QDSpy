## 0.95beta (May 2025) - experimental merged to main branch
- Switched to [`uv`](https://github.com/astral-sh/uv) for [installation procedure](https://github.com/eulerlab/QDSpy/wiki/Installation-under-Windows#installation-under-windows-11-using-uv-recommended)
- Linux compatibility (with a focus on the Raspberry Pi 5) was improved
- Helper functions for `QDSpy_stim_movie.py` added to remove direct calls to `pyglet`  in that module    

#### New feature(s):
- [MQTT version](https://github.com/eulerlab/QDSpy/wiki/Running-QDSpy-as-MQTT-client): `QDSpy_MQTT_main.py` is a headless version of QDSpy that can be controlled via [MQTT](https://en.wikipedia.org/wiki/MQTT) messages. Provided is also a simple test client (`test_mqtt.py`). 
- Distortion shader (experimental): This feature applies a "distortion" shader to the final stimulus (w/p changing the stimulus scripts), which can be used to adapt the stimulus presentation geometrically to the shape of the projection surface (e.g., to the inside of a sphere). Currently, this feature can only be activated in `QDSpy_global.py`:
   ```
   # Distortion shader
   QDSpy_useDistort            = False
   QDSpy_distort_vertex        = "distort_vertex_shader.glsl"
   QDSpy_distort_fragment      = "distort_barrel.frag"
   ```
   The shader program `distort_barrel.frag` contains the distortion code (here, a barrel distortion) that needs to be adapted to the projection geometry.