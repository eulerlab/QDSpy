## Release notes v0.91 (June 2024)

### Fixed issues
- Now works with the latest release of `pyglet` version 1 (v.1.5.29)
- GUI migrated ot `PyQt6`

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
  - Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)


