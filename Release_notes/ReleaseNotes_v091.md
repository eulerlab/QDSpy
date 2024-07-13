## Release notes v0.91 (July 2024)

### New features
- GUI migrated to `PyQt6`, now supporting dark mode.
- Progress shown in status bar during stimulus presentation.
- Added the option to play sounds, e.g., at the start and end of a stimulus presentation (see `QDSpy_global.py`, for settings) 

### Fixed issues
- Fixed finding shader files when run from the command line
- Running stimuli from the command line (w/o GUI) fixed
- Now works with the latest release of `pyglet` version 1 (v.1.5.29)
- GUI migrated to `PyQt6`
- More modules reformatted using `ruff`

### Changes:
- Additional dependency: `pygame`
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
- Linux version: Cannot abort qith `Q`
- Error message `QWindowsContext: OleInitialize() failed:  "COM error 0x80010106: Der Threadmodus kann nicht nach dem Einstellen geändert werden."` appears when starting QDSpy. It appears to result from some interaction between `pyglet` v1.5.x and `PyQt6` but seems to have no consequences. With `pyglet` v1.4.x the error is gone.
- Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)

### Notes on the 
- at [240 Hz](https://e2e.ti.com/support/dlp-products-group/dlp/f/dlp-products-forum/1054640/dlpdlcr230npevm-can-i-use-960x640-240hz-with-the-provided-firmware) - untested
- regarding running the DLPDLCR2000EVM (a different DLP) with [bookworm](https://e2e.ti.com/support/dlp-products-group/dlp/f/dlp-products-forum/1281455/dlpdlcr2000evm-raspberry-pi-configuration-using-dtoverlay-vc4-kms-dpi-generic-raspberry-pi-os-12-bookworm)

