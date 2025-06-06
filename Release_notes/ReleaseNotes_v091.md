## Release notes v0.91 (July 2024)

### New features
- GUI migrated to `PyQt6`, now supporting dark mode.
- Progress shown in status bar during stimulus presentation.
- Added the option to play sounds, e.g., at the start and end of a stimulus presentation (see `QDSpy_global.py`, for settings) 

### Fixed issues
- Fixed an issue with loading gamma LUTs
- Fixed finding shader files when run from the command line
- Running stimuli from the command line (w/o GUI) fixed
- Now works with a newer release of `pyglet` version 1 (v1.5.5 instead of v1.4.x)
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
  - Fixed a bug when using `pyglet` v1.5.x (still fixed to v1.5.5, see below)

### Open issues:
- Linux version: Cannot abort qith `Q`
- Error message `QWindowsContext: OleInitialize() failed:  "COM error 0x80010106: Der Threadmodus kann nicht nach dem Einstellen geändert werden."` appears when starting QDSpy. It appears to result from some interaction between `pyglet` v1.5.6 and higher and `PyQt6`. I first thought it has no consequences but then saw that now the file dialog is not working anymore. For now, make sure that `pyglet` v1.5.5 is used.
- Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)

### Notes on the 
- at [240 Hz](https://e2e.ti.com/support/dlp-products-group/dlp/f/dlp-products-forum/1054640/dlpdlcr230npevm-can-i-use-960x640-240hz-with-the-provided-firmware) - untested
- regarding running the DLPDLCR2000EVM (a different DLP) with [bookworm](https://e2e.ti.com/support/dlp-products-group/dlp/f/dlp-products-forum/1281455/dlpdlcr2000evm-raspberry-pi-configuration-using-dtoverlay-vc4-kms-dpi-generic-raspberry-pi-os-12-bookworm)

