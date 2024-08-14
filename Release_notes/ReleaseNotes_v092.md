## Release notes v0.92 (August 2024)

### New features
- Version that can be controlled via MQTT (work in progress)
- New digital I/O device added: "RaspberryPi". It uses by default pins GPIO26 for trigger-in and GPIO27 for marker-out. These pins cannot be changed as these are the only two free pins when using the DLP Lightcrafter 230NP EVM (dldcr203).

### Fixed issues

### Changes:
- Use `colorama` for console colors
- Messages from the worker thread (the one that presents the stimuli) and the host thread (the GUI or the MQTT client) can now be distinguished; worker thread messages start with a `|` character.
- `QDSpy_stim_movie.py` and `QDSpy_stim_video.py` are not anymore directly dependent on `pyglet` by adding helper functions to `renderer_opengl.py`.
- Log instance (`Log`) moved into own module `Libraries\log.helper.py`
- Multiprocessing support now in `Libraries\multiprocess_helper.py`

### Open issues:
- _Linux version:_ When running QDSpy via SSH, `q` does not abort stimulus presentation.
- Error message _`QWindowsContext: OleInitialize() failed:  "COM error 0x80010106: Der Threadmodus kann nicht nach dem Einstellen geändert werden."`_ appears when starting QDSpy. It appears to result from some interaction between `pyglet` v1.5.6 and higher and `PyQt6`. I first thought it has no consequences but then saw that now the file dialog is not working anymore. For now, __make sure that `pyglet` v1.5.5 is used__.- Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)
- __Gamma LUT functionality does not work reliably__. It works with a single screen, but not for all multiple screen configurations. The respective code has not changed, therefore I am unsure of the cause (changed packages, e.g. `pyglet`, `pyqt6` seem not to be responsible). 
- Stimulus containing a __wait__ raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)

## Feature requests
- Being able to save the background color explicitly in the `.pickle` file.
