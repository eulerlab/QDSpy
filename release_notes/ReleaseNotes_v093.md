## 0.93beta (January 2025)  
- Experimental and master branches merged

#### Changes:
- Path issues under Linux (hopefully) solved by collecting all file path related routines in one place (`QDSpy_file_support.py`) and by switching to `pathlib` for path handling.
- Dependencies between modules further untangled, such as `Log` has been moved into its own module; GUI-related methods have been moved from `QDSpy_GUI_support` to `QDSpy_GUI_main.py`; new `QDSpy_app.py` module, on which the GUI app and the MQTT app are based
- More `pyglet` calls encapsulated in `renderer_opengl.py` 