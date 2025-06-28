## 0.9.6 (started) - experimental branch
- Raspberry Pi/Linux: 
   - Some small improvements to the GUI (sort stimulus names alphabetically and show selected stimulus name w/o path)
   - Account for differences in `hid` (untested)
   - Issue with not centred movies when `bool_use3dtextures == 1` fixed
- Better error handling in `renderer_opengl.py` 
- Some bug fixes:
  - Fixed error in `GetVideoParameters`
  - Adapted to current `moviepy` (>= version 2)
  - Fixed a few bugs that prevented restarting the same video
  - Added missing error message strings

#### New feature(s):
- [Batch mode](https://github.com/eulerlab/QDSpy/wiki/Batch-mode): This allows presenting a list of stimuli in one batch.