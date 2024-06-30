## Release notes v0.91 (June 2024)

### New features
- GUI migrated to `PyQt6`, now supporting dark mode.
- Progress shown in status bar during stimulus presentation.
- Added the option to play sounds, e.g., at the start and end of a stimulus presentation (see `QDSpy_global.py`, for settings) 

### Fixed issues
- Now works with the latest release of `pyglet` version 1 (v.1.5.29)
- GUI migrated to `PyQt6`
- More modules reformatted using `ruff`

### Changes:
- `Graphics/sounds.py` w/ folder `Sounds` now supports audio signals.
- `QDSpy_GUI_main.py`, `QDSpy_GUI_main.ui`, `QDSpy_GUI_support.py`
  - Migrated to `PyQt6`
  - Fix for font color in log window for dark mode
- `QDSpy_global.py`, 
  - `QDSpy_useGUIScalingForHD` introduced to control if QDSpy attempts to rescale the GUI for high screen resolutions. If off for `PyQt6`. 
- `QDSpy_multiprocessing.py`
  - Small bug fix
- `Graphics/renderer_opengl.py`
  - Fixed a bug when using `pyglet` higher than v1.5.7

### Open issues:
- Running stimuli from the command line (w/o GUI) does not work currently.
- Error message `QWindowsContext: OleInitialize() failed:  "COM error 0x80010106: Der Threadmodus kann nicht nach dem Einstellen geändert werden."` appears when starting QDSpy. It appears to result from some interaction between `pyglet` v1.5.x and `PyQt6` but seems to have no consequences. With `pyglet` v1.4.x the error is gone.
- Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)


