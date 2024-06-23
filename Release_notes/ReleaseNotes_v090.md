## Release notes v0.90 (June 2024)

### Fixed issues
- Spot probe tool works again
- `movie_water.py` stimulus fixed and move error handling improved
- Issues with Python v3.12 and `configparser` fixed
- `hid.cp312-win_amd64.pyd` added to `Devices\`

### Changes:
  - `QDSpy_GUI_main.py`
    - Reformatted (using Ruff)
    - Small fixes for PEP violations
    - `int()` where Qt5 does not accept float

  - `QDSpy_global.py`
    - Fix for breaking change in `configparser` (see `QDSpy_config.py`): `QDSpy_rec_setup_id` cannot be `None` -> changed to -1 for no setup defined

  - `QDSpy_stim.py`
    - Reformatted (using Ruff)
    - Small fixes for PEP violations  
    - Bug fix related to correct error handling for movie compilation errors

  - `QDSpy_config.py`           
    - Reformatted (using Ruff)
    - Fix for breaking change in `configparser`; now using `ConfigParser` instead of `RawConfigParser`
    - Small fixes for PEP violations  
    - Set `rec_setup_id` to `None` if < 0

  - `QDSpy_core.py`
    - Reformatted (using Ruff)
    - Catch if `conda` is not installed

  - `QDSpy_core_presenter.py`
    - Reformatted (using Ruff)  
    - Improved error message for movie errors

  - `Graphics/renderer_opengl.py`
    - Reformatted (using Ruff)
    - Fixed a bug that prevented using the probe spot tool

### Open issues:
  - Stimulus containing a wait raises an uncaught error if no respective hardware is connected (e.g., stimulus `noise_Colored_Wait.py`)


