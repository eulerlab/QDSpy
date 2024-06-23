## Release notes v0.91 (June 2024)

### Fixed issues
- Now works with the latest release of `pyglet` version 1 (v.1.5.29)
- GUI migrated to `PyQt6`

### Changes:
- `QDSpy_GUI_main.py`, `QDSpy_GUI_main.ui`, `QDSpy_GUI_support.py`
  - Migrated to `PyQt6`
- `QDSpy_global.py`, 
  - `QDSpy_useGUIScalingForHD` introduced to control if QDSpy attempts to rescale the GUI for high screen resolutions. If off for `PyQt6`. 
- `QDSpy_multiprocessing.py`
  - Reformatted (using Ruff)
  - Small bug fix
- `Graphics/renderer_opengl.py`
  - Fixed a bug when using `pyglet` higher than v1.5.7

### Open issues:
- Error message `QWindowsContext: OleInitialize() failed:  "COM error 0x80010106: Der Threadmodus kann nicht nach dem Einstellen geändert werden."` appears when starting QDSpy. It appears to result from some interaction between `pyglet` and `PyQt6` but seems to have no consequences.
- Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)


